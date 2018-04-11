import pytest
import responses
from Accounts.RegistrationHelper.AccountsRegistration import \
    AccountsRegistration
from mockito import when
from robot.libraries.BuiltIn import BuiltIn
from Accounts.RegistrationHelper.AccountsRegistration import \
    UNEXPECTED_ELIGIBILITY_RESP_MSG, MAX_ELIGIBILITY_RETRIES_MSG
from RallyCommonRobotModules.RandomDataGenerator import RandomDataGenerator


PARTNER = 'rally'
CLIENT = 'rally_health'
AFFILIATION = 'rally_base'
PAYLOAD = {'user_info': 'bleep blap bloop'}
DATA_FIXTURE = RandomDataGenerator()


@pytest.fixture(scope="function")
def accounts_url():
    when(BuiltIn).get_variable_value("${RALLY_ACCOUNTS_URL}").thenReturn(
        "https://manatee-mountain")


@pytest.fixture(scope="function")
def sh_env_is_none():
    when(BuiltIn).get_variable_value("${RALLY_SORTINGHAT_ENV}").thenReturn(None)


@pytest.fixture(scope="function")
def sh_env_is_dev():
    when(BuiltIn).get_variable_value("${RALLY_SORTINGHAT_ENV}").thenReturn('dev')


@pytest.fixture(scope="function")
def elig_payload():
    when(AccountsRegistration).generate_new_eligibility_payload(
        PARTNER, CLIENT, AFFILIATION).thenReturn((DATA_FIXTURE, PAYLOAD))


@pytest.fixture(scope="function")
def log_level():
    when(BuiltIn).get_variable_value("${LOG LEVEL}").thenReturn(
        "DEBUG")


class TestAccountsRegistration(object):

    pytestmark = pytest.mark.usefixtures('unstub', 'accounts_url', 'sh_env_is_none', 'elig_payload', 'log_level')

    @responses.activate
    def test_create_user_in_engage_200(self):
        responses.add(
            responses.POST,
            'https://manatee-mountain/auth/v1/registerWithEligibility',
            json={'authToken': 'cowabunga',  'sessionToken': 'tubular'},
            status=200
        )
        elig_details = AccountsRegistration().register_user_in_auth(PARTNER, CLIENT, AFFILIATION)
        assert len(responses.calls) == 1
        assert elig_details == {'user_info': PAYLOAD,
                                'auth_token': 'cowabunga',
                                'session_token': 'tubular',
                                'data_fixture': DATA_FIXTURE}

    @responses.activate
    def test_create_user_in_engage_400(self):
        responses.add(
            responses.POST,
            'https://manatee-mountain/auth/v1/registerWithEligibility',
            json={'authToken': 'cowabunga',  'sessionToken': 'tubular'},
            status=400
        )
        with pytest.raises(Exception) as excinfo:
            AccountsRegistration().register_user_in_auth(PARTNER, CLIENT, AFFILIATION)
        assert len(responses.calls) == 5
        assert MAX_ELIGIBILITY_RETRIES_MSG % '400' in str(excinfo.value)

    @responses.activate
    def test_create_user_in_engage_other_status_code(self):
        other_status_code = 500
        responses.add(
            responses.POST,
            'https://manatee-mountain/auth/v1/registerWithEligibility',
            json={'authToken': 'cowabunga',  'sessionToken': 'tubular'},
            status=other_status_code
        )
        with pytest.raises(Exception) as excinfo:
            AccountsRegistration().register_user_in_auth(PARTNER, CLIENT, AFFILIATION)
        assert len(responses.calls) == 1
        assert UNEXPECTED_ELIGIBILITY_RESP_MSG % \
               other_status_code in str(excinfo.value)

    @responses.activate
    def test_create_user_in_engage_400_then_200(self):
        responses.add(
            responses.POST,
            'https://manatee-mountain/auth/v1/registerWithEligibility',
            status=400
        )
        responses.add(
            responses.POST,
            'https://manatee-mountain/auth/v1/registerWithEligibility',
            json={'authToken': 'cowabunga',  'sessionToken': 'tubular'},
            status=200
        )
        elig_details = AccountsRegistration().register_user_in_auth(PARTNER, CLIENT, AFFILIATION)
        assert len(responses.calls) == 2
        assert elig_details == {'user_info': PAYLOAD,
                                'auth_token': 'cowabunga',
                                'session_token': 'tubular',
                                'data_fixture': DATA_FIXTURE}


class TestAccountsRegistrationSortinghatEnv(object):

    pytestmark = pytest.mark.usefixtures('unstub', 'accounts_url', 'elig_payload', 'log_level')

    @pytest.mark.usefixtures('sh_env_is_dev')
    @responses.activate
    def test_sh_header_sent_when_sh_env_set(self):
        responses.add(
            responses.POST,
            'https://manatee-mountain/auth/v1/registerWithEligibility',
            json={'authToken': 'cowabunga',  'sessionToken': 'tubular'},
            status=200
        )
        AccountsRegistration().register_user_in_auth(PARTNER, CLIENT, AFFILIATION)
        assert responses.calls[0].request.headers['X-Rally-SortingHat-Env'] == 'dev'

    @pytest.mark.usefixtures('sh_env_is_none')
    @responses.activate
    def test_sh_header_not_sent_when_sh_env_is_none(self):
        responses.add(
            responses.POST,
            'https://manatee-mountain/auth/v1/registerWithEligibility',
            json={'authToken': 'cowabunga',  'sessionToken': 'tubular'},
            status=200
        )
        AccountsRegistration().register_user_in_auth(PARTNER, CLIENT, AFFILIATION)
        assert 'X-Rally-SortingHat-Env' not in responses.calls[0].request.headers