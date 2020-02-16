#!/bin/bash

docker run --rm -it -v $(pwd)/solv:/code -w /code golang:1.13-alpine go run main_solver.go -address $1
