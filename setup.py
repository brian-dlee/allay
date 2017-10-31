from setuptools import setup

setup(
    name='allay',
    version='0.3.1',
    description='Alleviate environmental pains',
    url='https://github.com/brian-dlee/Allay.git',
    author='Brian Lee',
    author_email='briandl92391@gmail.com',
    license='MIT',
    packages=['allay'],
    install_requires=[
        'PyYaml',
        'termcolor',
        'pip',
        'magnet==0.1.1'
    ],
    dependency_links=[
        "http://github.com/brian-dlee/magnet/tarball/master#egg=magnet-0.1.1"
    ],    
    scripts=['scripts/allay'],
    zip_safe=True,
    test_suite='allay.test',
)
