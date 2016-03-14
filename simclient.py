import requests

# We assume that there is a controller node running on localhost:5000
def run():
    # Send a SETUP message to each node
    requests.get('http://localhost:5000/controlller')

    # Start the clients


if __name__=='__main__':
    run()
