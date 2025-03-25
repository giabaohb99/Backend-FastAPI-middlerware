from setuptools import setup, find_packages

setup(
    name="customer_service",
    version="0.1.0",
    description="Customer management service",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.95.0",
        "uvicorn>=0.21.1",
        "sqlalchemy>=2.0.7",
        "pydantic>=1.10.7",
        "psycopg2-binary>=2.9.5",
        "alembic>=1.10.2",
        "python-dotenv>=1.0.0",
        "httpx>=0.23.3",
        "email-validator>=2.0.0",
        "python-multipart>=0.0.6",
        "op-core",
    ],
) 