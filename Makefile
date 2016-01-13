export PYTHONPATH := app:$(PYTHONPATH)


all:
	$(MAKE) test-coverage
	$(MAKE) default

skip-tests:
	$(MAKE) default

default:
	pip install -r requirements.txt
	mkdir -p app/static/build/js
	mkdir -p app/static/build/css
	python build/build_database.py --create
	python build/build_js.py --respect-environment
	python build/build_css.py

clean:
	rm -rf app/static/build
	python build/build_database.py --drop

test:
	python -m unittest discover -s tests -v

test-coverage:
	coverage run --source=app -m unittest discover -s tests -v
	coverage report -m
