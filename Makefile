export PYTHONPATH := app:$(PYTHONPATH)


test:
	python -m unittest discover -s tests -v

test-coverage:
	coverage run --source=app -m unittest discover -s tests -v
