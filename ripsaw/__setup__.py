#-- smash.setup.arguments

'''--- Smart Shell
    An integrated environment for reproducible research, development, testing, and production
'''

from pathlib import Path
import os

#----------------------------------------------------------------------------------------------#

def collect_package_data( package_path ) :
    root_path = Path( __file__ ).parents[2].resolve() / package_path
    package_data = list()

    for root, _, _ in os.walk( str( root_path ) ) :
        package_data.append( str( Path( root ) / '*' ) )

    return package_data


#----------------------------------------------------------------------------------------------#

options = dict(
    name            = 'ripsaw',
    version         = '0.0.0',
    description     = __doc__,
    license         = "MIT License",

    url             = 'https://github.com/philipov/ripsaw',
    author          = 'Philip Loguinov',
    author_email    = 'philipov@gmail.com',

    packages = [
        'ripsaw',
    ],

    zip_safe                = True,
    include_package_data    = True,
    #package_data = {
    #    'ripsaw' : collect_package_data( Path('ripsaw')/'templates' )
    #},
    entry_points = {
        'console_scripts': [
            'ripsaw         = ripsaw:console',
        ],
    },
    install_requires = [
        'powertools',       # std lib extension

    ],
    classifiers = [
        'Environment :: Console',
        'Environment :: Other Environment',

        'Intended Audience :: Information Technology',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Customer Service',

        'License :: Other/Proprietary License',

        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: POSIX :: Linux',

        'Programming Language :: Python :: 3.6'
    ]
)


__version__ = options['version']

#----------------------------------------------------------------------------------------------#
