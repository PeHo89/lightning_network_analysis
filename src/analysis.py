import sqlite3
import json
import time
import math
import os
import fnmatch
import ast
import requests
import hashlib
import base58

from os import listdir
from os.path import isfile, join

base_path = '../../../go/dev/alice/'

def create_connection():
    try:
        # connection = sqlite3.connect(base_path+'sqlite/db')
        connection = sqlite3.connect(base_path+'sqlite/final')
        return connection

    except sqlite3.Error as e:
        print(e)
        return None

def get_number_closed_channels_onchain(cursor):
    cursor.execute('select count(*) from potential_txes p inner join channels c on p.tx = c.funding_tx')
    return cursor.fetchall()[0][0]

def get_funding_txes_of_closed_channels_onchain(cursor):
    cursor.execute('select p.tx from potential_txes p inner join channels c on p.tx = c.funding_tx')
    return [element[0] for element in cursor.fetchall()]

def get_closed_channels_onchain(cursor):
    cursor.execute('select * from potential_txes p inner join channels c on p.tx = c.funding_tx')
    return [create_json_for_joined_table_entry(element) for element in cursor.fetchall()]

def get_number_potential_txes_onchain(cursor):
    cursor.execute('select count(distinct tx) from potential_txes')
    return cursor.fetchall()[0][0]

def get_number_total_unique_channels(cursor):
    cursor.execute('select count(*) from channels')
    return cursor.fetchall()[0][0]

def get_number_open_channels_offchain(cursor):
    cursor.execute('select count(*) from channel_snapshots where timestamp = ? or timestamp = ?', (get_latest_snapshot_hour()+1,get_latest_snapshot_hour()+2))
    return cursor.fetchall()[0][0]

def get_closed_channels_offchain(cursor):
    cursor.execute('select raw_data from channels')
    unique_funding_txes = [get_json_for_raw_db_data(element[0]) for element in cursor.fetchall()]

    #cursor.execute('select channel from channel_snapshots where timestamp = ? or timestamp = ?', (get_latest_snapshot_hour()+1,get_latest_snapshot_hour()+2))
    cursor.execute('select channel from channel_snapshots where timestamp = ?', (1580367601,))
    open_funding_txes = [element[0] for element in cursor.fetchall()]

    result = []

    for tx in unique_funding_txes:
        if tx['chan_point'].split(':')[0] not in open_funding_txes:
            result.append(tx)

    return result

def load_outputs_and_export_txes(cursor, funding_txes_of_closed_channels_offchain_but_not_onchain):
    funding_txes_with_outputs_of_closed_channels_offchain_but_not_onchain = []

    for funding_tx in funding_txes_of_closed_channels_offchain_but_not_onchain:
        cursor.execute('select output_idx from channels where funding_tx = ?', (funding_tx,))
        funding_txes_with_outputs_of_closed_channels_offchain_but_not_onchain.append({'funding_tx': funding_tx, 'output_idx': cursor.fetchall()[0][0]})

    out_file = open(base_path + 'analysis/' + 'funding_txes_with_outputs_of_closed_channels_offchain_but_not_onchain', 'w')
    json.dump(funding_txes_with_outputs_of_closed_channels_offchain_but_not_onchain, out_file)

def calculate_channels_with_lack_of_snapshots_during_known_lifetime(cursor):
    cursor.execute('select channel,idx,count(timestamp) from channel_snapshots group by channel having count(timestamp) < ?', (get_snaphot_amount(),))

    result = cursor.fetchall()

    channels_with_lack_of_snapshots = []

    for res in result:
        cursor.execute('select timestamp from channel_snapshots where channel = ? and idx = ?', (res[0], res[1]))

        timestamps = [element[0] for element in cursor.fetchall()]

        timestamps.sort()

        lack_of_snapshots = []

        for i in range(1, len(timestamps)):
            #3600 seconds +/-1 second because there are snapshots taken at second 2 of a hour, insted of second 1 of a hour
            if (timestamps[i-1]+3600 != timestamps[i]) and (timestamps[i-1]+3599 != timestamps[i]) and (timestamps[i-1]+3601 != timestamps[i]):
                lack_of_snapshots.append(timestamps[i]-timestamps[i-1])

        if len(lack_of_snapshots) > 0:
            channels_with_lack_of_snapshots.append({'funding_tx': res[0], 'output_idx': res[1], 'lack_of_snapshots': lack_of_snapshots})

    return channels_with_lack_of_snapshots

def get_total_unique_bitcoin_keys(cursor):
    cursor.execute('select raw_data from channels')

    raw_channel_data = [get_json_for_raw_db_data(element[0]) for element in cursor.fetchall()]

    bitcoin_keys = {}

    for channel in raw_channel_data:
        try:
            bitcoin_keys[channel['btc1_pub']]['count'] += 1
            bitcoin_keys[channel['btc1_pub']]['channels'].append(channel)

        except KeyError as e:
            bitcoin_keys[channel['btc1_pub']] = {"count": 1, "channels": [channel]}

        try:
            bitcoin_keys[channel['btc2_pub']]['count'] += 1
            bitcoin_keys[channel['btc2_pub']]['channels'].append(channel)

        except KeyError as e:
            bitcoin_keys[channel['btc2_pub']] = {"count": 1, "channels": [channel]}

    return bitcoin_keys

