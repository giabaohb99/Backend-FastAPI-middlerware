CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `email` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL,
  `hashed_password` varchar(255) NOT NULL,
  `full_name` varchar(255) NOT NULL DEFAULT '',
  `status` int NOT NULL DEFAULT '0',
  `created_at` int NOT NULL DEFAULT '0',
  `updated_at` int NOT NULL DEFAULT '0'
) COLLATE 'utf8mb4_0900_ai_ci';


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
    INDEX idx_created_at (created_at),
    INDEX idx_method (method),
    INDEX idx_status_code (status_code)
);

