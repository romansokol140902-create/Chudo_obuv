CREATE DATABASE IF NOT EXISTS chudo_obuv
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE chudo_obuv;

CREATE TABLE roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    login VARCHAR(100) NOT NULL UNIQUE,
    role_id INT NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    product_name VARCHAR(255) NOT NULL,
    manufacturer VARCHAR(255),
    image_path VARCHAR(500),
    description TEXT,
    composition TEXT,
    price DECIMAL(10,2) NOT NULL
);

CREATE TABLE sizes (
    size_id INT AUTO_INCREMENT PRIMARY KEY,
    size_value VARCHAR(10) NOT NULL UNIQUE
);

CREATE TABLE stock_items (
    stock_item_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    size_id INT NOT NULL,
    quantity_available INT NOT NULL DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (size_id) REFERENCES sizes(size_id) ON DELETE CASCADE,
    UNIQUE KEY unique_product_size (product_id, size_id)
);

CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    order_date DATE NOT NULL,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    size_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (size_id) REFERENCES sizes(size_id)
);

INSERT INTO roles (role_name) VALUES ('admin'), ('manager'), ('user');

INSERT INTO users (last_name, first_name, middle_name, login, role_id) VALUES
('Иванов', 'Иван', 'Иванович', 'ivanov', 3),
('Петров', 'Пётр', 'Петрович', 'petrov', 2),
('Сидоров', 'Сидор', 'Сидорович', 'sidorov', 1);

INSERT INTO sizes (size_value) VALUES
('36'), ('37'), ('38'), ('39'), ('40'), ('41'), ('42'), ('43'), ('44'), ('45');

INSERT INTO products (category, subcategory, product_name, manufacturer, image_path, description, composition, price) VALUES
('Женская обувь', 'Кроссовки', 'Air Max 270', 'Nike', 'images/nike_air_max.png', 'Удобные кроссовки', 'Кожа, текстиль', 8990.00),
('Мужская обувь', 'Ботинки', 'Timberland 6-inch', 'Timberland', 'images/timberland.png', 'Классические ботинки', 'Натуральная кожа', 12990.00),
('Женская обувь', 'Туфли', 'Classic Pumps', 'Zara', NULL, 'Элегантные туфли', 'Экокожа', 4590.00),
('Мужская обувь', 'Кроссовки', 'Ultraboost 22', 'Adidas', 'images/adidas_ultraboost.png', 'Беговые кроссовки', 'Текстиль, резина', 11990.00),
('Детская обувь', 'Кроссовки', 'Kids Run', 'Puma', NULL, 'Лёгкие кроссовки', 'Текстиль', 2990.00);

INSERT INTO stock_items (product_id, size_id, quantity_available) VALUES
(1, 2, 5), (1, 3, 3), (1, 4, 2),
(2, 6, 4), (2, 7, 1),
(3, 1, 2), (3, 2, 2),
(4, 5, 0), (4, 6, 3), (4, 7, 2),
(5, 1, 1), (5, 2, 1);
