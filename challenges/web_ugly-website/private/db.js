const Sequelize = require('sequelize');
const session = require('express-session')
const SequelizeStore = require('connect-session-sequelize')(session.Store);

const sequelize = new Sequelize({
    dialect: 'sqlite',
    storage: 'db.sqlite',
    pool: {
        max: 5,
        min: 0,
        idle: 10000
    },
    logging: false,
  });

const sess_store = new SequelizeStore({
    db: sequelize
})


sequelize
    .authenticate()
    .then(() => {
    console.log('Connection has been established successfully.');
    })
.catch(err => {
    console.error('Unable to connect to the database:', err);
    });

module.exports = {
    sequelize, sess_store
};