package main

import (
	"github.com/fasthttp/router"
	"github.com/valyala/fasthttp"
	"gopool/app"
	"gopool/config"
	"gopool/log"
	"net/http"
	"os"
)

func run() error {
	log.Log.Info("server starting")

	r := router.New()
	r.PanicHandler = func(ctx *fasthttp.RequestCtx, err interface{}) {
		log.Log.WithField("err", err).WithField("url", string(ctx.RequestURI())).Error("panic from http handler")
		ctx.Error("internal_error", http.StatusInternalServerError)
	}

	r.GET("/api/v1/comments", app.TimeoutMiddleware(app.HandleComments()))
	r.POST("/api/v1/add_comment", app.TimeoutMiddleware(app.HandleCommentAdd()))
	r.POST("/api/v1/report_meme", app.TimeoutMiddleware(app.HandleMemeReport()))
	r.GET("/secure_space/flag", app.TimeoutMiddleware(app.HandleFlag()))

	s := &fasthttp.Server{
		Handler: r.Handler,
	}
	log.Log.Info("server started")

	return s.ListenAndServeUNIX(config.Config.UnixSocket, os.ModeSocket|os.ModePerm)
}

func main() {
	if err := run(); err != nil {
		log.Log.WithError(err).Error("server closed with err")
		os.Exit(1)
	}
}
