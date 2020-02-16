// Constants
const PORT = 8080;
const HOST = '0.0.0.0';
const SECRET_KEY = process.env.SECRET_KEY
const DEBUG = process.env.DEBUG == "true"
const CODE_ADMIN = process.env.CODE_ADMIN
const CODE_USER = process.env.CODE_USER
const FLAG1 = process.env.FLAG1
const FLAG2 = process.env.FLAG2
const ADMIN_TOKEN = process.env.ADMIN_TOKEN
const RECAPTCHA_SITE_KEY = process.env.RECAPTCHA_SITE_KEY
const RECAPTCHA_SECRET_KEY = process.env.RECAPTCHA_SECRET_KEY
const BOT_URL = process.env.BOT_URL
const SERVER = process.env.CHALLENGE_BASEURL 
const PRODUCTION = process.env.PRODUCTION
const EASY_TIMEOUT = process.env.BOT_EASY_TIMEOUT
const HARD_TIMEOUT = process.env.BOT_HARD_TIMEOUT


module.exports = {
    PORT, HOST, SECRET_KEY, DEBUG, CODE_ADMIN, CODE_USER, FLAG1, FLAG2,
    ADMIN_TOKEN, RECAPTCHA_SECRET_KEY, RECAPTCHA_SITE_KEY, BOT_URL, SERVER,
    PRODUCTION, EASY_TIMEOUT, HARD_TIMEOUT
}