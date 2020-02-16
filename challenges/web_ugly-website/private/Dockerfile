FROM node:10

COPY package*.json ./

RUN npm install

# nie wiem co to, ale bylo zeby dodac xd
RUN npm ci --only=production
ENV NODE_ENV "production"

RUN groupadd -g 99999 justctf && \
    useradd --uid 99999 --gid 99999 justctf && \
    mkdir /home/justctf && \
    chown justctf /home/justctf -R && \
    chmod 755 /home/justctf -R

WORKDIR /home/justctf/
USER justctf

COPY *.js ./
COPY *.json ./
COPY static static
COPY views views

EXPOSE 8080
CMD [ "node", "server.js" ]
