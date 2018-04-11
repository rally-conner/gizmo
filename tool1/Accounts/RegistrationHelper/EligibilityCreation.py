import json

import requests
from robot.libraries.BuiltIn import BuiltIn

from Accounts.RegistrationHelper import _common
from EligibilityPayloadHelper import EligibilityPayloadHelper
from RallyCommonRobotModules.RandomDataGenerator import RandomDataGenerator
from RallyCommonRobotModules.Clients.SortingHat.AffiliationClient import \
    AffiliationClient


class EligibilityCreation(object):
    """Keywords for creating users rally users using different methods.

    User creation methods includes upserting eligibility records to SH instead
    of rally admin.
    """

    def __init__(self):
        self.PARTNERS_WITH_GENERIC_ELIGIBILITY = \
            ["all_savers", "baf", "excellus", "great_west_life", "rally",
             "rally_demo", "rally_direct", "univera"]

    def create_and_upsert_eligibity_record_in_sortinghat(
            self,
            partner='rally',
            data_fixture=None,
            client=None,
            affiliation=None):
        """Creates a payload and upserts eligibility record

        Arguments:
        - ``partner:``                  Partner to create and upsert elig
                                        record for
        - ``data_fixture:``             By default a random data obj is
                                        generated as the data_fixture if none
                                        is passed random data by using
                                        RandomDataGenerator.py lib.
        - ``client``                    Client
        - ``affiliation``               Affiliation
        - ``return:``                   Response object from the upsert request
        """
        if data_fixture is None:
            data_fixture = RandomDataGenerator().set_random_data()
        if affiliation and not client:
            raise ValueError("If affiliation is specified, client must also be specified")
        if not client:
            client = _common.get_default_client(partner)

        payload = self.generate_eligibility_record_payload_for_sorthinghat(
            partner,
            data_fixture,
            client,
            affiliation)
        raw_json_response = self._upsert_eligibility_record_to_sortinghat(
            payload,
            partner)
        return raw_json_response

    def generate_eligibility_record_payload_for_sorthinghat(
            self,
            partner,
            data_fixture=None,
            client=None,
            affiliation=None):
        """Creates payload to be used for the upsert eligibility request

        Arguments:
        - ``partner:``                  Partner to create upsert payload for
        - ``data_fixture:``             By default a random data obj is
                                        generated as the data_fixture if none
                                        is passed.
        - ``client``                    Client
        - ``affiliation``               Affiliation
        - ``return:``                   Json payload representing elig record
                                        for the upsert request
        """
        if data_fixture is None:
            data_fixture = RandomDataGenerator().set_random_data()
        if affiliation and not client:
            raise ValueError("If affiliation is specified, client "
                             "must also be specified")
        if not client:
            client = _common.get_default_client(partner)
        if partner == 'bcbs_south_carolina':
            payload = \
                EligibilityPayloadHelper().create_bcbs_eligibility_payload(
                    partner,
                    data_fixture)
        elif partner == 'health_alliance':
            payload = EligibilityPayloadHelper() \
                .create_health_alliance_eligibility_payload(
                partner,
                data_fixture)
        elif partner == 'optum':
            payload = EligibilityPayloadHelper() \
                .create_optum_eligibility_payload(data_fixture)
        elif partner in self.PARTNERS_WITH_GENERIC_ELIGIBILITY:
            payload = EligibilityPayloadHelper() \
                .create_generic_eligibility_payload(partner, data_fixture)
        else:
            raise ValueError(
                "Partner %s is unsupported for SH eligibility upsert" %
                partner)

        # default clients like optum_default may not have clientIds and
        # without a clientId, the user will be associated to the default client anyways
        if client != _common.get_default_client(partner):
            client_data = AffiliationClient().find_client(partner, client)
            client_ids = client_data['clientIds']
            if client_ids:
                client_id = client_ids[0]
                payload['clientId'] = client_id
            else:
                raise RuntimeError("No clientIds associated with the client")

        if affiliation:
            affiliation_data = AffiliationClient().find_affiliation(partner, client, affiliation)
            segmentation_ids = affiliation_data['segmentationIds']
            if segmentation_ids:
                segmentation_id = segmentation_ids[0]
                payload["segmentationId"] = segmentation_id
                payload["fields"]["segmentation"] = {"segmentationId": segmentation_id}
            else:
                raise RuntimeError("No segmentationIds associated with the affiliation")

        pretty_payload = json.dumps(payload, indent=4, sort_keys=True)
        BuiltIn().log(pretty_payload)
        return payload

    def _upsert_eligibility_record_to_sortinghat(
            self,
            payload,
            partner="optum"):
        """Makes the upsert eligiblity request to sortinghat

        Arguments:
        - ``payload:``                  Payload used for the request which is
                                        the payload specifying elig record.
        - ``partner:``                  Partner of the new user
        - ``return:``                   Response object
        """
        sortinghat_url = \
            BuiltIn().get_variable_value("${RALLY_SORTINGHATURL_URL}")
        response = requests.put(
            sortinghat_url + '/rest/eligibility/v1/%s/upsert'
            % partner, json=payload)
        assert response.status_code == 200, \
            "Problem occurred while upserting eligibility record, \
        (status_code=%s).\nERROR: %s" % (response.status_code, response.text)
        return {'payload': payload, 'response': response}
