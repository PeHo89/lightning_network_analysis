import os
import json
import requests

from dotenv import load_dotenv
load_dotenv()

data_dir = '../../../data/'
graph_sense_addr = 'http://192.168.243.2:9000'

if __name__ == '__main__':
    channels = json.load(open(data_dir+'channels'))

    body = {'username': os.environ.get('GRAPHSENSE_USER'), 'password': os.environ.get('GRAPHSENSE_PASSWORD')}

    response = requests.post(url = graph_sense_addr+'/login', json=body)
    jwt = response.json()['Authorization']

    header = {'Content-Type': 'application/json', 'Authorization': jwt}

    for channel in channels:
        funding_tx = channel['chan_point'].split(':')[0]
        output_idx = int(channel['chan_point'].split(':')[1])

        response = requests.get(url = graph_sense_addr+'/btc/txs/[TX_HASH]'.replace('[TX_HASH]', funding_tx), headers=header)

        if not response.status_code == 404 and not response.status_code == 500:
            data = response.json()

            # load input addresses of funding transaction
            channel['input_addresses'] = [input['address'] for input in data['inputs']]

            channel['input_entities'] = []

            # load entities to all input addresses
            for input_addr in channel['input_addresses']:
                response = requests.get(url = graph_sense_addr+'/btc/addresses/[ADDR]/entity'.replace('[ADDR]', input_addr), headers=header)

                if not response.status_code == 404 and not response.status_code == 500:
                    dat = response.json()

                    if dat['entity'] > 0 and not dat['entity'] in channel['input_entities']:
                        channel['input_entities'].append(dat['entity'])

            multisig_addr = data['outputs'][output_idx]['address']

            response = requests.get(url = graph_sense_addr+'/btc/addresses/[ADDR]/txs'.replace('[ADDR]', multisig_addr), headers=header)

            if not response.status_code == 404 and not response.status_code == 500:
                dat = response.json()

                # if there is a settlement transaction, then channel is already closed
                if len(dat['address_txs']) == 1:

                    settlement_tx = dat['address_txs'][0]['tx_hash']

                    response = requests.get(url = graph_sense_addr+'/btc/txs/[TX_HASH]'.replace('[TX_HASH]', settlement_tx), headers=header)

                    if not response.status_code == 404 and not response.status_code == 500:
                        da = response.json()

                        # load output addresses of settlement transaction
                        channel['output_addresses'] = [input['address'] for input in da['outputs']]

                        channel['output_entities'] = []

                        # load entities to all output addresses
                        for output_addr in channel['output_addresses']:
                            response = requests.get(url = graph_sense_addr+'/btc/addresses/[ADDR]/entity'.replace('[ADDR]', output_addr), headers=header)

                            if not response.status_code == 404 and not response.status_code == 500:
                                d = response.json()

                                if d['entity'] > 0 and not d['entity'] in channel['output_entities']:
                                    channel['output_entities'].append(d['entity'])

    out_file = open(data_dir + 'enriched_channels', 'w')
    json.dump(channels, out_file)