def get_latest_snapshot_hour():
    current_timestamp = int(time.time())
    remainer = current_timestamp % 3600

    return current_timestamp-remainer

def get_snaphot_amount():
    graph_file_names = [f for f in listdir(base_path + 'graph_backup/') if isfile(join(base_path + 'graph_backup/', f))]
    graph_file_names.remove('.info')
    return len(graph_file_names)

def get_json_for_raw_db_data(data):
    return json.loads(data.replace('u', '').replace('\'', '"').replace('None', '{}').replace('False', '"False"').replace('Tre', '"True"').replace('pb', 'pub').replace('pdate', 'update'))

def get_reused_bitcoin_keys(total_unique_bitcoin_keys):
    reused_bitcoin_keys = {}

    for key in total_unique_bitcoin_keys:
        if total_unique_bitcoin_keys[key]['count'] > 1:
            reused_bitcoin_keys[key] = total_unique_bitcoin_keys[key]

    return reused_bitcoin_keys

def get_missing_timestamps_in_db(cursor):
    cursor.execute('select distinct timestamp from channel_snapshots')

    distinct_timestamps = [int(element[0]) for element in cursor.fetchall()]

    all_graph_snapshot_timestamps = get_all_timestamps_from_graph_backup_files()

    missing_timestamps_in_db = []

    for timestamp in all_graph_snapshot_timestamps:
        if (not timestamp in distinct_timestamps) and (not timestamp+1 in distinct_timestamps) and (not timestamp-1 in distinct_timestamps):
            missing_timestamps_in_db.append(timestamp)

    return missing_timestamps_in_db

def get_all_timestamps_from_graph_backup_files():
    graph_file_names = [f for f in listdir(base_path + 'graph_backup/') if isfile(join(base_path + 'graph_backup/', f))]
    graph_file_names.remove('.info')

    timestamps = [int(f.split('_')[1]) for f in graph_file_names]

    return timestamps

def get_potential_txes_closing_tx_block_height_greater_block_height(target_block_height):
    cursor.execute('select raw_data from potential_txes')

    raw_channel_data = [json.loads(element[0].replace('\'', "\"")) for element in cursor.fetchall()]

    result = []

    for data in raw_channel_data:
        if int(data['block_height_closing_tx']) >= target_block_height:
            result.append(data)

    return result

def get_all_potential_ln_channel_txes():
    cursor.execute('select raw_data from potential_txes')

    return [json.loads(element[0].replace('\'', "\"")) for element in cursor.fetchall()]

def export_ln_channels_to_file():
    cursor.execute('select raw_data from channels')

    raw_channel_data = [ast.literal_eval(element[0]) for element in cursor.fetchall()]

    out_file = open(base_path + 'channels/all_channel_export_'+str(int(time.time())), 'w')
    json.dump(raw_channel_data, out_file)

def export_ln_nodes_to_file():
    cursor.execute('select raw_data from nodes')

    raw_node_data = [ast.literal_eval(element[0]) for element in cursor.fetchall()]

    out_file = open(base_path + 'channels/all_node_export_'+str(int(time.time())), 'w')
    json.dump(raw_node_data, out_file)

def export_closed_ln_channels_to_file(closed_channels_offchain):
    out_file = open(base_path + 'channels/closed_channel_export_'+str(int(time.time())), 'w')
    json.dump(closed_channels_offchain, out_file)

def create_file_with_all_interacting_input_output_addresses_of_all_channels():
    channels_with_onchain_data = json.load(open(base_path+'channels/all_channel_export_1580628321_onchain_data_1580628499'))

    addresses = []

    for channel_with_onchain_data in channels_with_onchain_data:
        try:
            addresses = addresses + channel_with_onchain_data['funding_tx_input_addresses']
        except KeyError as e:
            pass

        try:
            addresses = addresses + channel_with_onchain_data['closing_tx_output_addresses']
        except KeyError as e:
            pass

    out_file = open(base_path + 'channels/input_output_addresses_all_channels_'+str(int(time.time())), 'w')
    json.dump(addresses, out_file)

def load_tags_to_addresses():
    addresses = json.load(open(base_path+'channels/input_output_addresses_all_channels_1580648783'))

    body = {'username': 'graphsense_demo', 'password': 'preview'}

    response = requests.post(url = 'http://192.168.243.2:9000/login', json=body)
    jwt = response.json()['Authorization']

    header = {'Content-Type': 'application/json', 'Authorization': jwt}

    addresses_with_tags = {}

    for address in addresses:
        response = requests.get(url = 'http://192.168.243.2:9000/btc/addresses/[ADDR]'.replace('[ADDR]', address), headers=header)

        if not response.status_code == 404 and not response.status_code == 500:
            data = response.json()

            if len(data['tags']) > 0:
                addresses_with_tags[address] = data['tags']

    out_file = open(base_path + 'channels/input_output_addresses_all_channels_1580648783_with_tags', 'w')
    json.dump(addresses_with_tags, out_file)

