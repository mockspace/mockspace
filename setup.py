import io

from setuptools import find_packages
from setuptools import setup

long_description = '''
``mockspace`` is a tool that provides a convenient interface for quickly creating a mock environment:

- Add web-services;
- Fill them with the methods you need;
- Configure response parameters;

Distributed under the terms of the MIT license.
'''

# read the contents of README.md file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    readme = f.read()

setup(
    name="mockspace",
    version="0.1.4",
    url="https://mockspace.io",
    license="MIT",
    author="mockspace team",
    description="A convenient tool for quickly creating a mock environment: add web-services, fill"
                " them with the methods you need, configure response parameters",
    long_description=readme,
    # it's important to specify the content type for correct PyPI markdown:
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    zip_safe=False,
    python_requires='>=3.6',
    install_requires=["flask", "waitress"],
    extras_require={"test": ["pytest", "coverage"]},
    entry_points={
        'console_scripts': [
            'mockspace=mockspace.start_server:start_server',
        ],
    },
    project_urls={
        "Source": "https://github.com/mockspace/mockspace",
    },
)
