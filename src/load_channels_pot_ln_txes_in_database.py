import ast
import sqlite3
import json
import os
import fnmatch

from os import listdir
from os.path import isfile, join

base_path = '../../../go/dev/alice/'

def create_connection():
    try:
        #connection = sqlite3.connect(base_path+'sqlite/db')
        connection = sqlite3.connect(base_path+'sqlite/final')
        return connection

    except sqlite3.Error as e:
        print(e)
        return None

def load_and_insert_less_restrictive_potential_txes(connection):
    for filename in os.listdir(base_path+'blockchain_export/'):
        if fnmatch.fnmatch(filename, 'potential_total_channel_txes_*_less_restrictive'):
            insert_less_restrictive_potential_txes(connection, json.load(open(base_path+'blockchain_export/'+filename)))

def insert_less_restrictive_potential_txes(connection, txes):
    print('inserting potential txes: '+str(len(txes)))

    insert_potential_tx = 'insert into potential_txes_less_restrictive (tx, raw_data) values (?, ?)'

    update_potential_tx = 'update potential_txes_less_restrictive set raw_data = ? where tx = ?'

    cursor = connection.cursor()

    i = 0

    for tx in txes:
        i += 1

        if i == 10000:
            connection.commit()
            i = 0

        try:
            cursor.execute(insert_potential_tx, (tx['funding_tx_id'], str(tx)))

        except sqlite3.IntegrityError as e:
            cursor.execute('select raw_data from potential_txes_less_restrictive where tx = ?', (tx['funding_tx_id'],))

            raw_data = str(cursor.fetchall()[0])

            if len(str(tx)) > len(raw_data):
                cursor.execute(update_potential_tx, (str(tx), tx['funding_tx_id']))

    connection.commit()

def load_and_insert_potential_txes(connection):
    for filename in os.listdir(base_path+'blockchain_export/'):
        #if fnmatch.fnmatch(filename, 'potential_total_channel_txes_*'):
        if fnmatch.fnmatch(filename, 'potential_total_channel_txes_605798-615178'):
            insert_potential_txes(connection, json.load(open(base_path+'blockchain_export/'+filename)))

def insert_potential_txes(connection, txes):
    print('inserting potential txes: '+str(len(txes)))

    insert_potential_tx = 'insert into potential_txes (tx, raw_data) values (?, ?)'

    update_potential_tx = 'update potential_txes set raw_data = ? where tx = ?'

    cursor = connection.cursor()

    i = 0

    for tx in txes:
        i += 1

        if i == 10000:
            connection.commit()
            i = 0

        try:
            cursor.execute(insert_potential_tx, (tx['funding_tx_id'], str(tx)))

        except sqlite3.IntegrityError as e:
            cursor.execute('select raw_data from potential_txes where tx = ?', (tx['funding_tx_id'],))

            raw_data = str(cursor.fetchall()[0])

            if len(str(tx)) > len(raw_data):
                cursor.execute(update_potential_tx, (str(tx), tx['funding_tx_id']))

    connection.commit()

def load_and_insert_graphs(connection):
    graph_file_names = [f for f in listdir(base_path+'graph_backup/') if isfile(join(base_path+'graph_backup/', f))]
    graph_file_names.remove('.info')

    #load specific graph snapshot files
    #graph_file_names = ['graph_1579932001']

    for graph_file_name in graph_file_names:
        timestamp = graph_file_name[6:]

        #only insert snapshots from a specific time
        if int(timestamp) > 1580367601:
            continue

        graph = json.load(open(base_path+'graph_backup/'+graph_file_name))

        insert_graph(connection, timestamp, graph)

def insert_graph(connection, timestamp, graph):
    print('inserting graph from timestamp: '+str(timestamp))

    insert_node = 'insert into nodes (pub_key, raw_data) values (?, ?)'
    insert_channel = 'insert into channels (funding_tx, output_idx, node_1, node_2, raw_data) values (?, ?, ?, ?, ?)'
    insert_node_snapshot = 'insert into node_snapshots (node, timestamp ) values (?, ?)'
    insert_channel_snapshot = 'insert into channel_snapshots (channel, idx, timestamp) values (?, ?, ?)'

    update_node = 'update nodes set raw_data = ? where pub_key = ?'
    update_channel = 'update channels set node_1 = ?, node_2 = ?, raw_data = ? where funding_tx = ? and output_idx = ?'

    cursor = connection.cursor()

    for node in graph['nodes']:
        try:
            cursor.execute(insert_node, (node['pub_key'], str(node)))

        except sqlite3.IntegrityError as e:
            cursor.execute('select raw_data from nodes where pub_key = ?', (node['pub_key'],))

            raw_data = str(cursor.fetchall()[0])

            if len(str(node)) > len(raw_data):
                cursor.execute(update_node, (str(node), node['pub_key']))

        try:
            cursor.execute(insert_node_snapshot, (node['pub_key'], timestamp))
        except sqlite3.IntegrityError as e:
            pass

    connection.commit()

    for channel in graph['edges']:
        try:
            cursor.execute(insert_channel, (channel['chan_point'].split(':')[0], int(channel['chan_point'].split(':')[1]), channel['node1_pub'], channel['node2_pub'], str(channel)))

        except sqlite3.IntegrityError as e:
            cursor.execute('select raw_data from channels where funding_tx = ? and output_idx = ?', (channel['chan_point'].split(':')[0], int(channel['chan_point'].split(':')[1])))

            raw_data = str(cursor.fetchall()[0])

            if len(str(channel)) > len(raw_data):
                cursor.execute(update_channel, (channel['node1_pub'], channel['node2_pub'], str(channel), channel['chan_point'].split(':')[0], int(channel['chan_point'].split(':')[1])))

        try:
            cursor.execute(insert_channel_snapshot, (channel['chan_point'].split(':')[0], int(channel['chan_point'].split(':')[1]), timestamp))
        except sqlite3.IntegrityError as e:
            pass

    connection.commit()

def test(connection):
    cursor = connection.cursor()

    cursor.execute('select raw_data from nodes')

    raw_data = [ast.literal_eval(element[0]) for element in cursor.fetchall()]

    print(len(raw_data))

if __name__ == '__main__':
    connection = create_connection()

    load_and_insert_graphs(connection)
    load_and_insert_potential_txes(connection)
    #load_and_insert_less_restrictive_potential_txes(connection)
    #test(connection)

    connection.close()