def load_entities_to_addresses():
    channels = json.load(open(base_path+'channels/all_channel_export_1580628321_onchain_data_1580628499'))

    body = {'username': 'graphsense_demo', 'password': 'preview'}

    response = requests.post(url = 'http://192.168.243.2:9000/login', json=body)
    jwt = response.json()['Authorization']

    header = {'Content-Type': 'application/json', 'Authorization': jwt}

    for channel in channels:
        try:
            channel['input_entities'] = []

            for address in channel['funding_tx_input_addresses']:

                response = requests.get(url = 'http://192.168.243.2:9000/btc/addresses/[ADDR]/entity'.replace('[ADDR]', address), headers=header)

                if not response.status_code == 404 and not response.status_code == 500:
                    data = response.json()

                    if data['entity'] > 0 and not data['entity'] in channel['input_entities']:
                        channel['input_entities'].append(data['entity'])
        except KeyError as e:
            pass

        try:
            channel['output_entities'] = []

            for address in channel['closing_tx_output_addresses']:

                response = requests.get(url = 'http://192.168.243.2:9000/btc/addresses/[ADDR]/entity'.replace('[ADDR]', address), headers=header)

                if not response.status_code == 404 and not response.status_code == 500:
                    data = response.json()

                    if data['entity'] > 0 and not data['entity'] in channel['output_entities']:
                        channel['output_entities'].append(data['entity'])
        except KeyError as e:
            pass

    out_file = open(base_path + 'channels/all_channel_export_1580628321_onchain_data_1580628499_with_entities', 'w')
    json.dump(channels, out_file)

def count_input_output_addresses_and_entities():
    channels = json.load(open(base_path+'channels/all_channel_export_1580628321_onchain_data_1580628499_with_entities'))

    input_address_count = 0
    output_address_count = 0
    input_entity_count = 0
    output_entity_count = 0
    empty_input_count = 0
    empty_output_count = 0

    for channel in channels:
        try:
            input_address_count += len(channel['funding_tx_input_addresses'])
        except KeyError as e:
            pass

        try:
            output_address_count += len(channel['closing_tx_output_addresses'])
        except KeyError as e:
            pass

        try:
            input_entity_count += len(channel['input_entities'])

            if len(channel['input_entities']) > 1:
                print(channel['input_entities'])

            if len(channel['input_entities']) == 0:
                empty_input_count += 1

        except KeyError as e:
            pass

        try:
            output_entity_count += len(channel['output_entities'])

            if len(channel['output_entities']) > 1:
                print(channel['output_entities'])

            if len(channel['output_entities']) == 0:
                empty_output_count += 1

        except KeyError as e:
            pass

    print('Input address count: ' + str(input_address_count))
    print('Output address count: ' + str(output_address_count))
    print('Input entity count: ' + str(input_entity_count))
    print('Output entity count: ' + str(output_entity_count))
    print('Empty input entity count: ' + str(empty_input_count))
    print('Empty output entity count: ' + str(empty_output_count))

