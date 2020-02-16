FROM sagemath/sagemath:8.9

# Required by solver
RUN sage --pip install pycrypto repoze.lru

ADD solve.sage /home/sage/solve.sage
ADD utils.py /home/sage/utils.py

WORKDIR /home/sage
