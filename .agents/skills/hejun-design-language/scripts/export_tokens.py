"""Export Hejun semantic color and font tokens as CSS (Python standard library only)."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_tokens():
    tokens = json.loads((ROOT / 'assets/tokens.json').read_text(encoding='utf-8'))
    for key, value in tokens['color'].items():
        if not re.fullmatch(r'#[0-9a-fA-F]{6}', value):
            raise ValueError(f'Invalid color {key}: {value}')
    return tokens


def css_text():
    tokens = load_tokens()
    lines = [f'  --hejun-{key.replace("_", "-")}: {value};' for key, value in tokens['color'].items()]
    stack = [tokens['font']['preferred'], *tokens['font']['fallback']]
    quoted = [json.dumps(font) if font != 'sans-serif' else font for font in stack]
    lines.append('  --hejun-font: ' + ', '.join(quoted) + ';')
    return ':root {\n' + '\n'.join(lines) + '\n}\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = css_text()
    if args.output:
        # Avoid silently replacing a user's CSS file.
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(result)
    else:
        print(result, end='')


if __name__ == '__main__':
    main()
