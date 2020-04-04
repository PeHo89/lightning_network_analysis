import json

data_dir = '../../../data/'

if __name__ == '__main__':
    channels = json.load(open(data_dir+'enriched_channels'))

    input_entities = {}
    output_entities = {}
    input_output_entities = {}

    for channel in channels:

        try:
            for entity in channel['input_entities']:
                try:
                    input_entities[entity].append(channel)
                except KeyError as e:
                    input_entities[entity] = [channel]

                try:
                    input_output_entities[entity].append(channel)
                except KeyError as e:
                    input_output_entities[entity] = [channel]
        except KeyError as e:
            pass

        try:
            for entity in channel['output_entities']:
                try:
                    output_entities[entity].append(channel)
                except KeyError as e:
                    output_entities[entity] = [channel]

                try:
                    input_output_entities[entity].append(channel)
                except KeyError as e:
                    input_output_entities[entity] = [channel]
        except KeyError as e:
            pass

    data = {'input_entity': input_entities, 'output_entity' : output_entities, 'input_output_entity': input_output_entities}

    out_file = open(data_dir+'entities_mapped_to_channels', 'w')
    json.dump(data, out_file)