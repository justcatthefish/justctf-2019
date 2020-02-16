FROM disconnect3d/nsjail:2.9

RUN groupadd -g 99999 jailed && \
    useradd --uid 99999 --gid 99999 jailed && \
    mkdir /home/jailed && \
    chown jailed /home/jailed -R && \
    chmod 755 /home/jailed -R

RUN apt-get update && apt-get install -y python3 && rm -rf /var/lib/apt/lists/*

RUN mkdir /task

ADD ./md5service.py /task/md5service.py
ADD ./md5service.sh /task/md5service.sh

# Add flag
RUN mkdir /0c8702194e16f006e61f45d5fa0cd511
ADD ./flag_a6214417905b7d091f00ff59b51d5d78.txt /0c8702194e16f006e61f45d5fa0cd511/flag_a6214417905b7d091f00ff59b51d5d78.txt

ADD ./nsjail.cfg /nsjail.cfg
ADD ./run_task.sh /run_task.sh

CMD /run_task.sh
