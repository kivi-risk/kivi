import io
import setuptools
from kivi import __version__

__title__ = "kivi"
__license__ = "MIT"
__description__ = "A Bank Risk Manager"
__author_email__ = "chensy.cao@foxmail.com"
__url__ = "https://github.com/Risk-KIVI/kivi"

__requires__ = [
    'scikit-learn', 'statsmodels', 'numpy',
    'pandas', 'tqdm', 'openpyxl', 'pyspark',
    'jieba',
]


with io.open("README.md", "r+", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name=__title__,
    version=__version__,
    author="chensy.cao",
    author_email=__author_email__,
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=__url__,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=__requires__,
    package_data={
        '': ['*.csv', '*.xlsx', '*.pickle'],
    },
)


# python setup.py sdist bdist_wheel

