FROM python:3.13-slim
LABEL authors="PyAdminRU"

WORKDIR /app

# Обновляем пакеты и ставим curl
RUN apt-get update && apt-get install -y curl bash \
    && curl -fsSL https://yuccastream.github.io/install.sh | bash \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run_all.py"]