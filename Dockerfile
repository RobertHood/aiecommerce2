FROM python:3.10-slim

# Ngăn Python tạo *.pyc
ENV PYTHONDONTWRITEBYTECODE 1
# Đảm bảo log được in ra console trực tiếp
ENV PYTHONUNBUFFERED 1

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Cài đặt các thư viện hệ thống cần thiết (nếu có)
RUN apt-get update && apt-get install -y gcc default-libmysqlclient-dev && rm -rf /var/lib/apt/lists/*

# Copy file requirements và cài đặt thư viện
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# Thông thường nếu bạn load model best.pth trong Django thì cần cài torch 
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Copy toàn bộ mã nguồn vào thư mục làm việc
COPY . /app/
