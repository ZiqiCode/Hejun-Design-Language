"""Create an editable two-page Word starter on the mandatory Shenzhen letterhead.

Uses Python standard library only. Preserves original header/footer parts and
embeds full original Regular/Bold fonts with standard OOXML obfuscation.
"""
import argparse
import html
import json
import re
import uuid
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT_FAMILY = 'HarmonyOS Sans SC'


def obfuscate(data, font_key):
    result = bytearray(data)
    key = uuid.UUID(font_key.strip('{}')).bytes[::-1]
    for i in range(min(32, len(result))):
        result[i] ^= key[i % 16]
    return bytes(result)


def paragraph(text, style='HejunBody', page_break=False):
    content = '<w:r><w:br w:type="page"/></w:r>' if page_break else ''
    content += '<w:r><w:t xml:space="preserve">' + html.escape(text) + '</w:t></w:r>'
    return '<w:p><w:pPr><w:pStyle w:val="' + style + '"/></w:pPr>' + content + '</w:p>'


def make_styles():
    styles = []
    for name, size, color, bold, outline in [
        ('HejunBody', 22, '313131', False, None),
        ('HejunTitle', 48, '313131', True, None),
        ('HejunHeading1', 32, 'B33734', True, 0),
        ('HejunSmall', 16, '6C6C6B', False, None),
    ]:
        ppr = '<w:spacing w:before="0" w:after="140" w:line="324" w:lineRule="auto"/><w:snapToGrid w:val="0"/>'
        if outline is not None:
            ppr += '<w:keepNext/><w:outlineLvl w:val="0"/>'
        if name == 'HejunTitle':
            ppr += '<w:keepNext/>'
        rpr = f'<w:rFonts w:ascii="{FONT_FAMILY}" w:hAnsi="{FONT_FAMILY}" w:eastAsia="{FONT_FAMILY}" w:cs="{FONT_FAMILY}"/>'
        rpr += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/><w:color w:val="{color}"/>'
        rpr += '<w:b/><w:bCs/>' if bold else '<w:b w:val="0"/><w:bCs w:val="0"/>'
        styles.append(f'<w:style w:type="paragraph" w:styleId="{name}"><w:name w:val="{name}"/><w:next w:val="HejunBody"/><w:qFormat/><w:pPr>{ppr}</w:pPr><w:rPr>{rpr}</w:rPr></w:style>')
    return ''.join(styles)


