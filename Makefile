default: container

container:
	docker build --no-cache --pull -t luzifer/dns .
	docker push luzifer/dns

.venv:
	virtualenv --python=python3 .venv
	./.venv/bin/pip3 install -r requirements.txt

auto-hook-pre-commit: .venv
	./.venv/bin/python3 checkZonefile.py
