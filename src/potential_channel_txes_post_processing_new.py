import json
import os
import fnmatch

base_path = '../../../go/dev/alice/'
aggregated_path = 'aggregated/'
blockchain_export_path = 'blockchain_export/'
result_path = 'result/'

aggregate_merged = True

potential_channel_txes_filename = ''

for filename in os.listdir(base_path+blockchain_export_path):
    if fnmatch.fnmatch(filename, 'potential_total_channel_txes_*'):
        potential_channel_txes_filename = filename
        break

potential_total_channel_txes = json.load(open(base_path + blockchain_export_path + potential_channel_txes_filename))

for filename in os.listdir(base_path+blockchain_export_path):
    if fnmatch.fnmatch(filename, 'potential_uncooperative_channel_txes_*'):
        potential_channel_txes_filename = filename
        break

potential_uncooperative_channel_txes = json.load(open(base_path + blockchain_export_path + potential_channel_txes_filename))

print('potential total channel on-chain transactions: ' + str(len(potential_total_channel_txes)))
print('potential uncooperative channel on-chain transactions: ' + str(len(potential_uncooperative_channel_txes)))

if aggregate_merged:
    channels = json.load(open(base_path+aggregated_path+'aggregated_merged_channels'))
else:
    channels = json.load(open(base_path+aggregated_path+'aggregated_channels'))

print('unique off-chain channels: '+str(len(channels)))

total_matching_txes = []
reduced_total_matching_txes = []

total_false_positive_txes = []
reduced_total_false_positive_txes = []

uncooperative_matching_txes = []
reduced_uncooperative_matching_txes = []

uncooperative_false_positive_txes = []
reduced_uncooperative_false_positive_txes = []

found_channels_onchain = []
not_found_channels_onchain = []

indexed_channels = {}

for channel in channels:
    indexed_channels[channel['chan_point'].split(':')[0]] = channel

for potential_channel_tx in potential_total_channel_txes:

    try:
        channel = indexed_channels[potential_channel_tx['funding_tx_id']]
        
        funding_tx = channel['chan_point'].split(':')[0]
        funding_tx_ouput_index = int(channel['chan_point'].split(':')[1])
        
        if funding_tx == potential_channel_tx['funding_tx_id'] and (channel['btc1_pub'] == potential_channel_tx['btc_key_1'] or channel['btc1_pub'] == potential_channel_tx['btc_key_2']) and (channel['btc2_pub'] == potential_channel_tx['btc_key_2'] or channel['btc2_pub'] == potential_channel_tx['btc_key_1']) and int(channel['capacity']) == potential_channel_tx['output_values'][funding_tx_ouput_index]:
            total_matching_txes.append({'on_chain_data': potential_channel_tx, 'off_chain_data': channel})
            reduced_total_matching_txes.append({'funding_tx_id': potential_channel_tx['funding_tx_id'], 'closing_tx_id': potential_channel_tx['closing_tx_id']})
        else:
            total_false_positive_txes.append({'on_chain_data': potential_channel_tx})
            reduced_total_false_positive_txes.append({'funding_tx_id': potential_channel_tx['funding_tx_id'], 'closing_tx_id': potential_channel_tx['closing_tx_id']})
        
    except KeyError as e:
        total_false_positive_txes.append({'on_chain_data': potential_channel_tx})
        reduced_total_false_positive_txes.append({'funding_tx_id': potential_channel_tx['funding_tx_id'], 'closing_tx_id': potential_channel_tx['closing_tx_id']})

