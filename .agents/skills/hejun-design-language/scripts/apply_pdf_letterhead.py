"""Place every page of a static PDF inside the Shenzhen A4 letterhead.

Requires PyMuPDF (import pymupdf). Content remains vector/searchable where the
input was vector/searchable. Links, annotations, forms and attachments are
rejected rather than silently discarded. Rebuild those PDFs from source.
"""
import argparse
import json
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
MARKER = 'hejun-letterhead-shenzhen-v1'


def apply(source, output):
    if output.exists() or output.resolve() == source.resolve():
        raise FileExistsError('Output must be new and different from source')
    config = json.loads((ROOT / 'assets/letterhead/source.json').read_text(encoding='utf-8'))
    with pymupdf.open(source) as content, pymupdf.open(ROOT / 'assets/letterhead/hejun-shenzhen-blank.pdf') as paper:
        if content.needs_pass or content.is_encrypted:
            raise ValueError('Encrypted PDF is unsupported; use an authorized editable source')
        if MARKER in (content.metadata.get('keywords') or ''):
            raise ValueError('PDF already carries this letterhead marker')
        if content.embfile_count() or content.get_sigflags() > 0:
            raise ValueError('Attached files or signatures require a source-specific workflow')
        for page in content:
            if page.first_annot or page.first_widget or page.get_links():
                raise ValueError('Links, annotations or forms require a source-specific workflow')
        if not len(content):
            raise ValueError('Source PDF has no pages')
        result = pymupdf.open()
        rect = paper[0].rect
        for index, _ in enumerate(content):
            target = result.new_page(width=rect.width, height=rect.height)
            target.show_pdf_page(target.rect, paper, 0)
            target.show_pdf_page(pymupdf.Rect(config['safe_content_rect_pt']), content, index, keep_proportion=True)
        toc = content.get_toc(simple=True)
        if toc:
            result.set_toc(toc)
        metadata = {key: value for key, value in content.metadata.items() if key not in ('format', 'encryption')}
        metadata['keywords'] = ((metadata.get('keywords') or '') + ' ' + MARKER).strip()
        result.set_metadata(metadata)
        output.parent.mkdir(parents=True, exist_ok=True)
        result.save(output, deflate=True, garbage=3)
        result.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    apply(args.source, args.output)
    print(args.output.resolve())


if __name__ == '__main__':
    main()
