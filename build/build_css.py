"""
This script compiles all CSS for a production environment, as specified in config.BUILD_ENVIRONMENT.
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config-environment',
        help='Compile SCSS according to the build environment specified in config.py',
        action='store_true'
    )
    parser.add_argument(
        '--dev',
        help='Compile SCSS in non-minified mode',
        action='store_true'
    )
    parser.add_argument(
        '--prod',
        help='Compile SCSS in minified mode',
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
                  'Compiling SCSS in non-minified mode.'
        else:
            print 'Configuration in config.py specified a prod environment.\n' \
                  'Compiling SCSS in minified mode.'
            style = 'compressed'
    if args.dev:
        print 'Compiling SCSS in non-minified mode.'
    if args.prod:
        print 'Compiling SCSS in minified mode.'
        style = 'compressed'

    scss_files = []
    for directory, subdirectories, files in os.walk('app/static/scss'):
        for scss_file in files:
            if not scss_file.startswith('_'):
                scss_files.append((directory, scss_file))

    print 'CSS build started.'
    for directory, scss_file in scss_files:
        scss_file_path = '{directory}/{scss_file}'.format(directory=directory, scss_file=scss_file)
        css_file_path = 'app/static/build/css/{css_file}'.format(css_file=scss_file.replace('.scss', '.css'))
        print 'Compiling CSS {scss_path} --> {css_path}'.format(scss_path=scss_file_path, css_path=css_file_path)
        abort_if_error(subprocess.call([
            'sass',
            '{scss_path}:{css_path}'.format(scss_path=scss_file_path, css_path=css_file_path),
            '--style', style,
        ]))
    print 'CSS build complete.'
