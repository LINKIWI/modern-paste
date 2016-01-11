"""
This script compiles all CSS for a production environment, as specified in config.BUILD_ENVIRONMENT.
"""

import os
import subprocess
import config
import constants


if __name__ == '__main__':
    if config.BUILD_ENVIRONMENT == constants.build_environment.DEV:
        print 'Configuration in config.py specified a dev environment.\n' \
              'This script will compile CSS, but in non-minified mode.'

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
        subprocess.call([
            'sass',
            '{scss_path}:{css_path}'.format(scss_path=scss_file_path, css_path=css_file_path),
            '--style', 'compressed' if config.BUILD_ENVIRONMENT == constants.build_environment.PROD else 'expanded',
        ])
