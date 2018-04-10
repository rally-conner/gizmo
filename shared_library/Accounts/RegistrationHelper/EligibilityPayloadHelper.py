import json

from robot.libraries.String import String

import RallyCommonRobotModules.utils.CoreUtils
from RallyCommonRobotModules.RandomDataGenerator import RandomDataGenerator


class EligibilityPayloadHelper:
    """Creates the payload for upserting eligibility records to SH"""

    def create_generic_eligibility_payload(self, partner, data_fixture=None):
        """Creates a generic payload for upserting eligibility record to SH.

        A number of partners share the same payload structure for the upsert
         elig record request.
        List resides in UserCreationHelper.PARTNERS_WITH_GENERIC_ELIGIBILITY
        For registration in the UI use these partner/client combos and url:
                  GWL:
                   /partner/great_west_life/great_west_life_default/register,
                    id=last4ssn
                  Rally:
                   /partner/rally/register, id=last4ssn
        This also dictates the partner/client to use in the
         `create_user_using_eligibility_record_via_ui` kw.

                Arguments:
                - ``partner:``                  Partner to create and upsert
                                                elig record for
                - ``data_fixture:``             By default a random data obj is
                                                generated as the data_fixture
                                                if none is passed.
                                                Generate random data by using
                                                RandomDataGenerator.py lib.
                - ``return:``                   Json object which will be used
                                                to upsert the eligibility
                                                 record
        """
        if data_fixture is None:
            data_fixture = RandomDataGenerator.get_random_data()

        json_outside_fields = self._create_common_pre_field_json(
            partner,
            data_fixture
        )
        json_common_in_fields = self._create_common_field_json(
            kind="rally_direct"
        )
        random_partner_uuid = String().generate_random_string(
            12,
            '[NUMBERS]'
        )

        inner_fields = {
            "last4SSN": data_fixture.ssn_last_4_digits,
            "partner": str(partner),
            "inUserData": {
                "partnerUUID": random_partner_uuid,
                "firstName": data_fixture.first_name,
                "lastName": data_fixture.last_name,
                "dob": data_fixture.dob_format_iso8601
            }
        }
        inner_fields.update(json_common_in_fields)
        fields = {"fields": inner_fields}
        body = dict()
        body.update(fields)
        body.update(json_outside_fields)
        return body

    def create_optum_eligibility_payload(self, data_fixture=None):
        """Creates an optum payload for upserting eligibility record to SH.

            For registration in the UI use these partner/client combos and url:
                      /partner/optum/optum_default/register/
            This also dictates the partner/client to use in the
            `create_user_using_eligibility_record_via_ui` kw.

                    Arguments:
                    - ``data_fixture:``             By default a random data
                                                    obj is generated as the
                                                    data_fixture if none is
                                                    passed.
                                                    Generate random data by
                                                    using
                                                    RandomDataGenerator.py lib.
                    - ``return:``                   Json object which will be
                                                    used to upsert the
                                                    eligibility record
        """
        if data_fixture is None:
            data_fixture = RandomDataGenerator.get_random_data()

        body = json.loads("""
{
   "partner":"optum",
   "partnerUserId":{
      "idType":"multi",
      "idMap":{
         "personId":"0000000005",
         "search_id":"1000000005"
      },
      "uidKey":"personId"
   },
   "friendlyClientId":"182_Friendly",
   "segmentationName":null,
   "startDate":"2017-09-11T20:02:54.991Z",
   "fields":{
      "requiredEligibilityFields":{
         "firstName":"bob",
         "lastName":"blob",
         "dob":-230515200000,
         "searchId":"1000000005",
         "clientDefaultPolicyNumber":"182"
      },
      "idSet":{
         "idMap":{
            "personId":"0000000005",
            "search_id":"1000000005"
         }
      },
      "personId":"0000000005",
      "searchIdType":"MemNumMayBe",
      "clientName":"Target Inc.",
      "segmentation":null,
      "groupNumber":"2000000001",
      "gender":"Male",
      "zipcode":null,
      "memberAddress":{

      },
      "workLocationName":null,
      "employeeStatus":null,
      "policyNumber":"3000000001",
      "email":null,
      "phone":null,
      "relationshipId":null,
      "startDate":"2017-09-11T20:02:54.991Z",
      "endDate":null,
      "hireDate":null,
      "memberSSN":null,
      "subscriberSSN":null,
      "eligibilityFlags":null,
      "purchaserCode":null,
      "employerAssignedId":null,
      "unionStatus":null,
      "divisionName":null,
      "healthPlanProductCode":null,
      "ssoConfigMap":null,
      "kind":"optum"
   }
}
        """)
        body["fields"]["requiredEligibilityFields"]["dob"] = data_fixture.dob_in_ms
        body["fields"]["requiredEligibilityFields"]["firstName"] = data_fixture.first_name
        body["fields"]["requiredEligibilityFields"]["lastName"] = data_fixture.last_name
        body["fields"]["gender"] = data_fixture.gender

        body["partnerUserId"]["idMap"]["personId"] = data_fixture.partner_user_id
        body["fields"]["personId"] = data_fixture.partner_user_id
        body["fields"]["idSet"]["idMap"]["personId"] = data_fixture.partner_user_id

        body["partnerUserId"]["idMap"]["search_id"] = data_fixture.member_id
        body["fields"]["idSet"]["idMap"]["search_id"] = data_fixture.member_id
        body["fields"]["requiredEligibilityFields"]["searchId"] = data_fixture.member_id

        return body

    def create_bcbs_eligibility_payload(self, partner, data_fixture=None):
        """Creates a bcbs payload for upserting eligibility record to SH.

            For registration in the UI use these partner/client combos and url:
                      /partner/bcbs_south_carolina/register
            This also dictates the partner/client to use in the
            `create_user_using_eligibility_record_via_ui` kw.

                    Arguments:
                    - ``partner:``                  Partner to create and
                                                    upsert eligibility record
                                                    for
                    - ``data_fixture:``             By default, it's a random
                                                    data obj used for payload
                                                    and actual registration
                                                    via UI.  Optional to pass a
                                                    data fixture.
                    - ``return:``                   Json object which will be
                                                    used to upsert the
                                                    eligibility record.
        """
        if data_fixture is None:
            data_fixture = RandomDataGenerator.get_random_data()

        json_outside_fields = \
            self._create_partner_partneruserid_startdate_pre_field(
                partner,
                data_fixture.partner_user_id,
                data_fixture.start_date_format_iso8601
            )
        random_coverage_begin_date = RallyCommonRobotModules.utils.CoreUtils \
            .convert_date_to_miliseconds(
            data_fixture.start_date_format_iso8601
        )
        random_coverage_term_date = RallyCommonRobotModules.utils.CoreUtils \
            .convert_date_to_miliseconds(
            data_fixture.end_date_format_iso8601
        )
        dob_in_ms = RallyCommonRobotModules.utils.CoreUtils \
            .convert_date_to_miliseconds(data_fixture.dob_format_iso8601)

        body = {
            "endDate": data_fixture.end_date_format_iso8601,
            "fields": {
                "requiredEligibilityFields": {
                    "idCardNumber": data_fixture.member_id,
                    "firstName": data_fixture.first_name,
                    "lastName": data_fixture.last_name,
                    "dob": dob_in_ms
                },
                "partnerUserData": {
                    "parentClient": self._get_random_string(),
                    "uniqueId": self._get_random_string(),
                    "misc": {
                        "middleName": data_fixture.middle_initial,
                        "address1": data_fixture.street_address,
                        "language": self._get_random_string()
                    },
                    "employeeType": "PartTime",
                    "cesClientName": self._get_random_string(),
                    "coverageBeginDate": random_coverage_begin_date,
                    "coverageTermDate": random_coverage_term_date,
                    "cobIndicator": self._get_random_string(),
                    "lob": self._get_random_string(),
                    "businessName": self._get_random_string()
                },
                "kind": str(partner)
            }
        }
        body.update(json_outside_fields)
        return body

    def create_health_alliance_eligibility_payload(
            self,
            partner,
            data_fixture=None
    ):
        """Creates a health_alliance payload for upserting eligibility
         record to SH.

            For registration in the UI use these partner/client combos and url:
                      /partner/health_alliance/register
            This also dictates the partner/client to use in the
             `create_user_using_eligibility_record_via_ui` kw.

                    Arguments:
                    - ``partner:``                  Partner to create and
                                                    upsert eligibility record
                                                    for
                    - ``data_fixture:``             By default a random data
                                                    obj is generated as the
                                                    data_fixture if none is
                                                    passed.
                    - ``return:``                   Json object which will be
                                                    used to upsert the
                                                    eligibility record.
        """
        if data_fixture is None:
            data_fixture = RandomDataGenerator.get_random_data()

        json_outside_fields = \
            self._create_partner_partneruserid_startdate_pre_field(
                str(partner),
                data_fixture.partner_user_id,
                data_fixture.start_date_format_iso8601
            )
        body = {
            "fields": {
                "memberId": data_fixture.member_id,
                "lastName": data_fixture.last_name,
                "dob": data_fixture.dob_format_iso8601,
                "firstName": data_fixture.first_name,
                "middleInitial": data_fixture.middle_initial,
                "payer": self._get_random_string(),
                "planType": self._get_random_string(),
                "planCode": self._get_random_string(),
                "group": self._get_random_string(),
                "groupName": self._get_random_string(),
                "gender": data_fixture.gender,
                "ssn": data_fixture.ssn_no_dashes,
                "state": data_fixture.state,
                "city": data_fixture.city,
                "address1": data_fixture.street_address,
                "address2": "",
                "subscriberNum": self._get_random_string(),
                "employeeOrDependant": "Unknown",
                "kind": str(partner)
            }
        }
        body.update(json_outside_fields)
        return body

    def _get_random_string(self):
        """
        :return: 10 char string consisting of letters
        """
        return String().generate_random_string(10, "[LETTERS]")

    def _create_partner_partneruserid_startdate_pre_field(
            self,
            partner,
            partner_user_id,
            start_date
    ):
        """Json elements outside of the fields sub json.  Sub json consists of
         parnter, partner user id, and start date

        :param partner: Partner building json payload for
        :param partner_user_id: value set for partner_user_id
        :param start_date: value set for start_date
        :return: json consisting of partner, partner user id, and start date
        """
        body = {
            'partner': partner,
            'partnerUserId': partner_user_id,
            'startDate': start_date
        }
        return body

    def _create_common_pre_field_json(self, partner, data_fixture=None):
        """These are the json element that is common for all partners outside
         of the fields json element

        :param partner: partner used to build payload for
        :param data_fixture: By default a random data obj is generated as the
         data_fixture if none is passed.
        :return: json which is common to all partners outside of the fields
         json element
        """
        if data_fixture is None:
            data_fixture = RandomDataGenerator.get_random_data()

        pre_field_json = \
            self._create_partner_partneruserid_startdate_pre_field(
                partner,
                data_fixture.partner_user_id,
                data_fixture.start_date_format_iso8601
            )
        body = {
            'parentClientId': data_fixture.parent_client_id,
            'segmentationName': data_fixture.segmentation_name
        }
        body.update(pre_field_json)
        return body

    def _create_common_field_json(self, kind='base'):
        """These are common json elements inside the fields sub json.

        :param kind: value set for kind field
        :return: returns json element which all partners have in common inside
         the fields json element
        """
        body = {
            "groupData": {
                "subgroups": [
                ]
            },
            "healthData": {
                "conditionGroups": [
                ]
            },
            "kind": kind
        }
        return body
