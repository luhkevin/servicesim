import json
import treq
import logging
from simparser import route_parser
import random
import time

# TODO: setup logging

class Simnode():
    def __init__(self, node_id, config, inventory, default_port):
        self.node_id = node_id
        self.routes = dict()
        self.status_code = 200
        self.latency = 0.1
        self.infotable = {'node_id' : node_id,  'status_code': self.status_code, 'latency': self.latency}

        if self.node_id == 'controller':
            self.config = config
            self.inventory = inventory
            self.default_port = default_port

            # This is for the controller node. Generates routes from servicemap config and inventory
            self.servicemap, self.inv_table, self.client_node_ids = route_parser(config, inventory, default_port)
            self.infotable['servicemap'] = self.servicemap

    def set_stat(self, stat):
        stat_type = stat['type']
        self.infotable[stat_type] = stat[stat_type]
        if stat_type == 'status_code':
            self.status_code = stat[stat_type]

    def print_infotable(self):
        return json.dumps(self.infotable)

    def get_status_code(self):
        return self.status_code

    def ack_response(self, resp):
        print str(self.node_id) + " received response"

    def make_requests(self):
        print "ROUTES ARE: ", self.routes
        for hop in self.routes:
            for dest in hop['dests']:
                for uri in hop['uris']:
                    url = 'http://' + dest + uri
                    print "URL IS: ", url
                    df = treq.get(url)
                    df.addCallback(self.ack_response)

    """
    node_servicemap is a dict that represents the routing table for this node
    See 'servicemap.json' for an example
    """
    # TODO: Do some validity checking on this later
    def create_routes(self, node_servicemap):
        self.routes = node_servicemap
