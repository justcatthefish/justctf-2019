FROM opensuse/leap:15.1

# for debugging
#RUN zypper install -y socat tmux

# install nsjail here
# hash sie nie zgadza!
RUN zypper --no-gpg-checks install -y https://download.opensuse.org/repositories/security/openSUSE_Leap_15.1/x86_64/nsjail-2.8-lp151.11.2.x86_64.rpm

RUN groupadd -g 99999 jailed && \
    useradd --uid 99999 --gid 99999 jailed && \
    mkdir /home/jailed && \
    chown jailed /home/jailed -R && \
    chmod 755 /home/jailed -R

RUN mkdir /task
#RUN mkdir /task_private
ADD ./phonebook /task/
ADD ./flag.txt /task/
#ADD ./libc.so.6 /task_private/
ADD ./nsjail.cfg /nsjail.cfg
ADD ./run_task.sh /run_task.sh

CMD /run_task.sh
