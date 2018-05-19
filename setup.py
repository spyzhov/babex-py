from setuptools import setup

setup(
    name='babex',
    version='1.0.1',
    install_requires=[
        "pika"
    ],
    description="Имплементация протокола общения между сервисами, через очередь сообщений RabbitMQ.",
    author='Stepan Pyzhov',
    maintainer='Stepan Pyzhov',
    packages=['babex'],
    package_dir={'babex': 'src'},
    url='https://github.com/spyzhov/babex-py',
)