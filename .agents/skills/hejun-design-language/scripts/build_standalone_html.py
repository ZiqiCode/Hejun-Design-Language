"""Bundle a static Hejun HTML document. Unsupported resource forms fail explicitly."""
import argparse
import base64
import html
import mimetypes
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

CSS_URL = re.compile(r'url\(\s*([\'"]?)(.*?)\1\s*\)', re.I)


class Builder(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source.resolve()
        self.root = self.source.parent
        self.parts = []
        self.styles = False
        self.embedded = set()

    def path(self, url, base):
        if url.startswith('data:') or url.startswith('#'):
            return None
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc:
            raise ValueError(f'Remote or unsupported presentation resource: {url}')
        if parsed.query:
            raise ValueError(f'Resource query strings are unsupported: {url}')
        path = (base / unquote(parsed.path)).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError(f'Resource escapes source folder: {url}')
        if not path.is_file():
            raise FileNotFoundError(path)
        return path

    def uri(self, url, base):
        path = self.path(url, base)
        if path is None:
            return url
        self.embedded.add(path)
        mime = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
        encoded = base64.b64encode(path.read_bytes()).decode('ascii')
        # Preserve an SVG fragment used by CSS or img.
        fragment = urlsplit(url).fragment
        return f'data:{mime};base64,{encoded}' + (f'#{fragment}' if fragment else '')

    def css(self, text, base):
        if re.search(r'@import\b', text, re.I):
            raise ValueError('CSS @import is unsupported; merge stylesheets first')
        return CSS_URL.sub(lambda m: 'url("' + self.uri(m.group(2), base) + '")', text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if 'srcset' in values:
            raise ValueError('srcset is unsupported; use a single local src')
        if tag in ('iframe', 'object', 'embed', 'video', 'audio', 'source', 'base'):
            raise ValueError(f'Unsupported resource element: {tag}')
        if tag == 'script' and values.get('type', '').lower() == 'module':
            raise ValueError('Module scripts are unsupported')
        if tag == 'link':
            rel = values.get('rel', '').lower().split()
            if 'stylesheet' in rel:
                if values.get('media', '').lower() not in ('', 'all'):
                    raise ValueError('Stylesheet media attribute is unsupported; use CSS @media')
                path = self.path(values.get('href', ''), self.root)
                if path is None:
                    raise ValueError('Stylesheet must be a local file')
                self.embedded.add(path)
                text = self.css(path.read_text(encoding='utf-8'), path.parent)
                if '</style' in text.lower():
                    raise ValueError('Stylesheet contains a closing style tag')
                self.parts.append('<style>' + text + '</style>')
                return
            if any(x not in ('icon', 'shortcut') for x in rel):
                raise ValueError(f'Unsupported link relation: {rel}')
        if tag == 'script' and values.get('src'):
            # data: is valid for classic scripts; browser executes in document context.
            values['src'] = self.uri(values['src'], self.root)
        if tag == 'img' and values.get('src'):
            values['src'] = self.uri(values['src'], self.root)
        if tag == 'link' and values.get('href'):
            values['href'] = self.uri(values['href'], self.root)
        if values.get('style'):
            values['style'] = self.css(values['style'], self.root)
        if tag == 'image' and ('href' in values or 'xlink:href' in values):
            key = 'href' if 'href' in values else 'xlink:href'
            values[key] = self.uri(values[key], self.root)
        encoded = ''.join(' ' + key + ('="' + html.escape(value, quote=True) + '"' if value is not None else '') for key, value in values.items())
        self.parts.append('<' + tag + encoded + '>')
        if tag == 'style':
            self.styles = True

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.parts[-1].endswith('>'):
            self.parts[-1] = self.parts[-1][:-1] + '/>'

    def handle_endtag(self, tag):
        self.parts.append('</' + tag + '>')
        if tag == 'style':
            self.styles = False

    def handle_data(self, data):
        self.parts.append(self.css(data, self.root) if self.styles else data)

    def handle_entityref(self, name):
        self.parts.append('&' + name + ';')

    def handle_charref(self, name):
        self.parts.append('&#' + name + ';')

    def handle_comment(self, data):
        self.parts.append('<!--' + data + '-->')

    def handle_decl(self, decl):
        self.parts.append('<!' + decl + '>')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path, nargs='?')
    args = parser.parse_args()
    source = args.source.resolve()
    text = source.read_text(encoding='utf-8')
    match = re.search(r'<title[^>]*>(.*?)</title>', text, re.I | re.S)
    name = html.unescape(match.group(1)) if match else source.parent.name
    name = re.sub(r'[^\w]+', '_', name).strip('_')[:100] or 'Document'
    output = args.output.resolve() if args.output else source.with_name(name + '_Hejun_Standalone.html')
    if output == source or output.exists():
        raise ValueError('Output must be new and different from source')
    builder = Builder(source)
    builder.feed(text)
    builder.close()
    result = ''.join(builder.parts)
    # Never write a partial document if a resource could not be bundled.
    with output.open('x', encoding='utf-8') as stream:
        stream.write(result)
    print(f'{output}\nembedded_files={len(builder.embedded)}')


if __name__ == '__main__':
    main()
