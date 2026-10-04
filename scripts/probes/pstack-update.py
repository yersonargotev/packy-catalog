#!/usr/bin/env python3
"""Opt-in pstack checks, separate from inert catalog validation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

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


def check_plans(project):
    template = (Path(__file__).parent / 'fixtures/pstack-plan.md').read_text(encoding='utf-8')
    for host, cadence in (('common', '/loop 1h'), ('codex', 'hourly audit')):
        skills = project / 'packs/pstack/skills'
        source = skills / ('codex/' if host == 'codex' else '') / 'poteto-mode/scripts/check-plan.mjs'
        valid = template.replace('@AUDIT@', cadence)
        scenarios = (
            ('valid', valid, 0, '1 PR sections, 0 problems'),
            ('obsolete-cadence', valid.replace(cadence, '30-minute audit'), 1,
             f'Program checklist lacks "{cadence}"'),
            ('missing-lane', '\n'.join(line for line in valid.splitlines()
                                      if not line.startswith('- [ ] Lane 10.')), 1, 'expected 1 to 10'),
        )
        with tempfile.TemporaryDirectory(prefix='pstack-plan-probe-') as directory:
            scratch = Path(directory)
            helper = scratch / 'check-plan.mjs'
            shutil.copy2(source, helper)
            plan = scratch / 'plan.md'
            for name, content, code, diagnostic in scenarios:
                plan.write_text(content, encoding='utf-8')
                result = subprocess.run(
                    ['node', str(helper), str(plan)], cwd=scratch,
                    env={'PATH': os.environ.get('PATH', ''), 'HOME': directory, 'TMPDIR': directory},
                    text=True, capture_output=True, timeout=15,
                )
                output = result.stdout if code == 0 else result.stderr
                if result.returncode != code or diagnostic not in output:
                    raise ValueError(f'{host}/{name}: expected exit {code} and {diagnostic!r}; '
                                     f'got exit {result.returncode}\n{result.stdout}{result.stderr}')
        print(f'{host}: 3 plan scenarios passed; execution copies removed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    contracts = commands.add_parser('contracts', help='compare preserved hosts with a clean baseline')
    contracts.add_argument('--project', type=Path, default=PROJECT)
    contracts.add_argument('--baseline', type=Path, required=True)
    contracts.add_argument('--preserve-surface', action='append', required=True,
                           choices=('claude', 'codex', 'opencode'))
    plans = commands.add_parser('plans', help='execute reviewed common/Codex plan checkers in temporary copies')
    plans.add_argument('--project', type=Path, default=PROJECT)
    args = parser.parse_args()
    try:
        if args.command == 'contracts':
            compare_surfaces(args.project, args.baseline, args.preserve_surface)
        else:
            check_plans(args.project)
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        print(f'pstack probe: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
