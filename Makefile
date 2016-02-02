all:
	mkdir -p build
	java -jar lib/compiler.jar --js static/controller.js --js_output_file build/controller.js
	sass static/stylesheet.scss:build/stylesheet.css --style compressed

clean:
	rm -rf build
