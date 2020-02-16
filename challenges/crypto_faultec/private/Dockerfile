FROM disconnect3d/nsjail:2.9

RUN apt-get update && apt-get -y install python3 python3-pip libgmp3-dev libmpc-dev python-gmpy && rm -rf /var/lib/apt/lists/*
RUN pip3 install gmpy2

RUN groupadd -g 99999 jailed && \
    useradd --uid 99999 --gid 99999 jailed && \
    mkdir /home/jailed && \
    chown jailed /home/jailed -R && \
    chmod 755 /home/jailed -R

ADD ./ec.py /home/jailed/ec.py
ADD ./hashcash.py /home/jailed/hashcash.py
ADD ./fault.py /home/jailed/fault.py
ADD ./secret.py /home/jailed/secret.py
ADD ./utils.py /home/jailed/utils.py

ADD ./nsjail.cfg /nsjail.cfg
ADD ./run_task.sh /run_task.sh

RUN chmod +x /run_task.sh
CMD /run_task.sh
