import os
import json
from pprint import pprint

def tuple_to_str(tuple, delimiter):
    return str(tuple[0]) + ':' + str(tuple[1])

# Transforms "servicesim.json" and the inventory file into "smap" -- servicemap.json
def route_parser(servicesim_config, inventory, default_port):
    """
    The <inventory> is an ansible inventory file
    The inv_table is a hashmap (dict) of <node_id, ["ip_addr:port", ...]>
    Port will probably just be hardcoded/defaulted to 8080 or something
    """
    default_port = str(default_port)
    servicemap = list()
    inv_table = dict()
    client_nodes = list()
    with open(inventory, 'r') as inv_file:
        # Skip the "[servers]" heading
        inv_file.readline()
        for line in inv_file:
            tags = dict()
            line = line.strip()
            line_toks = line.split()
            node_addr, tag_toks = line_toks[0], line_toks[1:]
            print "TAG TOKS: ", str(tag_toks)
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
        client_node_ids = sim_config['clients']
        nodes = sim_config['nodes']
        links = sim_config['links']

        # Update inv_table with containers
        # Container addresses (e.g. hosts) are hardcoded to node_id.marathon.mesos (assume we use Mesos-DNS)
        # Container ports are hardcoded to 31000 + n, where n is a number in the node id "node-c-n"
        for node in nodes:
            node_id = node['id']
            if '-' in node_id:
                print "NODE IS: ", node_id
                index = int(node_id.split('-')[2])
                if node_id not in inv_table:
                    inv_table[node_id] = list()
                inv_table[node_id].append(node_id + '.marathon.mesos' + ':' + str(31000 + index))

        pprint(inv_table)

        # This is a hashmap of <node_id, node>, where the node is just an object in the 'nodes' array in servicesim.json
        node_table = dict()
        for node in nodes:
            node_id = node['id']
            node_table[node_id] = node

        # This is one element of the "servicemap" list
        for node_id, ipaddrs in inv_table.items():
            node_servicemap = dict()
            node_servicemap['id'] = node_id
            node_servicemap['srcs'] = inv_table[node_id]
            node_servicemap['next_hops'] = list()
            for link in links:
                hop = dict()
                if node_id == link['src']:
                    dest_node_id = link['dest']
                    hop['id'] = link['dest']
                    hop['dests'] = inv_table[dest_node_id]
                    hop['uris'] = node_table[dest_node_id]['uris']
                    node_servicemap['next_hops'].append(hop)
                    servicemap.append(node_servicemap)

    # Do some json tranformations
    pprint(servicemap)
    return servicemap, inv_table, client_node_ids, node_table

if __name__ == '__main__':
    route_parser('/tmp/servicesim-config-docker.json', '/tmp/servicesim-inv', '8000')
