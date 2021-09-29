import json

from os import listdir
from os.path import isfile, join

base_path = '../../../go/dev/alice/'
stats_path = 'stats/'
merged_path = 'merged/'

# load file names of graph backups
graph_file_names = [f for f in listdir(base_path+merged_path) if isfile(join(base_path+merged_path, f))]

channel_time_series = {}

for graph_file_name in graph_file_names:

    print('analyzing '+graph_file_name+' ...')

    timestamp = graph_file_name[13:]

    graph = json.load(open(base_path+merged_path+graph_file_name))

    for channel in graph:
        try:
            channel_time_series[channel["channel_id"]]
        except KeyError as e:
            channel_time_series[channel["channel_id"]] = []

        channel_time_series[channel["channel_id"]].append(timestamp)

out_file = open(base_path+stats_path+'channel_stats', 'w')
json.dump(channel_time_series, out_file)

aggregated_channel_stats = []

for channel in channel_time_series:
    timestamps = [int(x) for x in channel_time_series[channel]]

    from_unixtime = min(timestamps)
    to_unixtime = max(timestamps)

    aggregated_channel_stats.append({'channel_id': channel, 'from': from_unixtime, 'to': to_unixtime})

out_file = open(base_path+stats_path+'aggregated_channel_stats', 'w')
json.dump(aggregated_channel_stats, out_file)