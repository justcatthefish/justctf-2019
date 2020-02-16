# build bot
FROM golang:1.13.4-stretch as builder_bot
WORKDIR /code/
COPY bot .
RUN go build -v ./cmd/main/

# build meme
FROM golang:1.13.4-stretch as builder_meme
WORKDIR /code/
COPY web .
RUN go build -v ./cmd/main/

FROM ubuntu:18.04
RUN apt-get update -y && apt-get install -y wget curl unzip gnupg

# install nginx
RUN apt-get install -y nginx

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -  && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get -y update && \
    apt-get install -y google-chrome-stable

# install chromedriver
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip && \
        unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# install iptables
RUN apt-get install -y iptables

WORKDIR /root/
COPY --from=builder_meme /code/main meme
COPY --from=builder_bot /code/main bot
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY scripts scripts
RUN chmod +x scripts/iptables.sh && \
    chmod +x scripts/run.sh

COPY . /public/

CMD ["./scripts/run.sh"]
