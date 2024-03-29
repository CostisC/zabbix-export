#!/usr/bin/env python3

import http.client
import argparse, json

def parse_args():
    parser = argparse.ArgumentParser(description =
        """
        Generare a Zabbix server authorization token.
        """)
    parser.add_argument('-s', '--server', action = "store", required = True,
        help = "The Zabbix server's IP address")
    parser.add_argument('-P', '--port', action = "store",
        help = "The Zabbix server's listening port. Default: %(default)s",
        default = 80)
    parser.add_argument('-u', '--user', action = "store", required = True,
        help = "The admin's username")
    parser.add_argument('-p', '--password', action = "store", required = True,
        help = "The admin's password")
    parser.add_argument('-t', '--tls', action = 'store_true',
        help = "Connect over HTTPS")

    return parser.parse_args()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                ~~~~ MAIN ~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

args = parse_args()

connClass = http.client.HTTPSConnection if args.tls else http.client.HTTPConnection
conn = connClass(args.server, args.port)


payload = '''{{
    "jsonrpc": "2.0",
    "method": "user.login",
    "params": {{
        "username": "{}",
        "password": "{}"
    }},
    "id": 1,
    "auth": null
}}'''.format(args.user, args.password)

headers = {
  'Content-Type': 'application/json-rpc'
}

conn.request("GET", "/api_jsonrpc.php", payload, headers)

res = conn.getresponse()
data = res.read().decode("utf-8")
data_dir = json.loads(data)

print(f"Generated Token: {data_dir['result']}")
