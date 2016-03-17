import time
import requests
import argparse

def run(address, port, latency):
    # First, sleep so the controller node has time to spin up
    time.sleep(3)

    # Send a SETUP message to each node
    controller_url = 'http://' + str(address) + ':' + str(port)
    requests.post(url + '/controller/all')

    # Sleep for the other nodes' to accept their configuration
    time.sleep(3)

    # Setup some stats
    requests.post(url + '/setstatus/gamma/404')
    requests.post(url + '/setstatus/kappa/404')

    # Start the client
    while True:
        time.sleep(float(latency))
        requests.post(url + '/start/all')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', default='localhost', help="Specify the address of the controller")
    parser.add_argument('-p', '--port', default='8080', help="Specify the port of the controller")
    parser.add_argument('-l', '--latency', default='0.1', help="Specify the latency of requests")

    args = parser.parse_args()

    run(args.address, args.port, args.latency)

