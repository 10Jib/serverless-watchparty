FROM node:current-alpine

RUN apk add git

# need a better way for process managment
# RUN npm install -g pm2

RUN git clone https://github.com/howardchung/watchparty.git /app

WORKDIR /app
COPY start.sh .
RUN chmod +x start.sh

RUN git checkout a5d75fadcfb7e75f4b7864fd8e8c1b4f88de1513
# should do a multi stage build to reduce image size


RUN npm install
RUN npm run build


ENV PORT=3000
EXPOSE 3000

CMD ["./start.sh"]
