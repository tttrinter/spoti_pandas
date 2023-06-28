from setuptools import setup, find_packages

setup(
    name='spoti_pandas',
    version='0.1',
    author='Tom Trinter',
    author_email='tttrinter@gmail.com',
    packages=find_packages(),
    install_requires=['spotipy','pandas'],
)
