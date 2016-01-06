export PYTHONPATH := app:$(PYTHONPATH)

test:
	python -m unittest discover -s tests/util -v
	python -m unittest discover -s tests/uri -v
