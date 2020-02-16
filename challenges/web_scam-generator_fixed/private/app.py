# -*- coding: utf-8 -*-

import flask
import re
import json
import uuid
import os
import sys

from flask import Flask, render_template_string, request, Blueprint, g, redirect, session, render_template
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from template_scam import generate_scam


#load envs
TASK_ENVS = ['PROMO_CODE', 'ADMIN_TOKEN', 'ADMIN_PASSWORD']
CONFIG = json.loads(os.getenv('TASK_ENVS'))
CONFIG = {key: value for key, value in CONFIG.items() if key in TASK_ENVS}
FLAG = os.getenv('FLAG')

#pop envs
os.environ.pop('FLAG')
os.environ.pop('TASK_ENVS')


sys.stdout.flush()

db = SQLAlchemy()

bp = Blueprint('session', __name__)
sess = Session()


@bp.before_request
def before_request():
    user = User.query.filter_by(id=session.get('user_id', 0)).first()
    if user:
        g.user = {'id':user.id, 'username':user.username}
    else:
        g.user = None


@bp.after_request
def before_response(resp):
    resp.headers['X-Frame-Options'] = "deny"
    resp.headers['X-XSS-Protection'] = "0"
    return resp


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:////home/justctf/db/app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_USE_SIGNER = False
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = '/home/justctf/sessions/'
    PROMO_CODE = 'With PROMO CODE %s Admin will visit your page for 15 seconds!!!' % CONFIG['PROMO_CODE']


