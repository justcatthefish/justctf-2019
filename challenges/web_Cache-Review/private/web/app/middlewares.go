package app

import (
	"context"
	"github.com/sirupsen/logrus"
	"github.com/valyala/fasthttp"
	"gopool/config"
	"gopool/log"
	"net/http"
	"time"
)

func GetCtx(ctx *fasthttp.RequestCtx) context.Context {
	ctxReq, ok := ctx.UserValue("_ctx").(context.Context)
	if !ok {
		panic("not supported here please add TimeoutMiddleware")
	}
	return ctxReq
}

func goRecover(f func(), recovered chan<- interface{}) {
	go func() {
		done := false // just to handle panic(nil) https://github.com/golang/go/issues/25448
		defer func() {
			if !done {
				recovered <- recover()
			}
		}()
		f()
		done = true
	}()
}

func TimeoutMiddleware(h fasthttp.RequestHandler) fasthttp.RequestHandler {
	return fasthttp.CompressHandler(func(ctx *fasthttp.RequestCtx) {
		now := time.Now()
		ctxReq, cancel := context.WithTimeout(context.Background(), config.Config.RequestTimeout)
		defer cancel()
		done := make(chan struct{})
		recovered := make(chan interface{})

		ctx.SetUserValue("_ctx", ctxReq)
		goRecover(func() {
			h(ctx)
			close(done)
		}, recovered)

		select {
		case <-ctxReq.Done():
			log.Log.WithFields(logrus.Fields{
				"duration": time.Since(now),
				"url":      string(ctx.Request.RequestURI()),
			}).WithError(ctxReq.Err()).Error("request timeout")
			ctx.TimeoutErrorWithCode("request_timeout", http.StatusServiceUnavailable)
		case <-done:
			log.Log.WithFields(logrus.Fields{
				"status":   ctx.Response.StatusCode(),
				"duration": time.Since(now),
				"url":      string(ctx.Request.RequestURI()),
			}).Info("request ok")
		case err := <-recovered:
			panic(err) // just do re-panic :D
		}
	})
}

func AdminMiddleware(h fasthttp.RequestHandler) fasthttp.RequestHandler {
	return func(ctx *fasthttp.RequestCtx) {
		realIP := string(ctx.Request.Header.Peek("X-Real-IP"))
		if realIP != "127.0.0.1" {
			SendError(ctx, ResponseError{Message: "only access from localhost"})
			return
		}
		h(ctx)
	}
}

func UserMiddleware(h fasthttp.RequestHandler) fasthttp.RequestHandler {
	return func(ctx *fasthttp.RequestCtx) {
		realIP := string(ctx.Request.Header.Peek("X-Real-IP"))
		if realIP == "127.0.0.1" {
			SendError(ctx, ResponseError{Message: "only access from internet"})
			return
		}
		h(ctx)
	}
}
