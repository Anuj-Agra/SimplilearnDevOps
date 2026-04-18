"""
setup.py - PegaRE Python package setup for distribution and import
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split('\n')
    # Filter out comments and empty lines
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="pegare",
    version="1.0.0",
    author="Claude (Anthropic)",
    author_email="claude@anthropic.com",
    description="Intelligent Pega Reverse Engineering - Perfect for GitHub Copilot. Natural language interface for analyzing Pega applications.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/pegare",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology", 
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Reverse Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "langgraph": ["langgraph>=0.0.40", "langchain-core>=0.1.0"],
        "analysis": ["pandas>=2.0.0", "jupyter>=1.0.0", "plotly>=5.0.0"],
        "dev": ["pytest>=7.0.0", "black>=23.0.0", "mypy>=1.0.0"],
    },
    entry_points={
        "console_scripts": [
            "pegare=pega_re.auto_dispatcher:main",
            "pegare-analyze=pega_re.cli:analyze_command",
            "pegare-validate=pega_re.cli:validate_command",
        ],
    },
    package_data={
        "pega_re": [
            "skills/*/*.md",
            "templates/*.html",
            "templates/*.css",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="pega reverse-engineering documentation analysis modernization",
    project_urls={
        "Bug Reports": "https://github.com/your-org/pegare/issues",
        "Source": "https://github.com/your-org/pegare",
        "Documentation": "https://github.com/your-org/pegare/blob/main/README.md",
    },
)
