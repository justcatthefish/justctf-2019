FROM disconnect3d/pwntools:3.13.0-ubuntu18.04

RUN apt update && apt install -y hashcash python3 python3-pip libgmp3-dev libmpc-dev python-gmpy && rm -rf /var/lib/apt/lists/*
RUN pip3 install gmpy2
RUN pip3 install --upgrade git+https://github.com/arthaud/python3-pwntools.git

RUN mkdir /solv
ADD ./ec.py /solv/ec.py
ADD ./hashcash.py ./solv/hashcash.py
ADD ./solv.py ./solv/solv.py
ADD ./utils.py ./solv/utils.py
