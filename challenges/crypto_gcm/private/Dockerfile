FROM disconnect3d/nsjail:2.9

RUN apt-get update && apt-get -y install clang libssl-dev && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 99999 jailed && \
    useradd --uid 99999 --gid 99999 jailed && \
    mkdir /home/jailed && \
    chown jailed /home/jailed -R && \
    chmod 755 /home/jailed -R

ADD ./gcm.c /home/jailed/gcm.c
ADD ./run_task.sh /run_task.sh
ADD ./nsjail.cfg /nsjail.cfg

# Instead of compiling every time we will just copy a precompiled version there
#RUN clang -lcrypto -O2 home/jailed/gcm.c -o /home/jailed/gcm
ADD ./gcm /home/jailed/gcm

RUN chmod +x /run_task.sh
CMD /run_task.sh
