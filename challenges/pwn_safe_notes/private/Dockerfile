FROM disconnect3d/nsjail:2.9

RUN apt update && apt install -y libssl1.1 && rm -rf /var/lib/apt/lists/*


RUN groupadd -g 99999 jailed && \
    useradd --uid 99999 --gid 99999 jailed && \
    mkdir /home/jailed && \
    chown jailed /home/jailed -R && \
    chmod 755 /home/jailed -R

RUN mkdir /task
ADD ./program /task/safe-notes
ADD ./flag.txt /task/flag.txt
ADD ./nsjail.cfg /nsjail.cfg
ADD ./run_task.sh /run_task.sh

CMD /run_task.sh
