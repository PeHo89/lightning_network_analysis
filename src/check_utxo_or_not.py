import blocksci
import json

chain = blocksci.Blockchain("/var/data/blocksci_data/btc.cfg")

funding_txes_with_outputs_of_closed_channels_offchain_but_not_onchain = json.load(open('./analysis/funding_txes_with_outputs_of_closed_channels_offchain_but_not_onchain'))

print(str(len(funding_txes_with_outputs_of_closed_channels_offchain_but_not_onchain)) + ' transactions to check...')

spent_tx_outputs = []
unspent_tx_outputs = []

for tx in funding_txes_with_outputs_of_closed_channels_offchain_but_not_onchain:
    tx_output = chain.tx_with_hash(tx['funding_tx']).outputs[tx['output_idx']]

    if tx_output.spending_tx == None:
        unspent_tx_outputs.append(tx)
    else:
        spent_tx_outputs.append(tx)

print(str(len(spent_tx_outputs)) + ' spent outputs')
print(str(len(unspent_tx_outputs)) + ' unspent outputs')