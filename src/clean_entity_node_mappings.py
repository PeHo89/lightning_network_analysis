import json

data = json.load(open('../../../go/dev/alice/channels/entity_node_mapping'))
#data = [{'entity': 'a', 'node': [1,2,3]}, {'entity': 'b', 'node': [1,2]}, {'entity': 'c', 'node': [1]}]

print(str(len(data))+' entities before re-mapping')

safely_mappings = []
node_helper = []
to_be_mapped = []

for mapping in data:
    if len(mapping['node']) == 1:
        safely_mappings.append(mapping)
        node_helper.append(mapping['node'][0])
    elif len(mapping['node']) > 1:
        to_be_mapped.append(mapping)

print(str(len(safely_mappings))+' safely mapped entities before cross-checking')

re_mapped = True
re_map_count = 0

while re_mapped:
    re_mapped = False

    for mapping in to_be_mapped:

        new_node_mapping = []

        for node in mapping['node']:
            if not node in node_helper:
                new_node_mapping.append(node)

        if len(new_node_mapping) == 1:
            safely_mappings.append({'entity': mapping['entity'], 'node': new_node_mapping})
            node_helper.append(new_node_mapping[0])
            mapping['node'] = []
            re_mapped = True
            re_map_count += 1
        else:
            mapping['node'] = new_node_mapping


print(str(len(safely_mappings))+' safely mapped entities after cross-checking')

out_file = open('../../../go/dev/alice/channels/safely_mapped_entity_node_mapping', 'w')
json.dump(safely_mappings, out_file)