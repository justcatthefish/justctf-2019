package app

import (
	"bytes"
	"encoding/json"
	"io"
	"sync"
)

// just check interface at compilation time
var _ io.Reader = &responseBuffer{}
var _ io.ReadCloser = &responseBuffer{}

var responseBufferPool = sync.Pool{
	New: func() interface{} {
		return new(bytes.Buffer)
	},
}

type responseBuffer struct {
	buffer *bytes.Buffer
}

func (b *responseBuffer) Read(p []byte) (int, error) {
	return b.buffer.Read(p)
}

func (b *responseBuffer) Close() error {
	responseBufferPool.Put(b.buffer)
	return nil
}

type RequestData interface {
	SetStatusCode(int)
	SetBodyStream(io.Reader, int)
	SetBodyString(string)
}

func SendJson(ctx RequestData, code int, v interface{}) {
	buf := responseBufferPool.Get().(*bytes.Buffer)
	e := json.NewEncoder(buf)
	e.SetEscapeHTML(false)
	if err := e.Encode(v); err != nil {
		ctx.SetStatusCode(500)
		ctx.SetBodyString(err.Error())
		return
	}

	ctx.SetStatusCode(code)
	ctx.SetBodyStream(&responseBuffer{buf}, -1)
}

type ResponseError struct {
	Message string `json:"message"`
}

type ResponseData struct {
	Error *ResponseError `json:"error,omitempty"`
	Data  interface{}    `json:"data,omitempty"`
}

func SendError(ctx RequestData, v ResponseError) {
	SendJson(ctx, 422, ResponseData{Error: &v})
}

func SendData(ctx RequestData, v interface{}) {
	SendJson(ctx, 200, ResponseData{Data: v})
}
