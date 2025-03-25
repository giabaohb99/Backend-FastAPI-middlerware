# Microservices Project

Dự án microservices sử dụng FastAPI, MySQL, Redis và Docker với các tính năng bảo mật nâng cao.

## Yêu cầu hệ thống

- Docker và Docker Compose
- Python 3.9 hoặc cao hơn (nếu chạy không dùng Docker)
- MySQL 8.0 hoặc cao hơn (nếu chạy không dùng Docker)
- Redis 6.0 hoặc cao hơn (nếu chạy không dùng Docker)

## Cài đặt và Chạy

### 1. Khởi động các services bằng Docker

```bash
# Clone repository (nếu chưa có)


# Build và chạy các services
docker-compose up --build
```

Các services sẽ chạy ở các cổng sau:
- Users Service API: http://localhost:8000
- MySQL: localhost:3399
- Redis: localhost:6379
- Adminer (MySQL Management): http://localhost:8080

### 2. Khởi tạo Database

#### Sử dụng Adminer:
1. Truy cập http://localhost:8080
2. Đăng nhập với thông tin:
   - System: MySQL
   - Server: mysql-6f008b0-hb-fd17.e.aivencloud.com:18336
-> nếu có thay đổi thông tin của database, hãy thay đổi trong file config.py và .\mirco\certs\ca.crt
và Chứng chỉ CA được lấy từ console.aiven.io

#### Chạy migration SQL:
1. Mở Adminer và đăng nhập như trên
2. Chọn database "defaultdb"
3. Vào tab "SQL command"
4. Copy và thực thi các câu lệnh SQL sau:

```sql
-- Tạo bảng users
CREATE TABLE `users` (
  `u_id` int NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `u_email` varchar(256) NOT NULL,
  `u_password` varchar(255) NOT NULL,
  `u_fullname` varchar(255) DEFAULT '',
  `u_activatedcode` varchar(255) DEFAULT NULL,
  `u_status` int NOT NULL DEFAULT '0',
  `u_datecreated` int NOT NULL DEFAULT '0',
  `u_datemodified` int NOT NULL DEFAULT '0',
  `u_datelastlogin` int NOT NULL DEFAULT '0',
  UNIQUE KEY `ix_users_u_email` (`u_email`),
  INDEX `ix_users_u_id` (`u_id`)
) COLLATE 'utf8mb4_0900_ai_ci';

-- Tạo bảng logs để theo dõi API calls
CREATE TABLE logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    method VARCHAR(10) NOT NULL,
    url VARCHAR(255) NOT NULL,
    status_code INT,
    request_body TEXT,
    response_body TEXT,
    ip_address VARCHAR(50),
    user_agent VARCHAR(255),
    process_time FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    sql_queries text NULL,
    INDEX idx_created_at (created_at),
    INDEX idx_method (method),
    INDEX idx_status_code (status_code)
);

-- Tạo bảng user_tokens
CREATE TABLE `user_tokens` (
  `ut_id` int NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `ut_user_id` int NOT NULL,
  `ut_access_token` varchar(500) NOT NULL,
  `ut_refresh_token` varchar(500) DEFAULT NULL,
  `ut_device_info` varchar(500) DEFAULT NULL,
  `ut_ip_address` varchar(50) DEFAULT NULL,
  `ut_created_at` int NOT NULL DEFAULT '0',
  `ut_expires_at` int DEFAULT NULL,
  `ut_is_active` int NOT NULL DEFAULT '1',
  INDEX `ix_user_tokens_ut_user_id` (`ut_user_id`),
  FOREIGN KEY (`ut_user_id`) REFERENCES `users` (`u_id`) ON DELETE CASCADE
) COLLATE 'utf8mb4_0900_ai_ci';
```

## Tính năng Bảo mật

### 1. Rate Limiting
- Giới hạn số lượng request từ mỗi IP
- Cooldown period giữa các request
- Theo dõi request theo path và body hash
- Trả về thông tin chi tiết khi vượt quá giới hạn

### 2. Logging và Monitoring
- Log tất cả các request/response
- Theo dõi SQL queries và thời gian thực thi
- Tự động xóa logs cũ (mặc định 30 phút)
- Log chi tiết các lỗi và stack traces

### 3. Error Handling
- Xử lý lỗi chi tiết cho SQL queries
- Trả về JSON responses với thông tin lỗi
- Log các lỗi với timestamp
- Bảo vệ thông tin nhạy cảm trong logs

### 4. Redis Security
- Yêu cầu mật khẩu cho Redis
- Phân tách databases cho các mục đích khác nhau
- Rate limiting sử dụng Redis
- Persistent storage cho Redis data

## API Endpoints

### 1. Đăng ký người dùng

```bash
curl -X POST http://localhost:8000/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'
```

Hoặc sử dụng Postman:
- Method: POST
- URL: http://localhost:8000/api/v1/register
- Headers: Content-Type: application/json
- Body (raw JSON):
```json
{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
}
```

### 2. Đăng nhập

```bash
curl -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

Response sẽ trả về access token để sử dụng cho các API khác.

## Kiểm tra Logs

### 1. Truy cập Logs qua Adminer
1. Truy cập Adminer: http://localhost:8080
2. Đăng nhập như hướng dẫn ở trên
3. Chọn database "defaultdb"
4. Chọn bảng "logs"
5. Xem các request logs với câu lệnh:
```sql
SELECT * FROM logs ORDER BY created_at DESC;
```

### 2. Redis Monitoring
1. Truy cập Redis CLI:
```bash
docker exec -it mirco_redis_1 redis-cli
AUTH 123456789
```

2. Các lệnh Redis hữu ích:
```bash
# Xem tất cả keys
KEYS *

# Xem thông tin server
INFO

# Xóa tất cả keys trong database hiện tại
FLUSHDB

# Xóa tất cả keys trong tất cả databases
FLUSHALL
```

## Cấu trúc Project

```plaintext
mirco/
├── docker-compose.yml          # Docker Compose configuration
├── README.md                   # Project documentation
├── microservices/             # Microservices directory
│   ├── op_core/               # Core package shared across services
│   │   └── core/              # Core modules
│   │       ├── config.py      # Configuration settings
│   │       ├── database.py    # Database connection
│   │       ├── middleware.py  # Middleware components
│   │       └── security.py    # Security utilities
│   └── users_service/         # Users microservice
│       ├── Dockerfile         # Docker build instructions
│       ├── app/               # Application code
│       │   ├── api/          # API endpoints
│       │   ├── crud/         # Database operations
│       │   ├── models/       # Database models
│       │   └── schemas/      # Pydantic models
│       └── requirements.txt   # Python dependencies
└── certs/                     # SSL certificates

-- note: trước mỗi API khi có truyền token điều phải kiểm tra ít nhất 2 điều kiện là thời gian và trạng thái
