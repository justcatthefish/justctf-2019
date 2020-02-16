'use strict';

const bodyParser = require('body-parser');
const express = require('express');
const fileUpload = require('express-fileupload');
const cookieParser = require('cookie-parser')
const session = require('express-session')
const csp = require('express-csp-header');
const fetch = require('node-fetch');
const Recaptcha = require('express-recaptcha').RecaptchaV3;

const config = require('./config');
const models = require("./models");
const utils = require('./utils');
const db = require('./db');
const compress = require('compression');

const recaptcha = new Recaptcha(config.RECAPTCHA_SITE_KEY, config.RECAPTCHA_SECRET_KEY, {callback:'cb'});


const CSP_POLICIES = {
  'default-src': [csp.SELF],
  'style-src': [csp.NONCE],
  'img-src': ['data:', 'http:', 'https:'],
  'font-src': ['data:', 'http', 'https:'],
  'script-src': ['https://www.google.com/recaptcha/', 'https://www.gstatic.com/recaptcha/'],
  'frame-src': ['https://www.google.com/recaptcha/']
}

const User = models.User;

const app = express();

app.use(compress());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true })); // support encoded bodies
app.use(function(req, res, next){
    let ip_real = req.header('X-Real-IP') || req.connection.remoteAddress;
    req.user_ip = ip_real; 
    next()
})


app.use(session({
    secret : config.SECRET_KEY,
    store: db.sess_store,
    resave: false,
    saveUninitialized: false,
    checkExpirationInterval: 15 * 60 * 1000,
    expiration: 60 * 60 * 1000,
}));

app.use(csp({
  policies: CSP_POLICIES
}));

app.use(function (req, res, next) {
  res.locals.nonce = req.nonce;
  if(req.session && req.session.user) res.locals.css_path = req.session.user.css_path;
  else res.locals.css_path = '/static/default.css';
  next()
})

app.use(function (req,res,next){
  res.set({
    'X-Content-Type-Options':' nosniff',
    'X-Frame-Options': 'deny',
    'X-XSS-Protection': '0',
  });
  next();
});

app.use('/uploads', express.static('uploads'));
app.use('/static', express.static('static'));
app.set('view engine', 'ejs');

db.sess_store.sync();

function isAuth(req,res,next){
  if(req.session.user && req.session.user.id){
    return next();
  }
  return res.redirect('/login');
}

function smth_wrng(res){
  return res.send("Something went wrong");
}


app.get('/', isAuth, (req, res) => {
  const timestamp = parseInt(utils.getTimestamp());
  const id = req.session.user.id;
  const hmac = utils.generate_hmac_string(id, timestamp);
  
  res.render('index', {user:req.session.user, signature: hmac, timestamp: timestamp, hard_timeout:config.HARD_TIMEOUT, easy_timeout:config.EASY_TIMEOUT});
});


app.get('/login', (req, res) =>{
  return res.render('login');
});


app.get('/api/secret', async (req, res) =>{
  const id = parseInt(req.query.user_id);
  const timestamp = parseInt(req.query.timestamp);
  const hmac = req.query.sgn;

  if(!utils.is_fresh(timestamp)) {
    return res.send('Signature has expired.');
  }
  if(!utils.is_valid_hmac(hmac, id, timestamp)) {
    return res.send('Signature check has failed.');
  }
  const user = await User.findOne({
    where: {id:id},
    attributes: ['secret']
  });
  if(user === null) return smth_wrng(res);
  res.type('text');
  res.send(`${user.secret}`);
});


app.post('/login', async (req, res) =>{
  let user = await User.create({name:req.body.name, secret:req.body.secret});
  if(user === null) return smth_wrng(res)
  req.session.user = {
    id: user.id,
    name: user.name,
    css_path: '/static/default.css',
    code: config.CODE_USER,
  };
  return res.redirect('/');
});


app.post('/upload_css', 
  fileUpload({
    useTempFiles : true,
    tempFileDir : '/tmp/',
    debug: config.DEBUG,
    createParentPath: true,
    limits: { fileSize: 500 * 1024 },
    abortOnLimit: true,
    responseOnLimit: "500kb filesize exceeded",
  }), 
  isAuth, 
  function(req, res) {
    if(!req.files || !req.files.file) return smth_wrng(res);
    const file = req.files.file;
    
    const fname = 'uploads/' + utils.calculate_hmac(req.user_ip) + '.css'
    req.session.user.css_path = fname;
    file.mv(fname);
    res.render('uploaded', {user:req.session.user});
  });


app.get('/logout', async (req, res) =>{
  req.session.destroy();
  res.redirect('/login');
});


app.get('/report', isAuth, (req, res) => {
  return res.render('report', { site_key: config.RECAPTCHA_SITE_KEY });
});

app.post('/report', recaptcha.middleware.verify, isAuth, async (req, res) =>{
  res.type('text');
  // if (req.recaptcha.error) {
  //   return res.send("CAPTCHA ERROR")
  // }

  let code = req.body.code.trim()
  let timeout = 0;
  let css_path = req.session.user.css_path
  let easy_flag = ""

  if(code === config.CODE_ADMIN){
    timeout = config.HARD_TIMEOUT
    easy_flag = `Looks like you have found a secret code! It surely deserves a flag: ${config.FLAG1}.\n There is another flag though, can you find it?\n\n`
  }else
  if(code === config.CODE_USER){
    timeout = config.EASY_TIMEOUT
  }
  if(timeout === 0) {
    return res.send("You must have a valid CODE to participate!");
  } 
  
  let login_url = new URL(config.SERVER)
  login_url.pathname += 's3rcet_adm1n_l0gin'
  login_url.searchParams.set('token', config.ADMIN_TOKEN)
  login_url.searchParams.set('css_path', css_path)
  
  let resp = await fetch(config.BOT_URL, {
      method:'POST', 
      headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'},
      body:new URLSearchParams({
        timeout,
        url: login_url.href,
        task_name: 'ugly-website',
        region: 'eu',
        user_ip: req.user_ip,
      }),
    })
  
  return res.send(`${easy_flag}Judges will evaluate your canditure shortly. \nTime: ${timeout}s | CSS file: ${css_path}`);
});

app.get('/s3rcet_adm1n_l0gin', async (req, res) =>{
  res.type('text');
  if(req.query.token === config.ADMIN_TOKEN){
    req.session.user = {
      id: 1,
      name: 'Admin',
      css_path: req.query.css_path || '/static/default.css',
      code: config.CODE_ADMIN,
    };
  }
  res.redirect('/');
});

app.get('/s3cr3t_r3p0rt', async (req, res) =>{
  let token = req.query.token

  if (token !== config.ADMIN_TOKEN) {
    return res.send("There is no vulnerability here, but how did you get here anyway?")
  }

  let css_path = req.query.css_path
  let timeout = req.query.timeout
  
  let login_url = new URL(config.SERVER)
  login_url.pathname += 's3rcet_adm1n_l0gin'
  login_url.searchParams.set('token', config.ADMIN_TOKEN)
  login_url.searchParams.set('css_path', css_path)

  let resp = await fetch(config.BOT_URL, {
    method:'POST', 
      headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'},
      body:new URLSearchParams({
        timeout,
        url: login_url.href,
        task_name: 'ugly-website',
        region: 'eu',
        user_ip: req.user_ip,
      }),
  })

  let text = await resp.text()

  return res.send(text)
});


app.listen(config.PORT, config.HOST);

console.log(`Running on http://${config.HOST}:${config.PORT}`);

process.on('SIGINT', function() {
  console.log( "\nGracefully shutting down from SIGINT (Ctrl-C)" );
  process.exit(1);
});
