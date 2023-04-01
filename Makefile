.DEFAULT_GOAL := lint

.PHONY: lint
lint:
	ansible-lint meta/main.yml
	ansible-lint tasks/main.yml
	ansible-lint tests/test.yml