"""
Transformer from primary data to licence schema

Data from http://www.secc.gov.kh/english/m52.php?pn=6
Mission: https://missions.opencorporates.com/missions/648
"""
import sys
import json

while True:
    line = sys.stdin.readline()
    if not line:
        break
    raw_record = json.loads(line)

    address = raw_record['address']
    in_cambodia = ('Cambodia' in address or 'Phnom Penh' in address)

    # Can't have an empty country jurisdiction due to schema restrictions
    # so have to leave out the whole row.
    licence_record = {
        'source_url': raw_record['source_url'],
        'sample_date': raw_record['sample_date'],
        'category': ["Financial"],
        'licence_holder': {
            'entity_type': 'company',
            'entity_properties': {
                'name': raw_record['name'],
                'mailing_address': raw_record['address'],
                'jurisdiction': "kh" if in_cambodia else '',
            }
        },
        "permissions": [{
            "activity_name": raw_record["type"],
            "permission_type": "operating",
        }],
        "licence_issuer": {
            "name": "Securities and Exchange Commission of Cambodia",
            "jurisdiction": "Cambodia",
        },
        "jurisdiction_of_licence": "kh",
    }

    # Contact records. These:
    # (a) are not necessarily present in the raw record
    # (b) are stored as lists when they are present.
    # If present, first entry from each list should be taken
    entity = licence_record['licence_holder']['entity_properties']
    if 'website' in raw_record:
        entity['website'] = raw_record['website'][0]

    if 'tel' in raw_record:
        entity['telephone_number'] = raw_record['tel'][0]

    if 'fax' in raw_record:
        entity['fax_number'] = raw_record['fax'][0]

    print json.dumps(licence_record)
