import json
import tempfile
import uuid

import pytest


def write_config(filename, config):
    with open(filename, 'w') as f:
        f.write(config)


@pytest.mark.parametrize("data", [
    {
        "config": """{
            "auths": {
                "https://index.docker.io/v1/": {
                    "auth": "b64_username_password"
                }
            }
        }
        """,
        "valid": True
    },
    {
        "config": "not json",
        "valid": False
    }
])
def test_registry(cli, data):
    _, config_filename = tempfile.mkstemp()

    config_name = uuid.uuid4().hex

    write_config(config_filename, data['config'])

    create_cmd = cli('registry', 'create',
                     f'-n {config_name}',
                     f'-f {config_filename}')
    list_cmd = cli('registry', 'list')

    if data['valid']:
        assert create_cmd.return_code == 0
        assert config_name in list_cmd.out
        data['config'].replace('b64_username_password', 'new_b64_password')
        write_config(config_filename, data['config'])
        update_cmd = cli('registry', 'update',
                         f'-n {config_name}',
                         f'-f {config_filename}')
        assert update_cmd.return_code == 0
        assert 'Updated' in update_cmd.out
        get_cmd = cli('registry', 'get', f'-n {config_name}')
        assert get_cmd.return_code == 0
        assert json.loads(data['config']) == json.loads(get_cmd.out)
        delete_cmd = cli('registry', 'delete', f'-n {config_name}')
        assert delete_cmd.return_code == 0
        assert 'Deleted' in delete_cmd.out
    else:
        assert config_name not in list_cmd.out
        assert create_cmd.return_code == 1
