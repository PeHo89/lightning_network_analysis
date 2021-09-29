import json
import blocksci
import time

chain = blocksci.Blockchain("/var/data/blocksci_data/btc.cfg")

channel_data = json.load(open('./all_channel_export_1580628321'))

for channel in channel_data:
    funding_tx = channel['chan_point'].split(':')[0]
    output_id = int(channel['chan_point'].split(':')[1])

    try:
        tx = chain.tx_with_hash(funding_tx)
    except RuntimeError as e:
        print('no transaction with hash: '+funding_tx)
        channel['info'] = 'too new for BlockSci'
        continue

    channel['active'] = (tx.outputs[output_id].spending_tx == None)

    if not channel['active']:
        channel['closing_tx'] = str(tx.outputs[output_id].spending_tx.hash)
        channel['closing_block_height'] = str(tx.outputs[output_id].spending_tx.block_height)

        channel['closing_tx_output_addresses'] = []

        for i in range(0, tx.outputs[output_id].spending_tx.output_count):
            channel['closing_tx_output_addresses'].append(tx.outputs[output_id].spending_tx.outputs[i].address.address_string)

    channel['funding_tx_input_addresses'] = []

    for i in range(0, tx.input_count):
        channel['funding_tx_input_addresses'].append(tx.inputs[i].address.address_string)

    channel['funding_block_height'] = str(tx.block_height)

out_file = open('./analysis/all_channel_export_1580628321_onchain_data_'+str(int(time.time())), 'w')
json.dump(channel_data, out_file)