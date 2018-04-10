import pytest
import responses
from Accounts.RegistrationHelper.AccountsRegistration import \
    AccountsRegistration
from Accounts.RegistrationHelper.UserCreationHelper import \
    UserCreationHelper
from Accounts.RegistrationHelper.UserCreationHelper import \
    UNEXPECTED_REGISTRATION_RESP_MSG, MAX_REGISTRATION_RETRIES_MSG
from RallyCommonRobotModules.RandomDataGenerator import RandomDataGenerator
from mockito import when
from robot.libraries.BuiltIn import BuiltIn


PARTNER = 'rally'
CLIENT = 'rally_health'
AFFILIATION = 'rally_base'
DATA_FIXTURE = RandomDataGenerator()
AUTH_RESP = {'user_info': {'displayName': 'Kirby', 'userId': None}, 'data_fixture': DATA_FIXTURE}


@pytest.fixture(scope="function")
def engage_url():
    when(BuiltIn).get_variable_value("${RALLY_ENGAGE_URL}").thenReturn(
        "https://monkey-server")


@pytest.fixture(scope="function")
def auth_reg():
    when(AccountsRegistration).register_user_in_auth(
        PARTNER, CLIENT, AFFILIATION).thenReturn(AUTH_RESP)


@pytest.fixture(scope="function")
def profile_payload():
    when(UserCreationHelper).generate_profile_payload(
        AUTH_RESP).thenReturn({'displayName': 'Kirby'})


@pytest.fixture(scope="function")
def log_level():
    when(BuiltIn).get_variable_value("${LOG LEVEL}").thenReturn(
        "DEBUG")


class TestUserCreationHelper(object):

    pytestmark = pytest.mark.usefixtures('unstub')

    @pytest.mark.usefixtures("engage_url", "auth_reg", "profile_payload", "log_level")
    @responses.activate
    def test_create_user_in_engage_200(self):
        responses.add(
            responses.POST,
            'https://monkey-server/play/rest/registration/profile',
            json={'userId': 12345}, status=200)

        UCH = UserCreationHelper()
        user_details = UCH.create_user_in_engage_using_api(PARTNER, CLIENT, AFFILIATION)

        expected = AUTH_RESP['user_info'].copy()
        expected['data_fixture'] = AUTH_RESP['data_fixture']
        assert user_details == expected
        assert len(responses.calls) == 1

    @pytest.mark.usefixtures("engage_url", "auth_reg", "profile_payload", "log_level")
    @responses.activate
    def test_create_user_in_engage_409(self):
        responses.add(
            responses.POST,
            'https://monkey-server/play/rest/registration/profile',
            json={'userId': 12345}, status=409)

        with pytest.raises(Exception) as excinfo:
            UCH = UserCreationHelper()
            UCH.create_user_in_engage_using_api(PARTNER, CLIENT, AFFILIATION)

        assert MAX_REGISTRATION_RETRIES_MSG % '409' in str(excinfo.value)
        assert len(responses.calls) == 5

    @pytest.mark.usefixtures("engage_url", "auth_reg", "profile_payload", "log_level")
    @responses.activate
    def test_create_user_in_engage_other_status_code(self):
        other_status_code = 404
        responses.add(
            responses.POST,
            'https://monkey-server/play/rest/registration/profile',
            json={'userId': 12345}, status=other_status_code)

        with pytest.raises(Exception) as excinfo:
            UCH = UserCreationHelper()
            UCH.create_user_in_engage_using_api(PARTNER, CLIENT, AFFILIATION)

        assert UNEXPECTED_REGISTRATION_RESP_MSG % other_status_code in \
               str(excinfo.value)
        assert len(responses.calls) == 1