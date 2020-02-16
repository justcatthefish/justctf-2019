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
	Listen              string        `default:"0.0.0.0:8080" split_words:"true"`
	ChromeDriverPath    string        `default:"/usr/local/bin/chromedriver" split_words:"true"`
	CreateSandboxSh     string        `default:"/scripts/create.sh" split_words:"true"`
	DestroySandboxSh    string        `default:"/scripts/destory.sh" split_words:"true"`
	SandboxDuration     time.Duration `default:"600s" split_words:"true"`
	SandboxNewCreation  time.Duration `default:"300s" split_words:"true"`
	OneTimeHashDuration time.Duration `default:"30s" split_words:"true"`
	RateLimitPerSandbox time.Duration `default:"10s" split_words:"true"`

	HashcashDifficult int `default:"20" split_words:"true"`

	BotWorkers       int `default:"10" split_words:"true"`
	BotPoolPerWorker int `default:"10" split_words:"true"`

	DbFile string `default:"/tmp/sqllite.db" split_words:"true"`

	Flag string `default:"justCTF{here_should_be_real_flag}" split_words:"true"`
}
