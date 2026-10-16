"""Verify original letterhead preservation, full font embedding and PDF page safety."""
import hashlib
import importlib.util
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / '.agents/skills/hejun-design-language'
spec = importlib.util.spec_from_file_location('init_word', SKILL / 'scripts/init_word.py')
word = importlib.util.module_from_spec(spec)
spec.loader.exec_module(word)
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
try:
    import pymupdf
except ImportError:
    pymupdf = None


class WordLetterheadTests(unittest.TestCase):
    def test_source_and_starter_background_parts_identical(self):
        manifest = json.loads((SKILL / 'assets/letterhead/source.json').read_text(encoding='utf-8'))
        source = SKILL / 'assets/letterhead/hejun-shenzhen-original.docx'
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), manifest['source_sha256'])
        with zipfile.ZipFile(source) as original, zipfile.ZipFile(SKILL / 'assets/templates/hejun-starter.docx') as starter:
            for part in manifest['preserve_parts']:
                self.assertEqual(original.read(part), starter.read(part), part)
            document = ET.fromstring(starter.read('word/document.xml'))
            margins = document.find('.//w:sectPr/w:pgMar', NS)
            for name, value in manifest['safe_margins_twips'].items():
                self.assertEqual(margins.get('{' + NS['w'] + '}' + name), str(value))
            self.assertIsNotNone(document.find('.//w:tbl', NS))
            self.assertIsNotNone(document.find('.//w:tblHeader', NS))
            self.assertIsNone(document.find('.//w:titlePg', NS))

    def test_complete_fonts_and_license_embedded_in_word(self):
        with zipfile.ZipFile(SKILL / 'assets/templates/hejun-starter.docx') as archive:
            table = ET.fromstring(archive.read('word/fontTable.xml'))
            family = table.find("w:font[@w:name='HarmonyOS Sans SC']", NS)
            for weight, element in [('Regular', 'embedRegular'), ('Bold', 'embedBold')]:
                embed = family.find('w:' + element, NS)
                key = embed.get('{' + NS['w'] + '}fontKey')
                decoded = word.obfuscate(archive.read('word/fonts/hejun-' + weight.lower() + '.odttf'), key)
                self.assertEqual(decoded, (SKILL / f'assets/fonts/HarmonyOS_Sans_SC_{weight}.ttf').read_bytes())
            license_node = ET.fromstring(archive.read('customXml/hejun-font-license.xml'))
            self.assertEqual(license_node.text, (SKILL / 'assets/fonts/LICENSE-readable.txt').read_text(encoding='utf-8'))

    def test_initializer_escapes_title_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'test.docx'
            word.create(path, '<标题 & "测试">')
            with zipfile.ZipFile(path) as archive:
                document = ET.fromstring(archive.read('word/document.xml'))
                self.assertEqual(document.find('.//w:t', NS).text, '<标题 & "测试">')
            original = path.read_bytes()
            with self.assertRaises(FileExistsError):
                word.create(path, 'other')
            self.assertEqual(path.read_bytes(), original)


@unittest.skipIf(pymupdf is None, 'PyMuPDF is required for PDF helper checks')
class PdfLetterheadTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('paper', SKILL / 'scripts/apply_pdf_letterhead.py')
        self.paper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.paper)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.input = self.root / 'input.pdf'
        self.output = self.root / 'output.pdf'

    def test_mixed_page_sizes_keep_searchable_text_inside_letterhead(self):
        source = pymupdf.open()
        for i, (width, height) in enumerate([(595, 842), (960, 540)]):
            page = source.new_page(width=width, height=height)
            page.insert_text((20, 30), f'CONTENT_PAGE_{i+1}', fontsize=12)
        source.set_toc([[1, 'First', 1], [1, 'Second', 2]])
        source.save(self.input)
        source.close()
        self.paper.apply(self.input, self.output)
        safe = pymupdf.Rect(90, 110, 505.32, 661.92)
        with pymupdf.open(self.output) as document, pymupdf.open(SKILL / 'assets/letterhead/hejun-shenzhen-blank.pdf') as background:
            self.assertEqual(len(document), 2)
            self.assertEqual(document.get_toc(), [[1, 'First', 1], [1, 'Second', 2]])
            for i, page in enumerate(document):
                self.assertEqual(page.rect, background[0].rect)
                self.assertIn(f'CONTENT_PAGE_{i+1}', page.get_text())
                boxes = page.search_for(f'CONTENT_PAGE_{i+1}')
                self.assertTrue(all(safe.contains(box) for box in boxes))
                self.assertGreaterEqual(len(page.get_images()), 2)
                # Header and footer pixels match the original, on every page.
                for rect in [pymupdf.Rect(0, 0, page.rect.width, 100), pymupdf.Rect(0, 680, page.rect.width, page.rect.height)]:
                    self.assertEqual(page.get_pixmap(clip=rect).samples, background[0].get_pixmap(clip=rect).samples)

    def test_pdf_refuses_links_and_does_not_write_partial_output(self):
        document = pymupdf.open()
        page = document.new_page()
        page.insert_text((20, 30), 'LINK')
        page.insert_link({'kind': pymupdf.LINK_URI, 'from': pymupdf.Rect(15, 15, 90, 40), 'uri': 'https://example.com'})
        document.save(self.input)
        document.close()
        with self.assertRaisesRegex(ValueError, 'Links'):
            self.paper.apply(self.input, self.output)
        self.assertFalse(self.output.exists())

    def test_pdf_refuses_overwrite_and_repeated_letterhead(self):
        document = pymupdf.open()
        document.new_page().insert_text((20, 30), 'CONTENT')
        document.save(self.input)
        document.close()
        self.paper.apply(self.input, self.output)
        with self.assertRaises(FileExistsError):
            self.paper.apply(self.input, self.output)
        with self.assertRaisesRegex(ValueError, 'already carries'):
            self.paper.apply(self.output, self.root / 'duplicate.pdf')


if __name__ == '__main__':
    unittest.main()
