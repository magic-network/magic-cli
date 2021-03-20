from setuptools import setup, find_packages
import platform

required_packages = [
    'ethereum==2.3.2',
    'web3==4.8.1',
    'Click==7.0',
    'colorama==0.4.0',
    'future==0.17.1',
    'Jinja2==2.11.3',
    'prompt-toolkit==1.0.14',
    'pyfiglet==0.7.5',
    'Pygments==2.2.0',
    'PyInquirer==1.0.3',
    'six==1.11.0',
    'termcolor==1.1.0',
    'yaspin==0.14.0']

if platform.system() != 'Linux':
    required_packages.append('pyobjc==5.1.1')

setup(
    name='magic-cli',
    author="Magic Foundation",
    author_email="hello@magic.co",
    version='0.1.0',
    description="Command Line Interface (CLI) for connecting to the Magic Network",
    long_description_markdown_filename='README.md',
    license="MIT",
    keywords="magic cli hologram",
    url="https://magic.co",
    packages=find_packages(),
    package_data={'magic': ['resources/*']},

    entry_points={
        'console_scripts': [
            'magic-cli=magic.__main__:main'
        ]
    },

    install_requires=required_packages,
    dependency_links=[
      'git+https://github.com/polyswarm/ethash.git#egg=pyethash-0.1.27'
    ],
    python_requires='>=3.6,<4',
    classifiers=[
        'Development Status :: 1 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ]
)
