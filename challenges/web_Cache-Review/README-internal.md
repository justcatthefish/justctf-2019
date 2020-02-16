### Cache Review

#### Requirements
- [docker](https://www.docker.com/)
- [docker-compose](https://docs.docker.com/compose/)
- UNIX

#### Run
`./run.sh`

#### Usage
Challenge will be available on:
`http://localhost:80`

#### Solver
`./healtcheck.sh <ip/domain>:<port>`

#### Bugs
- nginx alias traversal by `static../`
- misconfigured nginx proxy_cache_key, basic cache poisoning
- misconfigured sync.Pool, not clearing buffer before `Put` to pool again
