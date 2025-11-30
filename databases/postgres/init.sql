-- PostgreSQL Initialization Script
-- Tworzenie bazy danych i struktur dla testów bezpieczeństwa
-- UŻYWANE PRZEZ simulate_activity.py (DB: secure_data)

-- 1) Baza danych, z którą łączy się symulator
CREATE DATABASE secure_data;

\connect secure_data

-- 2) Włączenie logowania / audytu (globalne, ale odpalamy to przy okazji inicjalizacji)
ALTER SYSTEM SET log_connections = 'on';
ALTER SYSTEM SET log_disconnections = 'on';
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_duration = 'on';
ALTER SYSTEM SET log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h ';
SELECT pg_reload_conf();

-- 3) Użytkownicy testowi – takie same jak w simulate_activity.py
CREATE USER app_user        WITH PASSWORD 'AppUser123!';
CREATE USER analyst         WITH PASSWORD 'Analyst123!';
CREATE USER dba             WITH PASSWORD 'DBA123!' SUPERUSER;
CREATE USER readonly_user   WITH PASSWORD 'ReadOnly123!';
CREATE USER suspicious_user WITH PASSWORD 'Suspicious123!';

-- 4) Tabele – dokładnie to, czego używa symulator
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name  VARCHAR(100) NOT NULL,
    email      VARCHAR(255) UNIQUE NOT NULL,
    phone      VARCHAR(20),
    pesel      VARCHAR(11),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE financial_transactions (
    transaction_id   SERIAL PRIMARY KEY,
    customer_id      INTEGER REFERENCES customers(customer_id),
    amount           DECIMAL(15, 2) NOT NULL,
    transaction_type VARCHAR(50),
    account_number   VARCHAR(26),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status           VARCHAR(20) DEFAULT 'completed'
);

CREATE TABLE sensitive_medical_data (
    record_id   SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    diagnosis   VARCHAR(500),
    treatment   VARCHAR(1000),
    doctor_name VARCHAR(200),
    record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_confidential BOOLEAN DEFAULT TRUE
);

CREATE TABLE audit_log (
    log_id    SERIAL PRIMARY KEY,
    user_name VARCHAR(100),
    action    VARCHAR(100),
    table_name VARCHAR(100),
    record_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45)
);

CREATE TABLE user_permissions (
    permission_id SERIAL PRIMARY KEY,
    user_name     VARCHAR(100),
    table_name    VARCHAR(100),
    permission_type VARCHAR(20),
    granted_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted_by    VARCHAR(100)
);

-- 5) Przykładowe dane – jak poprzednio
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

INSERT INTO sensitive_medical_data (customer_id, diagnosis, treatment, doctor_name) VALUES
    (1, 'Nadciśnienie',       'Leki hipotensyjne',          'Dr. Kowalczyk'),
    (2, 'Cukrzyca typu 2',    'Metformina, dieta',          'Dr. Nowicki'),
    (3, 'Migrana',            'Tryptany, profilaktyka',     'Dr. Zieliński');

-- 6) Uprawnienia – zgodne z tym, co robi symulator
GRANT USAGE ON SCHEMA public TO app_user, analyst, readonly_user;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
GRANT SELECT, INSERT, UPDATE ON customers, financial_transactions TO app_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO analyst;

-- Zapisanie info o uprawnieniach
INSERT INTO user_permissions (user_name, table_name, permission_type, granted_by) VALUES
    ('readonly_user', 'customers',                'SELECT',               'postgres'),
    ('readonly_user', 'financial_transactions',   'SELECT',               'postgres'),
    ('app_user',      'customers',                'SELECT,INSERT,UPDATE', 'postgres'),
    ('app_user',      'financial_transactions',   'SELECT,INSERT,UPDATE', 'postgres'),
    ('analyst',       'ALL',                      'ALL',                  'postgres');

-- 7) Funkcja audytowa + triggery
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (user_name, action, table_name, record_id, ip_address)
    VALUES (
        current_user,
        TG_OP,
        TG_TABLE_NAME,
        COALESCE(NEW.customer_id, OLD.customer_id),
        inet_client_addr()::TEXT
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_customers
AFTER INSERT OR UPDATE OR DELETE ON customers
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_financial
AFTER INSERT OR UPDATE OR DELETE ON financial_transactions
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_medical
AFTER INSERT OR UPDATE OR DELETE ON sensitive_medical_data
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- 8) Widok z aktywnymi sesjami – używany przez simulate_activity.py (analyst)
CREATE VIEW active_sessions AS
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    backend_start,
    state,
    query
FROM pg_stat_activity
WHERE state != 'idle';

GRANT SELECT ON active_sessions TO analyst;

-- 9) Informacja o zakończeniu inicjalizacji
DO $$
BEGIN
    RAISE NOTICE 'PostgreSQL database initialized successfully (secure_data)';
    RAISE NOTICE 'Users created: app_user, analyst, dba, readonly_user, suspicious_user';
    RAISE NOTICE 'Tables created: customers, financial_transactions, sensitive_medical_data, audit_log';
    RAISE NOTICE 'Logging enabled for security monitoring';
END $$;
