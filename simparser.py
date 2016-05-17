import os
import json
from pprint import pprint

def tuple_to_str(tuple, delimiter):
    return str(tuple[0]) + ':' + str(tuple[1])

# Transforms "servicesim.json" and the inventory file into "smap" -- servicemap.json
def route_parser(servicesim_config, inventory=None, deploy_env='marathon'):
    """
    The <inventory> is an ansible inventory file

    Returns:
        **servicemap** -- A list of each node's servicemaps.
        Each element in the servicemap is a dict that consists of the mappings:
            <'id', node_id>
            <'next_hops', list of next hops>

        **inv_table** -- A dict with the mapping:
            <node_id, node_addresses>
        where 'node_addresses' is ["host:port", ...]

        **client_node_table** -- This is a dict with the maping:
            <client_node_id, node>
        The 'node' value is just an object in the 'nodes' array in the servicesim.json config.
    """

    servicemap = list()
    inv_table = dict()
    client_nodes = list()

    # Only for non-container servicesims, where the hostname is an ip address instead of DNS
    if inventory:
        with open(inventory, 'r') as inv_file:
            # Skip the "[servers]" heading
            inv_file.readline()
            for line in inv_file:
                tags = dict()
                line = line.strip()
                line_toks = line.split()
                node_addr, tag_toks = line_toks[0], line_toks[1:]
                for tag in tag_toks:
                    tag_pair = tag.split('=')
                    tags[tag_pair[0]] = tag_pair[1]
                node_port = tags['port']
                node_id = tags['label'].split(':')[1]
                if node_id not in inv_table:
                    inv_table[node_id] = list()
                inv_table[node_id].append(str(tags['private_ip']) + ':' + str(node_port))

    with open(servicesim_config, 'r') as sim_config:
        sim_config = json.load(sim_config)
        client_node_table = sim_config['clients']
        nodes = sim_config['nodes']
        links = sim_config['links']

        # Update node data from servicesim.json
        # Container addresses (e.g. hosts) are hardcoded to node_id.marathon.mesos (assume we use Mesos-DNS)
        # Container ports are hardcoded to 31000 + n, where n is a number in the node id "node-c-n"
        # Update other attributes too -- latency and status code
        node_table = dict()
        attributes = dict()
        for node in nodes:
            node_attr = dict()
            node_id = node['id']
            node_table[node_id] = node

            if 'latency' in node:
                node_attr['latency'] = node['latency']
            if 'status' in node:
                node_attr['status'] = node ['status']
            attributes[node_id] = node_attr

            if '-' in node_id:
                index = int(node_id.split('-')[2])

                if node_id not in inv_table:
                    inv_table[node_id] = list()

                hostname = ''
                if deploy_env == 'marathon':
                    hostname = 'dev-' + node_id + '.marathon.mesos'
                inv_table[node_id].append(hostname + ':' + str(31000 + index))

        pprint(inv_table)
        # Create the servicemap structure
        # This is one element of the "servicemap" list
        for node_id, ipaddrs in inv_table.items():
            route = dict()
            route['id'] = node_id
            route['attr'] = attributes[node_id]
            route['next_hops'] = list()
            for link in links:
                hop = dict()
                if node_id == link['src']:
                    # Check for multiple dests in a link entry
                    dests = link['dest'].split(',')
                    for dest_node_id in dests:
                        hop['id'] = dest_node_id
                        hop['dests'] = inv_table[dest_node_id]
                        hop['uris'] = node_table[dest_node_id]['uris']
                        route['next_hops'].append(hop)
            servicemap.append(route)

        pprint(servicemap)
    return servicemap, inv_table, client_node_table

if __name__ == '__main__':
    route_parser('/tmp/servicesim-config-docker.json', '/tmp/servicesim-inv', '8000')
