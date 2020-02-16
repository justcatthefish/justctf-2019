FROM disconnect3d/nsjail:2.9

RUN apt-get update && apt-get install -y \
 gcc python3

RUN groupadd -g 1000 aturing && \
    useradd --uid 1000 --gid 1000 aturing && \
    mkdir /home/aturing && \
    chown aturing /home/aturing -R && \
    chmod 755 /home/aturing -R

RUN tac /etc/passwd > /tmp/a && mv /tmp/a /etc/passwd
RUN mkdir /home/aturing/submission
ADD ./willitstop /home/aturing/submission/
ADD flag flag.txt /home/aturing/
ADD ./nsjail.cfg /nsjail.cfg
ADD ./run_task.sh /run_task.sh


CMD /run_task.sh
