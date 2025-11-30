FROM python:3.11-slim

# Instalacja zależności systemowych
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiowanie pliku z wymaganiami
COPY requriments.txt .

# Instalacja zależności Python
RUN pip install --no-cache-dir -r requriments.txt

# Kopiowanie skryptu symulacyjnego
COPY simulate_activity.py .

# Nadanie uprawnień do wykonania
RUN chmod +x simulate_activity.py

# Domyślna komenda - tryb ciągły
CMD ["python3", "simulate_activity.py", "continuous"]