for potential_channel_tx in potential_uncooperative_channel_txes:

    try:
        channel = indexed_channels[potential_channel_tx['funding_tx_id']]
        
        funding_tx = channel['chan_point'].split(':')[0]
        funding_tx_ouput_index = int(channel['chan_point'].split(':')[1])
        
        if funding_tx == potential_channel_tx['funding_tx_id'] and (channel['btc1_pub'] == potential_channel_tx['btc_key_1'] or channel['btc1_pub'] == potential_channel_tx['btc_key_2']) and (channel['btc2_pub'] == potential_channel_tx['btc_key_2'] or channel['btc2_pub'] == potential_channel_tx['btc_key_1']) and int(channel['capacity']) == potential_channel_tx['output_values'][funding_tx_ouput_index]:
            uncooperative_matching_txes.append({'on_chain_data': potential_channel_tx, 'off_chain_data': channel})
            reduced_uncooperative_matching_txes.append({'funding_tx_id': potential_channel_tx['funding_tx_id'], 'closing_tx_id': potential_channel_tx['closing_tx_id']})
        else:
            uncooperative_false_positive_txes.append({'on_chain_data': potential_channel_tx})
            reduced_uncooperative_false_positive_txes.append({'funding_tx_id': potential_channel_tx['funding_tx_id'], 'closing_tx_id': potential_channel_tx['closing_tx_id'], 'timelocked_tx_id': potential_channel_tx['timelocked_tx_id']})
        
    except KeyError as e:
        uncooperative_false_positive_txes.append({'on_chain_data': potential_channel_tx})
        reduced_uncooperative_false_positive_txes.append({'funding_tx_id': potential_channel_tx['funding_tx_id'], 'closing_tx_id': potential_channel_tx['closing_tx_id'], 'timelocked_tx_id': potential_channel_tx['timelocked_tx_id']})


indexed_total_matching_txes = {}

for total_matching_tx in total_matching_txes:
    indexed_total_matching_txes[total_matching_tx['on_chain_data']['funding_tx_id']] = total_matching_tx

for channel in channels:
    try:
        key_test = indexed_total_matching_txes[channel['chan_point'].split(':')[0]]
        found_channels_onchain.append(channel)

    except KeyError as e:
        not_found_channels_onchain.append(channel)

out_file = open(base_path + result_path + 'total_matching_txes', 'w')
json.dump(total_matching_txes, out_file)

out_file = open(base_path + result_path + 'total_false_positive_txes', 'w')
json.dump(total_false_positive_txes, out_file)

out_file = open(base_path + result_path + 'reduced_total_matching_txes', 'w')
json.dump(reduced_total_matching_txes, out_file)

out_file = open(base_path + result_path + 'reduced_total_false_positive_txes', 'w')
json.dump(reduced_total_false_positive_txes, out_file)

out_file = open(base_path + result_path + 'uncooperative_matching_txes', 'w')
json.dump(uncooperative_matching_txes, out_file)

out_file = open(base_path + result_path + 'uncooperative_false_positive_txes', 'w')
json.dump(uncooperative_false_positive_txes, out_file)

out_file = open(base_path + result_path + 'reduced_uncooperative_matching_txes', 'w')
json.dump(reduced_uncooperative_matching_txes, out_file)

out_file = open(base_path + result_path + 'reduced_uncooperative_false_positive_txes', 'w')
json.dump(reduced_uncooperative_false_positive_txes, out_file)

out_file = open(base_path + result_path + 'found_channels_onchain', 'w')
json.dump(found_channels_onchain, out_file)

out_file = open(base_path + result_path + 'not_found_channels_onchain', 'w')
json.dump(not_found_channels_onchain, out_file)

print(str(len(total_matching_txes)) + ' are total positives')
print(str(len(uncooperative_matching_txes)) + ' are uncooperative positives')

print(str(len(total_false_positive_txes)) + ' are total false positives')
print(str(len(uncooperative_false_positive_txes)) + ' are uncooperative false positives')

print(str(len(found_channels_onchain)) + ' channels were found on-chain')
print(str(len(not_found_channels_onchain)) + ' channels were not found on-chain')

print(str(len(total_matching_txes) / len(potential_total_channel_txes) * 100) + ' percent of on-chain transactions are total LN channels')
print(str(len(uncooperative_matching_txes) / len(potential_uncooperative_channel_txes) * 100) + ' percent of on-chain transactions are uncooperative LN channels')
print(str(len(uncooperative_matching_txes) / len(total_matching_txes) * 100) + ' percent of matching transactions are uncooperative LN channels')