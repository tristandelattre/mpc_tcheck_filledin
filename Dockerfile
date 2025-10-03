FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installe les dépendances Playwright (navigateurs + libs système)
RUN playwright install --with-deps

COPY . .

# ✅ Exposer le port 8080 requis par Cloud Run
EXPOSE 8080

# ✅ Lancer le bon fichier Python qui démarre ton serveur HTTP
CMD ["python", "main.py"]
