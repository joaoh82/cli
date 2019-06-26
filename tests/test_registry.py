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

    runner.invoke(
        registry.create,
        args=[
            '-n', config_name,
            '-i'
        ],
        input='\n'.join(config_data.values()))

    config = registry.generate_config(
        registry_url=config_data['url'] or registry.DOCKER_HUB_REGISTRY_URL,
        username=config_data['username'],
        password=config_data['password']
    )

    Registry.create.assert_called_with(config_name, config)


@mark.parametrize('config_data', [{
    'type': 'gcr',
    'hostname': 'gcr.io',
    'service_account_json_key': '{"type": "service_account", ...}'
}])
def test_registry_create_gcr(runner, patch, config_data):

    config_name = 'my_config'

    patch.object(Registry, 'create')

    runner.invoke(
        registry.create,
        args=[
            '-n', config_name,
            '-i'
        ],
        input='\n'.join(config_data.values())
    )

    config = registry.generate_config(
        registry_url=f'https://{config_data["hostname"]}',
        username='_json_key',
        password=config_data['service_account_json_key']
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

    patch.object(registry, 'load_json', side_effect=registry.load_json)
    patch.object(Registry, 'create')

    runner.invoke(
        registry.create,
        args=[
            '-n', config_name,
            '-f', config_path
        ]
    )

    registry.load_json.assert_called_with(config_path)
    Registry.create.assert_called_with(config_name, config_json)


def test_registry_list(patch, runner):
    patch.object(Registry, 'list')
    runner.invoke(registry.list_command)
    Registry.list.assert_called_with()


def test_registry_get(patch, runner):

    config_name = 'my_config'

    patch.object(Registry, 'get')

    runner.invoke(
        registry.get,
        args=['-n', config_name]
    )
    Registry.get.assert_called_with(config_name)


@mark.parametrize('config_args', [
    ['-i'],
    ['-f', '/tmp/config.json']
])
def test_registry_update(runner, patch, config_args):

    config_name = 'my_config'
    config_data = {'auths': {'url': {'auth': 'username:password'}}}

    patch.object(registry, 'get_config_interactive', return_value=config_data)
    patch.object(registry, 'load_json', return_value=config_data)
    patch.object(Registry, 'update')

    runner.invoke(
        registry.update,
        args=[
            '-n', config_name,
            *config_args
        ]
    )

    if config_args[0] == '-i':
        registry.get_config_interactive.assert_called_with()
    elif config_args[0] == '-f':
        registry.load_json.assert_called_with('/tmp/config.json')

    Registry.update.assert_called_with(config_name, config_data)


def test_registry_delete(runner, patch):

    config_name = 'my_config'

    patch.object(Registry, 'delete')

    runner.invoke(
        registry.delete,
        args=[
            '-n', config_name
        ]
    )

    Registry.delete.assert_called_with(config_name)
