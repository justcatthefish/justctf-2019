### Ugly website

#### Requirements
- [docker](https://www.docker.com/)
- [docker-compose](https://docs.docker.com/compose/)
- UNIX environment

#### Run
`./run.sh`

#### Usage
Challenge will be available on:
- main page: `http://localhost:8888`

#### Solver
To use the solver the main challange page must be shared to public and two ENVIRONMENT variables must be replaced with the adequate values:
- `SOLVER_DOMAIN`
- `CHALLENGE_BASEURL`   

Then to solve basic version:
- `SOLVER_WHAT=num ./solver.sh`

To solve hard version:
- `SOLVER_WHAT=sgn ./solver.sh`
