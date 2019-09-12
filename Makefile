default: container

container:
	docker build --no-cache --pull -t luzifer/dns .
	bash -eo pipefail -c '[ "$(REF)" == "refs/heads/master" ] && docker push luzifer/dns || true'

.venv:
	virtualenv --python=python3 .venv
	./.venv/bin/pip3 install -r requirements.txt

alpine-prereq:
	apk --no-cache add make python3
	pip3 install virtualenv

.PHONY: container
