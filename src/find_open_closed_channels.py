import json

from os import listdir
from os.path import isfile, join

base_path = '../../../go/dev/alice/'
aggregated_path = 'aggregated/'
merged_path = 'merged/'
result_path = 'result/'

all_channels = json.load(open(base_path + aggregated_path + 'aggregated_merged_channels'))

print('unique off-chain channels: ' + str(len(all_channels)))

merged_graph_file_names = [f for f in listdir(base_path + merged_path) if isfile(join(base_path + merged_path, f))]

latest_timestamp = 0

for merged_graph_file_name in merged_graph_file_names:
    timestamp = int(merged_graph_file_name.split('_')[2])

    if timestamp > latest_timestamp:
        latest_timestamp = timestamp

latest_channels = json.load(open(base_path + merged_path + 'merged_graph_' + str(latest_timestamp)))

print('latest channels: ' + str(len(latest_channels)))

open_channels = []
closed_channels = []

indexed_latest_channels = {}

for latest_channel in latest_channels:
    indexed_latest_channels[latest_channel['channel_id']] = latest_channel

for all_channel in all_channels:
    try:
        key_test = indexed_latest_channels[all_channel['channel_id']]
        open_channels.append(all_channel)

    except KeyError as e:
        closed_channels.append(all_channel)

print('open channels: ' + str(len(open_channels)))
print('closed channels: ' + str(len(closed_channels)))

total_matching_txes = json.load(open(base_path+result_path+'total_matching_txes'))

print('total matching txes: ' + str(len(total_matching_txes)))

indexed_matching_txes = {}

for indexed_matching_tx in total_matching_txes:
    indexed_matching_txes[indexed_matching_tx['on_chain_data']['funding_tx_id']] = indexed_matching_tx

found_onchain_closed_channels = []
not_found_onchain_closed_channels = []

for closed_channel in closed_channels:
    try:
        key_test = indexed_matching_txes[closed_channel['chan_point'].split(':')[0]]

        found_onchain_closed_channels.append(closed_channel)
    except KeyError as e:
        not_found_onchain_closed_channels.append(closed_channel)

print('found closed channels on-chain: ' + str(len(found_onchain_closed_channels)))
print('not found closed channels on-chain: ' + str(len(not_found_onchain_closed_channels)))