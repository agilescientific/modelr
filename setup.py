
from setuptools import setup, find_packages, Extension

def main():
    try:
        long_description = open('README.rst').read()
    except IOError as err:
        long_description = str(err)
    try:
        version_str = open('version.txt').read()
    except IOError as err:
        version_str = '???'
        

    setup(
        name='modelr',
        version=version_str,
        
        author='Agile Geoscience.',
        author_email='hello@agilegeoscience.com',
        url='https://github.com/agile-geoscience/modelr',
        
        packages=find_packages(),
            
        classifiers=[c.strip() for c in """\
            Development Status :: 5 - Production/Stable
            Intended Audience :: Developers
            Intended Audience :: Science/Research
            License :: OSI Approved :: BSD License
            Operating System :: MacOS
            Operating System :: Microsoft :: Windows
            Operating System :: OS Independent
            Operating System :: POSIX
            Operating System :: Unix
            Programming Language :: Python :: 2
            Topic :: Scientific/Engineering
            Topic :: Software Development
            Topic :: Software Development :: Libraries
            """.splitlines() if len(c.strip()) > 0],
        description='Web Service like google charts API',
        long_description=long_description,
        license='BSD',
        
    entry_points={
                    'console_scripts': [
                                        'modelr-server = modelr.web.server:main',
                                        ],
                    }

          )


if __name__ == '__main__':
    main()