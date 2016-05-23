import time
import requests
import argparse
import json

def parse_client_nodes(sim_config_path, deploy_env):
    """For now, we will only use the first node in the cluster to initiate the requests
    """
    client_urls = list()
    with open(sim_config_path, 'r') as sim_config:
        config = json.load(sim_config)
        client_node_ids = config['clients']
        nodes = config['nodes']

        for node in nodes:
            node_id = node['id']
            if node_id in client_node_ids:
                for uri in node['uris']:
                    port = node['port']
                    hostname = node_id + '-0' + '.marathon.mesos'
                    if deploy_env == 'compose':
                        hostname = node_id
                    client_urls.append('http://' +  node_id + ':' + str(port) + uri)
    return client_urls

def run(latency, config, deploy_env):
    client_urls = parse_client_nodes(config, deploy_env)
    print client_urls
    # Start the client
    while True:
        for url in client_urls:
            time.sleep(float(latency))
            try:
                requests.get(url)
            except requests.ConnectionError:
                print "Got a connection error"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--latency', default='1.0', help="Specify the latency of requests")
    parser.add_argument('-c', '--config', default='', help='Servicesim config')
    parser.add_argument('-d', '--deploy_env', default='marathon', help='The deploy environment')

    args = parser.parse_args()

    run(args.latency, args.config, args.deploy_env)

