#!/usr/bin/env python3
"""Download and verify the complete 335 catalogue plus named-settings handoff.

Python 3.9+; standard library only; no Git checkout or GitHub login required.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
import urllib.request
from zipfile import ZipFile

sys.dont_write_bytecode = True
RELEASE = 'https://github.com/recdpz/ravedio-avatar-previews/releases/download/avatar-art335-source/'
ART_COMMIT = 'f7a01d28eb3784310ace9c38af2f00e6df68af52'
CATALOGUE_SHA = '55a9409b199b46e313c2aa67e28b21789805f06292cac1f9933e1c1db15c7bfc'
ARCHIVES = {
    'catalogue': ('Ravedio335-full-source-catalogue.zip', 1197016866,
                  '4130f4500777b0457a3159cdf636b393ec2a3b61f6910cda5aa6238d3439e322'),
    'handoff': ('Ravedio335-mobile-selection-handoff.zip', 204636,
                '46402f6291fc5ddf9e5d9d88934a26144263754271c9e0f68e8d8222d42bb87e'),
}


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def checked_archive(path, size, checksum):
    if path.stat().st_size != size or digest(path) != checksum:
        raise ValueError('Archive size/checksum mismatch: ' + str(path))
    return path


def download(directory, record):
    name, size, checksum = record
    target = directory / name
    if target.exists():
        return checked_archive(target, size, checksum)
    temporary = directory / (name + '.' + str(os.getpid()) + '.part')
    if temporary.exists():
        raise ValueError('Existing partial download; use another output directory: ' + str(temporary))
    request = urllib.request.Request(RELEASE + name, headers={'User-Agent': 'Ravedio335-artwork-transfer'})
    print('Downloading ' + name + ' (' + str(size) + ' bytes)', flush=True)
    count = 0
    milestone = 0
    with urllib.request.urlopen(request, timeout=600) as response, temporary.open('xb') as stream:
        for chunk in iter(lambda: response.read(4 * 1024 * 1024), b''):
            stream.write(chunk)
            count += len(chunk)
            if count > size:
                raise ValueError('Download exceeds pinned size: ' + name)
            if count // (128 * 1024 * 1024) > milestone:
                milestone = count // (128 * 1024 * 1024)
                print('  ' + str(count // (1024 * 1024)) + ' MiB', flush=True)
    checked_archive(temporary, size, checksum)
    temporary.rename(target)
    return target


def contained_path(root, name):
    relative = PurePosixPath(name)
    if (relative.is_absolute() or not relative.parts or '\\' in name or
            any(part in ('..', '.') or ':' in part for part in relative.parts)):
        raise ValueError('Unsafe archive path: ' + name)
    path = root.joinpath(*relative.parts)
    path.resolve().relative_to(root.resolve())
    return path


def extract(archive, destination):
    if destination.exists():
        raise ValueError('Refusing to overwrite an existing directory: ' + str(destination))
    with ZipFile(archive) as source:
        entries = source.infolist()
        if sum(entry.file_size for entry in entries) > 3_000_000_000:
            raise ValueError('Unexpected expanded archive size')
        for entry in entries:
            contained_path(destination, entry.filename)
            if stat.S_ISLNK(entry.external_attr >> 16):
                raise ValueError('Symbolic links are not expected in the source archive')
        destination.mkdir()
        for entry in entries:
            target = contained_path(destination, entry.filename)
            if entry.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with source.open(entry) as incoming, target.open('xb') as outgoing:
                    shutil.copyfileobj(incoming, outgoing, length=4 * 1024 * 1024)


def verify_installation(root):
    catalogue = root / 'catalogue'
    handoff = root / 'handoff'
    if digest(catalogue / 'catalogue.json') != CATALOGUE_SHA:
        raise ValueError('Wrong catalogue.json; expected exact artwork 335')
    data = json.loads((catalogue / 'catalogue.json').read_bytes())
    if data['revision'] != 335 or len(data['components']) != 638 or len(data['fit_rows']) != 1792:
        raise ValueError('Incomplete 335 catalogue')
    print('Checking all 638 component checksums...', flush=True)
    for checksum, entry in data['components'].items():
        path = contained_path(catalogue, entry['file'])
        if path.stat().st_size != entry['bytes'] or digest(path) != checksum:
            raise ValueError('Component mismatch: ' + str(path))
    for name in ('Ravedio335-Wavy-bob.blend', 'sources/approved-B334.blend',
                 'tools/render_review.py', 'studio.json', 'palette.json'):
        if not (catalogue / name).is_file():
            raise ValueError('Missing source/renderer dependency: ' + name)
    manifest = json.loads((handoff / 'manifest.json').read_bytes())
    for name, entry in manifest['files'].items():
        path = contained_path(handoff, name)
        if path.stat().st_size != entry['bytes'] or digest(path) != entry['sha256']:
            raise ValueError('Handoff file mismatch: ' + str(path))
    spec = importlib.util.spec_from_file_location('ravedio335_asset_reference', handoff / 'resolve_avatar.py')
    resolver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(resolver)
    examples = json.loads((handoff / 'named-examples.json').read_bytes())
    for example in examples:
        if resolver.resolve(example['input'], data, catalogue) != example['expected']:
            raise ValueError('Worked example mismatch: ' + example['id'])
    return {'artworkRevision': 335, 'artworkCommit': ART_COMMIT,
            'catalogueSha256': CATALOGUE_SHA, 'componentsVerified': 638,
            'fitRows': 1792, 'workedExamplesVerified': len(examples),
            'catalogue': str(catalogue.resolve()), 'handoff': str(handoff.resolve()),
            'protocolChanged': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path, help='Fresh output directory, e.g. ./Ravedio335')
    parser.add_argument('--catalogue-archive', type=Path, help='Reuse a local checksum-pinned full catalogue ZIP')
    parser.add_argument('--handoff-archive', type=Path, help='Reuse a local checksum-pinned handoff ZIP')
    args = parser.parse_args()
    root = args.destination.resolve()
    root.mkdir(parents=True, exist_ok=True)
    receipt = root / 'INSTALLATION.json'
    if receipt.is_file():
        result = verify_installation(root)
    else:
        if (root / 'catalogue').exists() or (root / 'handoff').exists():
            raise ValueError('Use a fresh output directory; existing files are not overwritten')
        downloads = root / 'downloads'
        downloads.mkdir(exist_ok=True)
        if shutil.disk_usage(root).free < 3_700_000_000:
            raise ValueError('Allow at least 3.7 GB free for downloaded and expanded source assets')
        supplied = {'catalogue': args.catalogue_archive, 'handoff': args.handoff_archive}
        for key, record in ARCHIVES.items():
            name, size, checksum = record
            path = checked_archive(supplied[key], size, checksum) if supplied[key] else download(downloads, record)
            print('Extracting ' + name, flush=True)
            extract(path, root / key)
        result = verify_installation(root)
    receipt.write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
    print('READY: complete artwork 335 and handoff verified.', flush=True)
    print('Catalogue: ' + result['catalogue'])
    print('Handoff:   ' + result['handoff'])
    print('Start with handoff/README.md and handoff/named-examples.json.')
    print('Use named settings for 3D testing; the larger wire profile is still proposed.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        raise SystemExit('335 setup failed: ' + str(error))
