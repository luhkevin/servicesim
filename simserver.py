#!/usr/bin/python3
import time
from klein import Klein
from twisted.internet.defer import inlineCallbacks, returnValue
from simnode import Simnode

app = Klein()
node = None
servicemap = None

# This is a simple key-value store for the controller node
@app.route('/kv/<node_id>/<key>', methods = ['GET', 'POST'])
def kv(request, key):
    return ""

@app.route('/controller/<params>', methods = ['POST'])
def control(request, params):
    return ""

@app.route('/info', methods = ['GET'])
def info(request):
    return node.print_infotable

# By default, everything returns 200 OK
@app.route('/status/<status_code>/<percentage>', methods = ['GET', 'POST'])
def status(request, status_code, percentage):
    node.set_stat({'type': 'status_code', 'status_code': int(status_code), 'percentage': int(percentage)})
    return "OK"

@app.route('/latency/<latency>', methods = ['GET', 'POST'])
def latency(request, latency):
    node.set_stat({'type': 'latency', 'latency': latency})
    return "OK"

@app.route('/echo')
def echo(request):
    # Create routes
    node.create_routes(servicemap)

    # Set response code
    request.setResponseCode(node.get_status_code)

    # Latency
    if node.infotable['latency'] > 0:
        time.sleep(node.infotable['latency'])

    # Make requests to other nodes based on routes
    node.make_requests()

    # Check for text or file payload
    # Add any methods as a callback
    return node.node_id

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--nodetype', nargs='?', help='Specify the type of node')
    parser.add_argument('-p', '--port', nargs='?', help='Specify the port the node will run on')
    parser.add_argument('-m', '--servicemap', nargs='?', help='Location of servicemap configuration')
    parser.add_argument('-l', '--servicemap_node', help='An <ip:port> string. An HTTP kv-store with the servicemap configuration exposed, typically the controller node.')

    port = int(args.port)
    node = Simnode(args.nodetype)
    servicemap = args.servicemap

    app.run('localhost', port)

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
