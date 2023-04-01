.DEFAULT_GOAL := test

.PHONY: lint
lint:
	ansible-lint meta/main.yml
	ansible-lint tasks/main.yml
	ansible-lint tests/test.yml

.PHONY: test
test:
	pre-commit run --all-files --show-diff-on-failure
