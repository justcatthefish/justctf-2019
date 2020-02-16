const crypto = require('crypto');
const config = require('./config');

function getTimestamp(){
    return Math.floor(Date.now() / 1000);
  }
  
  function calculate_hmac(str){
    const hmac = crypto.createHmac('sha256', config.SECRET_KEY);
    hmac.update(str);
    return hmac.digest('hex');
  }
  
  function generate_hmac_string(id, timestamp){
    const str = `ID:${id};TIMESTAMP:${timestamp}`;
    return calculate_hmac(str);
  }
  
  function is_valid_hmac(hmac, id, timestamp){
    return hmac === generate_hmac_string(id, timestamp);
  }
  
  // timestamp is only valid for 60 seconds
  function is_fresh(timestamp){
    return getTimestamp() - timestamp >= 0 && getTimestamp() - timestamp < 90;
  }

module.exports = {
    calculate_hmac, generate_hmac_string, is_valid_hmac, is_fresh, getTimestamp
}