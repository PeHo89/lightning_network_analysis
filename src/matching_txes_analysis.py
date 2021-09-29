import json

base_path = '../../../go/dev/alice/'
result_path = 'result/'

total_matching_txes = json.load(open(base_path + result_path + 'total_matching_txes'))
uncooperative_matching_txes = json.load(open(base_path + result_path + 'uncooperative_matching_txes'))

print('total matching transactions: ' + str(len(total_matching_txes)))
print('uncooperative matching transactions: ' + str(len(uncooperative_matching_txes)))
print('---')

capacities = []
block_durations = []

for matching_tx in total_matching_txes:
    capacities.append(int(matching_tx['off_chain_data']['capacity']))
    block_durations.append(matching_tx['on_chain_data']['block_height_closing_tx']-matching_tx['on_chain_data']['block_height_funding_tx'])

for matching_tx in uncooperative_matching_txes:
    capacities.append(int(matching_tx['off_chain_data']['capacity']))
    block_durations.append(matching_tx['on_chain_data']['block_height_closing_tx']-matching_tx['on_chain_data']['block_height_funding_tx'])

capacities.sort()
block_durations.sort()

capacities_average = sum(capacities)/len(capacities)
block_duration_average = sum(block_durations)/len(block_durations)

capacities_median = (capacities[(len(capacities)//2)]+capacities[~(len(capacities)//2)])/2
block_duration_median = (block_durations[(len(block_durations)//2)]+block_durations[~(len(block_durations)//2)])/2

print('capacities average is: '+str(capacities_average)+' satoshi ('+str(capacities_average/100000000)+' BTC)')
print('block duration average is: '+str(block_duration_average)+' blocks ('+ str(block_duration_average*10/60/24) +' days)')
print('---')
print('capacities median is: '+str(capacities_median)+' satoshi ('+str(capacities_median/100000000)+' BTC)')
print('block duration median is: '+str(block_duration_median)+' blocks ('+ str(block_duration_median*10/60/24) +' days)')