def export_entity_node_mapping():
    entity_channel_mapping = json.load(open(base_path+'channels/entity_mapped_all_channel_export_1580628321_onchain_data_1580628499_with_entities'))

    input_entity_node_mapping = {}
    output_entity_node_mapping = {}
    input_output_entity_node_mapping = {}

    for entity in entity_channel_mapping['input_entity'].keys():
        node_count = {}

        for channel in entity_channel_mapping['input_entity'][entity]:
            try:
                node_count[channel['node1_pub']] += 1
            except KeyError as e:
                node_count[channel['node1_pub']] = 1

            try:
                node_count[channel['node2_pub']] += 1
            except KeyError as e:
                node_count[channel['node2_pub']] = 1

        node_count = {k: node_count[k] for k in sorted(node_count, key=node_count.get, reverse=True)}

        if node_count[list(node_count.keys())[0]] > node_count[list(node_count.keys())[1]]:
            input_entity_node_mapping[entity] = [{'node': list(node_count.keys())[0], 'count': str(node_count[list(node_count.keys())[0]]), 'channels': str(len(entity_channel_mapping['input_entity'][entity]))}]

        elif node_count[list(node_count.keys())[0]] == node_count[list(node_count.keys())[1]]:
            input_entity_node_mapping[entity] = []

            for node in node_count.keys():
                if node_count[node] >= node_count[list(node_count.keys())[0]]:
                    input_entity_node_mapping[entity].append({'node': node, 'count': str(node_count[node]), 'channels': str(len(entity_channel_mapping['input_entity'][entity]))})

    for entity in entity_channel_mapping['output_entity'].keys():
        node_count = {}

        for channel in entity_channel_mapping['output_entity'][entity]:
            try:
                node_count[channel['node1_pub']] += 1
            except KeyError as e:
                node_count[channel['node1_pub']] = 1

            try:
                node_count[channel['node2_pub']] += 1
            except KeyError as e:
                node_count[channel['node2_pub']] = 1

        node_count = {k: node_count[k] for k in sorted(node_count, key=node_count.get, reverse=True)}

        if node_count[list(node_count.keys())[0]] > node_count[list(node_count.keys())[1]]:
            output_entity_node_mapping[entity] = [{'node': list(node_count.keys())[0], 'count': str(node_count[list(node_count.keys())[0]]), 'channels': str(len(entity_channel_mapping['output_entity'][entity]))}]

        elif node_count[list(node_count.keys())[0]] == node_count[list(node_count.keys())[1]]:
            output_entity_node_mapping[entity] = []

            for node in node_count.keys():
                if node_count[node] >= node_count[list(node_count.keys())[0]]:
                    output_entity_node_mapping[entity].append({'node': node, 'count': str(node_count[node]), 'channels': str(len(entity_channel_mapping['output_entity'][entity]))})

    for entity in entity_channel_mapping['input_output_entity'].keys():
        node_count = {}

        for channel in entity_channel_mapping['input_output_entity'][entity]:
            try:
                node_count[channel['node1_pub']] += 1
            except KeyError as e:
                node_count[channel['node1_pub']] = 1

            try:
                node_count[channel['node2_pub']] += 1
            except KeyError as e:
                node_count[channel['node2_pub']] = 1

        node_count = {k: node_count[k] for k in sorted(node_count, key=node_count.get, reverse=True)}

        if node_count[list(node_count.keys())[0]] > node_count[list(node_count.keys())[1]]:
            input_output_entity_node_mapping[entity] = [{'node': list(node_count.keys())[0], 'count': str(node_count[list(node_count.keys())[0]]), 'channels': str(len(entity_channel_mapping['input_output_entity'][entity]))}]

        elif node_count[list(node_count.keys())[0]] == node_count[list(node_count.keys())[1]]:
            input_output_entity_node_mapping[entity] = []

            for node in node_count.keys():
                if node_count[node] >= node_count[list(node_count.keys())[0]]:
                    input_output_entity_node_mapping[entity].append({'node': node, 'count': str(node_count[node]), 'channels': str(len(entity_channel_mapping['input_output_entity'][entity]))})

    input_output_entities = {'input_entity': input_entity_node_mapping, 'output_entity' : output_entity_node_mapping, 'input_output_entity': input_output_entity_node_mapping}

    out_file = open(base_path + 'channels/entity_mapped_nodes_export_1580628321_onchain_data_1580628499_with_entities', 'w')
    json.dump(input_output_entities, out_file)

    entity_node_mapping = []

    for entity in input_output_entity_node_mapping.keys():
        entity_node_mapping.append({'entity': entity, 'node': input_output_entity_node_mapping[entity]})

    out_file = open(base_path + 'channels/entity_node_mapping', 'w')
    json.dump(entity_node_mapping, out_file)

def export_entity_channel_mapping():
    channels = json.load(open(base_path+'channels/all_channel_export_1580628321_onchain_data_1580628499_with_entities'))

    input_entities = {}
    output_entities = {}
    input_output_entities = {}

    for channel in channels:

        for entity in channel['input_entities']:
            try:
                input_entities[entity].append(channel)
            except KeyError as e:
                input_entities[entity] = [channel]

            try:
                input_output_entities[entity].append(channel)
            except KeyError as e:
                input_output_entities[entity] = [channel]


        for entity in channel['output_entities']:
            try:
                output_entities[entity].append(channel)
            except KeyError as e:
                output_entities[entity] = [channel]

            try:
                input_output_entities[entity].append(channel)
            except KeyError as e:
                input_output_entities[entity] = [channel]

    input_output_entities = {'input_entity': input_entities, 'output_entity' : output_entities, 'input_output_entity': input_output_entities}

    out_file = open(base_path + 'channels/entity_mapped_all_channel_export_1580628321_onchain_data_1580628499_with_entities', 'w')
    json.dump(input_output_entities, out_file)

def export_edge_list():
    cursor.execute('select node_1, node_2 from channels')
    result = [{'node_1': res[0], 'node_2': res[1]} for res in cursor.fetchall()]

    out_file = open(base_path + 'channels/edge_list', 'w')
    json.dump(result, out_file)

