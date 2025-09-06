"""Setup script for Guardian App"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("guardian_app/requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="guardian-app",
    version="1.0.0",
    author="Guardian App Team",
    author_email="team@guardianapp.com",
    description="AI-Powered Child Safety Pipeline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/guardian-app/guardian-app",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.991",
        ],
    },
    entry_points={
        "console_scripts": [
            "guardian-app=guardian_app.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "guardian_app": ["requirements.txt"],
    },
)
