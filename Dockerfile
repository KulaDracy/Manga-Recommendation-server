FROM python:3.12-slim

# Cài các gói cần thiết để build dlib và opencv
RUN apt-get update && apt-get install -y \
    cmake \
    g++ \
    make \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements
COPY requirements_nover.txt .

# Cài pip packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_nover.txt

# Copy code
COPY . .

CMD ["python", "main.py"]
