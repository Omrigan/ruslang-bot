docker build -t russian-bot .
docker stop russian-bot
docker rm russian-bot
docker run --restart=always -d --name russian-bot russian-bot