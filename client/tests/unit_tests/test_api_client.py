import pytest
import responses
import urlparse

from tigerhost.api_client import ApiClient, ApiClientResponseError, ApiClientAuthenticationError


@pytest.fixture()
def fake_api_server_url():
    return 'http://fake'


@pytest.fixture()
def api_client(fake_api_server_url):
    return ApiClient(username='', api_key='', api_server_url=fake_api_server_url)


@responses.activate
def test_request_and_raise_failure(api_client, fake_api_server_url):
    path = 'v1/auth/register/'
    responses.add(responses.POST, urlparse.urljoin(
        fake_api_server_url, path), status=400)
    with pytest.raises(ApiClientResponseError):
        api_client._request_and_raise('POST', path)


@responses.activate
def test_request_and_raise_failure_authentication(api_client, fake_api_server_url):
    path = 'v1/auth/register/'
    responses.add(responses.POST, urlparse.urljoin(
        fake_api_server_url, path), status=401)
    with pytest.raises(ApiClientAuthenticationError):
        api_client._request_and_raise('POST', path)


@responses.activate
def test_test_api_key_success(api_client, fake_api_server_url):
    """
    @type api_client: ApiClient
    @type fake_api_server_url: str
    """
    responses.add(responses.GET, urlparse.urljoin(
        fake_api_server_url, 'api/test_api_key/'), status=200)
    api_client.test_api_key()


@responses.activate
def test_get_all_applications_success(api_client, fake_api_server_url):
    """
    @type api_client: ApiClient
    @type fake_api_server_url: str
    """
    ret = {
        'provider1': ['testid1', 'testid2']
    }
    responses.add(responses.GET, urlparse.urljoin(
        fake_api_server_url, 'api/v1/apps/'), status=200, json=ret)
    assert api_client.get_all_applications() == ret


@responses.activate
def test_create_application_success(api_client, fake_api_server_url):
    """
    @type api_client: DeisAuthenticatedClient
    @type fake_api_server_url: str
    """
    responses.add(responses.POST, urlparse.urljoin(
        fake_api_server_url, 'api/v1/apps/'), status=201)
    api_client.create_application('testid')


@responses.activate
def test_delete_application_success(api_client, fake_api_server_url):
    responses.add(responses.DELETE, urlparse.urljoin(
        fake_api_server_url, 'api/v1/apps/{}/'.format('testid')), status=204)
    api_client.delete_application('testid')


@responses.activate
def test_set_application_env_variables_success(api_client, fake_api_server_url):
    responses.add(responses.POST, urlparse.urljoin(
        fake_api_server_url, 'api/v1/apps/{}/env/'.format('testid')), status=201)
    api_client.set_application_env_variables(
        'testid', {'TESTING': 'testing'})


@responses.activate
def test_get_application_env_variables_success(api_client, fake_api_server_url):
    bindings = {'TESTING': 'testing'}
    responses.add(responses.GET, urlparse.urljoin(
        fake_api_server_url, 'api/v1/apps/{}/env/'.format('testid')), status=200, json=bindings)
    ret = api_client.get_application_env_variables('testid')
    assert ret == bindings


@responses.activate
def test_get_application_domains(api_client, fake_api_server_url):
    domains = ['a.com', 'b.com']
    responses.add(responses.GET, urlparse.urljoin(
        fake_api_server_url, 'api/v1/apps/{}/domains/'.format('testid')), status=200, json={'results': domains})
    ret = api_client.get_application_domains('testid')
    assert ret == domains


@responses.activate
def test_add_application_domain(api_client, fake_api_server_url):
    domain = 'a.example.com'
    responses.add(responses.POST, urlparse.urljoin(
        fake_api_server_url, 'api/v1/apps/{}/domains/'.format('testid')), status=201)
    api_client.add_application_domain('testid', domain)


@responses.activate
def test_remove_application_domain(api_client, fake_api_server_url):
    domain = 'a.example.com'
    responses.add(responses.DELETE, urlparse.urljoin(
        fake_api_server_url, 'api/v1/apps/{}/domains/{}/'.format('testid', domain)), status=204)
    api_client.remove_application_domain('testid', domain)


@responses.activate
def test_get_application_git_remote(api_client, fake_api_server_url):
    responses.add(responses.GET, urlparse.urljoin(
        fake_api_server_url, 'api/v1/apps/{}/'.format('testid')), status=200, json={'remote': 'git@fake'})
    assert api_client.get_application_git_remote(
        'testid') == 'git@fake'


@responses.activate
def test_get_application_owner(api_client, fake_api_server_url):
    responses.add(responses.GET, urlparse.urljoin(
        fake_api_server_url, 'api/v1/apps/{}/'.format('testid')), status=200, json={'owner': 'username'})
    assert api_client.get_application_owner(
        'testid') == 'username'


@responses.activate
def test_set_application_owner(api_client, fake_api_server_url):
    responses.add(responses.POST, urlparse.urljoin(
        fake_api_server_url, 'api/v1/apps/{}/'.format('testid')), status=200)
    api_client.set_application_owner('testid', 'username')


@responses.activate
def test_get_application_collaborators(api_client, fake_api_server_url):
    users = ['user1', 'user2']
    responses.add(responses.GET, urlparse.urljoin(
        fake_api_server_url, 'api/v1/apps/{}/collaborators/'.format('testid')), status=200, json={'results': users})
    ret = api_client.get_application_collaborators('testid')
    assert set(ret) == set(users)


@responses.activate
def test_add_application_collaborator(api_client, fake_api_server_url):
    username = 'username'
    responses.add(responses.POST, urlparse.urljoin(
        fake_api_server_url, 'api/v1/apps/{}/collaborators/'.format('testid')), status=201)
    api_client.add_application_collaborator('testid', username)


@responses.activate
def test_remove_application_collaborator(api_client, fake_api_server_url):
    username = 'username'
    responses.add(responses.DELETE, urlparse.urljoin(
        fake_api_server_url, 'api/v1/apps/{}/collaborators/{}/'.format('testid', username)), status=204)
    api_client.remove_application_collaborator(
        'testid', username)


@responses.activate
def test_get_application_keys(api_client, fake_api_server_url):
    keys = ['key1', 'key2']
    responses.add(responses.GET, urlparse.urljoin(
        fake_api_server_url, 'api/v1/keys/'), status=200, json={'results': [{'key_name': x, 'key': x} for x in keys]})
    ret = api_client.get_keys()
    assert ret == [{'key_name': x, 'key': x} for x in keys]


@responses.activate
def test_add_application_key(api_client, fake_api_server_url):
    responses.add(responses.POST, urlparse.urljoin(
        fake_api_server_url, 'api/v1/keys/'), status=201)
    api_client.add_key('key_name', 'key')


@responses.activate
def test_remove_application_key(api_client, fake_api_server_url):
    key_name = 'key_name'
    responses.add(responses.DELETE, urlparse.urljoin(
        fake_api_server_url, 'api/v1/keys/{}/'.format(key_name)), status=204)
    api_client.remove_key(key_name)
