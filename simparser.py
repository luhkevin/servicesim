import os
import json
from pprint import pprint

def tuple_to_str(tuple, delimiter):
    return str(tuple[0]) + ':' + str(tuple[1])

# Transforms "servicesim.json" and the inventory file into "smap" -- servicemap.json
def route_parser(servicesim_config, inventory, default_port):
    """
    The <inventory> is an ansible inventory file
    The inv_table is a hashmap (dict) of <node_id, [(ip_addr,port), ...]>
    Port will probably just be hardcoded/defaulted to 8080 or something
    """
    default_port = str(default_port)
    servicemap = list()
    inv_table = dict()
    with open(inventory, 'r') as inv_file:
        # Skip the "[servers]" heading
        inv_file.readline()
        for line in inv_file:
            line = line.strip()
            line_toks = line.split(' ')
            node_addr, port, label = line_toks[0], line_toks[1], line_toks[2]
            node_port = port.split('=')[1]
            node_id = label.split('=')[1].split(':')[1]
            if node_id not in inv_table:
                inv_table[node_id] = list()
            inv_table[node_id].append((node_addr,node_port))

        pprint(inv_table)

    with open(servicesim_config, 'r') as sim_config:
        sim_config = json.load(sim_config)
        nodes = sim_config['nodes']
        links = sim_config['links']

        # This is a hashmap of <node_id, node>, where the node is just an object in the 'nodes' array in servicesim.json
        node_table = dict()
        for node in nodes:
            node_id = node['id']
            node_table[node_id] = node

        # This is one element of the "servicemap" list
        for node_id, ipaddrs in inv_table.items():
            node_servicemap = dict()
            node_servicemap['id'] = node_id
            node_servicemap['srcs'] = [str(tup[0]) + ':' + str(tup[1]) for tup in inv_table[node_id]]
            node_servicemap['next_hops'] = list()
            for link in links:
                print "node_id is: ", node_id, "LINK IS: ", link
                hop = dict()
                if node_id == link['src']:
                    dest_node_id = link['dest']
                    hop['id'] = link['dest']
                    hop['dests'] = [str(tup[0]) + ':' + str(tup[1]) for tup in inv_table[dest_node_id]]
                    hop['uris'] = node_table[dest_node_id]['uris']
                    node_servicemap['next_hops'].append(hop)
                    servicemap.append(node_servicemap)

    # Do some json tranformations
    pprint(servicemap)
    return servicemap
