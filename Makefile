all:
	$(MAKE) dependencies
	$(MAKE) default

default:
	pre-commit run --all-files
	mkdir -p build
	java -jar lib/compiler.jar --js static/controller.js --js_output_file build/controller.js
	sass static/stylesheet.scss:build/stylesheet.css --style compressed

dependencies:
	gem install sass
	pip install pre-commit
	pre-commit install
	pre-commit autoupdate

clean:
	rm -rf build
