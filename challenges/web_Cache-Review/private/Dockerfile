# build bot
FROM golang:1.13.4-stretch as builder_manager
WORKDIR /code/
COPY manager .
RUN go build -v ./cmd/main/

# build meme
FROM golang:1.13.4-stretch as builder_sandbox
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

RUN groupadd -g 99999 justctf && \
    useradd --uid 99999 --gid 99999 justctf && \
    mkdir /home/justctf && \
    chown justctf /home/justctf -R && \
    chmod 755 /home/justctf -R

WORKDIR /home/justctf/
USER justctf
COPY --from=builder_sandbox /code/main sandbox
COPY --from=builder_manager /code/main manager
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY public /public/
COPY web /public/web/
COPY bot /public/bot/

# nginx files
USER root
RUN mkdir -p /nginx/proxy && \
    mkdir -p /nginx/cache && \
    mkdir -p /nginx/body && \
    mkdir -p /nginx/fastcgi && \
    mkdir -p /nginx/uwsgi && \
    mkdir -p /nginx/scgi && \
    chown www-data /nginx/ -R && \
    chmod 755 /nginx/ -R

# scripts
USER root
COPY scripts /scripts
RUN chmod +x /scripts/create.sh && \
    chmod +x /scripts/destory.sh && \
    chmod +x /scripts/iptables.sh && \
    chmod +x /scripts/run.sh
CMD ["/scripts/run.sh"]
