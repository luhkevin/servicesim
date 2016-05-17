#!/usr/bin/python
import time
import treq
from klein import Klein
from twisted.internet.defer import inlineCallbacks, returnValue
from simnode import Simnode
import argparse
import json
import logging
from pprint import pprint

app = Klein()
node = None
config = ''
inventory = ''

# Controller-node endpoints
@app.route('/setstat/<stat_type>/<node_id>/<stat>')
def setstat(request, stat_type, node_id, stat):
    """This endpoint is called by the controller node and sets the attributes or stats
    for a non-controller (main) servicesim node. It includes things like the response code
    or the latency.
    """
    dests = node.inv_table[node_id]
    for dest in dests:
        url = 'http://' + dest + '/' + str(stat_type) + '/' + stat
        d = treq.post(url)
        d.addCallback(node.ack_response)

@app.route('/start/<client_node_id>')
def start(request, client_node_id):
    """This endpoint starts servicesim by starting the traffic on all the client nodes.
    Client nodes are main servicesim nodes that are chosen to initiate the traffic.
    They exist so the traffic doesn't all come from the controller node.
    """
    client_node_ids = node.client_node_ids
    inv_table = node.inv_table
    node_table = node.node_table
    print "Clients are: "
    pprint(client_node_ids)
    for cid in client_node_ids:
        if client_node_id == cid or client_node_id == 'all':
            client_nodes = inv_table[cid]
            for client in client_nodes:
                for client_uri in node_table[cid]['uris']:
                    url = 'http://' + client + client_uri
                    d = treq.get(url, persistent=False)
                    d.addCallback(node.ack_response)

@app.route('/setup_nodes/<node_id>', methods = ['POST'])
def setup_nodes(request, node_id):
    """The 'setup_nodes' endpoint is called by the controller node and
    sets up the attributes for all the main nodes
    """
    servicemap = node.servicemap
    print "Servicemap is: "
    pprint(servicemap)
    if node_id == 'all' or node_id in node.inv_table.keys():
        for route in servicemap:
            node_id = route['id']
            addresses = node.inv_table[node_id]
            for addr in addresses:
                # Do the initial setup
                url = 'http://' + addr + '/setup'
                node_routes_json = json.dumps(route['next_hops'])
                print "NODE ROUTES JSON: ", str(node_routes_json)
                d = treq.post(url, data=node_routes_json)
                d.addCallback(node.ack_response)

                # Set attributes
                attributes = route['attr']
                for stat_key, stat_val in attributes.iteritems():
                    attr_url = 'http://' + addr + '/' + str(stat_key) + '/' + str(stat_val)
                    d = treq.post(attr_url)
                    d.addCallback(node.ack_response)
        # TODO: Logic is a bit broken here because if we're only setting up one node_id, we still iterate through the entire list
        return "OK"
    else:
        print "Skipping non-matched URL."

# Main, non-controller node endpoints
@app.route('/info', methods = ['GET'])
def info(request):
    return str(node.infotable)

@app.route('/status/<status>', methods = ['GET', 'POST'])
def status(request, status):
    node.set_stat({'type': 'status', 'status': int(status)})
    return "Status code set to " + str(status)

@app.route('/latency/<latency>', methods = ['GET', 'POST'])
def latency(request, latency):
    node.set_stat({'type': 'latency', 'latency': float(latency)})
    return "OK"

@app.route('/echo')
def echo(request):
    return node.node_id + '\n'

@app.route('/setup', methods = ['GET', 'POST'])
def setup(request):
    """This endpoint is called by the controller node to setup all the routes (e.g. next hops) and attributes
    of a main node.
    """
    print "SETUP ENDPOINT"
    routes = None
    if request.method == 'POST':
        content = request.content.read()
        routes = json.loads(content)
        print "ROUTES ARE: ", str(routes)
        node.routes = routes
        return "OK"
    else:
        print "Not a POST request."

@app.route('/gremlin', methods = ['GET', 'POST'])
def gremlin(request, node_id):
    """This endpoint throws a 500 error.
    """
    raise Exception("This endpoint is faulty!")

# "main_endpoint" tells a node to make requests to all of the nodes in its routing table
@app.route('/<node_id>', methods = ['GET', 'POST'])
def main_endpoint(request, node_id):
    """This is the main endpoint called by the main servicesim nodes to propagate all the requests.
    The route is a catch-all, and can accept any URI.
    """
    status = node.infotable['status']
# TODO: If status code = 500, should we exit or raise an exception here?
    request.setResponseCode(status)

    latency = node.infotable['latency']
    if latency > 0:
        time.sleep(latency)

    node.make_requests()

    return node.node_id

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--nodetype', nargs='?', help="Specify the type of node")
    parser.add_argument('-a', '--address', default='localhost', help="Specify the address the node will run on")
    parser.add_argument('-p', '--port', nargs='?', help="Specify the port the node will listen on")

    parser.add_argument('-c', '--config', default='', help="The config file. Only for the controller node")
    parser.add_argument('-i', '--inventory', default='', help="The inventory file")
    parser.add_argument('-d', '--default_port', default='8080', help="The default port for each non-controller servicesim node")
    parser.add_argument('-f', '--node_function', default='regular', help="The function of the node")

    args = parser.parse_args()

    address = str(args.address)
    port = int(args.port)
    config = args.config
    inventory = args.inventory
    default_port = args.default_port
    node_type = args.node_type

    node = Simnode(args.nodetype, config, inventory)
    app.run(address, port)

'''
routes:
/<node-id>
/<node-id>/status/<http status code>
/<node-id>/latency</latency>
/<node-id>/info

/<node-id>/text/<text payload>
/<node-id>/file/<absolute or relative file payload> ... We should also be able to POST files to a certain location on the filesystem and retrieve that file with GET
/<node-id>/method/<custom simnode method to call>/<csv-separated args>

NOTE: Should probably set limits on these...cpu, mem, I/O, and disk space to 75% max
/<node-id>/cpu/<cpu percentage> ... can probably use this: http://people.seas.harvard.edu/~apw/stress/
/<node-id>/mem/<memory percentage>
/<node-id>/IO/<io percentage>
/<node-id>/disk/<disk percentage>
'''

#@app.route('/cpu', methods = ['GET'])
#@app.route('/mem', methods = ['GET', 'POST'])
#@app.route('/io', methods = ['GET', 'POST'])
#@app.route('/disk', methods=['GET'])
