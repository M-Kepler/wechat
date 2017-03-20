from flask import Flask, render_template, request, make_response
import time
import hashlib
import xml.etree.ElementTree as ET
app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def wechat_auth():
    if request.method == 'GET':
        if len(request.args)>3:
            token = 'kepler'
            query = request.args
            signature = query['signature']
            timestamp = query['timestamp']
            nonce = query['nonce']
            echostr = query['echostr']
            s= [timestamp, nonce, token]
            s.sort()
            sha1str = hashlib.sha1(s).hexdigest()
            if sha1str == signature:
                return make_response(echostr)
            else:
                return make_response("认证失败")
        else:
            return "认证失败"
