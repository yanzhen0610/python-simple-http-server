import setuptools

with open('README.md', 'r') as file_stream:
    long_description = file_stream.read()

setuptools.setup(
    name='simple-http-server',
    version='1.0.1',
    author='Yz.',
    author_email='yanzhen610@gamil.com',
    description='A simple HTTP server library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yanzhen0610/python-simple-http-server',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