class Victim(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    firstname = db.Column(db.String(127))
    surname = db.Column(db.String(127))
    fullname = db.Column(db.String(256))
    money = db.Column(db.String(64))
    type = db.Column(db.String(256))
    user_id = db.Column(db.Integer, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.surname,
            'props': json.dumps({
                'firstname': self.firstname,
                'surname': self.surname,
                'fullname': self.fullname,
                'money': self.money,
            },indent=2)
        }

#    def __repr__(self):
#        return '<Victim %r>' % self.name


class Scammer(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    firstname = db.Column(db.String(127))
    surname = db.Column(db.String(127))
    fullname = db.Column(db.String(256))
    phone_number = db.Column(db.String(256))
    user_id = db.Column(db.Integer, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.surname,
            'props': json.dumps({
                'firstname': self.firstname,
                'surname': self.surname,
                'fullname': self.fullname,
            },indent=2)
        }

#    def __repr__(self):
#        return '<Scammer %r>' % self.name


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    secret = db.Column(db.String(120), nullable=False)

#    def __repr__(self):
#        return '<User %r>' % self.username


def safe_handle(var):
    if re.search('[^ a-zA-Z0-9\.]', var):
        raise Exception("Unsafe characters")
    else:
        return var


@bp.route('/')
def home():
    if not g.user:
        return redirect('/login')

    victims = Victim.query.filter_by(user_id=g.user['id'])
    scammers = Scammer.query.filter_by(user_id=g.user['id'])

    victims = [
        obj.to_dict()
        for obj in victims
    ]
    identities = [
        obj.to_dict()
        for obj in scammers
    ]

    return render_template('index.html', user=g.user['username'], victims=victims, identities=identities)


@bp.route('/add_identity', methods=['POST'])
def add_identity():
    if not g.user:
        return redirect('/login')
    if g.user['id'] == 1:
        return 'Nice try! :)'
    firstname = request.form.get('firstname', type=str)
    surname = request.form.get('surname', type=str)
    fullname = request.form.get('fullname', type=str)
    phone = request.form.get('phone', type=str)    

    user = Scammer(
        id=str(uuid.uuid4()),
        surname=surname,
        fullname=fullname,
        firstname=firstname,
        phone_number=phone,
        user_id=g.user['id'],
    )
    db.session.add(user)
    db.session.commit()

    return redirect('/')


@bp.route('/add_victim', methods=['POST'])
def add_victim():
    if not g.user:
        return redirect('/login')
    if g.user['id'] == 1:
        return 'Nice try! :)'
    firstname = request.form.get('firstname', type=str)
    surname = request.form.get('surname', type=str)
    fullname = request.form.get('fullname', type=str)
    money = request.form.get('money', type=str)
    utype = request.form.get('type', type=str)
    try:
        utype_handler = safe_handle(utype)
    except:
        return "Unsafe characters"

    print("User type: %s" % utype) 

    user = Victim(
        id=str(uuid.uuid4()),
        surname=surname,
        fullname=fullname,
        firstname=firstname,
        money=money,
        type=utype_handler,
        user_id=g.user['id'],
    )
    db.session.add(user)
    db.session.commit()

    return redirect('/')


@bp.route('/gen_scam')
def gen_scam():
    if not g.user:
        return redirect('/login')

    args_victim = request.args.get('victim', type=str)  # id victim (hash)
    args_scammer = request.args.get('scammer', type=str)  # id scammer (hash)
    args_utype = request.args.get('type', type=str, default="scam.victim.fullname")
    try:
        utype_handler = safe_handle(args_utype)
    except:
        return "Unsafe characters"

    victim = Victim.query.filter_by(id=args_victim).first()
    scammer = Scammer.query.filter_by(id=args_scammer).first()
    
    if not victim or not scammer:
        return "victim or scammer not exists"

    try:
        resp = flask.Response(
            render_template_string(
                generate_scam(victim.type),
                scam={'scammer':scammer, 'victim':victim},
            ))
        resp.headers['X-Content-Type-Options'] = "nosniff"
    except:
        resp = flask.Response('Oh no, hacker detected :(')

    return resp   

def add_defaults(user_id):
    victim = Victim(
        id=str(uuid.uuid4()),
        firstname='',
        surname='Carlos',
        fullname='Carlos',
        money='US $20.000.000.000',
        type='scam.victim.surname',
        user_id=user_id,
    )
    db.session.add(victim)
    db.session.commit()

    scammer = Scammer(
        id=str(uuid.uuid4()),
        firstname='Abraham',
        surname='Morrison',
        fullname='Abraham Morrison,Esq',
        phone_number='0-700-880-774',
        user_id=user_id,
    )
    db.session.add(scammer)
    db.session.commit()


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET': 
        return render_template('login.html')

    user = User.query.filter_by(username=request.form['username']).first()
    if not user:
        #register if not found
        user = User(
            username=request.form['username'],
            secret=request.form['password'],
        )
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        add_defaults(user.id)
        return redirect('/')

    if user.secret != request.form['password']:
        return render_template('login.html', message='Invalid password')

    session['user_id'] = user.id
    return redirect('/')

@bp.route('/s3rcet_adm1n_l0gin')
def admin_login():
    token = request.args.get('token')
    url = request.args.get('url')
    if token == CONFIG['ADMIN_TOKEN']:
        session['user_id'] = 1
        return redirect(url)
    return redirect('/')

def add_admin():
    admin = User.query.filter_by(username='Admin').first()

    if admin:
        return

    user = User(
        username='Admin',
        secret=CONFIG['ADMIN_PASSWORD'],
    )
    db.session.add(user)
    db.session.commit()

    assert user.id == 1, "Admin does not have ID=1, %d" % user.id
    
    scammer = Scammer(
        id=str(uuid.uuid4()),
        firstname='Admin',
        surname='Morrison',
        fullname='Abraham Morrison,Esq',
        phone_number=FLAG,
        user_id=1,
    )
    db.session.add(scammer)
    db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    sess.init_app(app)

    with app.app_context():
        app.register_blueprint(bp)

        db.create_all()
        add_admin()
        return app


if __name__ == '__main__':
    app = create_app()
   
    app.run(
        host='0.0.0.0',
        port=8080,
    )
