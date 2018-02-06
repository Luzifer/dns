default: container

container:
	docker build --no-cache --pull -t luzifer/dns .
	docker push luzifer/dns

check_zones: .venv
	./.venv/bin/python3 checkZonefile.py

auto-hook-pre-commit: check_zones

.venv:
	virtualenv --python=python3 .venv
	./.venv/bin/pip3 install -r requirements.txt

.PHONY: check_zones auto-hook-pre-commit container
