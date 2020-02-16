package app

import (
	"encoding/json"
	"github.com/valyala/fasthttp"
	"gopool/config"
	"gopool/log"
	"net/http"
	"strings"
	"time"
)

func init() {
	http.DefaultClient.Timeout = time.Second
}

var dbComments []Comment

func init() {
	dbComments = make([]Comment, 0, 100)
}

type Comment struct {
	ID       int    `json:"id"`
	Nickname string `json:"nickname"`
	Message  string `json:"comment"`
}

func HandleComments() fasthttp.RequestHandler {
	return func(ctx *fasthttp.RequestCtx) {
		json.NewEncoder(ctx.Response.BodyWriter()).Encode(dbComments)
	}
}

func HandleCommentAdd() fasthttp.RequestHandler {
	type request struct {
		Nickname string `json:"nickname"`
		Comment  string `json:"comment"`
	}

	return func(ctx *fasthttp.RequestCtx) {
		var v request
		if err := json.Unmarshal(ctx.Request.Body(), &v); err != nil {
			// invalid json
			ctx.SetStatusCode(400)
			return
		}

		if len(v.Nickname) > 64 || len(v.Comment) > 500 {
			// big values
			ctx.SetStatusCode(400)
			return
		}

		if len(dbComments) > 100 {
			// comments limit hit
			ctx.SetStatusCode(400)
			return
		}

		dbComments = append(dbComments, Comment{
			Nickname: v.Nickname,
			Message:  v.Comment,
		})
		ctx.SetStatusCode(201)
	}
}

func HandleMemeReport() fasthttp.RequestHandler {
	return func(ctx *fasthttp.RequestCtx) {
		url := string(ctx.Request.PostArgs().Peek("url"))
		if !strings.HasPrefix(url, "http://") {
			ctx.SetStatusCode(400)
			return
		}

		logger := log.Log.WithField("url", url)
		logger.Info("start request")

		_, err := http.Get(url)
		if err != nil {
			logger.WithError(err).Info("err request")
			ctx.SetStatusCode(500)
			return
		}
		logger.Info("ok request")

		ctx.SetStatusCode(201)
	}
}

func HandleFlag() fasthttp.RequestHandler {
	return func(ctx *fasthttp.RequestCtx) {
		json.NewEncoder(ctx.Response.BodyWriter()).Encode(map[string]string{"flag": config.Config.Flag})
	}
}
