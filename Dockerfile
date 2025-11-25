# Použij oficiální Python image
FROM python:3.10-slim

# Nastav pracovní adresář
WORKDIR /app

# Zkopíruj requirements (vytvořím pokud chybí)
COPY requirements.txt ./

# Instaluj závislosti
RUN pip install --no-cache-dir -r requirements.txt

# Zkopíruj zbytek aplikace
COPY . .

# Exponuj port 5000
EXPOSE 5000

# Spusť migrace při startu (volitelně)
CMD ["sh", "-c", "flask db upgrade && flask run --host=0.0.0.0"]
