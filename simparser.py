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

def get_root_id(node_id):
    """If the node_id has a "-", which denotes a container id, then return the partition without the "-".
    Otherwise, return node_id
    """
    if '-' in node_id:
        return node_id.rpartition('-')[0]
    else:
        return node_id

def get_full_id(node_id, runtime='container', index=-1):
    """If the node_id has a "-", then return "<node_id>-0". Otherwise, return node_id"""
    if index == -1:
        index = 0

    if runtime == 'container':
        return node_id + '-' + str(index)
    else:
        return node_id

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
            --------

            optional:
            <'lbport', node load balancer port>
            <'deploy', deploy type>
            <'function', node function>

        Each element in the list of next hops has the form:
        {
            'dests': [host:port, ..],
            'id': 'node-id',
            'uris': ['/endpoint1', ...]
        }

        If the next-hop is reached via load-balancer, then the 'id' field will contain the general/root node id
        E.g. 'alpha-c'. This is opposed to the container node id, e.g. 'alpha-c-0'

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
	global_config = sim_config['global-config']

	runtime = global_config['runtime']

        # Update node data from servicesim.json
        node_table = dict()
        attributes = dict()
        for node in nodes:
            node_attr = dict()
            node_id = node['id']
            port = node.get('port', 8000)
	    if runtime == 'container':
                count = node['count']
                for i in range(int(count)):
                    # A 'cnode_id' is a container node id
                    cnode_id = node_id + '-' + str(i)
                    if cnode_id not in inv_table:
                        inv_table[cnode_id] = list()

                    hostname = ''
                    if deploy_env == 'marathon':
                        hostname = cnode_id + '.marathon.mesos'
                    elif deploy_env == 'compose':
                        hostname = cnode_id

                    inv_table[cnode_id].append(hostname + ':' + str(port))
                    node_table[cnode_id] = node
                    fill_attr_table(node, cnode_id, attributes)
            else:
                node_table[node_id] = node
                if node_id not in inv_table:
                    inv_table[node_id] = list()

                hostname = 'localhost'
                if deploy_env == 'compose':
                    hostname = node_id

                inv_table[node_id].append(hostname + ':' + str(port))
                fill_attr_table(node, node_id, attributes)

        print "Node table: "
        pprint(node_table)

        print "Inventory table: "
        pprint(inv_table)
        # Create the servicemap structure
        # This is one element of the "servicemap" list
        for node_id, ipaddrs in inv_table.items():
            route = dict()
            route['id'] = node_id
            route['attr'] = attributes[node_id]
            route['next_hops'] = list()

            # TODO: These can be refactored into a function
            # Resolve ports
            if node_table[node_id].has_key('port'):
                route['port'] = node_table[node_id]['port']

            # Resolve manual or automatic deploy
            if node_table[node_id].has_key('deploy-type'):
                route['deploy-type'] = node_table[node_id]['deploy-type']

            # Resolve node function
            if node_table[node_id].has_key('function'):
                route['function'] = node_table[node_id]['function']

            # Fill routing table with lbport
            if node_table[node_id].has_key('lbport'):
                route['lbport'] = node_table[node_id]['lbport']

            for link in links:
                root_node_id = get_root_id(node_id)
                if root_node_id == link['src']:
                    # Check for multiple dests in a link entry
                    dests = link['dest'].split(',')
                    for dest_node_id in dests:
                        dest_true_id = get_full_id(dest_node_id, runtime)
                        if link.has_key('lb') and link['lb'] == 'true':
                            # Resolve load-balancer routing
                            hop = dict()
                            hop['id'] = dest_node_id
                            hop['uris'] = node_table[dest_true_id]['uris']

                            # Get load-balancer port from node
                            lbport = node_table[dest_true_id]['lbport']
                            if deploy_env == 'marathon':
                                hop['dests'] = ['marathon-lb.marathon.mesos' + ':' + str(lbport)]
                            route['next_hops'].append(hop)
                        else:
                            # TODO: Refactor this whole part where we check for count...we should check for it before this
                            count = 1
                            if 'count' in node_table[dest_true_id]:
                                count = node_table[dest_true_id]['count']

                            for i in range(int(count)):
                                hop = dict()
                                dest_true_id = get_full_id(dest_node_id, runtime, str(i))
                                hop['id'] = dest_true_id
                                hop['dests'] = inv_table[dest_true_id]
                                hop['uris'] = node_table[dest_true_id]['uris']
                                route['next_hops'].append(hop)

                    # Overwrite the uris in the routing table, if necessary
                    if 'function' in route:
                        faulty_uri = list()
                        # Resolve faulty routes
                        if route['function'] == 'faulty404':
                            faulty_uri = ['/goblin/faulty']
                        elif route['function'] == 'faulty500':
                            faulty_uri = ['/gremlin']
                        else:
                            print "Node function not supported."
                        for hop in route['next_hops']:
                            hop['uris'] = faulty_uri

            servicemap.append(route)

        print "Servicemap: "
        pprint(servicemap)
    return servicemap, inv_table, client_node_table

if __name__ == '__main__':
    route_parser('/tmp/servicesim-config-docker.json', '/tmp/servicesim-inv', '8000')
