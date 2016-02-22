import pytest

from api_server.clients.deis_client_errors import DeisClientResponseError


@pytest.fixture
def deis_authenticated_client(deis_client, username, password, email):
    deis_client.register(username, password, email)
    return deis_client.login(username, password)


@pytest.yield_fixture
def create_application(deis_authenticated_client, app_id):
    """
    @type deis_authenticated_client: api_server.clients.deis_authenticated_client.DeisAuthenticatedClient
    """
    deis_authenticated_client.create_application(app_id)
    try:
        yield
    finally:
        deis_authenticated_client.delete_application(app_id)


def test_application_creation(deis_authenticated_client, app_id):
    """
    @type deis_authenticated_client: api_server.clients.deis_authenticated_client.DeisAuthenticatedClient
    """
    # create application
    deis_authenticated_client.create_application(app_id)

    with pytest.raises(DeisClientResponseError):
        deis_authenticated_client.create_application(app_id)

    ids = deis_authenticated_client.get_all_applications()
    assert ids == [app_id]

    # delete application
    deis_authenticated_client.delete_application(app_id)

    ids = deis_authenticated_client.get_all_applications()
    assert ids == []

    with pytest.raises(DeisClientResponseError):
        deis_authenticated_client.delete_application(app_id)


def test_application_env_variables(deis_authenticated_client, app_id, create_application):
    # test environmental variables
    bindings = {
        'TESTING1': '1',
        'TESTING2': '2'
    }
    old_vars = deis_authenticated_client.get_application_env_variables(app_id)
    deis_authenticated_client.set_application_env_variables(
        app_id, bindings)

    old_vars_updated = old_vars.copy()
    old_vars_updated.update(bindings)

    new_vars = deis_authenticated_client.get_application_env_variables(app_id)
    assert new_vars == old_vars_updated

    deis_authenticated_client.unset_application_env_variables(
        app_id, [key for key in bindings])
    new_vars_deleted = deis_authenticated_client.get_application_env_variables(
        app_id)
    assert old_vars == new_vars_deleted


def test_application_domains(deis_authenticated_client, app_id, create_application):
    domain = '{}.example.com'.format(app_id)
    old_domains = deis_authenticated_client.get_application_domains(app_id)
    deis_authenticated_client.add_application_domain(app_id, domain)
    assert deis_authenticated_client.get_application_domains(
        app_id) == old_domains + [domain]

    # can't add a domain twice
    with pytest.raises(DeisClientResponseError):
        deis_authenticated_client.add_application_domain(app_id, domain)

    deis_authenticated_client.remove_application_domain(app_id, domain)
    assert deis_authenticated_client.get_application_domains(
        app_id) == old_domains

    # can't remove a non-existent domain
    with pytest.raises(DeisClientResponseError):
        deis_authenticated_client.remove_application_domain(app_id, domain)
