
import json

# load data from file
# in_file = open('../../../go/dev/alice/graph')
# data = json.load(in_file)
#
# print('Graph consists of '+str(len(data["nodes"]))+ ' nodes spawning '+str(len(data["edges"]))+ ' channels')
#
# edges = data["edges"]
# nodes = data["nodes"]
#
# nodeCount = []



# merge edges and nodes and export to file
# mergedEdges = data["edges"].copy()
#
# for edge in mergedEdges:
#     for node in nodes:
#         if node["pub_key"] == edge["node1_pub"]:
#             edge["node1_pub"] = node.copy()
#
#         if node["pub_key"] == edge["node2_pub"]:
#             edge["node2_pub"] = node.copy()
#
#         nodeCount.append({"pub_key": node["pub_key"], "count": 0})
#
#
# out_file = open('../../../go/dev/alice/mergedEdges', 'w')
# json.dump(mergedEdges, out_file)



# count channels per node
# for edge in edges:
#     incrementedNode1 = False
#     incrementedNode2 = False
#
#     for node in nodeCount:
#         if node["pub_key"] == edge["node1_pub"]:
#             node["count"] += 1
#             incrementedNode1 = True
#
#         if node["pub_key"] == edge["node2_pub"]:
#             node["count"] += 1
#             incrementedNode2 = True
#
#     if not incrementedNode1:
#         nodeCount.append({"pub_key": edge["node1_pub"], "count": 0})
#
#     if not incrementedNode1:
#         nodeCount.append({"pub_key": edge["node1_pub"], "count": 0})
#
# out_file = open('../../../go/dev/alice/nodeCount', 'w')
# json.dump(nodeCount, out_file)