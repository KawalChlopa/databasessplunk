#!/bin/bash
# Init script dla katalogów logów MariaDB

set -e

echo "=== Tworzenie katalogów logów ==="

# Utwórz katalogi jeśli nie istnieją
mkdir -p /var/log/mysql
chown -R mysql:mysql /var/log/mysql
chmod 755 /var/log/mysql

# Utwórz puste pliki logów
touch /var/log/mysql/audit.log
touch /var/log/mysql/error.log
touch /var/log/mysql/slow.log

chown mysql:mysql /var/log/mysql/*.log
chmod 644 /var/log/mysql/*.log

echo "=== Katalogi logów gotowe ==="
ls -la /var/log/mysql/

echo "=== Sprawdzanie pluginu server_audit ==="
if [ -f /usr/lib/mysql/plugin/server_audit.so ]; then
    echo "✅ Plugin server_audit.so znaleziony"
else
    echo "❌ Brak pluginu server_audit.so w /usr/lib/mysql/plugin/"
    ls -la /usr/lib/mysql/plugin/ | grep -i audit || echo "Brak plików audit"
fi
