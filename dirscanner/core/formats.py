import json
import re
import xml.etree.ElementTree as ET
from typing import Dict, Optional
from xml.sax.saxutils import escape, quoteattr

ScanData = Dict[str, Optional[str]]

# Characters that cannot appear in an XML 1.0 document, even escaped.
INVALID_XML_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\ufffe\uffff]')
# The newline + indentation that precedes a closing </file> tag.
TRAILING_INDENT = re.compile(r'\n[ ]*\Z')

SUPPORTED_FORMATS = ('json', 'xml')

def newNode():
    return {'folders': {}, 'files': {}}

def buildTree(data: ScanData) -> dict:
    '''Turns {'src/a/b.py': '...'} into a nested folder/file structure.'''
    root = newNode()
    for path, content in data.items():
        *folders, fileName = path.split('/')
        node = root
        for folder in folders:
            node = node['folders'].setdefault(folder, newNode())
        node['files'][fileName] = content
    return root

def toJson(data: ScanData) -> str:
    return json.dumps(data, indent=4, ensure_ascii=False)

def fromJson(text: str) -> ScanData:
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError('Invalid JSON: top-level value must be an object')
    for path, content in data.items():
        if content is not None and not isinstance(content, str):
            raise ValueError(f'Invalid JSON: content of `{path}` must be a string or null')
    return data

def renderNode(node: dict, depth: int, lines: list) -> None:
    indent = '  ' * depth

    for name in sorted(node['folders']):
        lines.append(f'{indent}<folder name={quoteattr(name)}>')
        renderNode(node['folders'][name], depth + 1, lines)
        lines.append(f'{indent}</folder>')

    for name in sorted(node['files']):
        content = node['files'][name]
        attr = quoteattr(name)

        # Unreadable files (None) and text XML can't represent are emitted empty
        # and flagged, mirroring the `null` used in JSON.
        if content is None or INVALID_XML_CHARS.search(content):
            lines.append(f'{indent}<file name={attr} binary="true" />')
        else:
            body = escape(content, {'\r': '&#13;'})
            lines.append(f'{indent}<file name={attr}>\n{body}\n{indent}</file>')

def toXml(data: ScanData) -> str:
    lines = ['<project>']
    renderNode(buildTree(data), 1, lines)
    lines.append('</project>')
    return '\n'.join(lines)

def readNode(element: ET.Element, prefix: str, data: ScanData) -> None:
    for child in element:
        name = child.get('name')
        if not name:
            raise ValueError(f'Invalid XML: <{child.tag}> is missing the "name" attribute')

        path = f'{prefix}{name}'

        if child.tag == 'folder':
            readNode(child, f'{path}/', data)
        elif child.tag == 'file':
            if child.get('binary') == 'true':
                data[path] = None
            else:
                content = child.text or ''
                # Undo the layout added by toXml: one leading newline and
                # the newline + indent before the closing tag.
                if content.startswith('\n'):
                    content = content[1:]
                data[path] = TRAILING_INDENT.sub('', content, count=1)
        else:
            raise ValueError(f'Invalid XML: unexpected element <{child.tag}>')

def fromXml(text: str) -> ScanData:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        raise ValueError(f'Invalid XML: {e}') from e

    if root.tag != 'project':
        raise ValueError('Invalid XML: root element must be <project>')

    data: ScanData = {}
    readNode(root, '', data)
    return data

def serialize(data: ScanData, fmt: str) -> str:
    if fmt == 'json':
        return toJson(data)
    if fmt == 'xml':
        return toXml(data)
    raise ValueError(f'Unsupported format: {fmt}')

def parse(text: str, fmt: str) -> ScanData:
    if fmt == 'json':
        return fromJson(text)
    if fmt == 'xml':
        return fromXml(text)
    raise ValueError(f'Unsupported format: {fmt}')

def detectFormat(text: str) -> str:
    '''Guesses the format from the first meaningful character.'''
    stripped = text.lstrip('\ufeff \t\r\n')
    if stripped.startswith('<'):
        return 'xml'
    if stripped.startswith('{'):
        return 'json'
    raise ValueError('Could not detect format; use --json or --xml')