import sqlite3
import time
import json

#base_path = './'
base_path = '../../../go/dev/alice/'

def create_connection():
    try:
        connection = sqlite3.connect(base_path+'sqlite/db')
        return connection

    except sqlite3.Error as e:
        print(e)
        return None

def load_and_insert_latest_graph(connection):
    latest_snapshot_timestamp = get_latest_snapshot_timestamp()

    try:
        graph = json.load(open(base_path+'graph_backup/graph_'+str(latest_snapshot_timestamp)))
        insert_graph(connection, latest_snapshot_timestamp, graph)
    except FileNotFoundError as e:
        graph = json.load(open(base_path+'graph_backup/graph_'+str(latest_snapshot_timestamp+1)))
        insert_graph(connection, latest_snapshot_timestamp+1, graph)

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

def get_latest_snapshot_timestamp():
    current_timestamp = int(time.time())
    remainer = current_timestamp % 3600

    return current_timestamp-remainer+1

if __name__ == '__main__':
    connection = create_connection()

    load_and_insert_latest_graph(connection)

    connection.close()