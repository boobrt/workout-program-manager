"""Builds the prototype page and prototype.zip.

index.html = the starter's head and design block (unchanged, skin set to studio)
           + src/styles.css + src/body.html
           + the PFAI helper <script> element copied byte for byte from the starter
           + src/data.js and src/app.js in one script.
Run:  python3 -I build.py   (after python3 -I src/make_data.py when the persona files change)
"""
import json
import os
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
STARTER = os.path.join(HERE, 'kit', 'starter')
SITE = os.path.join(HERE, 'site')
ZIP = os.path.abspath(os.path.join(HERE, '..', 'prototype.zip'))
TITLE = 'Workout Program Manager'


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding='utf-8') as handle:
        return handle.read()


def main():
    starter = read('kit', 'starter', 'index.html')
    design_end = starter.index('/* PF-DESIGN-END */') + len('/* PF-DESIGN-END */')
    head = starter[:design_end]
    for old, new in (('<html lang="en" data-skin="ops">', '<html lang="en" data-skin="studio">'),
                     ('<title>Starter: Northstar Triage</title>', '<title>%s</title>' % TITLE)):
        assert head.count(old) == 1, old
        head = head.replace(old, new)
    helper_start = starter.index('<script>\n/* PFAI-HELPER-START')
    helper_end = starter.index('/* PFAI-HELPER-END */\n</script>') + len('/* PFAI-HELPER-END */\n</script>')
    helper = starter[helper_start:helper_end]

    page = ''.join([
        head, '\n', read('src', 'styles.css'), '</style>\n</head>\n<body>\n',
        read('src', 'body.html'), '\n',
        helper, '\n',
        '<script>\n(function () {\n  \'use strict\';\n', read('src', 'data.js'), '\n', read('src', 'app.js'), '})();\n</script>\n',
        '</body>\n</html>\n'])

    manifest = json.loads(read('kit', 'starter', 'capstone.json'))
    manifest['title'] = TITLE
    os.makedirs(SITE, exist_ok=True)
    with open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8') as handle:
        handle.write(page)
    with open(os.path.join(SITE, 'capstone.json'), 'w', encoding='utf-8') as handle:
        handle.write(json.dumps(manifest, indent=2) + '\n')

    with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.write(os.path.join(SITE, 'index.html'), 'index.html')
        archive.write(os.path.join(SITE, 'capstone.json'), 'capstone.json')
    print('index.html: %d bytes' % len(page.encode('utf-8')))
    print('wrote %s' % ZIP)


main()
