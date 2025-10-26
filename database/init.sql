SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET character_set_connection = utf8mb4;
SET character_set_server = utf8mb4;
SET character_set_database = utf8mb4;
SET character_set_client = utf8mb4;

CREATE DATABASE IF NOT EXISTS bookstore CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bookstore;

-- User Type
CREATE TABLE IF NOT EXISTS user_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(100) NOT NULL
);

-- Users
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_type_id INT,
    username VARCHAR(100) NOT NULL UNIQUE,
    first_name VARCHAR(100),
    middle_name VARCHAR(100),
    last_name VARCHAR(100),
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(150) UNIQUE,
    balance DECIMAL(10,2) DEFAULT 0,
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_type_id) REFERENCES user_type(id)
);

-- Product
CREATE TABLE IF NOT EXISTS product (
    id INT AUTO_INCREMENT PRIMARY KEY,
    price DECIMAL(10,2) NOT NULL,
    discount DECIMAL(5,2) DEFAULT 0,
    product_type VARCHAR(50)
);

-- Book
CREATE TABLE IF NOT EXISTS book (
    id INT PRIMARY KEY,
    isbn VARCHAR(20) UNIQUE,
    title VARCHAR(255) NOT NULL,
    publisher VARCHAR(150),
    publish_date DATE,
    description TEXT,
    genre VARCHAR(100),
    quantity INT DEFAULT 0,
    pages INT,
    reserved_quantity INT DEFAULT 0,
    FOREIGN KEY (id) REFERENCES product(id)
);

-- Author
CREATE TABLE IF NOT EXISTS author (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    middle_name VARCHAR(100),
    birth_date DATE,
    country VARCHAR(100),
    biography TEXT
);

-- Book-Author Relationship
CREATE TABLE IF NOT EXISTS book_author (
    author_id INT,
    book_id INT,
    PRIMARY KEY (author_id, book_id),
    FOREIGN KEY (author_id) REFERENCES author(id),
    FOREIGN KEY (book_id) REFERENCES book(id)
);

-- Address
CREATE TABLE IF NOT EXISTS address (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    address_type VARCHAR(50),
    street VARCHAR(150),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    house VARCHAR(50),
    country VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Cart
CREATE TABLE IF NOT EXISTS cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Cart Item
CREATE TABLE IF NOT EXISTS cart_item (
    cart_id INT,
    product_id INT,
    quantity INT DEFAULT 1,
    PRIMARY KEY (cart_id, product_id),
    FOREIGN KEY (cart_id) REFERENCES cart(id),
    FOREIGN KEY (product_id) REFERENCES product(id)
);

-- Order
CREATE TABLE IF NOT EXISTS order_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    delivery_address_id INT,
    payment_address_id INT,
    payment_method VARCHAR(50),
    status VARCHAR(50) DEFAULT 'обрабатывается',
    total_amount DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (delivery_address_id) REFERENCES address(id),
    FOREIGN KEY (payment_address_id) REFERENCES address(id)
);

-- Order Item
CREATE TABLE IF NOT EXISTS order_item (
    order_id INT,
    product_id INT,
    quantity INT DEFAULT 1,
    price_at_purchase DECIMAL(10,2),
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES order_table(id),
    FOREIGN KEY (product_id) REFERENCES product(id)
);

-- Типы пользователей
INSERT IGNORE INTO user_type (id, type_name) VALUES
(1, 'Администратор'),
(2, 'Пользователь');

-- Администратор
INSERT IGNORE INTO users (id, user_type_id, username, first_name, last_name, password_hash, email, balance) VALUES
(1, 1, 'admin', 'Admin', 'System', 'pbkdf2:sha256:260000$EEuFI2ErzyCsun8l$b67a3d3faea1fb4679f9dcb50e9d5665260c5d1ea4fbd5cd052fdee7ce26ad9f', 'admin@bookstore.ru', 0);

-- Адрес администратора
INSERT IGNORE INTO address (id, user_id, address_type, street, city, postal_code, house, country) VALUES
(1, 1, 'home', 'ул. Главная', 'Москва', '101000', 'д. 1', 'Россия');

-- Продукты
INSERT IGNORE INTO product (id, price, discount, product_type) VALUES
(1, 380.00, 0.00, 'book'),
(2, 650.00, 10.00, 'book'),
(3, 290.00, 0.00, 'book'),
(4, 720.00, 5.00, 'book'),
(5, 420.00, 0.00, 'book'),
(6, 520.00, 8.00, 'book'),
(7, 680.00, 12.00, 'book'),
(8, 580.00, 7.00, 'book');

-- Авторы
INSERT IGNORE INTO author (id, first_name, last_name, middle_name, birth_date, country, biography) VALUES
(1, 'Фёдор', 'Достоевский', 'Михайлович', '1821-11-11', 'Россия', 'Великий русский писатель, классик мировой литературы'),
(2, 'Джоан', 'Роулинг', NULL, '1965-07-31', 'Великобритания', 'Британская писательница, автор серии о Гарри Поттере'),
(3, 'Антуан', 'де Сент-Экзюпери', NULL, '1900-06-29', 'Франция', 'Французский писатель и летчик'),
(4, 'Лев', 'Толстой', 'Николаевич', '1828-09-09', 'Россия', 'Великий русский писатель, мыслитель'),
(5, 'Джордж', 'Оруэлл', NULL, '1903-06-25', 'Великобритания', 'Британский писатель и публицист');

-- Книги
INSERT IGNORE INTO book (id, isbn, title, publisher, publish_date, description, genre, quantity, pages, reserved_quantity) VALUES
(1, '978-5-17-148992-1', 'Преступление и наказание', 'АСТ', '1866-01-01', 'Глубокий психологический роман о студенте Раскольникове', 'Классика, Психологический роман', 10, 672, 0),
(2, '978-5-389-07435-4', 'Гарри Поттер и философский камень', 'Махаон', '1997-06-26', 'Первая книга о юном волшебнике Гарри Поттере', 'Фэнтези', 15, 432, 2),
(3, '978-5-699-97429-5', 'Маленький принц', 'Эксмо', '1943-04-06', 'Трогательная история о мальчике с астероида Б-612', 'Философская сказка', 8, 96, 1),
(4, '978-5-04-103680-3', 'Война и мир', 'Азбука', '1869-01-01', 'Эпический роман о войне 1812 года', 'Классика, Исторический роман', 5, 1360, 0),
(5, '978-5-17-147983-3', 'Скотный двор', 'АСТ', '1945-08-17', 'Сатирическая повесть о животных-революционерах', 'Сатира, Антиутопия', 12, 144, 1),
(6, '978-5-17-136492-4', 'Братья Карамазовы', 'АСТ', '1880-01-01', 'Последний роман Достоевского о вере и сомнении', 'Классика, Философский роман', 7, 830, 0),
(7, '978-5-389-07436-1', 'Гарри Поттер и Тайная комната', 'Махаон', '1998-07-02', 'Вторая книга о приключениях Гарри Поттера', 'Фэнтези', 13, 480, 3),
(8, '978-5-04-105983-3', 'Анна Каренина', 'Эксмо', '1877-01-01', 'Роман о трагической любви и общественных нормах', 'Классика, Роман', 9, 864, 1);

-- Связи книг и авторов
INSERT IGNORE INTO book_author (author_id, book_id) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 5),
(1, 6),
(2, 7),
(4, 8);

-- Корзина для администратора
INSERT IGNORE INTO cart (id, user_id) VALUES
(1, 1);