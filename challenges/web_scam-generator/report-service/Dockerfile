FROM python:3.7.5-buster

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN mkdir -p /home/justctf/db/ && \
    mkdir -p /home/justctf/sessions/ && \
    mkdir -p /home/justctf/code/ && \
    groupadd -g 99999 justctf && \
    useradd --uid 99999 --gid 99999 justctf && \
    mkdir -p /home/justctf && \
    chown justctf /home/justctf -R && \
    chmod 755 /home/justctf -R

WORKDIR /home/justctf/code/
USER justctf
COPY . .

USER root
RUN chmod +x run.sh

USER justctf
CMD ["./run.sh"]
