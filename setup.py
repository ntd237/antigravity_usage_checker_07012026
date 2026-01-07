from setuptools import setup, find_packages

setup(
    name="antigravity-usage-checker",
    version="1.0.0",
    description="CLI tool để kiểm tra mức sử dụng Antigravity AI models",
    author="ntd237",
    author_email="ntd237.work@gmail.com",
    url="https://github.com/ntd237/antigravity_usage_checker_07012026",
    packages=find_packages(),
    install_requires=[
        "psutil>=5.9.0",
        "requests>=2.31.0",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "agusage=main:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
