import setuptools

requirements = open('requirements.txt').readlines()
long_description = open('README.md', 'r', encoding='UTF-8').read()

setuptools.setup(
    name="FofaCli",
    version="0.0.4",
    author="0x4d0",
    author_email="bello.abcx@gmail.com",
    description="Command-line interaction tools for fofa.info",
    license='MIT Licence',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://fofa.info",
    packages=['fofa'],
    install_requires=requirements,
    classifiers=[  # 包的分类信息参考，https://pypi.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 7 - Inactive',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    entry_points={
        'console_scripts': ['fofaCli=fofa.__main__:main']
    }
)
