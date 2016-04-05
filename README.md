* First, run  `bash local-test.sh` to start the server nodes
* Then, run `python simserver.py -n controller -p 8080 -c tests/simple.json -i tests/simple-inv` to start the controller node
* Finally, run `python simclient.py -a localhost -p 8080 -l 0.05`
