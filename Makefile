export PYTHONPATH := app:$(PYTHONPATH)

test:
	python -m unittest discover -s tests/util -v
	python -m unittest discover -s tests/uri -v
	python -m unittest discover -s tests/database -v
