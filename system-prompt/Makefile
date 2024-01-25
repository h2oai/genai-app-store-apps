.PHONY: clean
clean:
	rm -rf venv

venv:
	python3.10 -m venv venv

.PHONY: setup
setup: venv
	./venv/bin/python3 -m pip install --upgrade pip
	./venv/bin/pip3 install -r requirements.txt

.PHONY: local-dev
local-dev:
	./venv/bin/wave run app

.PHONY: format
format:
	./venv/bin/pip3 install black
	./venv/bin/pip3 install isort
	./venv/bin/isort *.py
	./venv/bin/black *.py