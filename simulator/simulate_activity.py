#!/usr/bin/env python3
"""
Symulator aktywności użytkowników i ataków na bazy danych
Działa jako kontener w sieci Docker i łączy się z bazami danych
"""

import psycopg2
import pymongo
import mysql.connector
import time
import random
import sys
from datetime import datetime
from colorama import Fore, Style, init

# Inicjalizacja kolorów
init(autoreset=True)

# Konfiguracja połączeń
DB_CONFIG = {
    'postgres': {
        'host': 'postgres',
        'port': 5432,
        'database': 'secure_data',
        'users': {
            'app_user': 'AppUser123!',
            'analyst': 'Analyst123!',
            'readonly_user': 'ReadOnly123!',
            'suspicious_user': 'Suspicious123!',
            'dba': 'DBA123!'
        }
    },
    'mariadb': {
        'host': 'mariadb',
        'port': 3306,
        'database': 'secure_data',
        'users': {
            'dbadmin': 'DbAdmin123!',
            'root': 'MariadbPass123!'
        }
    },
    'mongodb': {
        'host': 'mongodb',
        'port': 27017,
        'database': 'secure_data',
        'users': {
            'appuser': 'AppPass123!',
            'reader': 'ReadPass123!',
            'admin': 'MongoPass123!'
        }
    }
}

