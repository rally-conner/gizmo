import logging

from RallyCommonRobotModules.Clients.SortingHat.AffiliationClient import AffiliationClient


DEFAULT_CLIENTS = {
    'all_savers': 'all_savers_default',
    'baf': 'baf_default',
    'bcbs_south_carolina': 'bcbs_south_carolina_default',
    'demo': 'demo_base',
    'excellus': 'excellus_base',
    'great_west_life': 'great_west_life_default',
    'health_alliance': 'health_alliance',
    'mercer': 'mercer_base',
    'military_wellness': 'military_wellness_default',
    'optum': 'optum_default',
    'rally': 'rally_health',
    'rally_direct': 'rally_direct_default',
    'rally_marketplace': 'rally_marketplace_default',
    'uk_government': 'uk_government_base',
    'univera': 'univera_base',
}


def get_default_client(partner):
    client = DEFAULT_CLIENTS.get(partner, None)
    if not client:
        logging.warn("Default client for %s not known, contacting sorting hat" % partner)
        partner_data = AffiliationClient().find_partner(partner)
        client = partner_data["defaultClient"]
    return client
