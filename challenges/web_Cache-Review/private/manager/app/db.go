package app

import (
	"database/sql"
	"errors"
	_ "github.com/mattn/go-sqlite3"
	"gopoolmanager/config"
	"time"
)

type db struct {
	db *sql.DB
}

func NewDB() (*db, error) {
	db2, err := sql.Open("sqlite3", config.Config.DbFile)
	if err != nil {
		return nil, err
	}
	s := &db{
		db: db2,
	}
	return s, nil
}

func (d *db) Init() error {
	sqlStmt := `
	create table if not exists users (
		user_ip TEXT not null unique,
		token TEXT not null,
		hash TEXT not null,
		expire_at INTEGER not null
	);
	`
	_, err := d.db.Exec(sqlStmt)
	if err != nil {
		return err
	}
	return nil
}

type UserData struct {
	UserIP      string
	ExpireAt    time.Time
	Token       string
	OneTimeHash string
}

func (u UserData) NeedRefreshOneTimeHash() bool {
	return time.Now().After(u.ExpireAt)
}

var ErrUserNotExists = errors.New("user not exists")

func (d *db) AddUser(user UserData) error {
	_, err := d.db.Exec(`insert into users (user_ip, expire_at, token, hash) values (?, ?, ?, ?)`, user.UserIP, user.ExpireAt.Unix(), user.Token, user.OneTimeHash)
	if err != nil {
		return err
	}
	return nil
}

func (d *db) UpdateUser(user UserData) error {
	_, err := d.db.Exec(`update users set expire_at = ?, token = ?, hash = ? where user_ip = ?`, user.ExpireAt.Unix(), user.Token, user.OneTimeHash, user.UserIP)
	if err != nil {
		return err
	}
	return nil
}

func (d *db) GetUser(userIP string) (UserData, error) {
	out := UserData{}
	stmt := d.db.QueryRow(`select user_ip, expire_at, token, hash from users where user_ip = ?`, userIP)
	var expireAt int
	if err := stmt.Scan(&out.UserIP, &expireAt, &out.Token, &out.OneTimeHash); err != nil {
		if err == sql.ErrNoRows {
			return out, ErrUserNotExists
		}
		return out, err
	}
	out.ExpireAt = time.Unix(int64(expireAt), 0)

	return out, nil
}
