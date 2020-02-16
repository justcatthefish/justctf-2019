const Sequelize = require('sequelize');
const config = require('./config');
const db = require('./db');

const Model = Sequelize.Model;

class User extends Model { }
User.init({
    // attributes
    id: {
        type: Sequelize.INTEGER,
        autoIncrement: true,
        primaryKey: true
    },
    name: {
        type: Sequelize.CHAR(50),

    },
    secret: {
        type : Sequelize.CHAR(50),
        default: "You have no secrets"
    },
}, {
    sequelize: db.sequelize,
    modelName: 'user',
});


User.sync({ force: true }).then(() => {
    return User.create({
      username: 'admin',
      secret: config.FLAG2
    });
});


module.exports = {
    User: User
};