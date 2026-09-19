#!/usr/bin/env python3
"""
🚀 Mova Core - Setup Configuration

Setup configuration for mova-core package - the foundational CLI and core utilities
for the Mova voice system ecosystem with professional modular architecture.
"""

from setuptools import setup, find_packages
import os

# Read version from __init__.py
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return "2.0.0"

# Read README for long description
def get_long_description():
    readme_path = os.path.join(os.path.dirname(__file__), '..', 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Mova Core - Professional CLI and core utilities for Mova voice system"

# Define core dependencies
CORE_DEPENDENCIES = [
    'requests>=2.28.0',
    'numpy>=1.21.0',
    'python-dateutil>=2.8.0',
    'click>=8.0.0',
    'colorama>=0.4.0',
    'rich>=12.0.0',
    'pydantic>=2.0.0',
    'typing-extensions>=4.0.0',
]

# Optional dependencies for enhanced features
OPTIONAL_DEPENDENCIES = {
    'audio': [
        'pyaudio>=0.2.11',
        'sounddevice>=0.4.0',
        'librosa>=0.9.0',
    ],
    'web': [
        'fastapi>=0.104.1',
        'uvicorn>=0.24.0',
        'websockets>=11.0.0',
    ],
    'dev': [
        'pytest>=7.0.0',
        'pytest-asyncio>=0.21.0',
        'black>=22.0.0',
        'flake8>=5.0.0',
        'mypy>=1.0.0',
        'pre-commit>=2.20.0',
    ],
    'docs': [
        'sphinx>=5.0.0',
        'sphinx-rtd-theme>=1.0.0',
        'myst-parser>=0.18.0',
    ]
}

# All optional dependencies combined
ALL_DEPENDENCIES = []
for deps in OPTIONAL_DEPENDENCIES.values():
    ALL_DEPENDENCIES.extend(deps)

OPTIONAL_DEPENDENCIES['all'] = ALL_DEPENDENCIES

setup(
    # Package metadata
    name='mova',
    version=get_version(),
    description='Professional CLI and core utilities for Mova voice system',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',

    # Author information
    author='Mova Development Team',
    author_email='dev@mova-voice.com',
    maintainer='Mova Core Team',
    maintainer_email='core@mova-voice.com',

    # URLs
    url='https://github.com/yourusername/mova',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/mova/issues',
        'Source': 'https://github.com/yourusername/mova',
        'Documentation': 'https://mova-voice.readthedocs.io',
        'Changelog': 'https://github.com/yourusername/mova/blob/main/CHANGELOG.md',
    },

    # Package discovery
    packages=find_packages(exclude=['tests*', 'examples*', 'docs*']),
    package_data={
        'mova_core': [
            'cli/templates/*',
            'commands/schemas/*',
            'config/*.yaml',
            'config/*.json',
        ],
    },
    include_package_data=True,

    # Dependencies
    python_requires='>=3.8',
    install_requires=CORE_DEPENDENCIES,
    extras_require=OPTIONAL_DEPENDENCIES,

    # Console scripts for CLI
    entry_points={
        'console_scripts': [
            'mova=mova_core.cli.main_cli:main',
            'mova-cli=mova_core.cli.main_cli:main',
            'mova-core=mova_core.cli.main_cli:main',
        ],
        'mova.cli.commands': [
            'logs=mova_core.commands.log_handlers',
            'voice=mova_core.commands.voice_handlers',
            'system=mova_core.commands.system_handlers',
            'web=mova_core.commands.web_handlers',
            'content=mova_core.commands.content_handlers',
        ],
    },

    # Classification
    classifiers=[
        # Development Status
        'Development Status :: 4 - Beta',

        # Intended Audience
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: End Users/Desktop',

        # License
        'License :: OSI Approved :: MIT License',

        # Operating System
        'Operating System :: OS Independent',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',

        # Programming Language
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',

        # Topic
        'Topic :: Communications',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',

        # Interface
        'Environment :: Console',
        'Environment :: Web Environment',
    ],

    # Keywords for discoverability
    keywords=[
        'voice', 'speech', 'tts', 'stt', 'cli', 'audio',
        'voice-interface', 'speech-recognition', 'text-to-speech',
        'command-line', 'automation', 'modular', 'microservices'
    ],

    # Package requirements
    zip_safe=False,

    # Testing
    test_suite='tests',
    tests_require=[
        'pytest>=7.0.0',
        'pytest-asyncio>=0.21.0',
        'pytest-cov>=4.0.0',
    ],

    # Configuration files
    data_files=[
        ('etc/mova', ['config/mova.conf.example']),
        ('share/doc/mova-core', ['README.md', 'CHANGELOG.md']),
    ] if os.path.exists('config/mova.conf.example') else [],
)
