import json
import sqlite3
import ast
import time

base_path = '../../../go/dev/alice/'

def create_connection():
    try:
        return sqlite3.connect(base_path+'sqlite/db')

    except sqlite3.Error as e:
        print(e)
        return None

def get_ip_from_node(node):
    if not node['addresses'] or len(node['addresses']) == 0:
        return None

    for address in node['addresses']:
        if address['network'] == 'tcp' and address['addr'].count('.') == 3 and address['addr'].count(':') == 1 and len(address['addr']) < 22:
            return address['addr'].split(':')[0]

    return None

if __name__ == '__main__':
    connection = create_connection()

    cursor = connection.cursor()

    cursor.execute('select raw_data from channels')

    raw_channel_data = [ast.literal_eval(element[0]) for element in cursor.fetchall()]

    channel_export = []

    for channel in raw_channel_data:
        channel_export.append({'chan_point': channel['chan_point'], 'node1_pub': channel['node1_pub'], 'node2_pub': channel['node2_pub']})

    cursor.execute('select raw_data from nodes')

    raw_node_data = [ast.literal_eval(element[0]) for element in cursor.fetchall()]

    node_alias_export = []
    node_ip_export = []

    for node in raw_node_data:
        node_alias_export.append({'pub_key': node['pub_key'], 'alias': node['alias']})
        node_ip_export.append({'pub_key': node['pub_key'], 'IP_address': get_ip_from_node(node)})

    timestamp = str(int(time.time()))

    out_file = open(base_path + 'lightning_study/edge_state_'+timestamp+'.json', 'w')
    json.dump(channel_export, out_file)

    out_file = open(base_path + 'lightning_study/node_state_'+timestamp+'.json', 'w')
    json.dump(node_alias_export, out_file)

    out_file = open(base_path + 'lightning_study/address_state_'+timestamp+'.json', 'w')
    json.dump(node_ip_export, out_file)