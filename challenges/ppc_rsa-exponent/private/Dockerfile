FROM disconnect3d/nsjail:2.9

RUN groupadd -g 99999 jailed && \
    useradd --uid 99999 --gid 99999 jailed && \
    mkdir /home/jailed && \
    chown jailed /home/jailed -R && \
    chmod 755 /home/jailed -R

RUN apt-get update && apt-get install -y python3 python3-gmpy2 && rm -rf /var/lib/apt/lists/*

RUN mkdir /task

ADD ./private.py /task/private.py
ADD ./public.py /task/public.py
ADD ./flag.txt /task/flag.txt

ADD ./nsjail.cfg /nsjail.cfg
ADD ./run_task.sh /run_task.sh

CMD /run_task.sh
