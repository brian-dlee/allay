from setuptools import setup

setup(
    name='allay',
    version='0.1.0',
    description='Alleviate environmental pains',
    url='https://github.com/orionnetworksolutions/Allay.git',
    author='Brian Lee',
    author_email='briandl92391@gmail.com',
    license='MIT',
    packages=['allay'],
    install_requires=['PyYaml'],
    scripts=['scripts/allay'],
    zip_safe=True,
    test_suite='allay.test',
)
