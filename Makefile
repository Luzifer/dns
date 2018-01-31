default: container

container:
	docker build --no-cache --pull -t luzifer/dns .
	docker push luzifer/dns
