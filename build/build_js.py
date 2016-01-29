"""
This script compiles all Javascript for a production environment, as specified in config.BUILD_ENVIRONMENT.
"""

import os
import sys
import subprocess
import argparse
import config
import constants


def abort_if_error(return_code):
    if return_code != 0:
        sys.exit(return_code)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config-environment',
        help='Compile Javascript according to the build environment specified in config.py',
        action='store_true'
    )
    parser.add_argument(
        '--dev',
        help='Don\'t compile Javascript',
        action='store_true'
    )
    parser.add_argument(
        '--prod',
        help='Compile Javascript at the default optimization level',
        action='store_true'
    )
    args = parser.parse_args()

    num_args = len(filter(lambda arg: arg, [args.config_environment, args.dev, args.prod]))
    if num_args > 1:
        print 'Arguments are ambiguous. Choose only one of --config-environment, --dev, and --prod.\nExiting.'
        sys.exit(1)
    if num_args == 0:
        print 'No arguments passed. Choose only one of --config-environment, --dev, and --prod.\nExiting.'
        sys.exit(1)

    style = 'expanded'
    if args.config_environment:
        if config.BUILD_ENVIRONMENT == constants.build_environment.DEV:
            print 'Configuration in config.py specified a dev environment.\n' \
                  'Skipping compilation of Javascript.'
            sys.exit()
        else:
            print 'Configuration in config.py specified a dev environment.\n' \
                  'Compiling Javascript with default optimizations.'
    if args.dev:
        print 'Skipping compilation of Javascript.'
        sys.exit()
    if args.prod:
        print 'Compiling Javascript with default optimizations.'

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

    print 'Javascript build started.'
    for js_file, js_output_file in zip(js_files, js_output_files):
        print 'Compiling {js_file} --> {js_output_file}'.format(js_file=js_file, js_output_file=js_output_file)
        abort_if_error(subprocess.call([
            'java', '-jar', CLOSURE_COMPILER_JAR,
            '--js', js_file,
            '--js', 'app/static/js/universal/**.js',
            '--js_output_file', js_output_file,
        ]))
    print 'Javascript build complete.'
