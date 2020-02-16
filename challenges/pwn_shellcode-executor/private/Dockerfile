FROM disconnect3d/nsjail:2.9

RUN groupadd -g 99999 jailed && \
    useradd --uid 99999 --gid 99999 jailed && \
    mkdir /home/jailed && \
    chown jailed /home/jailed -R && \
    chmod 755 /home/jailed -R

RUN mkdir /task
ADD ./shellcodeexecutor /task/
ADD ./nsjail.cfg /nsjail.cfg
ADD ./run_task.sh /run_task.sh

CMD /run_task.sh
