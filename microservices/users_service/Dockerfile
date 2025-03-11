FROM python:3.9

WORKDIR /app

# Copy the entire microservices directory
COPY . /app/

# Install requirements first
RUN pip install -r /app/op_core/requirements.txt

# Install op_core
RUN pip install -e /app/op_core

# Install users_service requirements and package
RUN pip install -r /app/users_service/requirements.txt
RUN pip install -e /app/users_service

# Command to run the application
CMD ["uvicorn", "users_service.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 