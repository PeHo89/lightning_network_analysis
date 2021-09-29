import json

data_dir = '../../../data/'

if __name__ == '__main__':
    entity_channel_mapping = json.load(open(data_dir+'entities_mapped_to_channels'))

    input_entity_node_mapping = {}
    output_entity_node_mapping = {}
    input_output_entity_node_mapping = {}

    for entity in entity_channel_mapping['input_entity'].keys():
        node_count = {}

        for channel in entity_channel_mapping['input_entity'][entity]:
            try:
                node_count[channel['node1_pub']] += 1
            except KeyError as e:
                node_count[channel['node1_pub']] = 1

            try:
                node_count[channel['node2_pub']] += 1
            except KeyError as e:
                node_count[channel['node2_pub']] = 1

        node_count = {k: node_count[k] for k in sorted(node_count, key=node_count.get, reverse=True)}

        if node_count[list(node_count.keys())[0]] > node_count[list(node_count.keys())[1]]:
            input_entity_node_mapping[entity] = [{'node': list(node_count.keys())[0], 'node_channel_count': node_count[list(node_count.keys())[0]], 'total_channel_count': len(entity_channel_mapping['input_entity'][entity])}]

        elif node_count[list(node_count.keys())[0]] == node_count[list(node_count.keys())[1]]:
            input_entity_node_mapping[entity] = []

            for node in node_count.keys():
                if node_count[node] >= node_count[list(node_count.keys())[0]]:
                    input_entity_node_mapping[entity].append({'node': node, 'node_channel_count': node_count[node], 'total_channel_count': len(entity_channel_mapping['input_entity'][entity])})

    for entity in entity_channel_mapping['output_entity'].keys():
        node_count = {}

        for channel in entity_channel_mapping['output_entity'][entity]:
            try:
                node_count[channel['node1_pub']] += 1
            except KeyError as e:
                node_count[channel['node1_pub']] = 1

            try:
                node_count[channel['node2_pub']] += 1
            except KeyError as e:
                node_count[channel['node2_pub']] = 1

        node_count = {k: node_count[k] for k in sorted(node_count, key=node_count.get, reverse=True)}

        if node_count[list(node_count.keys())[0]] > node_count[list(node_count.keys())[1]]:
            output_entity_node_mapping[entity] = [{'node': list(node_count.keys())[0], 'node_channel_count': node_count[list(node_count.keys())[0]], 'total_channel_count': len(entity_channel_mapping['output_entity'][entity])}]

        elif node_count[list(node_count.keys())[0]] == node_count[list(node_count.keys())[1]]:
            output_entity_node_mapping[entity] = []

            for node in node_count.keys():
                if node_count[node] >= node_count[list(node_count.keys())[0]]:
                    output_entity_node_mapping[entity].append({'node': node, 'node_channel_count': node_count[node], 'total_channel_count': len(entity_channel_mapping['output_entity'][entity])})

    for entity in entity_channel_mapping['input_output_entity'].keys():
        node_count = {}

        for channel in entity_channel_mapping['input_output_entity'][entity]:
            try:
                node_count[channel['node1_pub']] += 1
            except KeyError as e:
                node_count[channel['node1_pub']] = 1

            try:
                node_count[channel['node2_pub']] += 1
            except KeyError as e:
                node_count[channel['node2_pub']] = 1

        node_count = {k: node_count[k] for k in sorted(node_count, key=node_count.get, reverse=True)}

        if node_count[list(node_count.keys())[0]] > node_count[list(node_count.keys())[1]]:
            input_output_entity_node_mapping[entity] = [{'node': list(node_count.keys())[0], 'node_channel_count': node_count[list(node_count.keys())[0]], 'total_channel_count': len(entity_channel_mapping['input_output_entity'][entity])}]

        elif node_count[list(node_count.keys())[0]] == node_count[list(node_count.keys())[1]]:
            input_output_entity_node_mapping[entity] = []

            for node in node_count.keys():
                if node_count[node] >= node_count[list(node_count.keys())[0]]:
                    input_output_entity_node_mapping[entity].append({'node': node, 'node_channel_count': node_count[node], 'total_channel_count': len(entity_channel_mapping['input_output_entity'][entity])})

    data = {'input_entity': input_entity_node_mapping, 'output_entity' : output_entity_node_mapping, 'input_output_entity': input_output_entity_node_mapping}

    out_file = open(data_dir+'entities_mapped_to_nodes', 'w')
    json.dump(data, out_file)

    entity_node_mapping = []

    for entity in input_output_entity_node_mapping.keys():
        entity_node_mapping.append({'entity': entity, 'node': input_output_entity_node_mapping[entity]})

    out_file = open(data_dir+'entities_mapped_to_nodes_simplified', 'w')
    json.dump(entity_node_mapping, out_file)