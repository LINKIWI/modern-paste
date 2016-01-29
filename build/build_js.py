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
    """
    Abort the build if the return code of a subprocess call is nonzero.

    :param return_code: Return code of subprocess call
    """
    if return_code != 0:
        sys.exit(return_code)


def is_multipart_controller(path):
    """
    Check if the specified directory follows the pattern of a single controller split into multiple files.
    For example, a regular controller would have the directory structure
        js/user/LoginController.js
    A multipart controller split into multiple files would have the directory structure
        js/user/account/AccountController.js
        js/user/account/AccountPastesController.js
    Notice, in particular, the existence of an additional directory.

    :param path: String representing the path to the controller
    """
    return path.count('/') == 4 and os.path.isdir(path)


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
        if is_multipart_controller(directory):  # Single controller divided into multiple individual controllers
            js_files.append(directory)
        else:
            for js_file in files:
                if directory != 'app/static/js/universal':
                    js_files.append('{directory}/{js_file}'.format(directory=directory, js_file=js_file))
    js_output_files = []
    for file_path in js_files:
        if is_multipart_controller(file_path):
            controller_namespace = file_path.split('/')[-1]
            controller_name = controller_namespace[0].upper() + controller_namespace[1:] + 'Controller.js'
            js_output_files.append('/'.join(file_path.split('/')[:-1]).replace('static/js', 'static/build/js') + '/' + controller_name)
        else:
            js_output_files.append(file_path.replace('static/js', 'static/build/js'))

    print 'Javascript build started.'
    for js_file, js_output_file in zip(js_files, js_output_files):
        print 'Compiling {js_file} --> {js_output_file}'.format(js_file=js_file, js_output_file=js_output_file)
        abort_if_error(subprocess.call([
            'java', '-jar', CLOSURE_COMPILER_JAR,
            '--js', js_file + '/**.js' if is_multipart_controller(js_file) else js_file,
            '--js', 'app/static/js/universal/**.js',
            '--js_output_file', js_output_file,
        ]))
    print 'Javascript build complete.'
