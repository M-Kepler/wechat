from flask import Flask, g, request, make_response, render_template, abort
import time, hashlib, urllib, re, time, json
import xml.etree.ElementTree as ET
from wechatpy import parse_message, create_reply
from wechatpy.replies import ImageReply
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
app = Flask(__name__)

@app.route('/wechat', methods=['GET', 'POST'])
def wechat():
    signature = request.args.get('signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    echo_str = request.args.get('echostr', '')
    token='kepler'
    try:
        check_signature(token, signature, timestamp, nonce)
    except InvalidSignatureException:
        abort(403)
    if request.method == 'GET':
        return echo_str
    else:
        msg = parse_message(request.data)
        if msg.type == 'text':
            reply = create_reply(msg.content, msg)
        else:
            reply = create_reply('Sorry, can not handle this for now', msg)
        return reply.render()

@app.route('/')
@app.route('/index')
def index():
    return 'Hi There'
