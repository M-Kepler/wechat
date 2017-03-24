from flask import Flask, g, request, make_response
import time, hashlib
import xml.etree.ElementTree as ET

app = Flask(__name__)

def verification(request):
    signature = request.args.get('signature')
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')
    token = 'kepler'

    tmplist = [token, timestamp, nonce]
    tmplist.sort()
    tmpstr = ''.join(tmplist)
    tmp = tmpstr.encode('utf-8')

    hashstr = hashlib.sha1(tmp).hexdigest()

    if hashstr == signature:
        return True
    return False

@app.route('/wechat', methods=['GET'])
def wechat_access_verify():
    echostr = request.args.get('echostr')
    if verification(request) and echostr is not None:
        return echostr
    return 'access verification fail'

