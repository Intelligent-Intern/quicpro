#!/usr/bin/env python
from quicpro.client import Client

def main():
    # Create the client with configurable event loop workers.
    client = Client(remote_address=("127.0.0.1", 9090), timeout=5, event_loop_max_workers=4)
    
    # Send a GET request with query parameters.
    response = client.request("GET", "https://example.com", params={"q": "test"})
    print("Response:", response)
    
    # Close the client and all underlying resources.
    client.close()

if __name__ == "__main__":
    main()