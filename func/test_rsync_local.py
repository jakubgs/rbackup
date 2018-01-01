import os
import yaml
import pytest
from filecmp import cmpfiles
from random import sample
from string import ascii_lowercase
from tempfile import NamedTemporaryFile, mkdtemp

from rbackup.script import main as rbackup


def gen_filename(length=8):
    return ''.join(sample(ascii_lowercase, length))


@pytest.fixture
def config():
    src = mkdtemp(prefix='asset_src')
    dest = mkdtemp(prefix='target_dest')
    conf = {
        'assets': [
            {
                'id': 'asset_id',
                'src': src + '/',
                'dest': dest,
                'type': 'rsync',
                'target': 'local',
            }
        ],
        'targets': [],
    }
    yield conf
    os.rmdir(src)
    os.rmdir(dest)


@pytest.fixture
def gen_files(config):
    fnames = [gen_filename() for i in range(5)]
    assets = [
        os.path.join(config['assets'][0]['src'], fname)
            for fname in fnames
    ]
    for afile in assets:
        os.mknod(afile)
    yield fnames
    for afile in assets:
        os.remove(afile)
    for fname in fnames:
        os.remove(os.path.join(config['assets'][0]['dest'], fname))


@pytest.fixture
def config_file(config, gen_files):
    with NamedTemporaryFile(prefix='config_', mode='w') as cfg_file:
        yaml.dump(config, cfg_file)
        yield cfg_file


def test_rsync(config, config_file, gen_files):
    rbackup([
        'save', 'asset_id',
        '--config', config_file.name,
    ])
    # compare files to verify the rsync succeeded
    match, miss, err = cmpfiles(
        config['assets'][0]['src'], config['assets'][0]['dest'], gen_files
    )
    assert len(match) == len(gen_files)
    assert len(miss) == 0
    assert len(err) == 0
