import json
import treq
import logging
import os
from simparser import route_parser
import random
import time
from pool import UA_headers

# TODO: setup better logging

class Simnode():
    def __init__(self, node_id, config, inventory):
        self.node_id = node_id
        self.routes = dict()
        self.status = 200
        self.latency = 0

        # Load routes from environment
        self.get_routes_from_env()

        self.infotable = {'node_id' : node_id,  'status': self.status, 'latency': self.latency, 'routes': self.routes}
        if self.node_id == 'controller':
            self.config = config
            self.inventory = inventory

            # This is for the controller node. Generates routes from servicemap config and inventory
            self.servicemap, self.inv_table, self.client_node_table = route_parser(config, inventory)
            self.node_uris = dict()
            self.infotable['servicemap'] = self.servicemap

    def get_routes_from_env(self):
        """This method loads this node's routing table (e.g. its next-hops) from the environment.
        It will look for the variable 'NODE_ROUTES', which it will store as a JSON string.
        """
        print "Getting routes from the environment"
        NODE_ROUTES = str(os.environ.get('NODE_ROUTES', failobj='{}'))

        # Quick hack to replace escaped quotes. Marathon converts the quotes to '&quot;' when it set the env var...
        if NODE_ROUTES != {}:
            NODE_ROUTES = NODE_ROUTES.replace('&quot;', '"')
        self.routes = json.loads(NODE_ROUTES)

    def set_stat(self, stat):
        stat_type = stat['type']
        self.infotable[stat_type] = stat[stat_type]
        if stat_type == 'status':
            self.status = stat[stat_type]

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
