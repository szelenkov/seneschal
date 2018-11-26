init:
    pipenv install -e

test:
    py.test tests

.PHONY: init test
