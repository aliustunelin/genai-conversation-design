FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY . .

RUN chmod +x scripts/*.sh

RUN make install

EXPOSE 8000

CMD ["make", "run"]
