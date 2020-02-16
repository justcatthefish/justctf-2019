FROM disconnect3d/nsjail:2.9

RUN groupadd -g 99999 jailed && \
    useradd --uid 99999 --gid 99999 jailed && \
    mkdir /home/jailed && \
    chown jailed /home/jailed -R && \
    chmod 755 /home/jailed -R

RUN mkdir /task

ADD ./binary/atm /task/
ADD ./nsjail.cfg /nsjail.cfg
ADD ./run_task.sh /run_task.sh

ADD flag.txt /task/flag.txt

# For debugging
#RUN apt-get update && \
#    apt-get install -y gdb python git python-pip && \
#    pip install pwntools && \
#    git clone https://github.com/pwndbg/pwndbg /pwndbg && \
#    cd /pwndbg && ./setup.sh

CMD /run_task.sh
