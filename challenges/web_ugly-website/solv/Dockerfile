FROM python:3.6

WORKDIR /solver

RUN pip install z3-solver
RUN pip install Flask
RUN pip install requests

COPY server.py .
COPY z3solver.py .
COPY rules.py .

EXPOSE 8888
CMD [ "python3", "server.py" ]