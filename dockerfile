FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    wget curl gnupg unzip xvfb \
    chromium chromium-driver \
    && apt-get clean

# Переменные среды для Chrome
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Копируем код
WORKDIR /app
COPY . .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем Flask в фоне и админ-бота
CMD ["sh", "-c", "python3 app.py & sleep 2 && python3 admin_bot.py"]
