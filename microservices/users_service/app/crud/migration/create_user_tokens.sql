CREATE TABLE user_tokens (
    uk_id INT AUTO_INCREMENT PRIMARY KEY,
    uk_user_id INT NOT NULL,
    uk_access_token VARCHAR(500) NOT NULL,
    uk_device_info VARCHAR(500),
    uk_ip_address VARCHAR(50),
    uk_created_at INT NOT NULL DEFAULT 0,
    uk_expires_at INT NOT NULL,
    uk_is_active INT DEFAULT 1,
    UNIQUE INDEX idx_access_token (uk_access_token),
    INDEX idx_user_id (uk_user_id),
    INDEX idx_created_at (uk_created_at),
    INDEX idx_expires_at (uk_expires_at),
    FOREIGN KEY (uk_user_id) REFERENCES users(u_id) ON DELETE CASCADE
) COLLATE 'utf8mb4_0900_ai_ci'; 