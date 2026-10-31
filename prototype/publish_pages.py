"""Builds the live prototype for GitHub Pages.

Takes the studio page (prototype/studio/index.html), pastes Product Faculty's connection helper into its
/*__PFAI_HELPER__*/ placeholder line, and writes the result to index.html at the top of the repo, plus the
local test copy in prototype/studio-preview/. The helper comes from the build kit kept on this Mac at
prototype/kit/starter/pf-ai.js (course material, so it is git-ignored). Run from anywhere:

    python3 -I prototype/publish_pages.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.join(HERE, 'studio', 'index.html')
HELPER = os.path.join(HERE, 'kit', 'starter', 'pf-ai.js')
OUTPUTS = [os.path.join(HERE, '..', 'index.html'), os.path.join(HERE, 'studio-preview', 'index.html')]
PLACEHOLDER = '/*__PFAI_HELPER__*/'


def main():
    with open(STUDIO, encoding='utf-8') as handle:
        page = handle.read()
    with open(HELPER, encoding='utf-8') as handle:
        helper = handle.read().rstrip('\n')
    assert page.count(PLACEHOLDER) == 1, 'The studio page must have exactly one %s line.' % PLACEHOLDER
    assert 'PFAI-HELPER-START' in helper and 'PFAI-HELPER-END' in helper, 'pf-ai.js does not look like the helper.'
    built = page.replace(PLACEHOLDER, helper)
    for path in OUTPUTS:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(built)
        print('wrote %s (%d KB)' % (os.path.relpath(path, os.path.join(HERE, '..')), len(built.encode('utf-8')) // 1024))


main()