def native_table():
    rows = [('阶段', '工作内容', '交付物'), ('研究与诊断', '按项目范围补充', '按约定填写'), ('方案与实施', '按项目范围补充', '按约定填写')]
    widths = [1700, 3800, 2806]
    result = '<w:tbl><w:tblPr><w:tblW w:w="8306" w:type="dxa"/><w:tblLayout w:type="fixed"/><w:tblBorders>'
    result += ''.join(f'<w:{edge} w:val="single" w:sz="4" w:color="D9D9D9"/>' for edge in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV'])
    result += '</w:tblBorders></w:tblPr><w:tblGrid>' + ''.join(f'<w:gridCol w:w="{width}"/>' for width in widths) + '</w:tblGrid>'
    for i, row in enumerate(rows):
        result += '<w:tr>' + ('<w:trPr><w:tblHeader/></w:trPr>' if i == 0 else '')
        for text, width in zip(row, widths):
            result += f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>'
            if i == 0:
                result += '<w:shd w:fill="DDC8B5"/>'
            result += '</w:tcPr>' + paragraph(text) + '</w:tc>'
        result += '</w:tr>'
    return result + '</w:tbl>'


def create(output, title):
    if output.exists():
        raise FileExistsError('Output already exists; choose a new path')
    source = ROOT / 'assets/letterhead/hejun-shenzhen-original.docx'
    with zipfile.ZipFile(source) as archive:
        parts = {name: archive.read(name) for name in archive.namelist() if not name.endswith('/')}
    document = parts['word/document.xml'].decode('utf-8')
    section = re.search(r'<w:sectPr\b.*?</w:sectPr>', document, re.S).group(0)
    config = json.loads((ROOT / 'assets/letterhead/source.json').read_text(encoding='utf-8'))
    for key, value in config['safe_margins_twips'].items():
        section = re.sub(r'(w:' + key + r'=\")[^\"]*(\")', lambda m: m.group(1) + str(value) + m.group(2), section)
    body = paragraph(title, 'HejunTitle')
    body += paragraph('客户提案或研究报告', 'HejunBody')
    body += paragraph('项目背景', 'HejunHeading1')
    body += paragraph('填写本项目的背景、研究范围和业务约束。保留事实、单位、日期与来源。')
    body += paragraph('核心判断', 'HejunHeading1')
    body += paragraph('填写有证据支持的主要结论，尚未确认的信息单独标注。')
    body += paragraph('分析与建议', 'HejunHeading1', page_break=True)
    body += paragraph('填写现状、证据与对应建议，保留适用条件和实施边界。')
    body += paragraph('工作安排', 'HejunHeading1') + native_table()
    body += paragraph('来源：填写实际资料名称、日期与口径。', 'HejunSmall')
    body += paragraph('本模板使用 HarmonyOS Sans Fonts。Copyright 2021 Huawei Device Co., Ltd. 完整许可随文件保留。', 'HejunSmall')
    document = re.sub(r'(<w:body>).*?(</w:body>)', lambda m: m.group(1) + body + section + m.group(2), document, flags=re.S)
    parts['word/document.xml'] = document.encode('utf-8')
    styles = parts['word/styles.xml'].decode('utf-8')
    parts['word/styles.xml'] = styles.replace('</w:styles>', make_styles() + '</w:styles>').encode('utf-8')
    relationships = []
    font_entries = []
    for weight, element in [('Regular', 'embedRegular'), ('Bold', 'embedBold')]:
        key = '{' + str(uuid.uuid4()).upper() + '}'
        original = (ROOT / f'assets/fonts/HarmonyOS_Sans_SC_{weight}.ttf').read_bytes()
        name = f'hejun-{weight.lower()}.odttf'
        parts['word/fonts/' + name] = obfuscate(original, key)
        rid = 'rIdHejun' + weight
        relationships.append(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/font" Target="fonts/{name}"/>')
        font_entries.append(f'<w:{element} xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" r:id="{rid}" w:fontKey="{key}" w:subsetted="0"/>')
    font_table = parts['word/fontTable.xml'].decode('utf-8')
    font_table = font_table.replace('</w:fonts>', '<w:font w:name="HarmonyOS Sans SC">' + ''.join(font_entries) + '</w:font></w:fonts>')
    parts['word/fontTable.xml'] = font_table.encode('utf-8')
    parts['word/_rels/fontTable.xml.rels'] = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + ''.join(relationships) + '</Relationships>').encode('utf-8')
    types = parts['[Content_Types].xml'].decode('utf-8')
    types = types.replace('</Types>', '<Default Extension="odttf" ContentType="application/vnd.openxmlformats-officedocument.obfuscatedFont"/></Types>')
    parts['[Content_Types].xml'] = types.encode('utf-8')
    settings = parts['word/settings.xml'].decode('utf-8')
    settings = re.sub(r'<w:(?:embedTrueTypeFonts|saveSubsetFonts|doNotEmbedSystemFonts)\b[^>]*/>', '', settings)
    settings = settings.replace('</w:settings>', '<w:embedTrueTypeFonts/><w:saveSubsetFonts w:val="0"/><w:doNotEmbedSystemFonts w:val="0"/></w:settings>')
    parts['word/settings.xml'] = settings.encode('utf-8')
    license_text = (ROOT / 'assets/fonts/LICENSE-readable.txt').read_text(encoding='utf-8')
    parts['customXml/hejun-font-license.xml'] = ('<?xml version="1.0" encoding="UTF-8"?><fontLicense xmlns="urn:hejun:font-license">' + html.escape(license_text) + '</fontLicense>').encode('utf-8')
    rels = parts['word/_rels/document.xml.rels'].decode('utf-8')
    rels = rels.replace('</Relationships>', '<Relationship Id="rIdHejunFontLicense" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/customXml" Target="../customXml/hejun-font-license.xml"/></Relationships>')
    parts['word/_rels/document.xml.rels'] = rels.encode('utf-8')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in parts.items():
            archive.writestr(name, data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--title', required=True)
    args = parser.parse_args()
    if not args.title.strip():
        parser.error('Title must not be empty')
    create(args.output.resolve(), args.title.strip())
    print(args.output.resolve())


if __name__ == '__main__':
    main()
