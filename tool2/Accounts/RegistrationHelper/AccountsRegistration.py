import logging

from robot.libraries.BuiltIn import BuiltIn

from Accounts.RegistrationHelper import _common
from EligibilityCreation import EligibilityCreation
from RallyCommonRobotModules.RandomDataGenerator import RandomDataGenerator
from RallyCommonRobotModules import DateHelper
from PyUtils.RestClientLibrary import RestClientLibrary, no_response_code_check


MAX_ELIGIBILITY_RETRIES_MSG = \
    "Eligibility creation failed after 5 tries. Received %s on final attempt."
ELIGIBILITY_RETRY_MSG = \
    "Received 400 on eligibility creation - this often indicates the " \
    "generated partnerUserId already exists in the db. Attempting retry " \
    "with new payload."
UNEXPECTED_ELIGIBILITY_RESP_MSG = \
    "Eligibility creation failed. Received '%s' response status."


class AccountsRegistration(RestClientLibrary):
    """Keywords for creating users rally users using different methods.

    User creation methods includes upserting eligibility records to SH instead
    of rally admin.
    """

    def __init__(self):
        super(AccountsRegistration, self).__init__()
        self.PARTNERS_WITH_GENERIC_ELIGIBILITY = \
            ["all_savers", "baf", "excellus", "great_west_life", "rally",
             "rally_demo", "rally_direct", "univera"]

    @no_response_code_check
    def register_user_in_auth(self, partner='rally', client=None,
                              affiliation=None, attempts=5):
        """
        A dictionary with the created user's info along with auth and
        session token is returned. The data fixture used for upsert is
        returned as well with key `data_fixture`.

        Arguments:
        - ``partner`` Partner info for the user
        - ``client`` Client info for the user
        - ``affiliation`` Affiliation info for the user
        """
        if affiliation and not client:
            raise ValueError("If affiliation is specified, client must also be specified")
        if not client:
            client = _common.get_default_client(partner)
        payload = None
        response = None
        max_attempts = attempts = int(attempts)

        sh_env = BuiltIn().get_variable_value("${RALLY_SORTINGHAT_ENV}")
        if sh_env:
            self.session.headers.update({'X-Rally-SortingHat-Env': sh_env})

        while attempts >= 0:
            if attempts == 0:
                raise Exception(MAX_ELIGIBILITY_RETRIES_MSG %
                                response.status_code)
            data_fixture, payload = self.generate_new_eligibility_payload(partner, client, affiliation)

            logging.debug("%d/%d eligibility creation attempts remaining." % (attempts, max_attempts))
            response = \
                self.session.post(
                    BuiltIn().get_variable_value("${RALLY_ACCOUNTS_URL}")
                    + '/auth/v1/registerWithEligibility',
                    json=payload,
                    )
            if response.status_code == 200:
                logging.info(response.text)
                break
            elif response.status_code == 400:
                logging.warn(ELIGIBILITY_RETRY_MSG)
                logging.info(response.text)
                attempts -= 1
            else:
                logging.info(response.text)
                raise Exception(UNEXPECTED_ELIGIBILITY_RESP_MSG %
                                response.status_code)
        return {'user_info': payload,
                'auth_token': response.json()['authToken'],
                'session_token': response.json()['sessionToken'],
                'data_fixture': data_fixture}

    def generate_new_eligibility_payload(self, partner='rally', client=None, affiliation=None):
        if affiliation and not client:
            raise ValueError("If affiliation is specified, client must also be specified")
        if not client:
            client = _common.get_default_client(partner)
        data_fixture = RandomDataGenerator()
        res = EligibilityCreation(). \
            create_and_upsert_eligibity_record_in_sortinghat(
            partner, data_fixture=data_fixture, client=client, affiliation=affiliation)

        BuiltIn().log(res)
        if partner in self.PARTNERS_WITH_GENERIC_ELIGIBILITY:
            dob_new = DateHelper.convert_date_to_format(
                res['payload']['fields']['inUserData']['dob'],
                "%Y-%m-%dT%H:%M:%S.%f", "%m/%d/%Y")
            location_of_fields = res['payload']['fields']['inUserData']
        elif partner == 'bcbs_south_carolina':
            dob_new = DateHelper.convert_date_to_format(
                res['payload']['fields']['requiredEligibilityFields']['dob'],
                'epoch', "%m/%d/%Y")
            location_of_fields = \
                res['payload']['fields']['requiredEligibilityFields']
        elif partner == 'optum':
            dob_new = DateHelper.convert_date_to_format(
                res['payload']['fields']['requiredEligibilityFields']['dob'],
                'epoch', "%m/%d/%Y", in_utc=True)
            location_of_fields = res['payload']['fields']['requiredEligibilityFields']
        default_sponsor_fields = [
            {
                'id': 'first_name',
                'data': location_of_fields['firstName'],
                'dataType': 'String'
            },
            {
                'id': 'last_name',
                'data': location_of_fields['lastName'],
                'dataType': 'String'
            },
            {
                'id': 'date_of_birth',
                'data': dob_new,
                'dataType': 'DateTime'
            }
        ]

        if partner in self.PARTNERS_WITH_GENERIC_ELIGIBILITY:
            partner_sponsor_field = [
                {
                    'id': 'last_four_ssn',
                    'data': res['payload']['fields']['last4SSN'],
                    'dataType': 'String',
                }
            ]
        elif partner == 'optum':
            partner_sponsor_field = [
                {
                    'id': 'search_id',
                    'data': location_of_fields['searchId'],
                    'dataType': 'String',
                }
            ]
        elif partner == 'bcbs_south_carolina':
            partner_sponsor_field = [
                {
                    'id': 'id_card_no',
                    'data': location_of_fields['idCardNumber'],
                    'dataType': 'String',
                }
            ]
        else:
            raise ValueError('No valid partner information was provided')

        sponsor_fields = default_sponsor_fields + partner_sponsor_field
        payload = {
            'email': RandomDataGenerator().test_email,
            'password': RandomDataGenerator().password,
            'acceptedToS': True,
            'acceptedHipaa': True,
            'eligFields': sponsor_fields,
            'legalAgreements': [],
            'locale': 'en-US',
            'product': 'engage',
            'promoCode': 'none-none',
            'partner': partner,
            'client': client,
            'clientUrlSlug': None,
            'inviteCode': None
        }
        if affiliation:
            payload['affiliation'] = affiliation
        return data_fixture, payload
