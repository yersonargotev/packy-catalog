"""Validate the one reviewed catalog contract transition and independent versions."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OLD_PIN = ROOT / 'scripts/packy-release-v0.2.31.json'
NEW_VERSION = ('v0.2.32', '9d8a03a0c0070f20736d6f6ab94d4f5c303243ba')
SEMVER = re.compile(r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$')


def version_key(value):
    match = SEMVER.fullmatch(value)
    if not match:
        raise ValueError('invalid strict semantic version: ' + value)
    pre = match.group(4)
    identifiers = []
    if pre:
        for part in pre.split('.'):
            if part.isdigit():
                if len(part) > 1 and part.startswith('0'):
                    raise ValueError('invalid semantic version prerelease: ' + value)
                identifiers.append((0, int(part)))
            else:
                identifiers.append((1, part))
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)),
            1 if pre is None else 0, identifiers)


def compare_packs(candidate, baseline):
    for pack_id, current in candidate.items():
        previous = baseline.get(pack_id)
        if previous is None:
            continue
        new_manifest = dict(current['manifest'])
        old_manifest = dict(previous['manifest'])
        new_version, old_version = new_manifest.pop('version'), old_manifest.pop('version')
        unchanged = (new_manifest == old_manifest and
                     [f for f in current['files'] if f['path'] != 'pack.json'] ==
                     [f for f in previous['files'] if f['path'] != 'pack.json'])
        if unchanged and new_version != old_version:
            raise ValueError('Pack %r unchanged content must retain version %s' % (pack_id, old_version))
        if not unchanged and version_key(new_version) <= version_key(old_version):
            raise ValueError('Pack %r changed content requires a version greater than %s' % (pack_id, old_version))


def run(command):
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.stderr:
        sys.stderr.write(result.stderr)
    if result.returncode:
        raise ValueError('catalog validation/build failed: ' + (result.stderr.strip() or result.stdout.strip()))
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ValueError('invalid Packy report: ' + str(error)) from error


def build(project, output, old):
    engine = ([sys.executable, str(ROOT / 'scripts/packy_tool.py'), '--pin', str(OLD_PIN), '--']
              if old else [str(ROOT / 'scripts/packy.sh')])
    report = run(engine + ['catalog', 'build', '--project', str(project), '--out-dir', str(output),
                           '--source-repository', 'yersonargotev/packy-catalog',
                           '--source-commit', '1' * 40, '--json'])
    if report.get('report') != 'catalog-build' or report.get('result') != 'built':
        raise ValueError('unexpected catalog build report')
    packs = {}
    with tarfile.open(output / 'catalog-snapshot.tar.gz', 'r:gz') as archive:
        for entry in report['index']['packs']:
            pack_id = entry['id']
            member = archive.getmember('packs/' + pack_id + '/pack.json')
            if not member.isfile():
                raise ValueError('invalid archived Pack manifest')
            data = archive.extractfile(member).read()
            if hashlib.sha256(data).hexdigest() != entry['manifest_sha256']:
                raise ValueError('archived Pack manifest identity mismatch')
            manifest = json.loads(data)
            if manifest['id'] != pack_id or manifest['version'] != entry['version'] or pack_id in packs:
                raise ValueError('catalog build Pack identity mismatch')
            packs[pack_id] = {'manifest': manifest, 'files': entry['files'],
                              'manifest_sha256': entry['manifest_sha256'],
                              'closure_sha256': entry['closure_sha256']}
    return packs


def main():
    baseline = Path(sys.argv[1]).resolve(strict=True)
    json_output = sys.argv[2] == 'json'
    candidate_pin = json.loads((ROOT / 'packy-release.json').read_text())
    try:
        baseline_pin = json.loads((baseline / 'packy-release.json').read_text())
    except (OSError, ValueError):
        baseline_pin = None
    old_pin = json.loads(OLD_PIN.read_text())
    # This is a bounded exception for the single reviewed incompatible cut.
    # Every other baseline remains subject to Packy's ordinary baseline check.
    if ((candidate_pin.get('version'), candidate_pin.get('source_commit')) != NEW_VERSION or
            baseline_pin != old_pin):
        command = [str(ROOT / 'scripts/packy.sh'), 'catalog', 'validate', '--project', str(ROOT),
                   '--baseline', str(baseline)]
        if json_output:
            command.append('--json')
        return subprocess.call(command)
    try:
        validation = run([str(ROOT / 'scripts/packy.sh'), 'catalog', 'validate', '--project', str(ROOT), '--json'])
        with tempfile.TemporaryDirectory(prefix='catalog-transition-') as scratch:
            scratch = Path(scratch)
            previous = build(baseline, scratch / 'previous', True)
            current = build(ROOT, scratch / 'current', False)
            reported = {entry['id']: entry for entry in validation['packs']}
            if set(reported) != set(current) or any(
                reported[pack_id]['manifest_sha256'] != entry['manifest_sha256'] or
                reported[pack_id]['closure_sha256'] != entry['closure_sha256'] or
                reported[pack_id]['files'] != len(entry['files'])
                for pack_id, entry in current.items()
            ):
                raise ValueError('candidate changed between validation and version comparison')
            compare_packs(current, previous)
        if json_output:
            print(json.dumps(validation, separators=(',', ':')))
        else:
            print('Catalog Project valid; independent versions verified across the v0.2.31 to v0.2.32 contract cut')
        return 0
    except (OSError, ValueError, KeyError, tarfile.TarError) as error:
        message = str(error)
        print(message, file=sys.stderr)
        if json_output:
            print(json.dumps({'schema_version': 1, 'report': 'catalog-validation', 'result': 'invalid',
                              'fitness_rows': 0, 'error': {'code': 'validation_failed', 'message': message}}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
