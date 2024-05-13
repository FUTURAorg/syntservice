from python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu118

COPY models/.local /root/.local

COPY main.py main.py
COPY backends/ backends/