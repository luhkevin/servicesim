import json
import treq
import logging
from simparser import route_parser

# TODO: setup logging

class Simnode():
    def __init__(self, node_id):
        self.node_id = node_id
        self.status_code_freq = list()
        self.routes = dict()
        self.infotable = {'node_id' : node_id}

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
        return random.choice(status_code_freq)

    def make_requests(self):
        #d = treq.get('http://httpbin.org/get')
        #d.addCallback()
        pass

    def create_routes(self, servicemap):
        # TODO: Throw some error if servicemap doesn't exist yet
        self.routes = route_parser(servicemap)
        return ""
