import requests
import os
import json
import re

from flask import Flask, render_template, request, redirect
from flask_recaptcha import ReCaptcha
from urllib.parse import quote

#load envs
TASK_ENVS = ['PROMO_CODE', 'ADMIN_TOKEN', 'BOT_URL', 'SERVER', 'BOT_TIMEOUT', 'RECAPTCHA_SITE_KEY', 'RECAPTCHA_SECRET_KEY']
CONFIG = json.loads(os.getenv('TASK_ENVS'))
CONFIG = {key: value for key, value in CONFIG.items() if key in TASK_ENVS}

#pop envs
os.environ.pop('TASK_ENVS')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('report.html')

@app.route('/report', methods=['POST'])
def report():
    url = request.form.get('url')
    promo = request.form.get('promo_code')
    
    if not re.match(r'^https?://', url):
        return "Must be http:// or https://"
    url2 = '%s/s3rcet_adm1n_l0gin?token=%s&url=%s' % (CONFIG['SERVER'], CONFIG['ADMIN_TOKEN'],quote(url))

    #look how far people got
    print(promo, url)

    if not recaptcha.verify():
        return "Invalid reCAPTCHA"

    timeout = 2
    if promo == CONFIG['PROMO_CODE']:
        timeout = CONFIG['BOT_TIMEOUT']

    requests.post(CONFIG['BOT_URL'], data={
        'url': url2,
        'timeout': timeout,
	'sleep': timeout,
        'region': 'eu',
        'task_name': 'scam-generator-fixed',
        'user_ip': request.headers['X-Real-IP'] or request.remote_addr
    })
    
    return "Admin will visit your website shortly"


@app.route('/s3cr3t_r3p0rt', methods=['POST'])
def secret_report():
    token = request.form.get('token')
    if token != CONFIG['ADMIN_TOKEN']:
        redirect('/')

    url = request.form.get('url')
    timeout = request.form.get('timeout', default=15, type=int)
    region = request.form.get('region', default='eu', type=str)

    url2 = '%s/s3rcet_adm1n_l0gin?token=%s&url=%s' % (CONFIG['SERVER'], CONFIG['ADMIN_TOKEN'],quote(url))
    requests.post(CONFIG['BOT_URL'], data={
        'url': url2,
        'timeout': timeout,
	'sleep': timeout,
        'region': region,
        'task_name': 'scam-generator-fixed',
        'user_ip': request.headers['X-Real-IP'] or request.remote_addr
    })
    
    return "Admin will visit your website shortly"



app.config.update({
    "RECAPTCHA_SITE_KEY": CONFIG["RECAPTCHA_SITE_KEY"],
    "RECAPTCHA_SECRET_KEY": CONFIG["RECAPTCHA_SECRET_KEY"],
    "RECAPTCHA_ENABLED": True
})
recaptcha = ReCaptcha(app=app)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8080,
    )