def summarize_channel_balances_of_mapped_entities():
    data = json.load(open(base_path+'channels/entity_mapped_all_channel_export_1580628321_onchain_data_1580628499_with_entities'))

    for entity in data['input_entity'].keys():
        total_capacity = 0

        for channel in data['input_entity'][entity]:
            total_capacity += int(channel['capacity'])

        data['input_entity'][entity] = {'channels': data['input_entity'][entity], 'total_channel_balances': total_capacity}

    for entity in data['output_entity'].keys():
        total_capacity = 0

        for channel in data['output_entity'][entity]:
            total_capacity += int(channel['capacity'])

        data['output_entity'][entity] = {'channels': data['output_entity'][entity], 'total_channel_balances': total_capacity}

    for entity in data['input_output_entity'].keys():
        total_capacity = 0

        for channel in data['input_output_entity'][entity]:
            total_capacity += int(channel['capacity'])

        data['input_output_entity'][entity] = {'channels': data['input_output_entity'][entity], 'total_channel_balances': total_capacity}

    out_file = open(base_path + 'channels/summarized_entity_mapped_all_channel_export_1580628321_onchain_data_1580628499_with_entities', 'w')
    json.dump(data, out_file)

def load_entity_data():
    data = json.load(open(base_path+'channels/summarized_entity_mapped_all_channel_export_1580628321_onchain_data_1580628499_with_entities'))

    body = {'username': 'graphsense_demo', 'password': 'preview'}

    response = requests.post(url = 'http://192.168.243.2:9000/login', json=body)
    jwt = response.json()['Authorization']

    header = {'Content-Type': 'application/json', 'Authorization': jwt}

    for entity in data['input_entity'].keys():
        response = requests.get(url = 'http://192.168.243.2:9000/btc/entities/[ENTITY]'.replace('[ENTITY]', entity), headers=header)

        if not response.status_code == 404 and not response.status_code == 500:
            res = response.json()

            data['input_entity'][entity]['entity_info'] = {'balance': res['balance']['value'], 'first_tx': res['first_tx']['timestamp'], 'last_tx': res['last_tx']['timestamp'], 'no_addresses': res['no_addresses'], 'no_incoming_txs': res['no_incoming_txs'], 'no_outgoing_txs': res['no_outgoing_txs'], 'total_received': res['total_received']['value'], 'total_spent': res['total_spent']['value'], 'tags': res['tags']}

    for entity in data['output_entity'].keys():
        response = requests.get(url = 'http://192.168.243.2:9000/btc/entities/[ENTITY]'.replace('[ENTITY]', entity), headers=header)

        if not response.status_code == 404 and not response.status_code == 500:
            res = response.json()

            data['output_entity'][entity]['entity_info'] = {'balance': res['balance']['value'], 'first_tx': res['first_tx']['timestamp'], 'last_tx': res['last_tx']['timestamp'], 'no_addresses': res['no_addresses'], 'no_incoming_txs': res['no_incoming_txs'], 'no_outgoing_txs': res['no_outgoing_txs'], 'total_received': res['total_received']['value'], 'total_spent': res['total_spent']['value'], 'tags': res['tags']}

    for entity in data['input_output_entity'].keys():
        response = requests.get(url = 'http://192.168.243.2:9000/btc/entities/[ENTITY]'.replace('[ENTITY]', entity), headers=header)

        if not response.status_code == 404 and not response.status_code == 500:
            res = response.json()

            data['input_output_entity'][entity]['entity_info'] = {'balance': res['balance']['value'], 'first_tx': res['first_tx']['timestamp'], 'last_tx': res['last_tx']['timestamp'], 'no_addresses': res['no_addresses'], 'no_incoming_txs': res['no_incoming_txs'], 'no_outgoing_txs': res['no_outgoing_txs'], 'total_received': res['total_received']['value'], 'total_spent': res['total_spent']['value'], 'tags': res['tags']}

    out_file = open(base_path + 'channels/entity_infos_summarized_entity_mapped_all_channel_export_1580628321_onchain_data_1580628499_with_entities', 'w')
    json.dump(data, out_file)

