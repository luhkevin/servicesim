import argparse
import json
import os
from simparser import route_parser

def gen_spec(deploy_env, spec_output_dir, config):
    """This function generates a spec to use with the deployment environment of servicesim.
    E.g. if we are deploying servicesim in marathon, it will generate an 'options.json' file for each servicesim node that we deploy"""

    servicemap, inv_table, client_node_table = route_parser(config)
    for route in servicemap:
        node_id = route['id']
        node_routes_json = json.dumps(route['next_hops'])
        #print "NODE ROUTES JSON for ", node_id, str(node_routes_json)

        spec = {
            'servicesim': {
                'node_id': '',
                'node_routes': '',
                'node_port': 0,
                'node_type': ''
            }
        }
        spec_str = ''
        if deploy_env == 'marathon':
            root, _, index = node_id.split('-')
            servicesim_spec = spec['servicesim']
            servicesim_spec['node_id'] = str(node_id)
            servicesim_spec['node_root_id'] = str(root)
            servicesim_spec['node_routes'] = str(node_routes_json)
            servicesim_spec['node_port'] = 31000 + int(index)
            servicesim_spec['node_type'] = 'regular'

        spec_str = json.dumps(spec)

        with open(os.path.join(spec_output_dir, 'servicesim-' + spec['servicesim']['node_id'] + '-options.json'), 'w') as specfile:
            specfile.write(spec_str)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--deploy_env', default='marathon', help="The environment for which we're generating servicesim deploy specs")
    parser.add_argument('-s', '--spec_output_dir', default='/tmp', help="The directory to write all the servicesim specs")
    parser.add_argument('-c', '--config', default='servicesim.json', help="The servicesim config file that we parse to generate the specs")

    args = parser.parse_args()
    gen_spec(args.deploy_env, args.spec_output_dir, args.config)
