#!/usr/bin/env python3
"""Verify the shared statechart distribution against its immutable upstream."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def inventory(root):
    result = {}
    for file in sorted(root.rglob('*')):
        if file.is_symlink():
            raise ValueError('symlink in statechart tree: ' + str(file))
        if file.is_file():
            result[str(file.relative_to(root))] = {
                'sha256': hashlib.sha256(file.read_bytes()).hexdigest(),
                'mode': '0755' if file.stat().st_mode & 0o111 else '0644',
            }
    return result


def verify(project, upstream):
    pack = project / 'packs/pstack'
    manifest = json.loads((pack / 'pack.json').read_text())
    resource = next(r for r in manifest['resources'] if r['id'] == 'statechart')
    root = pack / resource['source']
    provenance = json.loads((root / 'references/upstream-files.json').read_text())
    origin = next(o for o in manifest['origins'] if o['id'] == resource['origin']['id'])
    commit = subprocess.check_output(['git', '-C', str(upstream), 'rev-parse', 'HEAD'], text=True).strip()
    if not (commit == origin['commit'] == provenance['commit']):
        raise ValueError('upstream, manifest and inventory commits differ')
    if origin['repository'] != provenance['repository'] or provenance['origin_scope'] != 'entry-document':
        raise ValueError('unexpected provenance identity or scope')
    expected_origin = {'id': origin['id'], 'path': provenance['upstream_root'] + '/SKILL.md', 'relationship': 'adapted'}
    if resource['origin'] != expected_origin:
        raise ValueError('statechart entry provenance differs')
    source = inventory(upstream / provenance['upstream_root'])
    if source != provenance['upstream_files']:
        raise ValueError('complete upstream file/hash/mode inventory differs')
    actual = inventory(root)
    retained = provenance['retained_files']
    for target, original in retained.items():
        if actual.get(target) != source.get(original) or original not in source:
            raise ValueError('retained upstream bytes or mode differ: ' + target)
    production = {name for name in source if not name.startswith('scripts/test/')}
    if set(retained.values()) != production - {'scripts/package.json'}:
        raise ValueError('production runtime or original entry is missing')
    if set(actual) != set(retained) | set(provenance['adapted_files']):
        raise ValueError('undeclared addition or omission in distributed tree')
    package = json.loads((root / 'scripts/package.json').read_text())
    if package != {'name': '@cursor-skill/statechart', 'private': True, 'type': 'module'}:
        raise ValueError('unexpected production package metadata')
    if set(b['surface'] for b in resource['bindings']) != {'agents', 'claude'} or resource.get('variants'):
        raise ValueError('statechart must have one shared source for both surfaces')
    return {'result': 'passed', 'commit': commit, 'upstream_files': len(source),
            'retained_files': len(retained), 'distributed_files': len(actual),
            'omitted_test_files': len(source) - len(production)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--upstream', type=Path, required=True, help='clean cursor/plugins checkout at the manifest commit')
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.project.resolve(), args.upstream.resolve()), sort_keys=True))
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
