package main

import (
	"gopoolbot/app"
	"gopoolbot/config"
	"gopoolbot/log"
	"net/http"
)

func main() {
	log.Log.Info("starting server")

	botPool := app.NewBrowserPool()
	http.HandleFunc("/bot", app.BotHandler(botPool))

	log.Log.Panic(http.ListenAndServe(config.Config.Listen, nil))
}
