from setuptools import setup

setup(
    name='babex',
    version='1.0.5',
    install_requires=[
        "pika"
    ],
    description="Babex is a modern solution for communications between microservices.",
    author='Stepan Pyzhov',
    author_email="turin.tomsk@gmail.com",
    maintainer='Stepan Pyzhov',
    packages=['babex'],
    package_dir={'babex': 'src'},
    url='https://github.com/spyzhov/babex-py',
)