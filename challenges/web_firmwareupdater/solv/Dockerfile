FROM ubuntu:18.04

RUN apt-get update && apt-get install -y zip curl &&rm -rf /var/lib/apt/lists/*

RUN mkdir /solv
ADD solver.sh /solv/solver.sh
