import argparse
import json
import os
from simparser import route_parser

def gen_spec(deploy_env, spec_output_dir, manual_spec_output_dir, config):
    """This function generates a spec to use with the deployment environment of servicesim.
    E.g. if we are deploying servicesim in marathon, it will generate an 'options.json' file for each servicesim node that we deploy"""

    servicemap, inv_table, client_node_table = route_parser(config, deploy_env=deploy_env)
    auto_deploy_specs = list()
    manual_deploy_specs = list()
    for route in servicemap:
        spec = { 'servicesim': {} }
        spec_str = ''

        cnode_id = route['id']
        node_routes_json = json.dumps(route['next_hops'])

        cnode_toks = cnode_id.split('-')
        root = cnode_toks[0]
        servicesim_spec = spec['servicesim']
        servicesim_spec['node_id'] = 'dev-' + str(cnode_id)
        servicesim_spec['node_type'] = 'dev-' + str(root)
        servicesim_spec['node_port'] = int(route['port'])
        servicesim_spec['node_function'] = 'regular'
        servicesim_spec['node_routes'] = str(node_routes_json)
        servicesim_spec['node_image_tag'] = 'dev-' + str(root)
        if route.has_key('lbport'):
            servicesim_spec['node_lbport'] = int(route['lbport'])

        spec_filename = 'servicesim-' + spec['servicesim']['node_id'] + '-options.json'
        spec_str = json.dumps(spec)
        if route.has_key('deploy-type') and route['deploy-type'] == 'manual':
            manual_deploy_specs.append((spec_filename, spec_str))
        else:
            auto_deploy_specs.append((spec_filename, spec_str))

    for spec_tuple in auto_deploy_specs:
        spec_filename, spec_str = spec_tuple
        with open(os.path.join(spec_output_dir, spec_filename), 'w') as specfile:
            specfile.write(spec_str)

    for spec_tuple in manual_deploy_specs:
        spec_filename, spec_str = spec_tuple
        with open(os.path.join(manual_spec_output_dir, spec_filename), 'w') as specfile:
            specfile.write(spec_str)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--deploy_env', default='marathon', help="The environment for which we're generating servicesim deploy specs")
    parser.add_argument('-s', '--spec_output_dir', default='/tmp', help="The directory to write all the servicesim specs")
    parser.add_argument('-m', '--manual_spec_output_dir', default='/tmp', help="The directory to write all the servicesim specs that will be manually deployed.")
    parser.add_argument('-c', '--config', default='servicesim.json', help="The servicesim config file that we parse to generate the specs")

    args = parser.parse_args()
    gen_spec(args.deploy_env, args.spec_output_dir, args.manual_spec_output_dir, args.config)