def load_tags_to_btc_addresses():
    data = json.load(open(base_path+'channels/entity_infos_summarized_entity_mapped_all_channel_export_1580628321_onchain_data_1580628499_with_entities'))

    body = {'username': 'graphsense_demo', 'password': 'preview'}

    response = requests.post(url = 'http://192.168.243.2:9000/login', json=body)
    jwt = response.json()['Authorization']

    header = {'Content-Type': 'application/json', 'Authorization': jwt}

    tag_address_count = 0

    for entity in data['input_entity'].keys():

        for channel in data['input_entity'][entity]['channels']:
            response = requests.get(url = 'http://192.168.243.2:9000/btc/addresses/[ADDR]'.replace('[ADDR]', convert_btc_pub_key_to_address(channel['btc1_pub'], True)), headers=header)

            if not response.status_code == 404 and not response.status_code == 500:
                res = response.json()

                if len(res['tags']) > 0:
                    channel['btc1_tags'] = res['tags']
                    tag_address_count += len(res['tags'])

            response = requests.get(url = 'http://192.168.243.2:9000/btc/addresses/[ADDR]'.replace('[ADDR]', convert_btc_pub_key_to_address(channel['btc2_pub'], True)), headers=header)

            if not response.status_code == 404 and not response.status_code == 500:
                res = response.json()

                if len(res['tags']) > 0:
                    channel['btc2_tags'] = res['tags']
                    tag_address_count += len(res['tags'])

    for entity in data['output_entity'].keys():

        for channel in data['output_entity'][entity]['channels']:
            response = requests.get(url = 'http://192.168.243.2:9000/btc/addresses/[ADDR]'.replace('[ADDR]', convert_btc_pub_key_to_address(channel['btc1_pub'], True)), headers=header)

            if not response.status_code == 404 and not response.status_code == 500:
                res = response.json()

                if len(res['tags']) > 0:
                    channel['btc1_tags'] = res['tags']
                    tag_address_count += len(res['tags'])

            response = requests.get(url = 'http://192.168.243.2:9000/btc/addresses/[ADDR]'.replace('[ADDR]', convert_btc_pub_key_to_address(channel['btc2_pub'], True)), headers=header)

            if not response.status_code == 404 and not response.status_code == 500:
                res = response.json()

                if len(res['tags']) > 0:
                    channel['btc2_tags'] = res['tags']
                    tag_address_count += len(res['tags'])

    for entity in data['input_output_entity'].keys():

        for channel in data['input_output_entity'][entity]['channels']:
            response = requests.get(url = 'http://192.168.243.2:9000/btc/addresses/[ADDR]'.replace('[ADDR]', convert_btc_pub_key_to_address(channel['btc1_pub'], True)), headers=header)

            if not response.status_code == 404 and not response.status_code == 500:
                res = response.json()

                if len(res['tags']) > 0:
                    channel['btc1_tags'] = res['tags']
                    tag_address_count += len(res['tags'])

            response = requests.get(url = 'http://192.168.243.2:9000/btc/addresses/[ADDR]'.replace('[ADDR]', convert_btc_pub_key_to_address(channel['btc2_pub'], True)), headers=header)

            if not response.status_code == 404 and not response.status_code == 500:
                res = response.json()

                if len(res['tags']) > 0:
                    channel['btc2_tags'] = res['tags']
                    tag_address_count += len(res['tags'])

    out_file = open(base_path + 'channels/tagged_entity_infos_summarized_entity_mapped_all_channel_export_1580628321_onchain_data_1580628499_with_entities', 'w')
    json.dump(data, out_file)

    print(str(tag_address_count))

def convert_btc_pub_key_to_address(pubkey, compressed):
    if (compressed):
        try:
            if (ord(bytearray.fromhex(pubkey[-2:])) % 2 == 0):
                pubkey_compressed = '02'
            else:
                pubkey_compressed = '03'
            pubkey_compressed += pubkey[2:66]
            hex_str = bytearray.fromhex(pubkey_compressed)
        except TypeError as e:
            return ''
    else:
        hex_str = bytearray.fromhex(pubkey)

    # Obtain key:

    key_hash = '00' + hash160(hex_str)

    # Obtain signature:

    sha = hashlib.sha256()
    sha.update( bytearray.fromhex(key_hash) )
    checksum = sha.digest()
    sha = hashlib.sha256()
    sha.update(checksum)
    checksum = sha.hexdigest()[0:8]

    return (base58.b58encode( bytes(bytearray.fromhex(key_hash + checksum)) )).decode('utf-8')

def hash160(hex_str):
    sha = hashlib.sha256()
    rip = hashlib.new('ripemd160')
    sha.update(hex_str)
    rip.update( sha.digest() )
    return rip.hexdigest()  # .hexdigest() is hex ASCII

