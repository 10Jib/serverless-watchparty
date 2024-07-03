FROM node:current-alpine

WORKDIR /app
COPY start.sh /app
RUN chmod +x /app/start.sh

RUN apt-get update && apt-get install -y git

# need a better way for process managment
# RUN npm install -g pm2

RUN git clone https://github.com/howardchung/watchparty.git /app
WORKDIR /app
RUN git checkout a5d75fadcfb7e75f4b7864fd8e8c1b4f88de1513
# should do a multi stage build to reduce image size


RUN npm install
RUN npm run build


ENV port=3000
EXPOSE 3000

CMD ["/app/start.sh"]