class DatabaseSimulator:
    def __init__(self):
        self.connections = {}
        
    def print_header(self, text):
        print(f"\n{Fore.CYAN}{'=' * 60}")
        print(f"{Fore.CYAN}{text}")
        print(f"{Fore.CYAN}{'=' * 60}\n")
    
    def print_scenario(self, text):
        print(f"{Fore.MAGENTA}[SCENARIUSZ] {text}")
    
    def print_normal(self, text):
        print(f"{Fore.GREEN}[NORMAL] {text}")
    
    def print_attack(self, text):
        print(f"{Fore.RED}[ATAK] {text}")
    
    def print_info(self, text):
        print(f"{Fore.BLUE}[INFO] {text}")
    
    def print_error(self, text):
        print(f"{Fore.YELLOW}[ERROR] {text}")
    
    def random_sleep(self, min_sec=1, max_sec=3):
        time.sleep(random.uniform(min_sec, max_sec))
    
    # ============================================
    # POSTGRESQL - Połączenia i operacje
    # ============================================
    
    def connect_postgres(self, username, password):
        """Nawiązuje połączenie z PostgreSQL"""
        try:
            conn = psycopg2.connect(
                host=DB_CONFIG['postgres']['host'],
                port=DB_CONFIG['postgres']['port'],
                database=DB_CONFIG['postgres']['database'],
                user=username,
                password=password,
                connect_timeout=5
            )
            return conn
        except Exception as e:
            self.print_error(f"Błąd połączenia PostgreSQL ({username}): {str(e)}")
            return None
    
    def execute_postgres(self, conn, query, fetch=False):
        """Wykonuje zapytanie SQL na PostgreSQL"""
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            if fetch:
                result = cursor.fetchall()
                cursor.close()
                return result
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.print_error(f"Błąd zapytania: {str(e)}")
            return None
    
    def postgres_normal_activity(self):
        """Normalna aktywność użytkowników PostgreSQL"""
        self.print_header("PostgreSQL - Normalna aktywność użytkowników")
        
        # Użytkownik app_user
        self.print_normal("Użytkownik app_user - Standardowe operacje biznesowe")
        conn = self.connect_postgres('app_user', 'AppUser123!')
        
        if conn:
            self.print_normal("Pobieranie listy klientów")
            self.execute_postgres(conn, 
                "SELECT customer_id, first_name, last_name, email FROM customers WHERE customer_id <= 3;", 
                fetch=True)
            self.random_sleep()
            
            self.print_normal("Rejestracja nowego klienta")
            self.execute_postgres(conn, 
                f"INSERT INTO customers (first_name, last_name, email, phone, pesel) "
                f"VALUES ('Tomasz', 'Kowalczyk', 'tomasz.k{random.randint(1000,9999)}@email.pl', '777888999', '91040198765');")
            self.random_sleep()
            
            self.print_normal("Aktualizacja numeru telefonu klienta")
            self.execute_postgres(conn, 
                "UPDATE customers SET phone = '666777888' WHERE email = 'jan.kowalski@email.pl';")
            self.random_sleep()
            
            self.print_normal("Rejestracja nowej transakcji finansowej")
            self.execute_postgres(conn, 
                f"INSERT INTO financial_transactions (customer_id, amount, transaction_type, account_number) "
                f"VALUES (1, {random.uniform(50, 500):.2f}, 'payment', '12345678901234567890123456');")
            self.random_sleep()
            
            self.print_normal("Pobieranie historii transakcji klienta")
            self.execute_postgres(conn, 
                "SELECT t.transaction_id, t.amount, t.transaction_type, t.transaction_date "
                "FROM financial_transactions t "
                "WHERE t.customer_id = 1 "
                "ORDER BY t.transaction_date DESC LIMIT 5;", 
                fetch=True)
            self.random_sleep()
            
            conn.close()
        
        # Użytkownik analyst
        self.print_normal("Użytkownik analyst - Analiza danych")
        conn = self.connect_postgres('analyst', 'Analyst123!')
        
        if conn:
            self.print_normal("Generowanie raportu miesięcznego")
            self.execute_postgres(conn, 
                "SELECT COUNT(*) as total_transactions, SUM(amount) as total_amount "
                "FROM financial_transactions "
                "WHERE transaction_date >= CURRENT_DATE - INTERVAL '30 days';", 
                fetch=True)
            self.random_sleep()
            
            self.print_normal("Sprawdzanie aktywnych sesji")
            self.execute_postgres(conn, "SELECT * FROM active_sessions;", fetch=True)
            self.random_sleep()
            
            conn.close()
    
    def postgres_attack_scenarios(self):
        """Scenariusze ataków na PostgreSQL"""
        self.print_header("PostgreSQL - Scenariusze ataków")
        
        conn = self.connect_postgres('app_user', 'AppUser123!')
        
        if conn:
            # 1. SQL Injection
            self.print_scenario("1. SQL Injection - próby wstrzyknięcia kodu")
            
            self.print_attack("Próba SQL Injection w warunku WHERE")
            self.execute_postgres(conn, 
                "SELECT * FROM customers WHERE email = 'admin@example.com' OR '1'='1';", 
                fetch=True)
            self.random_sleep()
            
            self.print_attack("Próba SQL Injection z UNION")
            self.execute_postgres(conn, 
                "SELECT first_name, last_name FROM customers WHERE customer_id = 1 "
                "UNION SELECT usename, passwd FROM pg_shadow;", 
                fetch=True)
            self.random_sleep()
            
            self.print_attack("Próba SQL Injection z komentarzem")
            self.execute_postgres(conn, 
                "SELECT * FROM customers WHERE customer_id = 1; DROP TABLE customers; --", 
                fetch=True)
            self.random_sleep()
            
            # 3. Eskalacja uprawnień
            self.print_scenario("3. Próby eskalacji uprawnień")
            
            self.print_attack("Próba nadania sobie uprawnień superusera")
            self.execute_postgres(conn, "ALTER USER app_user WITH SUPERUSER;")
            self.random_sleep()
            
            self.print_attack("Próba modyfikacji uprawnień innych użytkowników")
            self.execute_postgres(conn, 
                "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;")
            self.random_sleep()
            
            self.print_attack("Próba utworzenia nowego użytkownika z uprawnieniami")
            self.execute_postgres(conn, 
                "CREATE USER hacker WITH PASSWORD 'Hacked123!' SUPERUSER;")
            self.random_sleep()
            
            # 4. Eksfiltracja danych
            self.print_scenario("4. Próby eksfiltracji wrażliwych danych")
            
            self.print_attack("Próba eksfiltracji danych medycznych")
            self.execute_postgres(conn, 
                "SELECT c.first_name, c.last_name, c.pesel, m.diagnosis, m.treatment "
                "FROM customers c "
                "JOIN sensitive_medical_data m ON c.customer_id = m.customer_id;", 
                fetch=True)
            self.random_sleep()
            
            self.print_attack("Próba eksfiltracji danych finansowych")
            self.execute_postgres(conn, 
                "SELECT c.first_name, c.last_name, c.pesel, f.account_number, f.amount "
                "FROM customers c "
                "JOIN financial_transactions f ON c.customer_id = f.customer_id "
                "WHERE f.amount > 1000;", 
                fetch=True)
            self.random_sleep()
            
            # 5. Dostęp do zasobów systemowych
            self.print_scenario("5. Próby dostępu do zasobów systemowych")
            
            self.print_attack("Próba odczytu użytkowników systemu")
            self.execute_postgres(conn, 
                "SELECT usename, usesuper, usecreatedb FROM pg_user;", 
                fetch=True)
            self.random_sleep()
            
            self.print_attack("Próba odczytu haseł użytkowników")
            self.execute_postgres(conn, 
                "SELECT usename, passwd FROM pg_shadow;", 
                fetch=True)
            self.random_sleep()
            
            # 6. Podejrzane wzorce
            self.print_scenario("6. Podejrzane wzorce aktywności")
            
            self.print_attack("Seria zapytań skanujących strukturę bazy")
            self.execute_postgres(conn, 
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';", 
                fetch=True)
            self.random_sleep()
            
            self.execute_postgres(conn, 
                "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'customers';", 
                fetch=True)
            self.random_sleep()
            
            conn.close()
        
        # 2. Błędne logowania
        self.print_scenario("2. Próby nieautoryzowanego dostępu - błędne hasła")
        
        for i in range(1, 6):
            self.print_attack(f"Próba logowania z błędnym hasłem (próba {i})")
            self.connect_postgres('app_user', f'WrongPassword{i}')
            time.sleep(2)
        
        # Próba logowania na konta z wysokimi uprawnieniami
        self.print_attack("Próby brute force na konto DBA")
        for pwd in ['admin123', 'Admin123', 'dba123', 'password', 'DBA123']:
            self.connect_postgres('dba', pwd)
            time.sleep(1)
    
    # ============================================
    # MARIADB - Połączenia i operacje
    # ============================================
    
    def connect_mariadb(self, username, password):
        """Nawiązuje połączenie z MariaDB"""
        try:
            conn = mysql.connector.connect(
                host=DB_CONFIG['mariadb']['host'],
                port=DB_CONFIG['mariadb']['port'],
                database=DB_CONFIG['mariadb']['database'],
                user=username,
                password=password,
                connect_timeout=5
            )
            return conn
        except Exception as e:
            self.print_error(f"Błąd połączenia MariaDB ({username}): {str(e)}")
            return None
    
    def execute_mariadb(self, conn, query, fetch=False):
        """Wykonuje zapytanie SQL na MariaDB"""
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            if fetch:
                result = cursor.fetchall()
                cursor.close()
                return result
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.print_error(f"Błąd zapytania: {str(e)}")
            return None
    
    def mariadb_normal_activity(self):
        """Normalna aktywność użytkowników MariaDB"""
        self.print_header("MariaDB - Normalna aktywność użytkowników")
        
        self.print_normal("Użytkownik dbadmin - operacje na danych")
        conn = self.connect_mariadb('dbadmin', 'DbAdmin123!')
        
        if conn:
            self.print_normal("Pobieranie listy klientów")
            self.execute_mariadb(conn, "SELECT * FROM customers LIMIT 5;", fetch=True)
            self.random_sleep()
            
            self.print_normal("Dodawanie nowego klienta")
            self.execute_mariadb(conn, 
                f"INSERT INTO customers (first_name, last_name, email, phone) "
                f"VALUES ('Katarzyna', 'Nowacka', 'katarzyna.n{random.randint(1000,9999)}@email.pl', '555123456');")
            self.random_sleep()
            
            self.print_normal("Generowanie raportów")
            self.execute_mariadb(conn, 
                "SELECT DATE(transaction_date) as date, COUNT(*) as count, SUM(amount) as total "
                "FROM financial_transactions "
                "GROUP BY DATE(transaction_date);", 
                fetch=True)
            self.random_sleep()
            
            conn.close()
    
    def mariadb_attack_scenarios(self):
        """Scenariusze ataków na MariaDB"""
        self.print_header("MariaDB - Scenariusze ataków")
        
        conn = self.connect_mariadb('dbadmin', 'DbAdmin123!')
        
        if conn:
            # 1. SQL Injection
            self.print_scenario("1. SQL Injection - różne techniki")
            
            self.print_attack("Boolean-based blind SQL injection")
            self.execute_mariadb(conn, 
                "SELECT * FROM customers WHERE customer_id = 1 AND 1=1;", 
                fetch=True)
            self.random_sleep()
            
            self.print_attack("Time-based blind SQL injection")
            self.execute_mariadb(conn, 
                "SELECT * FROM customers WHERE customer_id = 1 AND SLEEP(2);", 
                fetch=True)
            self.random_sleep()
            
            self.print_attack("UNION-based SQL injection")
            self.execute_mariadb(conn, 
                "SELECT first_name, last_name FROM customers WHERE customer_id = 1 "
                "UNION SELECT user, password FROM mysql.user;", 
                fetch=True)
            self.random_sleep()
            
            # 2. Eskalacja uprawnień
            self.print_scenario("2. Eskalacja uprawnień - GRANT/REVOKE")
            
            self.print_attack("Próba nadania wszystkich uprawnień użytkownikowi")
            self.execute_mariadb(conn, 
                "GRANT ALL PRIVILEGES ON *.* TO 'dbadmin'@'%';")
            self.random_sleep()
            
            self.print_attack("Próba nadania uprawnień SUPER")
            self.execute_mariadb(conn, 
                "GRANT SUPER ON *.* TO 'dbadmin'@'%';")
            self.random_sleep()
            
            self.print_attack("Próba utworzenia nowego użytkownika z pełnymi uprawnieniami")
            self.execute_mariadb(conn, 
                "CREATE USER 'backdoor'@'%' IDENTIFIED BY 'secret123';")
            self.random_sleep()
            self.execute_mariadb(conn, 
                "GRANT ALL PRIVILEGES ON *.* TO 'backdoor'@'%' WITH GRANT OPTION;")
            self.random_sleep()
            
            self.print_attack("Próba odebrania uprawnień innemu użytkownikowi")
            self.execute_mariadb(conn, 
                "REVOKE SELECT ON secure_data.* FROM 'app_user'@'%';")
            self.random_sleep()
            
            self.print_attack("Próba nadania uprawnień do tabeli systemowej")
            self.execute_mariadb(conn, 
                "GRANT SELECT ON mysql.user TO 'dbadmin'@'%';")
            self.random_sleep()
            
            # 3. Eksfiltracja danych
            self.print_scenario("3. Eksfiltracja wrażliwych danych")
            
            self.print_attack("Eksport danych do pliku (próba)")
            self.execute_mariadb(conn, 
                "SELECT * FROM customers INTO OUTFILE '/tmp/stolen_data.csv';")
            self.random_sleep()
            
            self.print_attack("Masowy odczyt wrażliwych danych")
            self.execute_mariadb(conn, 
                "SELECT c.*, f.account_number, f.amount "
                "FROM customers c "
                "LEFT JOIN financial_transactions f ON c.customer_id = f.customer_id;", 
                fetch=True)
            self.random_sleep()
            
            # 4. Dostęp do systemu
            self.print_scenario("4. Próby dostępu do zasobów systemowych")
            
            self.print_attack("Odczyt użytkowników MySQL")
            self.execute_mariadb(conn, "SELECT user, host FROM mysql.user;", fetch=True)
            self.random_sleep()
            
            # 5. Podejrzane zapytania
            self.print_scenario("5. Podejrzane wzorce zapytań")
            
            self.print_attack("Szybka seria zapytań (możliwy atak automated)")
            for i in range(1, 11):
                self.execute_mariadb(conn, 
                    f"SELECT * FROM customers WHERE customer_id = {i};", 
                    fetch=True)
                time.sleep(0.5)
            
            conn.close()
        
        # 2. Błędne logowania
        self.print_scenario("2. Brute force - próby złamania hasła")
        
        for i in range(1, 8):
            self.print_attack(f"Próba logowania jako root z losowym hasłem (próba {i})")
            self.connect_mariadb('root', f'WrongPass{i}')
            time.sleep(1)
    
    # ============================================
    # MONGODB - Połączenia i operacje
    # ============================================
    
    def connect_mongodb(self, username, password):
        """Nawiązuje połączenie z MongoDB"""
        try:
            client = pymongo.MongoClient(
                host=DB_CONFIG['mongodb']['host'],
                port=DB_CONFIG['mongodb']['port'],
                username=username,
                password=password,
                authSource='admin',
                serverSelectionTimeoutMS=5000
            )
            # Test połączenia
            client.server_info()
            return client
        except Exception as e:
            self.print_error(f"Błąd połączenia MongoDB ({username}): {str(e)}")
            return None
    
    def mongodb_normal_activity(self):
        """Normalna aktywność użytkowników MongoDB"""
        self.print_header("MongoDB - Normalna aktywność użytkowników")
        
        self.print_normal("Użytkownik appuser - standardowe operacje")
        client = self.connect_mongodb('appuser', 'AppPass123!')
        
        if client:
            db = client[DB_CONFIG['mongodb']['database']]
            
            self.print_normal("Pobieranie dokumentów użytkowników")
            try:
                users = list(db.users.find().limit(3))
                print(f"  Znaleziono {len(users)} użytkowników")
            except Exception as e:
                self.print_error(str(e))
            self.random_sleep()
            
            self.print_normal("Dodawanie nowego użytkownika")
            try:
                db.users.insert_one({
                    'username': f'new_user_{random.randint(1000,9999)}',
                    'email': f'new{random.randint(100,999)}@example.com',
                    'role': 'user',
                    'created': datetime.now()
                })
            except Exception as e:
                self.print_error(str(e))
            self.random_sleep()
            
            self.print_normal("Aktualizacja danych użytkownika")
            try:
                db.users.update_one(
                    {'username': 'john_doe'},
                    {'$set': {'last_login': datetime.now()}}
                )
            except Exception as e:
                self.print_error(str(e))
            self.random_sleep()
            
            self.print_normal("Generowanie statystyk zamówień")
            try:
                pipeline = [
                    {'$group': {
                        '_id': '$user',
                        'total': {'$sum': '$total'},
                        'count': {'$sum': 1}
                    }}
                ]
                stats = list(db.orders.aggregate(pipeline))
                print(f"  Wygenerowano statystyki dla {len(stats)} użytkowników")
            except Exception as e:
                self.print_error(str(e))
            self.random_sleep()
            
            client.close()
    
    def mongodb_attack_scenarios(self):
        """Scenariusze ataków na MongoDB"""
        self.print_header("MongoDB - Scenariusze ataków")
        
        client = self.connect_mongodb('appuser', 'AppPass123!')
        
        if client:
            db = client[DB_CONFIG['mongodb']['database']]
            
            # 1. NoSQL Injection
            self.print_scenario("1. NoSQL Injection - próby obejścia autentykacji")
            
            self.print_attack("Próba NoSQL injection w zapytaniu")
            try:
                db.users.find({'username': {'$ne': None}}).limit(10)
            except Exception as e:
                self.print_error(str(e))
            self.random_sleep()
            
            self.print_attack("Próba injection z operatorem $where")
            try:
                db.users.find({'$where': 'this.username == "admin" || true'})
            except Exception as e:
                self.print_error(str(e))
            self.random_sleep()
            
            # 3. Eksfiltracja danych
            self.print_scenario("3. Masowa eksfiltracja danych")
            
            self.print_attack("Odczyt wszystkich użytkowników")
            try:
                all_users = list(db.users.find())
                print(f"  Wyeksfiltrowano {len(all_users)} użytkowników")
            except Exception as e:
                self.print_error(str(e))
            self.random_sleep()
            
            self.print_attack("Odczyt wszystkich zamówień")
            try:
                all_orders = list(db.orders.find())
                print(f"  Wyeksfiltrowano {len(all_orders)} zamówień")
            except Exception as e:
                self.print_error(str(e))
            self.random_sleep()
            
            # 4. Dostęp do zasobów systemowych
            self.print_scenario("4. Próby dostępu do danych systemowych")
            
            self.print_attack("Próba odczytu użytkowników systemu")
            try:
                admin_db = client['admin']
                admin_db.command('usersInfo')
            except Exception as e:
                self.print_error(str(e))
            self.random_sleep()
            
            # 5. Podejrzane operacje
            self.print_scenario("5. Podejrzane wzorce zapytań")
            
            self.print_attack("Próba enumeracji kolekcji")
            try:
                collections = db.list_collection_names()
                print(f"  Znaleziono {len(collections)} kolekcji")
            except Exception as e:
                self.print_error(str(e))
            self.random_sleep()
            
            self.print_attack("Szybka seria zapytań (automated attack)")
            for i in range(8):
                try:
                    db.users.find().limit(1)
                except Exception as e:
                    pass
                time.sleep(0.3)
            
            client.close()
        
        # 2. Błędne logowania
        self.print_scenario("2. Próby nieautoryzowanego dostępu")
        
        for i in range(1, 7):
            self.print_attack(f"Próba logowania z błędnymi poświadczeniami (próba {i})")
            self.connect_mongodb('admin', f'WrongPass{i}')
            time.sleep(2)
    
    # ============================================
    # SCENARIUSZE ZAAWANSOWANE
    # ============================================
    
    def advanced_attack_scenarios(self):
        """Scenariusze zaawansowane - APT"""
        self.print_header("Scenariusze zaawansowane - APT (Advanced Persistent Threat)")
        
        self.print_scenario("Symulacja wieloetapowego ataku APT")
        
        conn = self.connect_postgres('app_user', 'AppUser123!')
        
        if conn:
            # Etap 1: Reconnaissance
            self.print_attack("ETAP 1: Rozpoznanie - mapowanie struktury bazy")
            self.execute_postgres(conn, 
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';", 
                fetch=True)
            self.random_sleep()
            
            # Etap 2: Lateral movement
            self.print_attack("ETAP 2: Lateral movement - próba dostępu do innych kont")
            for user in ['analyst', 'dba', 'readonly_user']:
                self.connect_postgres(user, 'Guessed123!')
                time.sleep(1)
            
            # Etap 3: Eksfiltracja
            self.print_attack("ETAP 3: Eksfiltracja - kradzież wrażliwych danych")
            self.execute_postgres(conn, 
                "SELECT c.pesel, f.account_number, m.diagnosis "
                "FROM customers c "
                "LEFT JOIN financial_transactions f ON c.customer_id = f.customer_id "
                "LEFT JOIN sensitive_medical_data m ON c.customer_id = m.customer_id "
                "WHERE c.pesel IS NOT NULL;", 
                fetch=True)
            self.random_sleep()
            
            # Etap 4: Zatarcie śladów
            self.print_attack("ETAP 4: Zatarcie śladów - próba usunięcia logów audytu")
            self.execute_postgres(conn, 
                "DELETE FROM audit_log WHERE user_name = 'app_user';")
            self.random_sleep()
            
            conn.close()
    
    # ============================================
    # FUNKCJA GŁÓWNA
    # ============================================
    
    def run_simulation(self, mode):
        """Uruchamia symulację w wybranym trybie"""
        self.print_header(f"START SYMULACJI - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.print_info(f"Tryb: {mode}")
        
        if mode == "normal":
            self.postgres_normal_activity()
            self.mariadb_normal_activity()
            self.mongodb_normal_activity()
            
        elif mode == "attack":
            self.postgres_attack_scenarios()
            self.mariadb_attack_scenarios()
            self.mongodb_attack_scenarios()
            self.advanced_attack_scenarios()
            
        elif mode in ["full", "all"]:
            self.postgres_normal_activity()
            self.postgres_attack_scenarios()
            self.mariadb_normal_activity()
            self.mariadb_attack_scenarios()
            self.mongodb_normal_activity()
            self.mongodb_attack_scenarios()
            self.advanced_attack_scenarios()
            
        elif mode == "continuous":
            self.print_info("Tryb ciągły - symulacja będzie działać w pętli (Ctrl+C aby zatrzymać)")
            try:
                while True:
                    self.postgres_normal_activity()
                    time.sleep(30)
                    self.postgres_attack_scenarios()
                    time.sleep(30)
                    self.mariadb_normal_activity()
                    time.sleep(30)
                    self.mariadb_attack_scenarios()
                    time.sleep(30)
                    self.mongodb_normal_activity()
                    time.sleep(30)
                    self.mongodb_attack_scenarios()
                    time.sleep(60)
            except KeyboardInterrupt:
                self.print_info("\nPrzerwano symulację ciągłą")
        
        self.print_header(f"KONIEC SYMULACJI - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.print_info("Sprawdź logi w Splunk: http://localhost:8000")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Użycie: python3 simulate_activity.py {normal|attack|full|continuous}")
        print("\nTryby:")
        print("  normal      - Tylko normalna aktywność użytkowników")
        print("  attack      - Tylko scenariusze ataków")
        print("  full        - Pełna symulacja (normalna + ataki)")
        print("  continuous  - Ciągła symulacja w pętli")
        sys.exit(1)
    
    mode = sys.argv[1]
    simulator = DatabaseSimulator()
    simulator.run_simulation(mode)