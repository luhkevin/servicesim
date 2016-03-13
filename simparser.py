import os
import json

def parse_smap_nodes(smap):
    pass

def parse_smap_links(smap):
    pass

def parse_smap_clients(smap):
    pass

# Transforms "servicesim.json" and the inventory file into "smap" -- servicemap.json
def route_parser(servicesim_config, inventory):
    smap, inv = dict(), dict()
    with open(inventory, 'r') as inventory_file:
        print "PARSE INV FILE"
    with open(servicesim_json, 'r') as smap_file:
        smap_json = json.loads(smap_file)

    # Do some json tranformations
    print "JSON: ", smap
    return smap

