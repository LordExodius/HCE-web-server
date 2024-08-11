include .env

build:
	docker build -t hce/webserver .

deploy:
	docker run -d \
	--name hce-webserver \
	-p $(HOST_REST_PORT):8502 hce/webserver

deploy-local:
	docker run -d \
	--name hce-webserver \
	-e PORT=$(HOST_REST_PORT) \
	-p $(HOST_REST_PORT):8502 hce/webserver

deploy-shared:
	docker run -d \
	--name hce-webserver \
	-e DOCKER_SHARED_IP="172.17.0.1:8501" \
	-p $(HOST_REST_PORT):8502 hce/webserver 

clean:
	docker container rm -f hce-webserver

deploy-clean:
	docker container rm -f hce-webserver
	docker build -t hce/webserver .
	docker run -d --name hce-webserver \
	-p $(HOST_REST_PORT):8502 hce/webserver 

deploy-clean-local:
	docker container rm -f hce-webserver

	docker build -t hce/webserver .

	docker run -d \
	--name hce-webserver \
	-e PORT=$(HOST_REST_PORT) \
	-p $(HOST_REST_PORT):8502 hce/webserver 

deploy-shared-clean:
	docker container rm -f hce-webserver

	docker build -t hce/webserver .
	docker run -d \
	--name hce-webserver \
	-e DOCKER_SHARED_IP="172.17.0.1:8501" \
	-p $(HOST_REST_PORT):8502 hce/webserver 

