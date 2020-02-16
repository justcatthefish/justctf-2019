### Cache review but with no presents

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
`./solver.sh "http://<domain>" "<sandbox_hash>"`

#### Bugs
- nginx alias traversal by `static../`
- misconfigured nginx proxy_cache_key, basic cache poisoning
