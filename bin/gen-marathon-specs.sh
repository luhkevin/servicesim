#!/bin/bash
python gen_deploy_specs.py -d marathon -s ./config/demo/options -m ./config/demo/manual -c ./config/demo/demo-config.json
cp ./config/demo/servicesim-client.json ./config/demo/manual/servicesim-client.json
