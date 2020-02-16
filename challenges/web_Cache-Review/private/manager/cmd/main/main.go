package main

import (
	"gopoolmanager/app"
	"gopoolmanager/config"
	"gopoolmanager/log"
	"net/http"
	"os"
)

func run() error {
	log.Log.Info("starting server")

	botPool := app.NewBrowserPool()
	db, err := app.NewDB()
	if err != nil {
		return err
	}
	if err := db.Init(); err != nil {
		return err
	}

	http.HandleFunc("/bot", app.BotHandler(botPool))
	http.HandleFunc("/", app.SandboxHandler(db))

	return http.ListenAndServe(config.Config.Listen, nil)
}

func main() {
	if err := run(); err != nil {
		log.Log.WithError(err).Error("server shutdown with error")
		os.Exit(1)
	}
}
