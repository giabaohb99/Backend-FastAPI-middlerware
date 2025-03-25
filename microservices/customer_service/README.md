# Customer Service

This microservice handles customer management in the system.

## Features

- Customer CRUD operations
- Integration with User service for authentication
- Support for social logins (Google, Facebook, Yahoo)
- Automatic customer code generation

## API Endpoints

### GET /api/v1/customers
Get a list of customers with pagination and search capabilities.

### POST /api/v1/customers
Create a new customer. If user_id is not provided, a new user will be created automatically.

### GET /api/v1/customers/{customer_id}
Get detailed information about a specific customer.

### PUT /api/v1/customers/{customer_id}
Update customer information.

### DELETE /api/v1/customers/{customer_id}
Delete a customer from the system.

## Running the Service

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn app.main:app --reload
```

### Docker

```bash
# Build the Docker image
docker build -t customer-service .

# Run the container
docker run -p 8002:8000 customer-service
```

## Environment Variables

- `USER_SERVICE_URL`: URL of the User Service API
- `POSTGRES_SERVER`: Database server address
- `POSTGRES_PORT`: Database port
- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name 