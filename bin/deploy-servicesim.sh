#!/bin/bash
echo "Add package repo"
dcos package repo add luhkevin-universe https://github.com/luhkevin/luhkevin-universe/archive/master.zip

echo "Install servicesim servers"
cd ./config/demo/options
for options_file in *.json
do
    dcos package install --yes --options=${options_file} servicesim
done

echo "Install servicesim clients"
cd ../manual
dcos marathon app add servicesim-client.json
