import json

from os import listdir
from os.path import isfile, join

base_path = '../../../go/dev/alice/'
graph_path = 'graph_backup/'
merged_path = 'merged/'

merge_specific = False #set to True in order to take timestamps into consideration
timestamp_from = 1576238400 #block height 607,935 #13.12.2019 - 13:00:00
timestamp_to = 1576540800 #block height 608,434 #17.12.2019 - 01:00:00

# load file names of graph backups
graph_file_names = [f for f in listdir(base_path+graph_path) if isfile(join(base_path+graph_path, f))]
graph_file_names.remove('.info')

for graph_file_name in graph_file_names:

    timestamp = int(graph_file_name[6:])

    #only merge graphs within a certain block range
    if merge_specific and (timestamp < timestamp_from or timestamp > timestamp_to):
        continue

    print('merging '+graph_file_name+' ...')

    graph = json.load(open(base_path+graph_path+graph_file_name))

    nodes = {}

    for node in graph["nodes"]:
        nodes[node["pub_key"]] = node

    edges = graph["edges"]

    for edge in edges:
        edge["node1_pub"] = nodes[edge["node1_pub"]]
        edge["node2_pub"] = nodes[edge["node2_pub"]]

    out_file = open(base_path+merged_path+'merged_'+graph_file_name, 'w')
    json.dump(edges, out_file)