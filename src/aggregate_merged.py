import json

from os import listdir
from os.path import isfile, join

base_path = '../../../go/dev/alice/'
aggregated_path = 'aggregated/'
merged_path = 'merged/'

# load file names of graph backups
merged_graph_file_names = [f for f in listdir(base_path + merged_path) if isfile(join(base_path + merged_path, f))]

aggregated = []

for graph_file_name in merged_graph_file_names:

    print('aggregate '+graph_file_name+' ...')

    graph = json.load(open(base_path+merged_path+graph_file_name))

    for channel in graph:

        found = False

        for chan in aggregated:
            if channel['channel_id'] == chan['channel_id']:
                found = True

                if len(channel) > len(chan):
                    chan = channel

                break

        if not found:
            aggregated.append(channel)

out_file = open(base_path + aggregated_path + 'aggregated_channels', 'w')
json.dump(aggregated, out_file)