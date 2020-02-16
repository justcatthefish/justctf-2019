package config

import (
	"github.com/kelseyhightower/envconfig"
	"log"
	"time"
)

var Config *config

func init() {
	var s config
	err := envconfig.Process("", &s)
	if err != nil {
		log.Fatal(err.Error())
	}
	Config = &s
}

type config struct {
	RequestTimeout time.Duration `default:"25s" split_words:"true"`
	UnixSocket     string        `default:"/tmp/server.unix" split_words:"true"`
	Flag           string        `default:"justCTF{here_should_be_real_flag}" split_words:"true"`
}
