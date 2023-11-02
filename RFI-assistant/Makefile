.PHONY: setup
setup: #download_demo_data ## Setup
	python3.10 -m venv .waveenv
	./.waveenv/bin/python3.10 -m pip install --upgrade pip
	./.waveenv/bin/python3.10 -m pip install wheel
	./.waveenv/bin/python3.10 -m pip install -r requirements.txt
	mkdir -p ./var/lib/tmp/jobs

.PHONY: run
run: ## Run the App (run `make setup` first)
	./.waveenv/bin/wave run src.app

.PHONY: clean
clean: ## Remove all files produced by `make`
	rm -rf .waveenv
	rm -rf ./var

