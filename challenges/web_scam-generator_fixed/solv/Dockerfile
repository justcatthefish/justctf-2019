FROM python:3.7.5-buster

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

ARG TASK_ENVS

RUN mkdir -p /home/justctf && \
    mkdir -p /home/justctf/code/ && \
    groupadd -g 99999 justctf && \
    useradd --uid 99999 --gid 99999 justctf && \
    chown justctf /home/justctf -R && \
    chmod 755 /home/justctf -R

WORKDIR /home/justctf/code/
USER justctf
COPY . .

ENV TASK_ENVS=$TASK_ENVS

CMD ["python", "solve.py"]
