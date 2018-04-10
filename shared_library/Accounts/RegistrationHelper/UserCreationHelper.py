import time
import logging

from robot.libraries.BuiltIn import BuiltIn

from Accounts.RegistrationHelper import _common
from RallyPageObjects.RegistrationLandingPage import RegistrationLandingPage
from RallyPageObjects.RegistrationSetEmailPasswordPage \
    import RegistrationSetEmailPasswordPage
from RallyPageObjects.RegistrationHipaaPage import RegistrationHipaaPage
from RallyPageObjects.RegistrationSetEligibilityInfoPage \
    import RegistrationSetEligibilityInfoPage
from RallyPageObjects.CreateProfilePage import CreateProfilePage
from RallyPageObjects.SurveyPage import SurveyPage
from RallyCommonRobotModules.RandomDataGenerator import RandomDataGenerator
import RallyCommonRobotModules.utils.CoreUtils
from Accounts.RegistrationHelper.EligibilityCreation import EligibilityCreation
from Accounts.RegistrationHelper.AccountsRegistration import AccountsRegistration
from PyUtils.RestClientLibrary import RestClientLibrary, no_response_code_check


MAX_REGISTRATION_RETRIES_MSG = \
    "Reached maximum number of profile registration attempts. " \
    "Received %s on last attempt"
REGISTRATION_RETRY_MSG = \
    "Received 409 on profile registration, possibly due to username '%s' " \
    "already taken. Retrying with new username and payload."
UNEXPECTED_REGISTRATION_RESP_MSG = \
    "Profile registration failed. Received '%s' response status."


class UserCreationHelper(RestClientLibrary):
    """Keywords for creating users rally users using different methods.

    User creation methods includes upserting eligibility records to SH instead
    of rally admin.
    """

    def __init__(self):
        super(UserCreationHelper, self).__init__()

    def create_user_using_eligibility_record_via_ui(
            self,
            partner,
            client=None,
            data_fixture=None
    ):
        """End to end user creation: will create a user using elig record and
         register that user through the UI

        Last page navigated to will be the survey welcome page.

        Pre-condition:
        - Browser already opened

        Arguments:
        - ``data_fixture:``             By default a random data obj is
                                        generated as the data_fixture if none
                                        is passed.
        - ``partner:``                  Partner of the new user
        -  `client:``                   Client of the new user

        Examples:
        | Create User using Eligibility Record via UI | bcbs_south_carolina
        | Create User using Eligibility Record via UI | optum | optum_default
        | Create User using Eligibility Record via UI | rally
        """
        if not client:
            client = _common.get_default_client(partner)
        if data_fixture is None:
            data_fixture = RandomDataGenerator().set_random_data()

        EligibilityCreation().create_and_upsert_eligibity_record_in_sortinghat(
            partner,
            data_fixture)
        RegistrationLandingPage().load_registration_landing_page(
            partner,
            client)
        RegistrationLandingPage().click_the_sign_up_button()
        RegistrationSetEmailPasswordPage() \
            .fill_and_submit_email_and_password_registration_page(
            data_fixture.test_email,
            data_fixture.password
        )
        RegistrationHipaaPage().submit_hipaa_page_if_applicable()
        RegistrationSetEligibilityInfoPage() \
            .fill_and_submit_eligibility_info_registration_page(
            data_fixture.member_id,
            data_fixture.last_name,
            data_fixture.dob_format_mdy,
            data_fixture.ssn_last_4_digits,
            data_fixture.first_name,
            data_fixture.ssn_with_dashes,
            data_fixture.group_number
        )
        CreateProfilePage() \
            .enter_username_and_submit_create_profile_page(
            data_fixture.username
        )
        SurveyPage().verify_survey_welcome_page_is_loaded()

    @no_response_code_check
    def create_user_in_engage_using_api(self,
                                        partner='rally',
                                        client=None,
                                        affiliation=None,
                                        attempts=5,
                                        sleep=0.5):
        """Creates an eligibility record for user and registers the user

        Returns a dictionary that is an combination of the registration payload, the user info returned from
        `RallyCommonRobotModules.RegistrationHelpers.AccountsRegistration.Register User In Auth`, and the data_fixture
        used when creating the eligibility record. The data fixture is the value of the key ``data_fixture``.
        The data fixture is an instance of `RallyCommonRobotModules.RandomDataGenerator`.

        Arguments:
        - ``partner:``                Partner of the new user
        - ``client:``                 Client of the new user
        - ``affiliation``             affiliation to use
        - ``attempts``                The number of times to attempt the
                                      registration api request
        - ``sleep``                   Time in seconds to wait between attempts

        Examples:
        | &{user_info} | Create User In Engage Using API |                     |             |         |
        | &{user_info} | Create User In Engage Using API | univera             |             |         |
        | &{user_info} | Create User In Engage Using API | optum               | some_client |         |
        | &{user_info} | Create User In Engage Using API | bcbs_south_carolina | uc          | uhf78dg |

        Getting information from the return value:
        | ${user_id}         | Get From Dictionary | ${user_info}                                 | userId   |
        | ${email}           | Get From Dictionary | ${user_info}                                 | email    |
        | ${password}        | Get From Dictionary | ${user_info}                                 | password |
        | ${partner_user_id} | Set Variable        | ${user_info['data_fixture'].partner_user_id} |          |
        """
        if affiliation and not client:
            raise ValueError("If affiliation is specified, client must also be specified")
        if not client:
            client = _common.get_default_client(partner)
        auth_req = None
        response = None
        seconds = int(sleep)
        max_attempts = attempts = int(attempts)

        url = BuiltIn().get_variable_value("${RALLY_ENGAGE_URL}") \
              + '/play/rest/registration/profile'

        while attempts >= 0:
            if attempts == 0:
                raise Exception(MAX_REGISTRATION_RETRIES_MSG %
                                response.status_code)
            auth_req = AccountsRegistration(). \
                register_user_in_auth(partner, client, affiliation)
            payload = UserCreationHelper. \
                generate_profile_payload(self, auth_req)
            response = \
                self.session.post(url, json=payload)

            logging.debug("%d/%d profile registration attempts remaining." % (attempts, max_attempts))

            if response.status_code == 200:
                logging.info(response.text)
                break
            elif response.status_code == 409:
                logging.warn(REGISTRATION_RETRY_MSG % payload['displayName'])
                attempts -= 1
                if attempts > 0:
                    time.sleep(seconds)
            else:
                raise Exception(UNEXPECTED_REGISTRATION_RESP_MSG %
                                response.status_code)

        auth_req['user_info']['userId'] = response.json()['userId']
        ret = dict(list(payload.items()) + list(auth_req['user_info'].items()))
        ret['data_fixture'] = auth_req['data_fixture']
        return ret

    def generate_profile_payload(self, auth_req):
        user_name = "qaRf_" \
                    + RallyCommonRobotModules.utils.CoreUtils. \
                        generate_allowed_username()
        payload = {
            'viewTypeParam': 'create-profile',
            'authToken': auth_req['auth_token'],
            'sessionToken': auth_req['session_token'],
            'displayName': user_name,
            'avatar': 'avatars_BlondeGirl.png',
            'fields': [],
            'legalAgreements': [],
        }
        return payload
