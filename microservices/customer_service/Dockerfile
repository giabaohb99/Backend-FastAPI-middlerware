FROM python:3.9-slim

WORKDIR /app/

# Copy op_core and install it first
COPY ./op_core /app/op_core/
RUN pip install -r /app/op_core/requirements.txt
RUN pip install -e /app/op_core

# Copy requirements and install dependencies
COPY ./customer_service/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service code
COPY ./customer_service /app/customer_service/

# Set the working directory
WORKDIR /app/customer_service/

# Install the package
RUN pip install -e .

# Set Python path
ENV PYTHONPATH=/app

# Command to run the API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 