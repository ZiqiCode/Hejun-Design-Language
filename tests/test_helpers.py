"""Behavior checks for static HTML packaging and safe deliverable creation."""
import base64
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / '.agents/skills/hejun-design-language'
SCRIPTS = SKILL / 'scripts'
spec = importlib.util.spec_from_file_location('bundle', SCRIPTS / 'build_standalone_html.py')
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)


class HelpersTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_css_relative_image_and_logo_embed_exact_bytes(self):
        (self.root / 'css').mkdir()
        (self.root / 'img').mkdir()
        image = b'test image payload'
        (self.root / 'img/logo.png').write_bytes(image)
        (self.root / 'css/style.css').write_text('body{background:url(../img/logo.png)}', encoding='utf-8')
        src = self.root / 'index.html'
        src.write_text('<!doctype html><link rel="stylesheet" href="css/style.css"><img src="img/logo.png"><p>A &amp; B</p>', encoding='utf-8')
        builder = bundle.Builder(src)
        builder.feed(src.read_text(encoding='utf-8'))
        text = ''.join(builder.parts)
        expected = 'data:image/png;base64,' + base64.b64encode(image).decode()
        self.assertEqual(text.count(expected), 2)
        self.assertIn('A &amp; B', text)
        self.assertNotIn('href="css/style.css"', text)

    def test_remote_and_path_escape_fail_without_output(self):
        for resource in ['https://example.com/logo.png', '../private.png', 'file:///private.png']:
            with self.subTest(resource=resource):
                src = self.root / 'index.html'
                src.write_text(f'<img src="{resource}">', encoding='utf-8')
                output = self.root / 'out.html'
                result = subprocess.run([sys.executable, str(SCRIPTS / 'build_standalone_html.py'), str(src), str(output)], capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(output.exists())

    def test_unsupported_resources_fail(self):
        for text in ['<style>@import "a.css";</style>', '<img srcset="a.png 1x">', '<script type="module">import "a.js"</script>', '<iframe src="a.html"></iframe>']:
            with self.subTest(text=text):
                builder = bundle.Builder(self.root / 'index.html')
                with self.assertRaises(ValueError):
                    builder.feed(text)

    def test_init_escapes_title_and_refuses_existing_folder(self):
        out = self.root / 'deliverable'
        cmd = [sys.executable, str(SCRIPTS / 'init_deliverable.py'), str(out), '--title', '<script>alert(1)</script>']
        first = subprocess.run(cmd, capture_output=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn('&lt;script&gt;', (out / 'index.html').read_text(encoding='utf-8'))
        self.assertNotIn('<script>alert', (out / 'index.html').read_text(encoding='utf-8'))
        self.assertNotEqual(subprocess.run(cmd, capture_output=True).returncode, 0)

    def test_bundle_preserves_source_and_refuses_overwrite(self):
        src = self.root / 'index.html'
        content = '<title>中文示例</title><p>原文</p>'
        src.write_text(content, encoding='utf-8')
        output = self.root / 'out.html'
        cmd = [sys.executable, str(SCRIPTS / 'build_standalone_html.py'), str(src), str(output)]
        self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
        self.assertEqual(src.read_text(encoding='utf-8'), content)
        self.assertNotEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
        self.assertEqual(output.read_text(encoding='utf-8'), content)

    def test_export_matches_authoritative_color_tokens(self):
        import json
        result = subprocess.run([sys.executable, str(SCRIPTS / 'export_tokens.py')], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0)
        colors = json.loads((SKILL / 'assets/tokens.json').read_text(encoding='utf-8'))['color']
        for key, value in colors.items():
            self.assertIn('--hejun-' + key.replace('_', '-') + ': ' + value + ';', result.stdout)

    def test_bundled_fonts_match_official_manifest(self):
        import hashlib
        import json
        fonts = SKILL / 'assets/fonts'
        manifest = json.loads((fonts / 'source.json').read_text(encoding='utf-8'))
        for item in manifest['files']:
            data = (fonts / item['file']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), item['sha256'])
            self.assertEqual(len(data), item['bytes'])
        self.assertEqual(hashlib.sha256((fonts / 'LICENSE.txt').read_bytes()).hexdigest(), manifest['license_sha256'])

    def test_initializer_copies_font_and_licenses_for_standalone(self):
        out = self.root / 'fonts-deliverable'
        command = [sys.executable, str(SCRIPTS / 'init_deliverable.py'), str(out), '--title', '字体检查']
        result = subprocess.run(command, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        source = (out / 'index.html').read_text(encoding='utf-8')
        self.assertIn('assets/fonts/HarmonyOS_Sans_SC_Regular.ttf', source)
        self.assertIn('HarmonyOS Sans Fonts License Agreement', source)
        self.assertTrue((out / 'assets/fonts/LICENSE.txt').exists())
        self.assertEqual((out / 'assets/fonts/HarmonyOS_Sans_SC_Regular.ttf').read_bytes(),
                         (SKILL / 'assets/fonts/HarmonyOS_Sans_SC_Regular.ttf').read_bytes())


if __name__ == '__main__':
    unittest.main()
