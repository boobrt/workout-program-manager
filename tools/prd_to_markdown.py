"""Turns docs/capstone-prd.xlsx (the Product Faculty PRD template) into docs/PRD.md, so the PRD reads on GitHub.

The spreadsheet stays the original. Run after editing it:  python3 -I tools/prd_to_markdown.py
"""
import html
import os
import re
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(HERE, '..', 'docs', 'capstone-prd.xlsx')
OUT = os.path.join(HERE, '..', 'docs', 'PRD.md')
PHASES = ('DISCOVERY', 'DESIGN', 'DEVELOP', 'DEPLOY', 'FINAL')


def cell_text(attrs, inner, shared):
    if 't="s"' in attrs:
        value = re.search(r'<v>(.*?)</v>', inner)
        return shared[int(value.group(1))] if value else ''
    parts = re.findall(r'<t[^>]*>(.*?)</t>', inner, re.S) or re.findall(r'<v>(.*?)</v>', inner)
    return html.unescape(''.join(parts))


def read_rows():
    book = zipfile.ZipFile(XLSX)
    shared = []
    if 'xl/sharedStrings.xml' in book.namelist():
        for item in re.findall(r'<si>(.*?)</si>', book.read('xl/sharedStrings.xml').decode('utf-8'), re.S):
            shared.append(html.unescape(''.join(re.findall(r'<t[^>]*>(.*?)</t>', item, re.S))))
    sheet = book.read('xl/worksheets/sheet1.xml').decode('utf-8')
    rows = {}
    for number, body in re.findall(r'<row[^>]*r="(\d+)"[^>]*>(.*?)</row>', sheet, re.S):
        cells = {}
        for column, attrs, inner in re.findall(r'<c r="([A-Z]+)\d+"([^>]*?)(?:/>|>(.*?)</c>)', body, re.S):
            cells[column] = cell_text(attrs, inner or '', shared).strip()
        rows[int(number)] = cells
    return rows


def main():
    rows = read_rows()
    # Header rows: a label such as "Your Name:" in A, the value in the first filled cell after it (the template merges B:C).
    meta = {}
    for cells in rows.values():
        if cells.get('A', '').endswith(':'):
            meta[cells['A'].rstrip(':')] = next((cells[c] for c in 'BCDEFG' if cells.get(c)), '')
    lines = [
        '# %s: AI product requirements' % (meta.get('Agentic AI Product Name') or 'PRD'),
        '',
        '%s · Product Faculty AI Product Management capstone · last updated %s' % (meta.get('Your Name', ''), meta.get('Date', '')),
        '',
        '> Converted from [`capstone-prd.xlsx`](capstone-prd.xlsx), the Product Faculty PRD template, so it reads on GitHub. '
        'The spreadsheet is the original. Every athlete, calendar and record in this project is made up.',
    ]
    phase = None
    for number in sorted(rows):
        cells = rows[number]
        if cells.get('A', '').upper() in PHASES:
            phase = cells['A'].upper()
            lines += ['', '## ' + phase.title(), '']
        if not phase or not cells.get('F') or not cells.get('D'):
            continue
        lines += ['### ' + cells['D'], '', '*' + cells.get('E', '') + '*', '']
        lines += [line.rstrip() for line in cells['F'].split('\n')]
        lines.append('')
    with open(OUT, 'w', encoding='utf-8') as handle:
        handle.write('\n'.join(lines).rstrip() + '\n')
    print('wrote %s (%d lines)' % (os.path.relpath(OUT), len(lines)))


main()
