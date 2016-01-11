"""
This script compiles all Javascript for a production environment, as specified in config.BUILD_ENVIRONMENT.
"""

import os
import sys
import subprocess
import argparse
import config
import constants


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--respect-environment',
        help='Compile Javascript according to the build environment specified in config.py',
        action='store_true'
    )
    args = parser.parse_args()

    if args.respect_environment and config.BUILD_ENVIRONMENT == constants.build_environment.DEV:
        print 'Configuration in config.py specified a dev environment.\n' \
              'This script will respect that environment and not compile Javascript; exiting.'
        sys.exit()

    CLOSURE_COMPILER_JAR = 'app/static/lib/closure-compiler/compiler.jar'

    js_files = []
    for directory, subdirectories, files in os.walk('app/static/js'):
        for js_file in files:
            if directory != 'app/static/js/universal':
                js_files.append('{directory}/{js_file}'.format(directory=directory, js_file=js_file))
    js_output_files = map(
        lambda file_path: file_path.replace('static/js', 'static/build/js'),
        js_files,
    )

    for js_file, js_output_file in zip(js_files, js_output_files):
        print 'Compiling {js_file} --> {js_output_file}'.format(js_file=js_file, js_output_file=js_output_file)
        subprocess.call([
            'java', '-jar', CLOSURE_COMPILER_JAR,
            '--js', js_file,
            '--js', 'app/static/js/universal/**.js',
            '--js_output_file', js_output_file,
        ])
