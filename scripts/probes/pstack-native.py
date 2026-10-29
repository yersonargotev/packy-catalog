#!/usr/bin/env python3
"""Check current pstack native installation and retained access in disposable state."""
import importlib.util
import json
from pathlib import Path
import signal
import sys
import tempfile

spec = importlib.util.spec_from_file_location('content_probe', Path(__file__).with_name('content-probes.py'))
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)


def main():
    evidence = {'schema_version': 1, 'report': 'pstack-native-probe', 'provenance': 'local-candidate',
                'official_publication': False, 'commands': [], 'outcomes': [], 'result': 'failed'}
    root = None
    handler = signal.signal(signal.SIGTERM, legacy.interrupted)
    try:
        with tempfile.TemporaryDirectory(prefix='pstack-native-') as directory:
            root = Path(directory).resolve()
            env = legacy.isolated_environment(root)
            probe = legacy.Probe(root / 'packy', root / 'dist', root, env, evidence, 45)
            commit = legacy.checkout_commit(probe, legacy.ROOT)
            probe.set_context('acquisition')
            probe.execute([sys.executable, '-B', str(legacy.ROOT / 'scripts/packy_tool.py'), '--pin',
                           str(legacy.ROOT / 'packy-release.json'), '--executable-output', str(probe.executable)], timeout=180)
            evidence.update(legacy.build_catalog(probe, legacy.ROOT, commit, probe.snapshot))
            pack = legacy.ROOT / 'packs/pstack'
            manifest = json.loads((pack / 'pack.json').read_text())
            skills = [r for r in manifest['resources'] if r['kind'] == 'skill']
            ambient = {key: legacy.tree(Path(env[key])) for key in ('HOME', 'XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'XDG_CACHE_HOME')}
            for surface in ('agents', 'claude'):
                probe.set_context('content-acceptance', scenario='pstack-native', surface=surface, scope='project')
                workspace = probe.prepare('native-' + surface)
                before = legacy.tree(workspace / 'project')
                personal = {name: (workspace / name / 'personal-sentinel').read_bytes() for name in ('home', 'config')}
                probe.apply(workspace, ['install', 'pstack', '--surface', surface])
                probe.verify(workspace)
                native = workspace / 'project' / ('.agents/skills' if surface == 'agents' else '.claude/skills')
                legacy.require({p.name for p in native.iterdir()} == {r['id'] for r in skills}, 'native skill inventory differs')
                for resource in skills:
                    effective = next((v for v in resource.get('variants', []) if v['surface'] == surface), resource)
                    legacy.require(legacy.tree(native / resource['id']) == legacy.tree(pack / effective['source']),
                                   'native bytes or modes differ: ' + resource['id'])
                notices = (workspace / 'project/PACKY-NOTICES.md').read_bytes()
                for notice in (r for r in manifest['resources'] if r['kind'] == 'notice'):
                    legacy.require((pack / notice['source']).read_bytes() in notices, 'native legal notice differs')
                snapshot = None
                for name in ('poteto-mode', 'interrogate', 'create-formal-verification-skill',
                             'maintain-formal-verification-skill', 'ketchup-video', 'statechart'):
                    args = ['get', 'skill', 'pstack:' + name, '--surface', surface, '--json']
                    if snapshot:
                        args += ['--snapshot', snapshot]
                    report = probe.candidate(workspace, args)
                    legacy.require(snapshot is None or report['snapshot_id'] == snapshot, 'retrieval switched the requested snapshot')
                    snapshot = report['snapshot_id']
                    entry = Path(report['entry_document'])
                    legacy.require(report['result'] == 'prepared' and report['surface'] == surface
                                   and report['qualified_skill'] == 'pstack:' + name and report['pack_version'] == manifest['version']
                                   and entry.is_file() and '{{packy.access:' not in entry.read_text(), 'retained access differs: ' + name)
                    first_bytes = entry.read_bytes()
                    retained = probe.candidate(workspace, [*args, '--snapshot', snapshot] if '--snapshot' not in args else args)
                    legacy.require(retained['snapshot_id'] == snapshot and Path(retained['entry_document']).read_bytes() == first_bytes,
                                   'pinned access changed')
                    for dependency in report['dependencies']:
                        legacy.require(dependency['snapshot_id'] == snapshot and dependency['surface'] == surface
                                       and Path(dependency['entry_document']).is_file(), 'prepared dependency context differs')
                probe.apply(workspace, ['uninstall', 'pstack', '--surface', surface])
                for name in ('AGENTS.md', 'CLAUDE.md', 'unrelated.txt'):
                    legacy.require((workspace / 'project' / name).read_bytes().rstrip(b'\n') == before[name][1].rstrip(b'\n'), 'foreign document changed')
                legacy.require(not native.exists() or not list(native.iterdir()), 'managed skills remain')
                for name in ('packy.json', 'packy.lock.json', 'PACKY-NOTICES.md'):
                    legacy.require(not (workspace / 'project' / name).exists(), 'managed state remains: ' + name)
                legacy.require(personal == {name: (workspace / name / 'personal-sentinel').read_bytes() for name in personal}, 'foreign personal file changed')
                evidence['outcomes'].append({'surface': surface, 'skills': len(skills), 'access_roots': 6, 'result': 'passed'})
            legacy.require(ambient == {key: legacy.tree(Path(env[key])) for key in ambient}, 'ambient state changed')
            legacy.require(legacy.checkout_commit(probe, legacy.ROOT) == commit, 'candidate changed during probe')
            evidence['result'] = 'passed'
    except (OSError, ValueError, KeyError, RuntimeError, legacy.subprocess.SubprocessError, KeyboardInterrupt) as error:
        evidence['error'] = str(error) or 'interrupted'
        print('pstack native probe: ' + evidence['error'], file=sys.stderr)
    finally:
        signal.signal(signal.SIGTERM, handler)
        evidence['cleanup'] = 'removed' if root is None or not root.exists() else 'failed'
        if evidence['cleanup'] != 'removed':
            evidence['result'] = 'failed'
        print(json.dumps(evidence, indent=2))
    return 0 if evidence['result'] == 'passed' else 1


if __name__ == '__main__':
    sys.exit(main())
