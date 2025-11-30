-- MariaDB init script dla simulate_activity.py
-- Baza: secure_data, użytkownik: dbadmin / DbAdmin123!

CREATE DATABASE secure_data;
USE secure_data;

-- Użytkownik aplikacyjny
CREATE USER 'dbadmin'@'%' IDENTIFIED BY 'DbAdmin123!';
GRANT ALL PRIVILEGES ON secure_data.* TO 'dbadmin'@'%';
FLUSH PRIVILEGES;

-- Tabela customers – kompatybilna z zapytaniami symulatora
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name  VARCHAR(100) NOT NULL,
    last_name   VARCHAR(100) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    phone       VARCHAR(20),
    pesel       VARCHAR(11),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabela financial_transactions – jak w Postgresie
CREATE TABLE financial_transactions (
    transaction_id   INT AUTO_INCREMENT PRIMARY KEY,
    customer_id      INT,
    amount           DECIMAL(15,2) NOT NULL,
    transaction_type VARCHAR(50),
    account_number   VARCHAR(26),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status           VARCHAR(20) DEFAULT 'completed',
    CONSTRAINT fk_fin_customers
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Opcjonalnie, żeby mieć podobny zestaw tabel jak w Postgresie
CREATE TABLE sensitive_medical_data (
    record_id   INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    diagnosis   VARCHAR(500),
    treatment   VARCHAR(1000),
    doctor_name VARCHAR(200),
    record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_confidential TINYINT(1) DEFAULT 1,
    CONSTRAINT fk_med_customers
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE audit_log (
    log_id     INT AUTO_INCREMENT PRIMARY KEY,
    user_name  VARCHAR(100),
    action     VARCHAR(100),
    table_name VARCHAR(100),
    record_id  INT,
    ts         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45)
);

-- Dane przykładowe – podobne jak w Postgresie
INSERT INTO customers (first_name, last_name, email, phone, pesel) VALUES
    ('Jan',       'Kowalski',   'jan.kowalski@email.pl',   '123456789', '90010112345'),
    ('Anna',      'Nowak',      'anna.nowak@email.pl',     '987654321', '85050554321'),
    ('Piotr',     'Wiśniewski', 'piotr.wisniewski@email.pl','555666777','78111198765'),
    ('Maria',     'Dąbrowska',  'maria.dabrowska@email.pl','444333222','92020287654'),
    ('Krzysztof', 'Lewandowski','krzysztof.lew@email.pl',  '111222333','88030376543');

INSERT INTO financial_transactions (customer_id, amount, transaction_type, account_number) VALUES
    (1, 1500.00,  'transfer',  '12345678901234567890123456'),
    (2, 3200.50,  'payment',   '98765432109876543210987654'),
    (3, 500.00,   'withdrawal','11111111111111111111111111'),
    (4, 15000.00, 'transfer',  '22222222222222222222222222'),
    (1, 200.00,   'payment',   '12345678901234567890123456');
