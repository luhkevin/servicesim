import json
import treq
import logging
from simparser import route_parser
import random
import time
from pool import UA_headers

# TODO: setup logging

class Simnode():
    def __init__(self, node_id, config, inventory, default_port):
        self.node_id = node_id
        self.routes = dict()
        self.status_code = 200
        self.latency = 0
        self.infotable = {'node_id' : node_id,  'status_code': self.status_code, 'latency': self.latency}

        if self.node_id == 'controller':
            self.config = config
            self.inventory = inventory
            self.default_port = default_port

            # This is for the controller node. Generates routes from servicemap config and inventory
            self.servicemap, self.inv_table, self.client_node_ids, self.node_table = route_parser(config, inventory, default_port)
            self.node_uris = dict()
            self.infotable['servicemap'] = self.servicemap

    def set_stat(self, stat):
        stat_type = stat['type']
        self.infotable[stat_type] = stat[stat_type]
        if stat_type == 'status_code':
            self.status_code = stat[stat_type]

    def print_infotable(self):
        return str(self.infotable)

    def get_status_code(self):
        return self.status_code

    def ack_response(self, resp):
        print str(self.node_id) + " received response"

    def make_requests(self):
        ua_header = random.choice(UA_headers)
        headers = { ua_header[0]: ua_header[1] }
        for hop in self.routes:
            for dest in hop['dests']:
                for uri in hop['uris']:
                    url = 'http://' + dest + uri
                    df = treq.get(url, headers=headers, persistent=False)
                    df.addCallback(self.ack_response)

    # TODO: Implement and use this
    def check_routes(self, node_servicemap):
        """Checks the routes for validity
        node_servicemap -- the routing table for this node. See 'servicemap.json' for an example.
        """
        pass
