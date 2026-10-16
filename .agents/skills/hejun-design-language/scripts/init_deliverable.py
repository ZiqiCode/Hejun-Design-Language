"""Create a new Hejun HTML source folder; never merge into an existing folder."""
import argparse
import html
import json
import shutil
from pathlib import Path
from export_tokens import css_text

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--title', required=True)
    parser.add_argument('--audience', default='待确认')
    args = parser.parse_args()
    if not args.title.strip():
        parser.error('Title must not be empty')
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    shutil.copytree(ROOT / 'assets/logos', output / 'assets/logos')
    shutil.copytree(ROOT / 'assets/fonts', output / 'assets/fonts')
    source = (ROOT / 'assets/templates/hejun-starter.html').read_text(encoding='utf-8')
    source = source.replace('../logos/', 'assets/logos/')
    source = source.replace('../fonts/', 'assets/fonts/')
    source = source.replace('项目名称', html.escape(args.title.strip()))
    (output / 'index.html').write_text(source, encoding='utf-8')
    (output / 'tokens.css').write_text(css_text(), encoding='utf-8')
    brief = {'project': {'title': args.title, 'audience': args.audience},
             'variant': 'red-v2026', 'assumptions': [],
             'qa': {'content': 'pending', 'desktop': 'pending', 'mobile': 'pending', 'print': 'pending', 'offline': 'pending'}}
    (output / 'hejun-brief.json').write_text(json.dumps(brief, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(output)


if __name__ == '__main__':
    main()
