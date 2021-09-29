import json
import blocksci

chain = blocksci.Blockchain("/var/data/blocksci_data/btc.cfg")

reduced_total_matching_txes = json.load(open('./results/reduced_total_matching_txes'))
reduced_total_false_positive_txes = json.load(open('./results/reduced_total_false_positive_txes'))
#reduced_uncooperative_false_positive_txes = json.load(open('./results/reduced_uncooperative_false_positive_txes'))
#reduced_uncooperative_matching_txes = json.load(open('./results/reduced_uncooperative_matching_txes'))

total_matching_funding_output_types = []
total_false_positive_funding_output_types = []

for matching_tx_pair in reduced_total_matching_txes:
    tx = chain.tx_with_hash(matching_tx_pair['funding_tx_id'])

    data = {}

    for i in range(len(tx.outputs)):
        data['output_'+str(i)] = str(tx.outputs[i].address.type)

    total_matching_funding_output_types.append(data)

for matching_tx_pair in reduced_total_false_positive_txes:
    tx = chain.tx_with_hash(matching_tx_pair['funding_tx_id'])

    data = {}

    for i in range(len(tx.outputs)):
        data['output_'+str(i)] = str(tx.outputs[i].address.type)

    total_false_positive_funding_output_types.append(data)

out_file = open('./analysis/total_matching_funding_output_types', 'w')
json.dump(total_matching_funding_output_types, out_file)

out_file = open('./analysis/total_false_positive_funding_output_types', 'w')
json.dump(total_false_positive_funding_output_types, out_file)