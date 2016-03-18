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

def ack_response(resp):
    print "Controller received response"

# CONTROLLER NODE
@app.route('/setstat/<stat_type>/<node_id>/<stat>')
def setstat(request, stat_type, node_id, stat):
    dests = node.inv_table[node_id]
    for dest in dests:
        url = ''
        if stat_type == 'status':
            url = 'http://' + dest + '/status/' + stat
        elif stat_type == 'latency':
            url = 'http://' + dest + '/latency/' + stat
        d = treq.post(url)
        d.addCallback(ack_response)

@app.route('/start/<client_node_id>')
def start(request, client_node_id):
    client_node_ids = node.client_node_ids
    inv_table = node.inv_table
    node_table = node.node_table
    print "IN /start. clients are: ", client_node_ids
    pprint(client_node_ids)
    for cid in client_node_ids:
        if client_node_id == cid or client_node_id == 'all':
            client_nodes = inv_table[cid]
            for client in client_nodes:
                for client_uri in node_table[cid]['uris']:
                    url = 'http://' + client + client_uri
                    d = treq.get(url, persistent=False)
                    d.addCallback(ack_response)

@app.route('/controller/<node_id>', methods = ['POST'])
def control(request, node_id):
    servicemap = node.servicemap
    print "IN /controller. servicemap is: "
    pprint(servicemap)
    for route in servicemap:
        if node_id == route['id'] or node_id == 'all':
            srcs = route['srcs']
            for src in srcs:
                print "src: ", src
                #src = ip:port
                url = "http://" + src + '/setup'
                node_routes_json = json.dumps(route['next_hops'])
                d = treq.post(url, data=node_routes_json)
                d.addCallback(ack_response)
        else:
            print "Skipping non-matched URL"

    return "OK"

# OTHER NODES
@app.route('/info', methods = ['GET'])
def info(request):
    return node.print_infotable

# By default, everything returns 200 OK
@app.route('/status/<status_code>', methods = ['GET', 'POST'])
def status(request, status_code):
    node.set_stat({'type': 'status_code', 'status_code': int(status_code)})
    return "STATUS CODE set to " + str(status_code)

@app.route('/latency/<latency>', methods = ['GET', 'POST'])
def latency(request, latency):
    node.set_stat({'type': 'latency', 'latency': float(latency)})
    return "OK"

@app.route('/echo/<node_id>')
def echo(request, node_id):
    return "ECHO " + node_id + "\n"

@app.route('/setup', methods = ['GET', 'POST'])
def setup(request):
    routes = None
    if request.method == 'POST':
        content = request.content.read()
        routes = json.loads(content)

        node.create_routes(routes)
        return "OK"
    else:
        print "MUST POST"

# Replace this with a catch-all parameter so we can request any URI
# "loop" tells a node to make requests to all of the nodes in its routing table
@app.route('/<node_id>', methods = ['GET', 'POST'])
def loop_endpoint(request, node_id):
    request.setResponseCode(node.get_status_code())

    # Set Latency
    if node.infotable['latency'] > 0:
        time.sleep(node.infotable['latency'])

    node.make_requests()

    # Check for text or file payload
    # Add any methods as a callback
    return node.node_id

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--nodetype', nargs='?', help="Specify the type of node")
    parser.add_argument('-a', '--address', default='localhost', help="Specify the address the node will run on")
    parser.add_argument('-p', '--port', nargs='?', help="Specify the port the node will listen on")

    parser.add_argument('-c', '--config', default='', help="The config file. Only for the controller node")
    parser.add_argument('-i', '--inventory', default='', help="The inventory file")
    parser.add_argument('-d', '--default_port', default='8080', help="The default port for each non-controller servicesim node")

    args = parser.parse_args()

    address = str(args.address)
    port = int(args.port)
    config = args.config
    inventory = args.inventory
    default_port = args.default_port

    # Can we have two different constructors?
    node = Simnode(args.nodetype, config, inventory, default_port)
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

@app.route('/less', methods = ['GET'])
def less(request):
    return "FIRST LEVEL LESS"

@app.route('/less/<lessvar>', methods = ['GET'])
def lesser(request, lessvar):
    return "SECOND LEVEL LESS: " + str(lessvar)


These are load balancer configurations...incorporate these later
[LB-1]
E|A
E|C

[LB-2]
B|D
C|D
'''

#@app.route('/text/<text_payload>', methods = ['GET'])
#@app.route('/file/<file_payload>', methods = ['GET', 'POST'])
#@app.route('/method/<custom_method>/<args>', methods = ['GET', 'POST'])
#@app.route('/cpu', methods = ['GET'])
#@app.route('/mem', methods = ['GET', 'POST'])
#@app.route('/io', methods = ['GET', 'POST'])
#@app.route('/disk', methods=['GET'])
