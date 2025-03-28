#!/usr/bin/env python
"""
Example to run the HTTP/3 client.
"""

from quicpro.client import Client

def main():
    """
    Create and run the HTTP/3 client, send a GET request with query parameters,
    print the response, and then close the client.
    """
    client = Client(remote_address=("127.0.0.1", 9090),
                    timeout=5,
                    event_loop_max_workers=4)
    response = client.request("GET", "https://example.com", params={"q": "test"})
    print("Response:", response)
    client.close()

if __name__ == "__main__":
    main()
