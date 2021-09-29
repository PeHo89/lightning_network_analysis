import blocksci
import json
import datetime

chain = blocksci.Blockchain("/var/data/blocksci_data/btc.cfg")

block_index = len(chain.blocks)-1
#block_index = 401000
block_index_copy = block_index

target_block_index = 399999 #0 for the whole blockchain
#target_block_index = block_index-52500 #for 500 blocks
#target_block_index = 605798 #blocknumber right after the hourly LN snapshots started

print('started at: '+str(datetime.datetime.now()))
print('starting at block height: '+str(block_index))

block_data = {}

while block_index > target_block_index:
    block = chain.blocks[block_index]

    tx_counter = 0
    two_of_two_tx_counter = 0

    for tx in block.txes:

        tx_counter += 1

        if tx.input_count == 1:

            tx_input = tx.inputs[0]

            if tx_input.address.type == blocksci.address_type.witness_scripthash and tx_input.address.wrapped_address.type == blocksci.address_type.multisig and tx_input.address.wrapped_address.total == 2 and tx_input.address.wrapped_address.required == 2 and ((len(tx_input.spent_tx.outputs) == 1 and tx_input.spent_tx.outputs[0].address.type == blocksci.address_type.witness_scripthash) or (len(tx_input.spent_tx.outputs) == 2 and ((tx_input.spent_tx.outputs[0].address.type == blocksci.address_type.witness_scripthash) or (tx_input.spent_tx.outputs[1].address.type == blocksci.address_type.witness_scripthash)))):
                two_of_two_tx_counter += 1

    block_data[block_index] = {'total_txes': tx_counter, '2of2_txes': two_of_two_tx_counter}

    block_index -= 1

print('finished at: '+str(datetime.datetime.now()))
print('finishing at block height: '+str(block_index+1))
print('total transactions: '+str(tx_counter))
print('2of2 multisig transactions: '+str(two_of_two_tx_counter))

out_file = open('./exports/total_and_2of2_txes_count_'+str(block_index+1)+'-'+str(block_index_copy), 'w')
json.dump(block_data, out_file)
