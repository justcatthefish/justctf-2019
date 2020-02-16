package app

import (
	"encoding/json"
	"fmt"
	"github.com/valyala/fasthttp"
	"gopool/config"
	"net/http"
	"net/url"
	"strings"
)

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
		SendData(ctx, dbComments)
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
		reqCtx := GetCtx(ctx)
		realIP := string(ctx.Request.Header.Peek("X-Real-IP"))

		sandboxPath := string(ctx.Request.Header.Peek("X-Sandbox-Path"))
		visitUrl := fmt.Sprintf("http://127.0.0.1/%s/admin/", sandboxPath)
		postData := url.Values{
			"url":          []string{visitUrl},
			"sandbox_path": []string{sandboxPath},
			"user_ip":      []string{realIP},
		}

		req, err := http.NewRequest("POST", config.Config.BotURL, strings.NewReader(postData.Encode()))
		if err != nil {
			// bot not working
			ctx.SetStatusCode(500)
			return
		}
		req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
		req = req.WithContext(reqCtx)

		resp, err := http.DefaultClient.Do(req)
		if err != nil {
			// bot not working
			ctx.SetStatusCode(500)
			return
		}

		if resp.StatusCode == http.StatusTooManyRequests {
			// bot is to busy
			ctx.SetStatusCode(http.StatusTooManyRequests)
			return
		}
		if resp.StatusCode == http.StatusRequestTimeout {
			// bot process request with timeout
			ctx.SetStatusCode(http.StatusRequestTimeout)
			return
		}
		if resp.StatusCode == http.StatusGone {
			// bot maybe error
			ctx.SetStatusCode(http.StatusGone)
			return
		}

		// im fine
		ctx.SetStatusCode(201)
	}
}

func HandleFlag() fasthttp.RequestHandler {
	return func(ctx *fasthttp.RequestCtx) {
		SendData(ctx, map[string]string{"flag": config.Config.Flag})
	}
}
