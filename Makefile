default: container

container:
	docker build --no-cache --pull -t luzifer/dns .
	docker push luzifer/dns

check_zones: .venv
	./.venv/bin/python3 checkZonefile.py

.venv:
	virtualenv --python=python3 .venv
	./.venv/bin/pip3 install -r requirements.txt

alpine-prereq:
	apk --no-cache add make python3
	pip3 install virtualenv

.PHONY: check_zones container
