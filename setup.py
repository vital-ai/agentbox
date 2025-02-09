from setuptools import setup, find_packages

setup(
    name='vital-agentbox',
    version='0.0.2',
    author='Marc Hadfield',
    author_email='marc@vital.ai',
    description='Vital Agent Box',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/vital-ai/vital-agentbox',
    packages=find_packages(exclude=["test", "test_data"]),
    license='Apache License 2.0',
    install_requires=[

        'pypandoc>=1.5',

        'playwright',
        'black',

        'lark',

        'PyGithub>=2.5.0',

        'panflute>=2.3.1',

        'matplotlib',
        'numpy',

        'vital-ai-vitalsigns>=0.1.27',
        'vital-ai-domain>=0.1.4',

        'kgraphservice>=0.0.6',
    ],
    extras_require={

    },
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)