def print_stats_all_ln_channels_with_onchain_data():
    channels_with_onchain_data = json.load(open(base_path+'channels/all_channel_export_1580628321_onchain_data_1580628499'))

    openChannels = []
    closedChannels = []
    input_addresses = {}
    output_addresses = {}
    input_output_addresses = {}
    input_address_count = 0
    output_address_count = 0

    for channel_with_onchain_data in channels_with_onchain_data:

        try:
            for input_address in channel_with_onchain_data['funding_tx_input_addresses']:
                input_address_count += 1
                try:
                    input_addresses[input_address] += 1
                except KeyError as e:
                    input_addresses[input_address] = 1

                try:
                    input_output_addresses[input_address] += 1
                except KeyError as e:
                    input_output_addresses[input_address] = 1
        except KeyError as e:
            pass

        try:
            for output_address in channel_with_onchain_data['closing_tx_output_addresses']:
                output_address_count += 1
                try:
                    output_addresses[output_address] += 1
                except KeyError as e:
                    output_addresses[output_address] = 1

                try:
                    input_output_addresses[output_address] += 1
                except KeyError as e:
                    input_output_addresses[output_address] = 1
        except KeyError as e:
            pass

        try:
            if channel_with_onchain_data['active']:
                openChannels.append(channel_with_onchain_data)
            else:
                closedChannels.append(channel_with_onchain_data)
        except KeyError as e:
            pass

    reused_input_addresses = {}
    reused_output_addresses = {}
    reused_input_output_addresses = {}

    for key in input_addresses.keys():
        if input_addresses[key] > 1:
            reused_input_addresses[key] = input_addresses[key]

    for key in output_addresses.keys():
        if output_addresses[key] > 1:
            reused_output_addresses[key] = output_addresses[key]

    for key in input_output_addresses.keys():
        #if input_output_addresses[key] > 1:
        if input_output_addresses[key] > 10:
            reused_input_output_addresses[key] = input_output_addresses[key]

    print(str(len(channels_with_onchain_data))+' total unique channels')
    print(str(len(openChannels))+' open channels (checked ln channels against on chain transactions)')
    print(str(len(closedChannels))+' closed channels (checked ln channels against on chain transactions)')
    print('***')
    print(str(len(reused_input_addresses))+' addresses of funding transaction inputs are re-used')
    print(str(input_address_count) + ' input addresses in total')
    print(str(len(reused_output_addresses))+' addresses of closing transaction outputs are re-used')
    print(str(output_address_count) + ' output addresses in total')
    print(str(len(reused_input_output_addresses))+' addresses of funding transaction or closing transaction inputs and outputs are re-used')
    print(str(reused_input_output_addresses))

def print_stats_closed_ln_channels_with_onchain_data():
    channels_with_onchain_data = json.load(open(base_path+'channels/closed_channel_export_1579333342_onchain_data'))

    openChannels = []
    closedChannels = []

    for channel_with_onchain_data in channels_with_onchain_data:
        if channel_with_onchain_data['active']:
            openChannels.append(channel_with_onchain_data)
        else:
            closedChannels.append(channel_with_onchain_data)

    print(str(len(openChannels))+' open channels (closed believed: unique channels not present in last snapshot) (checked ln channels against on chain transactions)')
    print(str(len(closedChannels))+' closed channels (closed believed: unique channels not present in last snapshot) (checked ln channels against on chain transactions)')
    print(str(len(channels_with_onchain_data))+' total closed believed (unique channels not present in last snapshot) channels')

def get_txes_of_potential_uncooperative_closed_channels():
    uncooperative_closed_channels = []

    for filename in os.listdir(base_path+'blockchain_export/'):
        if fnmatch.fnmatch(filename, 'potential_uncooperative_channel_txes_*'):
            uncooperative_closed_channels += json.load(open(base_path+'blockchain_export/'+filename))

    return uncooperative_closed_channels

def create_json_for_joined_table_entry(joined_data):
    result = {}

    result['on_chain'] = json.loads(joined_data[1].replace('\'', "\""))
    result['off_chain'] = get_json_for_raw_db_data(joined_data[6])

    return result

def get_timelocked_txes_not_in_potential_txes():
    cursor.execute('select tx from potential_txes')
    unique_potential_funding_txes = [element[0] for element in cursor.fetchall()]

    timelocked_txes = [element['funding_tx_id'] for element in get_txes_of_potential_uncooperative_closed_channels()]

    timelocked_txes_not_in_potential_txes = []

    for tx in timelocked_txes:
        if tx not in unique_potential_funding_txes:
            timelocked_txes_not_in_potential_txes.append(tx)

    return timelocked_txes_not_in_potential_txes

def print_and_export_entities_with_more_channels():
    mapped_channels_to_entity = json.load(open(base_path+'channels/entity_mapped_all_channel_export_1580628321_onchain_data_1580628499_with_entities'))

    input_entities_with_more_than_one_channel = {}
    output_entities_with_more_than_one_channel = {}

    for entity in mapped_channels_to_entity['input_entity'].keys():
        if len(mapped_channels_to_entity['input_entity'][entity]) > 1:
            input_entities_with_more_than_one_channel[entity] = mapped_channels_to_entity['input_entity'][entity]

    for entity in mapped_channels_to_entity['output_entity'].keys():
        if len(mapped_channels_to_entity['output_entity'][entity]) > 1:
            output_entities_with_more_than_one_channel[entity] = mapped_channels_to_entity['output_entity'][entity]

    print(str(len(input_entities_with_more_than_one_channel)) + ' input entities with more than one channel')
    print(str(len(output_entities_with_more_than_one_channel)) + ' output entities with more than one channel')

    input_output_entities = {'input_entity': input_entities_with_more_than_one_channel, 'output_entity' : output_entities_with_more_than_one_channel}

    out_file = open(base_path + 'channels/entities_with_more_than_one_channel_entity_mapped_all_channel_export_1580628321_onchain_data_1580628499_with_entities', 'w')
    json.dump(input_output_entities, out_file)

