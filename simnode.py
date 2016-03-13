import json
import treq
import logging
from simparser import route_parser
import random
import time

# TODO: setup logging

class Simnode():
    def __init__(self, node_id, config, inventory):
        self.node_id = node_id
        self.status_code_freq = [200]
        self.routes = dict()
        self.infotable = {'node_id' : node_id, 'latency': 0.25}

        if self.node_id == 'control':
            self.config = config
            self.inventory = inventory
            self.parse_servicesim_config(config, inventory)
            self.servicemap = dict()

    def set_stat(self, stat):
        if stat['type'] == 'status_code':
            status_code = stat['status_code']
            percentage = stat['percentage']
            status_code_freq = [200] * (100 - percentage)
            fill_code_freq = [status_code] * percentage
            status_code_freq.extend(fill_code_freq)
            self.infotable['status_code'] = (status_code, percentage)
        elif stat['type'] == 'latency':
            self.infotable['latency'] = stat['latency']

    def print_infotable(self):
        return json.dumps(self.infotable)

    def get_status_code(self):
        return random.choice(self.status_code_freq)

    def make_requests(self):
        print "ROUTES ARE: ", self.routes
        for hop in self.routes['next_hops']:
            for uri in hop['uris']:
                url = 'http://' + hop['addr'] + ':' + hop['port'] + uri
                print "URL IS: ", url
                df = treq.get(url)
                #df.addCallback()

    """
    servicemap is a dict that represents the routing table for this node
    See 'servicemap.json' for an example
    """
    # TODO: Do some validity checking on this later
    def create_routes(self, servicemap):
        self.routes = servicemap

    # This is for the controller node. Generates routes from servicemap config and inventory
    def parse_servicesim_config(self, servicesim_config, inventory):
        self.servicemap = route_parser(servicesim_config, inventory)
