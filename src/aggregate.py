import json

from os import listdir
from os.path import isfile, join

base_path = '../../../go/dev/alice/'
aggregated_path = 'aggregated/'
graph_path = 'graph_backup/'

# load file names of graph backups
graph_file_names = [f for f in listdir(base_path + graph_path) if isfile(join(base_path + graph_path, f))]

aggregated = {}

for graph_file_name in graph_file_names:

    print('aggregate '+graph_file_name+' ...')

    graph = json.load(open(base_path+graph_path+graph_file_name))['channels']

    for channel in graph:

        try:
            aggregated[channel["channel_id"]]
        except KeyError as e:
            aggregated[channel["channel_id"]] = channel

        if len(channel) > len(aggregated[channel["channel_id"]]):
            aggregated[channel["channel_id"]] = channel

result = []

for key in aggregated:
    result.append(aggregated[key])

out_file = open(base_path + aggregated_path + 'aggregated_channels', 'w')
json.dump(result, out_file)