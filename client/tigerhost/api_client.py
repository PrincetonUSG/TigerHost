import requests
import urlparse

from wsse import WSSEAuth


class ApiClientResponseError(Exception):

    def __init__(self, response):
        """Create a new ``ApiClientResponseError``.

        @type response: requests.Response
        """
        self.response = response

    def __unicode__(self):
        return """Response Code {code}

        {body}
        """.format(code=self.response.status_code, body=self.response.text)

    def __str__(self):
        return self.__unicode__().encode('utf-8')


class ApiClientAuthenticationError(ApiClientResponseError):
    pass


class ApiClient(object):

    def __init__(self, api_server_url, username, api_key):
        """Create a new ``ApiClient``.

        @type api_server_url: str
        @type username: str
        @type api_key: str
        """
        self.api_server_url = api_server_url
        self.username = username
        self.api_key = api_key

    def _request_and_raise(self, method, path, **kwargs):
        """Sends a request to the api server.

        @type method: str
            HTTP method, such as "POST", "GET", "PUT"

        @type path: str
            The extra http path to be appended to the deis URL

        @rtype: requests.Response

        @raise e: ApiClientAuthenticationError
            if the response status code is 401

        @raise e: ApiClientResponseError
            if the response status code is not 401 and not in the [200, 300) range.
        """
        resp = requests.request(method, urlparse.urljoin(
            self.api_server_url, path), auth=WSSEAuth(self.username, self.api_key), **kwargs)

        if resp.status_code == 401:
            raise ApiClientAuthenticationError(resp)
        if not 200 <= resp.status_code < 300:
            raise ApiClientResponseError(resp)
        return resp

    def test_api_key(self):
        """Hit the test end point for API key

        @raise e: ApiClientResponseError
        @raise e: ApiClientAuthenticationError
        """
        self._request_and_raise('GET', 'api/test_api_key/')

    def get_providers(self):
        """Get the providers that this user has access to.

        @rtype: dict
            dictionary with the following format:
            {
                'providers': ['provider1', 'provider2', ...]
                'default': 'provider1'
            }
        """
        resp = self._request_and_raise('GET', 'api/v1/providers/')
        return resp.json()

    def create_application(self, app_id, provider=None):
        """Create a new application with the specified ID.

        @type app_id: str
        @type provider: str

        @raises ApiClientResponseError
        """
        body = {
            'id': app_id
        }
        if provider is not None:
            body['provider'] = provider
        self._request_and_raise('POST', 'api/v1/apps/', json=body)

    def delete_application(self, app_id):
        """Delete an application with the specified ID.

        @type app_id: str

        @raises ApiClientResponseError
        """
        self._request_and_raise('DELETE', 'api/v1/apps/{}/'.format(app_id))

    def get_all_applications(self):
        """Get all application IDs associated with this user.

        @rtype: dict
        format:
        {
            'provider1': ['app1', ...],
            'provider2': ['app1', ...],
            ...
        }
        """
        resp = self._request_and_raise('GET', 'api/v1/apps/')
        return resp.json()

    def set_application_env_variables(self, app_id, bindings):
        """Set the environmental variables for the specified app ID. To unset a variable, set it to ``None``.

        @type app_id: str

        @type bindings: dict
            The key-value pair to set in the environmental. ``None`` value = unset.

        @raises ApiClientResponseError
        """
        self._request_and_raise(
            'POST', 'api/v1/apps/{}/env/'.format(app_id), json=bindings)

    def get_application_env_variables(self, app_id):
        """Get the environmental variables for the specified app ID.

        @type app_id: str

        @rtype: dict
            The key-value pair representing the environmental variables

        @raises e: ApiClientResponseError
        """
        resp = self._request_and_raise(
            'GET', 'api/v1/apps/{}/env/'.format(app_id))
        return resp.json()

    def get_application_domains(self, app_id):
        """Get all domains associated with the specified app ID.

        @type app_id: str

        @rtype: list
            List of domains (str)

        @raises e: ApiClientResponseError
        """
        resp = self._request_and_raise(
            'GET', 'api/v1/apps/{}/domains/'.format(app_id))
        return resp.json()['results']

    def add_application_domain(self, app_id, domain):
        """Add a new domain to the specified app ID.

        @type app_id: str
        @type domain: str

        @raises e: ApiClientResponseError
        """
        self._request_and_raise(
            'POST', 'api/v1/apps/{}/domains/'.format(app_id), json={'domain': domain})

    def remove_application_domain(self, app_id, domain):
        """Remove a domain from the specified app ID.

        @type app_id: str
        @type domain: str

        @raises e: ApiClientResponseError
        """
        self._request_and_raise(
            'DELETE', 'api/v1/apps/{}/domains/{}/'.format(app_id, domain))

    def get_application_git_remote(self, app_id):
        """Get the git remote for the specified app ID.

        @type app_id: str

        @rtype: str

        @raises e: ApiClientResponseError
        """
        resp = self._request_and_raise('GET', 'api/v1/apps/{}/'.format(app_id))
        return resp.json()['remote']

    def get_application_owner(self, app_id):
        """Get the username of the owner of the specified app ID.

        @type app_id: str

        @rtype: str

        @raises e: ApiClientResponseError
        """
        resp = self._request_and_raise('GET', 'api/v1/apps/{}/'.format(app_id))
        return resp.json()['owner']

    def set_application_owner(self, app_id, username):
        """Set the owner of the application to be the specified username.
        Can only be done by someone with admin privilege on this application.

        @type app_id: str
        @type username: str

        @raises e: ApiClientResponseError
        """
        self._request_and_raise('POST', 'api/v1/apps/{}/'.format(app_id), json={
            'owner': username
        })

    def get_application_collaborators(self, app_id):
        """Returns the list of users sharing this application.
        This does NOT include the application owner.

        @type app_id: str

        @rtype: list
            The list of usernames of collaborators (str)

        @raises e: ApiClientResponseError
        """
        resp = self._request_and_raise(
            'GET', 'api/v1/apps/{}/collaborators/'.format(app_id))
        return resp.json()['results']

    def add_application_collaborator(self, app_id, username):
        """Adds the user with the specified username to the list of
        collaborators

        @type app_id: str
        @type username: str

        @raises e: ApiClientResponseError
        """
        self._request_and_raise('POST', 'api/v1/apps/{}/collaborators/'.format(app_id), json={
            'username': username
        })

    def remove_application_collaborator(self, app_id, username):
        """Removes the user with the specified username from the list of
        collaborators

        @type app_id: str
        @type username: str

        @raises e: ApiClientResponseError
        """
        self._request_and_raise(
            'DELETE', 'api/v1/apps/{}/collaborators/{}/'.format(app_id, username))

    def get_keys(self):
        """Get all public keys associated with this user.

        @rtype: dict
        format:
        {
            'provider1': [{
                            "key_name": "my_key_name",
                            "key": "ssh-rsa ..."
                            }, ...],
            'provider2': [...],
            ...
        }

        @raises e: ApiClientResponseError
        """
        resp = self._request_and_raise(
            'GET', 'api/v1/keys/')
        return resp.json()

    def add_key(self, key_name, key, provider):
        """Add a public key to this user.

        @type key_name: str
            An ID to be associated with this key

        @type key: str
        @type provider: str

        @raises e: ApiClientResponseError
        """
        self._request_and_raise('POST', 'api/v1/keys/', json={
            'key_name': key_name,
            'key': key,
            'provider': provider,
        })

    def remove_key(self, key_name, provider):
        """Remove the specified key from this user.

        @type key_name: str
            The ID associated with this key when added.

        @raises e: ApiClientResponseError
        """
        self._request_and_raise('DELETE', 'api/v1/keys/{}/{}/'.format(provider, key_name))
