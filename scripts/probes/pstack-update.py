#!/usr/bin/env python3
"""Opt-in pstack checks, separate from inert catalog validation."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[2]


def file_inventory(source):
    if source.is_symlink():
        raise ValueError(f'symlink in resource: {source}')
    paths = sorted(source.rglob('*')) if source.is_dir() else [source]
    inventory = {}
    for path in paths:
        if path.is_symlink():
            raise ValueError(f'symlink in resource: {path}')
        if path.is_file():
            inventory[str(path.relative_to(source))] = (
                bool(path.stat().st_mode & 0o111), hashlib.sha256(path.read_bytes()).hexdigest()
            )
        elif not path.is_dir():
            raise ValueError(f'missing or unsupported resource path: {path}')
    return inventory


def surface_contract(project, surface):
    pack = (project / 'packs/pstack').resolve(strict=True)
    manifest = json.loads((pack / 'pack.json').read_text(encoding='utf-8'))
    resources = {f"{r['kind']}:{r['id']}": r for r in manifest['resources']}
    roots = {key for key, resource in resources.items()
             if any(b['surface'] == surface for b in resource['bindings'])}
    selected = {}

    def visit(key):
        if key in selected:
            return
        resource = resources[key]
        bindings = [b for b in resource['bindings'] if b['surface'] == surface]
        if resource['kind'] != 'notice' and not bindings:
            raise ValueError(f'{surface}: unavailable dependency {key}')
        effective = {k: v for k, v in resource.items()
                     if k not in ('variants', 'bindings', 'surface_exclusions')}
        for variant in resource.get('variants', []):
            if variant['surface'] == surface:
                effective.update({k: v for k, v in variant.items() if k != 'surface'})
        effective['bindings'] = bindings
        inventory = {}
        if effective.get('source'):
            source = pack / effective['source']
            source.resolve(strict=True).relative_to(pack)
            inventory = file_inventory(source)
        selected[key] = (effective, inventory)
        for dependency in effective.get('requires', []) + effective.get('notices', []):
            visit(dependency)

    for key in sorted(roots):
        visit(key)
    pack_contract = {k: v for k, v in manifest.items()
                     if k not in ('version', 'origins', 'resources')}
    # Compare the selected host's support; other hosts may be explicitly retired.
    pack_contract['surfaces'] = [host for host in manifest['surfaces'] if host == surface]
    pack_contract['origins'] = [
        {k: v for k, v in origin.items() if k != 'commit'}
        for origin in manifest['origins']
    ]
    return pack_contract, roots, selected


def compare_surfaces(project, baseline, surfaces):
    for surface in surfaces:
        old_pack, old_roots, old = surface_contract(baseline, surface)
        new_pack, new_roots, new = surface_contract(project, surface)
        if old_pack != new_pack:
            raise ValueError(f'{surface}: Pack contract drift')
        if old_roots != new_roots or old.keys() != new.keys():
            raise ValueError(f'{surface}: resource selection drift')
        for key in sorted(old):
            if old[key][0] != new[key][0]:
                raise ValueError(f'{surface}: contract drift at {key}')
            if old[key][1] != new[key][1]:
                raise ValueError(f'{surface}: content or executable-mode drift at {key}')
        print(f'{surface}: preserved {len(new_roots)} roots and {len(new)} closure resources')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    contracts = commands.add_parser('contracts', help='compare preserved hosts with a clean baseline')
    contracts.add_argument('--project', type=Path, default=PROJECT)
    contracts.add_argument('--baseline', type=Path, required=True)
    contracts.add_argument('--preserve-surface', action='append', required=True,
                           choices=('agents', 'claude'))
    args = parser.parse_args()
    try:
        compare_surfaces(args.project, args.baseline, args.preserve_surface)
    except (OSError, ValueError, KeyError) as error:
        print(f'pstack probe: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
