import base64
import json
from tempfile import mkstemp

from pytest import mark

from story.api import Registry
from story.commands import registry


@mark.parametrize('config_data', [{
    'registry_url': 'quay.io/username/repository_name',
    'username': 'username',
    'password': 'password'
}])
def test_registry_generate_config(config_data):
    config = registry.generate_config(**config_data)
    assert base64.b64decode(
        config['auths'][config_data['registry_url']]['auth']
    ).decode() == f"{config_data['username']}:{config_data['password']}"


@mark.parametrize('config_data', [{
    'type': '',     # default - docker_login
    'url': '',      # default - docker hub
    'username': 'my_dockerhub_username',
    'password': 'my_dockerhub_password'
}, {
    'type': 'docker_login',
    'url': 'quay.io',
    'username': 'my_quay_username',
    'password': 'my_quay_password',
}])
def test_registry_create_dockerlogin(runner, patch, config_data):

    config_name = 'my_config'

    patch.object(Registry, 'create')

    with runner.runner.isolated_filesystem():
        runner.run(
            registry.create,
            args=['-n', config_name],
            stdin='\n'.join(config_data.values()))

    config = registry.generate_config(
        registry_url=config_data['url'] or registry.DOCKER_HUB_REGISTRY_URL,
        username=config_data['username'],
        password=config_data['password']
    )

    Registry.create.assert_called_with(config_name, config)


@mark.parametrize('config_data', [{
    'type': 'gcr',
    'hostname': 'gcr.io',
    'service_account_json_key_path': 'conf_file_path'
}])
def test_registry_create_gcr(runner, patch, config_data):

    config_name = 'my_config'

    patch.object(Registry, 'create')
    patch.object(registry, 'load_json_file',
                 return_value='contents_of_conf_file_path')

    with runner.runner.isolated_filesystem():
        runner.run(
            registry.create,
            args=['-n', config_name],
            stdin='\n'.join(config_data.values())
        )

    config = registry.generate_config(
        registry_url=f'https://{config_data["hostname"]}',
        username='_json_key',
        password='contents_of_conf_file_path'
    )

    Registry.create.assert_called_with(config_name, config)


@mark.parametrize('config_json', [{
    'auths': {
        'https://index.docker.io/v1/': {
            'auth': 'b64_username_password'
        }
    }
}])
def test_registry_create_file(runner, patch, config_json):

    config_name = 'my_config'
    _, config_path = mkstemp()

    with open(config_path, 'w') as f:
        json.dump(config_json, f)

    # To be able to assert_called_with later
    patch.object(registry, 'load_json_file',
                 side_effect=registry.load_json_file)
    patch.object(Registry, 'create')

    with runner.runner.isolated_filesystem():
        runner.run(
            registry.create,
            args=[
                '-n', config_name,
                '-f', config_path
            ]
        )

    registry.load_json_file.assert_called_with(config_path)
    Registry.create.assert_called_with(config_name, config_json)


def test_registry_list(patch, runner):
    patch.object(Registry, 'list')
    with runner.runner.isolated_filesystem():
        runner.run(registry.list_command)
    Registry.list.assert_called_with()


def test_registry_get(patch, runner):

    config_name = 'my_config'

    patch.object(Registry, 'get', return_value='')

    with runner.runner.isolated_filesystem():
        runner.run(
            registry.get,
            args=['-n', config_name]
        )
    Registry.get.assert_called_with(config_name)


@mark.parametrize('file_args', [
    ['-f', '/tmp/config.json'],
    []
])
def test_registry_update(runner, patch, file_args):

    config_name = 'my_config'
    config_data = {'auths': {'url': {'auth': 'username:password'}}}

    patch.object(registry, 'get_config_interactive', return_value=config_data)
    patch.object(registry, 'load_json_file', return_value=config_data)
    patch.object(Registry, 'update')

    with runner.runner.isolated_filesystem():
        runner.run(
            registry.update,
            args=[
                '-n', config_name,
                *file_args
            ]
        )

    if file_args:
        registry.load_json_file.assert_called_with('/tmp/config.json')
    else:
        registry.get_config_interactive.assert_called_with()

    Registry.update.assert_called_with(config_name, config_data)


def test_registry_delete(runner, patch):

    config_name = 'my_config'

    patch.object(Registry, 'delete')

    with runner.runner.isolated_filesystem():
        runner.run(
            registry.delete,
            args=['-n', config_name]
        )

    Registry.delete.assert_called_with(config_name)
