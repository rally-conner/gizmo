""" Invite Codes"""
import logging
import requests

from robot.libraries.BuiltIn import BuiltIn
from robot.utils import is_truthy


def _get_req_rf_var(name):
    value = BuiltIn().get_variable_value(name)
    if value is None:
        raise RuntimeError("robot variable {} not defined".format(name))
    return value


def create_invite_code_for_uk_devon(multi_use_code=False):
    """Request a UK Devon invite code from Sorting Hat service

    Arguments:
    - ``multi_use_code:``        reusable code, default=False
    - ``return:``                Invite code generated from Sorting Hat service
    """
    multi_use_code = is_truthy(multi_use_code)
    rf_string_library = BuiltIn().get_library_instance("String")
    random_word = rf_string_library.generate_random_string(28)
    payload = {
        "partner": "uk_government",
        "client": "devon",
        "affiliation": "uk_government_devon_aff_20170215_192747_IGAG",
        "roleNames": ["UKGovernmentBase", "ViewSurvey"],
        "registrationType": {"value": "registration-uk-government"},
        "isMultiUse": multi_use_code,
        "code": random_word
    }

    sh_url = _get_req_rf_var("${RALLY_SORTINGHAT_URL}")
    session_headers = {"Content-Type": "application/json"}
    response = requests.post(sh_url + '/rest/invitecode/v1/invites',
                             json=payload, headers=session_headers)
    assert response.status_code == 201, "Expected POST to sortinghat invite " \
                                        "URL to yield 201 but got {}". \
        format(response.status_code)
    logging.info(response.json())
    return response.json()['code']
