import os
import json
from pprint import pprint

def tuple_to_str(tuple, delimiter):
    return str(tuple[0]) + ':' + str(tuple[1])

def fill_attr_table(node, node_id, attributes):
    node_attr= dict()
    if 'latency' in node:
        node_attr['latency'] = node['latency']
    if 'status' in node:
        node_attr['status'] = node['status']
    attributes[node_id] = node_attr

# Transforms "servicesim.json" and the inventory file into "smap" -- servicemap.json
def route_parser(servicesim_config, inventory=None, deploy_env='marathon'):
    """
    The <inventory> is an ansible inventory file

    Returns:
        **servicemap** -- A list of each node's servicemaps.
        Each element in the servicemap is a dict that consists of the mappings:
            <'id', node_id>
            <'next_hops', list of next hops>
            <'port', node host port>
            <'lbport', node load balancer port>

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
        # Update other attributes too -- latency and status code
        node_table = dict()
        attributes = dict()
        for node in nodes:
            node_attr = dict()
            node_id = node['id']

            if '-' in node_id:
                count = node['count']
                for i in range(int(count)):
                    # A 'cnode_id' is a container node id
                    cnode_id = node_id + '-' + str(i)
                    if cnode_id not in inv_table:
                        inv_table[cnode_id] = list()

                    hostname = ''
                    port = int(node['port'])
                    if deploy_env == 'marathon':
                        hostname = 'dev-' + cnode_id + '.marathon.mesos'
                    inv_table[cnode_id].append(hostname + ':' + str(port))
                    node_table[cnode_id] = node
                    fill_attr_table(node, cnode_id, attributes)
            else:
                node_table[node_id] = node
                fill_attr_table(node, node_id, attributes)

        print "Inventory table: "
        pprint(inv_table)
        # Create the servicemap structure
        # This is one element of the "servicemap" list
        for node_id, ipaddrs in inv_table.items():
            route = dict()
            route['id'] = node_id
            route['attr'] = attributes[node_id]
            route['next_hops'] = list()
            route['port'] = node_table[node_id]['port']

            # Fill routing table with lbport
            if node_table[node_id].has_key('lbport'):
                route['lbport'] = node_table[node_id]['lbport']

            for link in links:
                node_id_prefix = node_id.rpartition('-')[0]
                if node_id_prefix == link['src']:
                    # Check for multiple dests in a link entry
                    dests = link['dest'].split(',')
                    for dest_node_id in dests:
                        # Resolve load-balancer routing
                        if link.has_key('lb') and link['lb'] == 'true':
                            hop = dict()
                            hop['id'] = dest_node_id
                            hop['uris'] = node_table[dest_node_id + '-0']['uris']

                            # Get load-balancer port from node
                            lbport = node_table[dest_node_id + '-0']['lbport']
                            if deploy_env == 'marathon':
                                hop['dest'] = 'marathon-lb.marathon.mesos' + ':' + str(lbport)
                            route['next_hops'].append(hop)
                        else:
                            count = node_table[dest_node_id + '-0']['count']
                            for i in range(int(count)):
                                hop = dict()
                                dest_cnode_id = dest_node_id + '-' + str(i)
                                hop['id'] = dest_cnode_id
                                hop['dest'] = inv_table[dest_cnode_id]
                                hop['uris'] = node_table[dest_cnode_id]['uris']
                                route['next_hops'].append(hop)
            servicemap.append(route)

        print "Servicemap: "
        pprint(servicemap)
    return servicemap, inv_table, client_node_table

if __name__ == '__main__':
    route_parser('/tmp/servicesim-config-docker.json', '/tmp/servicesim-inv', '8000')