def print_alias_stats():
    cursor.execute('select raw_data from nodes')

    raw_node_data = [ast.literal_eval(element[0]) for element in cursor.fetchall()]

    print(str(len(raw_node_data))+' unique nodes')

    nodes_with_alias = [ele for ele in raw_node_data if len(ele['alias']) > 0]

    print(str(len(nodes_with_alias))+' nodes with alias')

if __name__ == '__main__':
    connection = create_connection()

    cursor = connection.cursor()

    # closed_channels_onchain = get_closed_channels_onchain(cursor)
    # print(str(len(closed_channels_onchain)) + ' closed channels were found on-chain (merged potential txes with ln channels)')
    #
    # number_potential_txes_onchain = get_number_potential_txes_onchain(cursor)
    # print(str(number_potential_txes_onchain) + ' total potential channel transacations were found on-chain')
    #
    # number_total_unique_channels = get_number_total_unique_channels(cursor)
    # print(str(number_total_unique_channels) + ' total unique channels were found off-chain')
    #
    # number_open_channels_offchain = get_number_open_channels_offchain(cursor)
    # print(str(number_open_channels_offchain) + ' open channels were found off-chain (all channels that are present in latest channel snapshot - not complete)')
    #
    # funding_txes_of_closed_channels_offchain = get_closed_channels_offchain(cursor)
    # print(str(len(funding_txes_of_closed_channels_offchain)) + ' closed channels were found off-chain (at least actually not known to the LND client)')
    # export_closed_ln_channels_to_file(funding_txes_of_closed_channels_offchain)
    #
    # funding_txes_of_closed_channels_onchain = get_funding_txes_of_closed_channels_onchain(cursor)
    #
    # funding_txes_of_closed_channels_offchain_but_not_onchain = funding_txes_of_closed_channels_offchain.copy()
    #
    # for tx in funding_txes_of_closed_channels_onchain:
    #     funding_txes_of_closed_channels_offchain_but_not_onchain.remove(tx)
    #
    # print('seems, that there are ' + str(len(funding_txes_of_closed_channels_offchain_but_not_onchain)) + ' channels closed off-chain, but no respective transaction could be found on-chain')
    #
    # load_outputs_and_export_txes(cursor, funding_txes_of_closed_channels_offchain_but_not_onchain)
    #
    # channels_with_lack_of_snapshots = calculate_channels_with_lack_of_snapshots_during_known_lifetime(cursor)
    # print(str(len(channels_with_lack_of_snapshots)) + ' channels are not part of every snapshot during their known lifetimes')
    #
    # total_unique_bitcoin_keys = get_total_unique_bitcoin_keys(cursor)
    # print(str(len(total_unique_bitcoin_keys)) + ' unique bitcoin keys')
    #
    # reused_bitcoin_keys = get_reused_bitcoin_keys(total_unique_bitcoin_keys)
    # print(str((reused_bitcoin_keys)) + ' bitcoin keys are reused')
    #
    # missing_timestamps_in_db = get_missing_timestamps_in_db(cursor)
    # print(str(missing_timestamps_in_db) + ' timestamps are missing in database')
    #
    # 605798 is the block height right after hourly LN graph snapshots started (~ 9 p.m. on 28th of November 2019)
    # potential_txes_closing_tx_block_height_greater_605798 = get_potential_txes_closing_tx_block_height_greater_block_height(605798)
    # print(str(len(potential_txes_closing_tx_block_height_greater_605798)) + ' potential onchain LN transactions where closing block height is greater than 605798 (begin of hourly LN snapshots)')
    #
    # all_potential_ln_channel_txes = get_all_potential_ln_channel_txes()
    # print(str(len(all_potential_ln_channel_txes)) + ' total potential LN transactions starting from block 500,000')
    #
    # export_ln_channels_to_file()
    #
    # print_stats_all_ln_channels_with_onchain_data()
    #
    # txes_of_potential_uncooperative_closed_channels = get_txes_of_potential_uncooperative_closed_channels()
    # print(str(len(txes_of_potential_uncooperative_closed_channels)) + ' transactions are potential uncooperative closed channels')
    #
    # timelocked_txes_not_in_potential_txes = get_timelocked_txes_not_in_potential_txes()
    # print(str(len(timelocked_txes_not_in_potential_txes)) + ' of timelocked transactions are not part of potential transactions (should be 0)')
    #
    # print_stats_closed_ln_channels_with_onchain_data()
    #
    # create_file_with_all_interacting_input_output_addresses_of_all_channels()
    #
    # load_tags_to_addresses()
    #
    # load_entities_to_addresses()
    #
    # count_input_output_addresses_and_entities()
    #
    # export_entity_channel_mapping()
    #
    # print_and_export_entities_with_more_channels()
    #
    # summarize_channel_balances_of_mapped_entities()
    #
    # export_entity_node_mapping()
    #
    # export_edge_list()
    #
    # load_entity_data()
    #
    # load_tags_to_btc_addresses()
    #
    # export_ln_nodes_to_file()
    #
    print_alias_stats()
    #
    connection.close()