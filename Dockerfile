FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    cron \
    wget \
    unzip \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    && rm -rf /var/lib/apt/lists/*

RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && apt-get update \
    && apt-get install -y postgresql-client-16 \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list

RUN apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
COPY main.py .
COPY utils/ ./utils/
COPY scrapers/ ./scrapers/
COPY cron_script.sh .
COPY .env .

RUN chmod +x cron_script.sh

RUN pip install --no-cache-dir -r requirements.txt

RUN echo "0 12 * * * /app/cron_script.sh >> /app/logs/cron.log 2>&1" > /etc/cron.d/scraper-cron
RUN crontab /etc/cron.d/scraper-cron

RUN ln -sf /usr/share/zoneinfo/Europe/Kiev /etc/localtime

CMD ["cron", "-f"]