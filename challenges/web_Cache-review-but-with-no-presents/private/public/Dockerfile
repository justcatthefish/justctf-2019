# build meme
FROM golang:1.13.4-stretch as builder_meme
WORKDIR /code/
COPY web .
RUN go build -v ./cmd/main/

FROM ubuntu:18.04
RUN apt-get update -y && apt-get install -y wget curl unzip gnupg

# install nginx
RUN apt-get install -y nginx

# install iptables
RUN apt-get install -y iptables

WORKDIR /root/
COPY --from=builder_meme /code/main meme
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY scripts scripts
COPY scripts scripts
RUN chmod +x scripts/iptables.sh && \
    chmod +x scripts/run.sh

COPY . /public/

CMD ["./scripts/run.sh"]
