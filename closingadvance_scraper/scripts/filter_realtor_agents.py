import csv
import os

realtor_agents_file = csv.DictReader(open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/realtor_agents.csv"),
                                     delimiter=";")
realtor_brokers_file = csv.DictReader(
    open(os.path.dirname(os.path.realpath(__file__)) + "/../external_data/realtor_brokers.csv"),
    delimiter=";")
filtered_realtor_agents = []
# "officeName";"officePhone";

realtor_agents_list = list(realtor_agents_file)
realtor_brokers_list = list(realtor_brokers_file)

with open('filtered agent list.csv', 'w') as filtered_agents_file:  # Just use 'w' mode in 3.x
    writer = csv.DictWriter(filtered_agents_file, list(realtor_agents_list[0].keys()) + ['brokers_list'], delimiter=';')
    writer.writeheader()

    for realtor_agent in realtor_agents_list:
        qualified_realtor_agent = None

        if realtor_agent['officeName'].strip() or realtor_agent['officePhone'].strip():
            for realtor_broker in realtor_brokers_list:
                if (realtor_agent['officeName'].strip() and realtor_agent['officeName'] == realtor_broker['officeName'] and
                    realtor_agent['officeName'] == realtor_broker['officeName'] and
                    realtor_agent['officeAddress'] == realtor_broker['officeAddress']) or \
                        (realtor_agent['officePhone'].strip() and realtor_agent['officePhone'] == realtor_broker['officePhone']):
                    if not qualified_realtor_agent:
                        qualified_realtor_agent = dict(realtor_agent)

                    if not qualified_realtor_agent.get('brokers_list', None):
                        qualified_realtor_agent['brokers_list'] = []

                    qualified_realtor_agent['brokers_list'].append(realtor_broker['id'])

        if qualified_realtor_agent:
            qualified_realtor_agent['brokers_list'] = ' ' . join(qualified_realtor_agent['brokers_list'])
            writer.writerow(qualified_realtor_agent)
            # filtered_realtor_agents.append(qualified_realtor_agent)
