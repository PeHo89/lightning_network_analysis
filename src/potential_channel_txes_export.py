import blocksci
import json

chain = blocksci.Blockchain("/var/data/blocksci_data/btc.cfg")

#block_index = len(chain.blocks)-1
block_index = 608434
block_index_copy = block_index

potential_total_channel_txes = []
potential_uncooperative_channel_txes = []
tx_counter = 0

#target_block_index = 0 #for the whole blockchain
target_block_index = block_index-500 #for 500 blocks
#target_block_index = 605798 #blocknumber right after the hourly LN snapshots started

print('starting at block height: '+str(block_index))

while block_index > target_block_index:
    block = chain.blocks[block_index]

    for tx in block.txes:

        tx_counter += 1

        if tx.input_count == 1:

            tx_input = tx.inputs[0]

            if tx_input.address.type == blocksci.address_type.witness_scripthash and tx_input.address.wrapped_address.type == blocksci.address_type.multisig and tx_input.address.wrapped_address.total == 2 and tx_input.address.wrapped_address.required == 2:
                #total closing
                closing_tx_id = str(tx.hash)
                funding_tx_id = str(tx_input.spent_tx.hash)

                block_height_closing_tx = tx.block_height
                block_height_funding_tx = tx_input.spent_tx.block_height

                output_values = []

                for output in tx_input.spent_tx.outputs:
                    output_values.append(output.value)

                btc_key_1 = tx_input.address.wrapped_address.addresses[0].pubkey.hex()
                btc_key_2 = tx_input.address.wrapped_address.addresses[1].pubkey.hex()

                btc_addr_1 = tx_input.address.wrapped_address.addresses[0].address_string
                btc_addr_2 = tx_input.address.wrapped_address.addresses[1].address_string

                potential_total_channel_txes.append({
                    'funding_tx_id': funding_tx_id,
                    'closing_tx_id': closing_tx_id,
                    'block_height_funding_tx': block_height_funding_tx,
                    'block_height_closing_tx': block_height_closing_tx,
                    'btc_key_1': btc_key_1,
                    'btc_key_2': btc_key_2,
                    'btc_addr_1': btc_addr_1,
                    'btc_addr_2': btc_addr_2,
                    'output_values': output_values
                })

            elif tx_input.address.type == blocksci.address_type.witness_scripthash and tx_input.address.wrapped_address.type == blocksci.address_type.nonstandard and tx.output_count == 1 and len(tx_input.address.wrapped_address.out_script) > 0 and tx_input.address.wrapped_address.out_script.startswith('OP_IF') and tx_input.address.wrapped_address.out_script.endswith('OP_CHECKSIG') and 'OP_ELSE' in tx_input.address.wrapped_address.out_script and 'OP_CHECKSEQUENCEVERIFY' in tx_input.address.wrapped_address.out_script and 'OP_DROP' in tx_input.address.wrapped_address.out_script and 'OP_ENDIF' in tx_input.address.wrapped_address.out_script and tx_input.spent_tx.inputs[0].address.type == blocksci.address_type.witness_scripthash and tx_input.spent_tx.inputs[0].address.wrapped_address.type == blocksci.address_type.multisig and tx_input.spent_tx.inputs[0].address.wrapped_address.total == 2 and tx_input.spent_tx.inputs[0].address.wrapped_address.required == 2:
                #uncooperative closing

                timelocked_tx_id = str(tx.hash)
                closing_tx_id = str(tx_input.spent_tx.hash)
                funding_tx_id = str(tx_input.spent_tx.inputs[0].spent_tx.hash)

                block_height_timelocked_tx = tx.block_height
                block_height_closing_tx = tx_input.spent_tx.block_height
                block_height_funding_tx = tx_input.spent_tx.inputs[0].spent_tx.block_height

                output_values = []

                for output in tx_input.spent_tx.inputs[0].spent_tx.outputs:
                    output_values.append(output.value)

                btc_key_1 = tx_input.spent_tx.inputs[0].address.wrapped_address.addresses[0].pubkey.hex()
                btc_key_2 = tx_input.spent_tx.inputs[0].address.wrapped_address.addresses[1].pubkey.hex()

                btc_addr_1 = tx_input.spent_tx.inputs[0].address.wrapped_address.addresses[0].address_string
                btc_addr_2 = tx_input.spent_tx.inputs[0].address.wrapped_address.addresses[1].address_string

                potential_uncooperative_channel_txes.append({
                    'funding_tx_id': funding_tx_id,
                    'closing_tx_id': closing_tx_id,
                    'timelocked_tx_id': timelocked_tx_id,
                    'block_height_funding_tx': block_height_funding_tx,
                    'block_height_closing_tx': block_height_closing_tx,
                    'block_height_timelocked_tx': block_height_timelocked_tx,
                    'btc_key_1': btc_key_1,
                    'btc_key_2': btc_key_2,
                    'btc_addr_1': btc_addr_1,
                    'btc_addr_2': btc_addr_2,
                    'output_values': output_values
                })

    block_index -= 1

print('finishing at block height: '+str(block_index+1))
print('total transactions: '+str(tx_counter))

print('potential total channel transactions: '+str(len(potential_total_channel_txes)))
print('potential uncooperative channel transactions: '+str(len(potential_uncooperative_channel_txes)))

out_file = open('./exports/potential_total_channel_txes_'+str(block_index+1)+'-'+str(block_index_copy), 'w')
json.dump(potential_total_channel_txes, out_file)

out_file = open('./exports/potential_uncooperative_channel_txes_'+str(block_index+1)+'-'+str(block_index_copy), 'w')
json.dump(potential_uncooperative_channel_txes, out_file)