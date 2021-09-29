import json
import os
import fnmatch

base_path = '../../../go/dev/alice/'
aggregated_path = 'aggregated/'
blockchain_export_path = 'blockchain_export/'
result_path = 'result/'

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

for potential_channel_tx in potential_total_channel_txes:

    for channel in channels:

        funding_tx = channel['chan_point'].split(':')[0]
        funding_tx_ouput_index = int(channel['chan_point'].split(':')[1])

        if funding_tx == potential_channel_tx['funding_tx_id'] and (channel['btc1_pub'] == potential_channel_tx['btc_key_1'] or channel['btc1_pub'] == potential_channel_tx['btc_key_2']) and (channel['btc2_pub'] == potential_channel_tx['btc_key_2'] or channel['btc2_pub'] == potential_channel_tx['btc_key_1']) and int(channel['capacity']) == potential_channel_tx['output_values'][funding_tx_ouput_index]:
        #if funding_tx == potential_channel_tx['funding_tx_id'] and int(channel['capacity']) == potential_channel_tx['output_values'][funding_tx_ouput_index]:
        #if funding_tx == potential_channel_tx['funding_tx_id']:
            total_matching_txes.append({'on_chain_data': potential_channel_tx, 'off_chain_data': channel})
            #reduced_total_matching_txes.append({'funding_tx_id': potential_channel_tx['funding_tx_id'], 'closing_tx_id': potential_channel_tx['closing_tx_id']})
        #else:
            #reduced_total_false_positive_txes.append({'funding_tx_id': potential_channel_tx['funding_tx_id'], 'closing_tx_id': potential_channel_tx['closing_tx_id']})
            #total_false_positive_txes.append({'on_chain_data': potential_channel_tx, 'off_chain_data': channel})

for potential_channel_tx in potential_uncooperative_channel_txes:

    for channel in channels:

        funding_tx = channel['chan_point'].split(':')[0]
        funding_tx_ouput_index = int(channel['chan_point'].split(':')[1])

        if funding_tx == potential_channel_tx['funding_tx_id'] and (channel['btc1_pub'] == potential_channel_tx['btc_key_1'] or channel['btc1_pub'] == potential_channel_tx['btc_key_2']) and (channel['btc2_pub'] == potential_channel_tx['btc_key_2'] or channel['btc2_pub'] == potential_channel_tx['btc_key_1']) and int(channel['capacity']) == potential_channel_tx['output_values'][funding_tx_ouput_index]:
        #if funding_tx == potential_channel_tx['funding_tx_id'] and int(channel['capacity']) == potential_channel_tx['output_values'][funding_tx_ouput_index]:
        #if funding_tx == potential_channel_tx['funding_tx_id']:
            uncooperative_matching_txes.append({'on_chain_data': potential_channel_tx, 'off_chain_data': channel})
            #reduced_uncooperative_matching_txes.append({'funding_tx_id': potential_channel_tx['funding_tx_id'], 'closing_tx_id': potential_channel_tx['closing_tx_id'], 'timelocked_tx_id': potential_channel_tx['timelocked_tx_id']})
        #else:
            #reduced_uncooperative_false_positive_txes.append({'funding_tx_id': potential_channel_tx['funding_tx_id'], 'closing_tx_id': potential_channel_tx['closing_tx_id'], 'timelocked_tx_id': potential_channel_tx['timelocked_tx_id']})
            #uncooperative_false_positive_txes.append({'on_chain_data': potential_channel_tx, 'off_chain_data': channel})

out_file = open(base_path + result_path + 'total_matching_txes', 'w')
json.dump(total_matching_txes, out_file)

#out_file = open(base_path + result_path + 'total_false_positive_txes', 'w')
#json.dump(total_false_positive_txes, out_file)

#out_file = open(base_path + result_path + 'reduced_total_matching_txes', 'w')
#json.dump(reduced_total_matching_txes, out_file)

#out_file = open(base_path + result_path + 'reduced_total_false_positive_txes', 'w')
#json.dump(reduced_total_false_positive_txes, out_file)

out_file = open(base_path + result_path + 'uncooperative_matching_txes', 'w')
json.dump(uncooperative_matching_txes, out_file)

#out_file = open(base_path + result_path + 'uncooperative_false_positive_txes', 'w')
#json.dump(uncooperative_false_positive_txes, out_file)

#out_file = open(base_path + result_path + 'reduced_uncooperative_matching_txes', 'w')
#json.dump(reduced_uncooperative_matching_txes, out_file)

#out_file = open(base_path + result_path + 'reduced_uncooperative_false_positive_txes', 'w')
#json.dump(reduced_uncooperative_false_positive_txes, out_file)

print(str(len(total_matching_txes) / len(potential_total_channel_txes) * 100) + ' percent of on-chain transactions are total LN channels')
print(str(len(uncooperative_matching_txes) / len(potential_uncooperative_channel_txes) * 100) + ' percent of on-chain transactions are uncooperative LN channels')
#print(str(len(total_false_positive_txes)) + ' are total false positives')
#print(str(len(uncooperative_false_positive_txes)) + ' are uncooperative false positives')
print(str(len(potential_total_channel_txes) - len(total_matching_txes)) + ' are total false positives')
print(str(len(potential_uncooperative_channel_txes) - len(uncooperative_matching_txes)) + ' are uncooperative false positives')