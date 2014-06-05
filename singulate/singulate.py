# !/usr/bin/env python
import io
import sys
import json
import subprocess
import ipaddress

import requests
from flask import Flask, request, abort


app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():
    config = json.loads(io.open('config.json', 'r').read())
    github = requests.get('https://api.github.com/meta').json()['hooks']

    if request.method == 'GET':
        return 'You shouldn\'t be here...'

    elif request.method == 'POST':
        for addr in github:
            ip = ipaddress.ip_address(u'%s' % request.remote_addr)
            if ipaddress.ip_address(ip) in ipaddress.ip_network(addr):
                break
        else:
            abort(403)

        if request.headers.get('X-GitHub-Event') == "ping":
            return json.dumps({'msg': 'Pong!'})
        if request.headers.get('X-GitHub-Event') != "push":
            return json.dumps({'msg': "wrong event type"})

        payload = json.loads(request.data)
        repo = {
            'name': payload['repository']['name'],
            'owner': payload['repository']['owner']['name'],
        }

    if repo == {'name': 'singularity', 'owner': 'neersighted'}:
        pull = subprocess.call('git pull origin master')
        return 'OK'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=sys.argv[1], debug=True)