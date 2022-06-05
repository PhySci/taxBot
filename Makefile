docker_build:
	docker build -t taxbot:v0.1 -f ./docker/Dockerfile .
docker_run:
	docker run --rm -it -p 10080:80 --env-file ./.env --name taxbot taxbot:v0.1