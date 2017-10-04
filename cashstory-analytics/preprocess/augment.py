# coding: utf-8
from __future__ import unicode_literals

import pandas as pd

from app.etl.cache import cache

@cache()
def compute_domain_c(domain_a, domain_b):
    # [do some heavy and slow computation]
    domain_c = domain_a + domain_b
    return domain_c


def augment(dfs):
    """
    Insert here code to augment your data frames during preprocessing
    """
    #identifier toucan dans username
    #identifier renault dans username
    users = dfs['users'].copy()
    analytics = dfs['analytics'].copy()
    hierarchy = dfs['hierarchy'].copy()

    users['type'] = 'agent'
    users.ix[users.username.str.contains('toucan'),'type'] = 'toucan'
    users.ix[users.username.str.contains('renault'),'type'] = 'renault_corporate'

    #keys : user_uid, DEALER_NUMBER
    #sometimes dealer name is nan but when type is agent, we sha
    users.ix[(users.DEALER_NAME.isnull())&(users.type=='agent'),'DEALER_NAME'] = users.ix[(users.DEALER_NAME.isnull())&(users.type=='agent'), 'DEALER_CITY']

    #same for hierarchy
    hierarchy.ix[hierarchy.RAISON_SOC.isnull(),'RAISON_SOC'] = hierarchy.ix[hierarchy.RAISON_SOC.isnull(), 'NOM_COM']

    hierarchy_clean =hierarchy.drop_duplicates(subset=['RAISON_SOC'])
    hierarchy_clean.RAISON_SOC.fillna('99999999', inplace=True)
    df = pd.merge(users, analytics,left_on='user_uid',right_on='User ID').drop_duplicates(subset=['User ID'])
    df_1 = pd.merge(df, hierarchy_clean.drop_duplicates(subset=['RAISON_SOC']), left_on='DEALER_NAME', right_on='RAISON_SOC', how='left')
    
    TO_KEEP = [
        u'DEALER_CITY', u'USER_GIVENNAME', u'USER_NAME',u'DEALER_NAME',u'NOM_COM','type',
        u'DR', u'Reseau',u'NOM_USUEL',u'RRF',
        u'NOM_MAV',u'PRENOM_MAV',u'PRENOM_TMR',u'NOM_TMR',
        u'Durée moyenne des sessions',u'Sessions',u'RAISON_SOC',
        u'Pere_Lib_Nat', u'DT_SORTIE',u'DR_LIB','User ID','username'
    ]

    df_1['label_name'] = df_1['USER_GIVENNAME'] + '-' + df_1['USER_NAME'] 
    df_1.ix[df_1.type=='renault_corporate','label_name'] = df_1.ix[df_1.type=='renault_corporate','username'] 

    df_1['DR_LIB'].fillna('N/A', inplace=True)

    dfs['user-id-analytics'] = df_1[df_1.type != 'toucan']
    # Add domain to each dataframe
    for domain, df in dfs.iteritems():
        df['domain'] = domain

    # Example calcuation that will only be done if the data or function code has changed
    # dfs['domain_c'] = compute_domain_c(dfs['domain_a'], dfs['domain_b'])


    return dfs
