package app

import (
	"context"
	"errors"
	"fmt"
	"github.com/tebeka/selenium"
	"github.com/tebeka/selenium/chrome"
	"gopoolbot/config"
	"gopoolbot/log"
	"net"
	"net/http"
	"sync"
	"time"
)

func GetFreePort() (int, error) {
	addr, err := net.ResolveTCPAddr("tcp", "localhost:0")
	if err != nil {
		return 0, err
	}

	l, err := net.ListenTCP("tcp", addr)
	if err != nil {
		return 0, err
	}
	defer l.Close()
	return l.Addr().(*net.TCPAddr).Port, nil
}

type browser struct {
	port    int
	service *selenium.Service
}

func NewBrowser() (*browser, error) {
	freePort, err := GetFreePort()
	if err != nil {
		return nil, err
	}
	opts := []selenium.ServiceOption{
		//selenium.Output(os.Stderr),
	}
	service, err := selenium.NewChromeDriverService(config.Config.ChromeDriverPath, freePort, opts...)
	if err != nil {
		return nil, err
	}

	s := &browser{
		service: service,
		port:    freePort,
	}
	return s, nil
}

func (b *browser) Get(url string) error {
	caps := selenium.Capabilities{
		"browserName": "chrome",
	}
	caps.AddChrome(chrome.Capabilities{
		Args: []string{
			"--no-sandbox",
			"--headless",
			"--window-size=1420,1080",
			"--disable-gpu",
		},
	})
	browser, err := selenium.NewRemote(caps, fmt.Sprintf("http://localhost:%d/wd/hub", b.port))
	if err != nil {
		return err
	}
	defer browser.Quit()

	err = browser.SetPageLoadTimeout(time.Second * 10)
	if err != nil {
		return err
	}

	err = browser.Get(url)
	if err != nil {
		return err
	}

	time.Sleep(time.Second * 2)

	//output, _ := browser.PageSource()
	//log.Log.Infof("output: %v", output)
	return nil
}

func (b *browser) Close() error {
	return b.service.Stop()
}

///
type jobResult struct {
	ID       int
	Url      string
	Deadline <-chan struct{}
	Finished chan<- error
}

func worker(workerID int, jobs <-chan jobResult) {
	for job := range jobs {
		log.Log.WithField("id", job.ID).WithField("worker", workerID).Info("started job")

		select {
		case <-job.Deadline:
			log.Log.WithField("id", job.ID).WithField("worker", workerID).Info("cancel job")
			continue
		default:
		}

		err := (func(url string) error {
			b, err := NewBrowser()
			if err != nil {
				return err
			}
			defer b.Close()

			err = b.Get(url)
			if err != nil {
				return err
			}
			return nil
		})(job.Url)

		select {
		case job.Finished <- err:
		default:
		}

		log.Log.WithField("id", job.ID).WithField("worker", workerID).WithError(err).Info("finished job")
	}
}

type browserPool struct {
	jobs chan jobResult
}

func NewBrowserPool() *browserPool {
	s := &browserPool{
		jobs: make(chan jobResult, config.Config.BotWorkers*config.Config.BotPoolPerWorker),
	}
	for w := 1; w <= config.Config.BotWorkers; w++ {
		go worker(w, s.jobs)
	}
	return s
}

var ErrPoolIsFull = errors.New("pool is full")

func (p *browserPool) AddJobWait(ctx context.Context, url string) error {
	fin := make(chan error)
	job := jobResult{
		ID:       int(time.Now().UnixNano()),
		Url:      url,
		Deadline: ctx.Done(),
		Finished: fin,
	}
	select {
	case p.jobs <- job:
	default:
		return ErrPoolIsFull
	}

	select {
	case err := <-fin:
		return err
	case <-ctx.Done():
		return ctx.Err()
	}
}

func BotHandler(p *browserPool) http.HandlerFunc {
	rateLimiter := &sync.Map{}

	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "GET" {
			w.Header().Set("Content-Type", "text/html")
			fmt.Fprintf(w, `
<form method="POST">
    <label>URL:</label>
    <input type="text" value="https://twitter.com/patryk4815" name="url"/>
	<button>send url</button>
</form>
`)
			return
		}
		if err := r.ParseForm(); err != nil {
			fmt.Fprintf(w, "ParseForm() err: %v", err)
			return
		}
		url := r.FormValue("url")
		userIP := r.FormValue("user_ip")
		sandboxPath := r.FormValue("sandbox_path")
		logger := log.Log.WithField("user_ip", userIP).WithField("sandbox_path", sandboxPath)

		if value, ok := rateLimiter.Load(sandboxPath); ok {
			castedValue := value.(time.Time)
			if castedValue.After(time.Now()) {
				logger.Warning("rate limited by sandbox path")
				w.WriteHeader(http.StatusTooManyRequests)
				fmt.Fprintf(w, "AddJobWait() err: rate limited by sandbox path")
				return
			}
		}

		expireAt := time.Now().Add(config.Config.RateLimitPerSandbox)
		rateLimiter.Store(sandboxPath, expireAt)

		ctx, cancel := context.WithTimeout(context.Background(), time.Second*20)
		defer cancel()

		if err := p.AddJobWait(ctx, url); err != nil {
			if err == ErrPoolIsFull {
				w.WriteHeader(http.StatusTooManyRequests)
			} else if err == context.DeadlineExceeded {
				w.WriteHeader(http.StatusRequestTimeout)
			} else {
				w.WriteHeader(http.StatusGone)
			}
			logger.Warning("bot page err")
			fmt.Fprintf(w, "AddJobWait() err: %v", err)
		} else {
			fmt.Fprintf(w, "AddJobWait() success")
		}
	}
}
