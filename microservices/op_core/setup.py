from setuptools import setup, find_packages

setup(
    name="op-core",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "pydantic>=1.8.0",
        "SQLAlchemy>=1.4.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-dotenv>=0.19.0",
        "pymysql>=1.0.2",
        "redis>=4.0.0",
        "elasticsearch>=7.0.0",
        "uvicorn>=0.15.0",
        "python-multipart>=0.0.5"
    ],
) 