.PHONY: clean
clean:
	rm -rf venv

.PHONY: setup
setup:
	python3.10 -m venv venv
	./venv/bin/python3 -m pip install --upgrade pip
	./venv/bin/pip3 install -r requirements.txt

.PHONY: local-dev
local-dev:
	H2O_WAVE_NO_LOG=True ./venv/bin/wave run src.app

.PHONY: format
format:
	./venv/bin/pip3 install black
	./venv/bin/pip3 install isort
	./venv/bin/isort src/*.py
	./venv/bin/black src/*.py