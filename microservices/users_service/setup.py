from setuptools import setup, find_packages




setup(
    name="users_service",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic[email]>=1.8.0",
        "python-multipart>=0.0.5",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "SQLAlchemy>=1.4.0",
        "pymysql>=1.0.2",
        "python-dotenv>=0.19.0"
    ]
) 