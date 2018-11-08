try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='finance_crawler',
    packages=['finance_crawler'],
    install_requires=[
        'requests', 
        'beautifulsoup4',
        'pandas'
    ],
    version='0.0.1',
    description='Scrapes data from Yahoo! Finance earnings calendar',
    author='fricative',
    classifiers=[],
)