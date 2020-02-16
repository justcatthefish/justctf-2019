W Dockerfile podmienić `SOLVER_DOMAIN` i `CHALLENGE_BASEURL` na odpowiednie wartosci, gdzie solver_domain to IP/domena solvera dostepnego na zewnatrz, a challenge_baseurl to adres challenge.

Następnie

Docker build
```sh
docker build -t terjanq/ugly-website-solver .
```

Docker run
```sh
docker run --rm -p 337:8888 -it terjanq/ugly-website-solver
```

Zalogować się na admina: `http://terjanq.cf:1337/s3rcet_adm1n_l0gin?token=4e062a879b31892d3c724bc0aaa0411fd4be40b7b57ec2f41fd08b5529d493f9`

Wygenerowany plik w dockerze `sgn.css` zauploadowac adminowi jako stylesheet na stronie, następnie wrócić na stronę główną.

Poczekać jakąs minutę, w logach `server.py` powinna się znaleźć flaga. 