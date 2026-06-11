# AI E-Commerce 2

## Update: catalog data and AI chatbot

The store now seeds 14 electronics products across 10 categories in both databases:

- Main storefront database: `ecommerce_ai/migrations/0002_seed_initial_catalog.py` and `0003_seed_more_electronics.py`
- Catalog microservice database: `services/catalog_service/catalog/migrations/0002_seed_initial_catalog.py` and `0003_seed_more_electronics.py`

The AI service now has a catalog-aware chatbot fallback in:

```text
services/ai_service/assistant/catalog_qa.py
```

How it works:

- The AI service reads product data from `CATALOG_SERVICE_URL/api/products/`.
- In Docker, `CATALOG_SERVICE_URL=http://catalog:8001` is configured for the AI container.
- If the catalog service is not running, the chatbot uses an internal fallback copy of the seeded catalog.
- It can answer product list, category, price, stock, feature, budget, premium, and recommendation questions without requiring Groq or Neo4j.

Run locally:

```powershell
python manage.py migrate
cd services/catalog_service
python manage.py migrate
python manage.py runserver 127.0.0.1:8001
```

In another terminal:

```powershell
cd services/ai_service
python manage.py migrate
python manage.py runserver 127.0.0.1:8004
```

Sample chatbot prompts:

```text
What products do you have?
Show me cheap products
Recommend a gaming product
Price of DevStation X1
What audio products are in stock?
Which product is good for smart home security?
```

Đây là một dự án Django mô phỏng website thương mại điện tử có giao diện bán hàng, giỏ hàng theo session, trang thanh toán, chatbot AI và phần thử nghiệm hệ thống gợi ý dựa trên dữ liệu hành vi người dùng. Codebase kết hợp 3 phần chính:

- Ứng dụng web Django hiển thị cửa hàng `Nexus Store`.
- Hệ thống RAG/AI chat dùng LangChain, Neo4j và Groq.
- Pipeline tạo dữ liệu giả lập và huấn luyện mô hình dự đoán hành vi bằng RNN/LSTM/BiLSTM.

## Công nghệ sử dụng

- Python
- Django
- Django REST Framework
- SQLite
- Pandas, NumPy, scikit-learn
- PyTorch
- Matplotlib
- Neo4j
- LangChain
- LangChain Neo4j
- LangChain Groq
- Docker và Docker Compose

## Kiến trúc hiện tại sau refactor microservices

Project đã được chuyển theo hướng microservice từng bước. Storefront Django hiện đóng vai trò Backend-for-Frontend (BFF), còn các domain chính được tách thành service riêng:

- `web` / storefront: render giao diện, giữ session cart, gọi các service qua HTTP khi bật `USE_MICROSERVICES=1`.
- `catalog_service`: sở hữu dữ liệu `Category`, `Product`, tồn kho và API catalog.
- `order_service`: sở hữu dữ liệu `Order`, `OrderItem`, tạo đơn hàng và gọi `catalog_service` để reserve stock.
- `user_service`: sở hữu dữ liệu khách hàng/người dùng, đăng ký, đăng nhập cơ bản và hồ sơ người dùng.
- `ai_service`: sở hữu API chatbot/RAG, kết nối Neo4j và Groq, lưu log câu hỏi.
- `payment_service`: sở hữu dữ liệu thanh toán, tạo và xác nhận payment cho đơn hàng.
- `product_service`: sở hữu dữ liệu kho hàng, inventory item và stock movement.
- `shipping_service`: sở hữu đối tác vận chuyển, shipment và lộ trình giao nhận.
- `neo4j`: graph database phục vụ AI/RAG chatbot.

Mô hình:

```text
Browser
  |
  v
Storefront / BFF (Django :8000)
  |-- HTTP --> Catalog Service (Django :8001, catalog DB)
  |-- HTTP --> Order Service   (Django :8002, order DB)
  |-- HTTP --> User Service    (Django :8003, user DB)
  |-- HTTP --> AI Service      (Django :8004, AI DB, Neo4j/Groq)
  |-- HTTP --> Payment Service (Django :8005, payment DB)
  |-- HTTP --> Product Service (Django :8006, inventory DB)
  `-- HTTP --> Shipping Service (Django :8007, shipping DB)
```

Storefront vẫn có fallback ORM local để dễ phát triển và test:

```text
USE_MICROSERVICES=0  # chạy kiểu monolith/local ORM
USE_MICROSERVICES=1  # chạy kiểu microservices qua HTTP
```

## Cấu trúc thư mục

```text
aiecommerce2/
|-- aiecommerce2/                  # Cấu hình project Django
|   |-- settings.py                # Cấu hình Django, database, app, template
|   |-- urls.py                    # Route cấp project
|   |-- asgi.py                    # ASGI entrypoint
|   `-- wsgi.py                    # WSGI entrypoint
|-- ecommerce_ai/                  # App chính của website thương mại điện tử
|   |-- views.py                   # Logic hiển thị trang, cart API, chat API
|   |-- urls.py                    # Route của app ecommerce_ai
|   |-- models.py                  # Category, Product, Order, OrderItem
|   |-- admin.py                   # Cấu hình quản trị catalog và đơn hàng
|   |-- tests.py                   # File test mặc định
|   `-- templates/ecommerce_ai/    # HTML template của website
|       |-- index.html             # Trang danh sách sản phẩm và chatbot
|       |-- product_detail.html    # Trang chi tiết sản phẩm
|       |-- cart.html              # Trang giỏ hàng
|       |-- checkout.html          # Trang thanh toán
|       `-- checkout_success.html  # Trang đặt hàng thành công
|-- generate_data.py               # Sinh dữ liệu hành vi người dùng giả lập
|-- train_models.py                # Huấn luyện RNN, LSTM, BiLSTM
|-- setup_neo4j.py                 # Nạp dữ liệu CSV vào Neo4j
|-- rag_chat.py                    # Tạo GraphCypherQAChain và hỏi đáp với Neo4j
|-- data_user500.csv               # Dataset hành vi 500 user
|-- model_best.pth                 # Trọng số model tốt nhất sau huấn luyện
|-- evaluation_plots.png           # Biểu đồ loss/accuracy sau huấn luyện
|-- db.sqlite3                     # Database SQLite của Django
|-- requirements.txt               # Danh sách thư viện Python chính
|-- Dockerfile                     # Image cho Django app
|-- docker-compose.yml             # Chạy Django + Neo4j
|-- services/
|   |-- catalog_service/           # Microservice quản lý catalog và tồn kho
|   |-- order_service/             # Microservice quản lý đơn hàng
|   |-- user_service/              # Microservice quản lý người dùng
|   |-- ai_service/                # Microservice chatbot/RAG
|   |-- payment_service/           # Microservice thanh toán
|   |-- product_service/           # Microservice quản lý kho hàng
|   `-- shipping_service/          # Microservice vận chuyển/giao nhận
|-- api-gateway/                   # Tài liệu API gateway và nginx route mẫu
|-- manage.py                      # Django management script
`-- BaoCao_HeThongDeXuat.tex       # Báo cáo LaTeX về hệ thống đề xuất
```

## Microservice Catalog

Thư mục:

```text
services/catalog_service/
```

Service này sở hữu dữ liệu:

- `Category`
- `Product`

Các API chính:

| Endpoint | Method | Chức năng |
| --- | --- | --- |
| `/health/` | GET | Kiểm tra service sống |
| `/api/categories/` | GET | Danh sách danh mục |
| `/api/products/` | GET | Danh sách sản phẩm |
| `/api/products/<id>/` | GET | Chi tiết sản phẩm |
| `/api/stock/reserve/` | POST | Trừ/reserve tồn kho khi tạo đơn |

Chạy riêng:

```bash
cd services/catalog_service
python manage.py migrate
python manage.py runserver 127.0.0.1:8001
```

## Microservice Order

Thư mục:

```text
services/order_service/
```

Service này sở hữu dữ liệu:

- `Order`
- `OrderItem`

Các API chính:

| Endpoint | Method | Chức năng |
| --- | --- | --- |
| `/health/` | GET | Kiểm tra service sống |
| `/api/orders/` | POST | Tạo đơn hàng |
| `/api/orders/<id>/` | GET | Xem chi tiết đơn |

Khi tạo đơn, `order_service` gọi sang `catalog_service` để reserve stock, thay vì truy cập trực tiếp database catalog. Đây là nguyên tắc quan trọng của microservices: service chỉ giao tiếp qua API.

Chạy riêng:

```bash
cd services/order_service
set CATALOG_SERVICE_URL=http://127.0.0.1:8001
python manage.py migrate
python manage.py runserver 127.0.0.1:8002
```

## Microservice User

Thư mục:

```text
services/user_service/
```

Service này sở hữu dữ liệu:

- `Customer`

Các trường chính của `Customer`:

- `email`
- `password_hash`
- `full_name`
- `phone`
- `address`
- `city`
- `postal_code`
- `role`
- `is_active`

Các API chính:

| Endpoint | Method | Chức năng |
| --- | --- | --- |
| `/health/` | GET | Kiểm tra service sống |
| `/api/users/` | GET | Danh sách người dùng |
| `/api/users/` | POST | Đăng ký người dùng |
| `/api/users/login/` | POST | Đăng nhập cơ bản |
| `/api/users/<id>/` | GET | Xem hồ sơ người dùng |
| `/api/users/<id>/` | PATCH/PUT | Cập nhật hồ sơ/trạng thái |

Ví dụ đăng ký:

```json
{
  "email": "customer@example.com",
  "password": "secret123",
  "full_name": "Nguyen Van A",
  "phone": "0900000000",
  "address": "123 Market Street",
  "city": "Bangkok",
  "postal_code": "10110"
}
```

Chạy riêng:

```bash
cd services/user_service
python manage.py migrate
python manage.py runserver 127.0.0.1:8003
```

## Microservice AI

Thư mục:

```text
services/ai_service/
```

Service này tách phần chatbot/RAG ra khỏi storefront. Nó dùng lại logic trong `rag_chat.py`, kết nối Neo4j và Groq, đồng thời lưu log câu hỏi vào model `ChatLog`.

Các API chính:

| Endpoint | Method | Chức năng |
| --- | --- | --- |
| `/health/` | GET | Kiểm tra service sống |
| `/api/chat/` | POST | Gửi câu hỏi đến chatbot/RAG |

Ví dụ request:

```json
{
  "message": "Which products are popular?"
}
```

Chạy riêng:

```bash
cd services/ai_service
python manage.py migrate
python manage.py runserver 127.0.0.1:8004
```

## Microservice Payment

Thư mục:

```text
services/payment_service/
```

Service này sở hữu model `Payment`, quản lý thông tin thanh toán theo đơn hàng. Hiện tại service mô phỏng payment flow cơ bản, phù hợp cho giai đoạn MVP trước khi tích hợp cổng thanh toán thật.

Các API chính:

| Endpoint | Method | Chức năng |
| --- | --- | --- |
| `/health/` | GET | Kiểm tra service sống |
| `/api/payments/` | POST | Tạo payment |
| `/api/payments/<id>/` | GET | Xem chi tiết payment |
| `/api/payments/<id>/confirm/` | POST | Xác nhận payment thành công |
| `/api/payments/<id>/fail/` | POST | Đánh dấu payment thất bại |

Ví dụ tạo payment:

```json
{
  "order_id": 1,
  "amount": "2157.84",
  "customer_email": "customer@example.com",
  "method": "cod",
  "currency": "USD"
}
```

Chạy riêng:

```bash
cd services/payment_service
python manage.py migrate
python manage.py runserver 127.0.0.1:8005
```

## Microservice Product/Inventory

Thư mục:

```text
services/product_service/
```

Service này quản lý hàng hóa trong kho, tách khỏi catalog bán hàng. Catalog trả dữ liệu sản phẩm để hiển thị, còn Product/Inventory service theo dõi hàng hóa thực tế trong warehouse.

Model chính:

- `Warehouse`
- `InventoryItem`
- `StockMovement`

API chính:

| Endpoint | Method | Chức năng |
| --- | --- | --- |
| `/health/` | GET | Kiểm tra service sống |
| `/api/warehouses/` | GET/POST | Danh sách/tạo kho |
| `/api/inventory/` | GET/POST | Danh sách/tạo hàng hóa trong kho |
| `/api/inventory/<id>/` | GET | Chi tiết tồn kho |
| `/api/inventory/<id>/adjust/` | POST | Điều chỉnh tồn kho |
| `/api/inventory/<id>/reserve/` | POST | Reserve hàng hóa |
| `/api/inventory/<id>/release/` | POST | Hoàn reserve |
| `/api/movements/` | GET | Lịch sử biến động kho |

Admin của service này hiển thị kho, item tồn kho và stock movement ngay trên trang admin của Product service.

Chạy riêng:

```bash
cd services/product_service
python manage.py migrate
python manage.py runserver 127.0.0.1:8006
```

## Microservice Shipping

Thư mục:

```text
services/shipping_service/
```

Service này điều phối đối tác vận chuyển và lộ trình giao nhận.

Model chính:

- `Carrier`
- `Shipment`
- `RouteEvent`

API chính:

| Endpoint | Method | Chức năng |
| --- | --- | --- |
| `/health/` | GET | Kiểm tra service sống |
| `/api/carriers/` | GET/POST | Danh sách/tạo đối tác vận chuyển |
| `/api/shipments/` | GET/POST | Danh sách/tạo shipment |
| `/api/shipments/<id>/` | GET | Chi tiết shipment và lộ trình |
| `/api/shipments/<id>/assign/` | POST | Gán đối tác vận chuyển |
| `/api/shipments/<id>/events/` | POST | Thêm trạng thái/lộ trình giao nhận |

Admin của service này hiển thị carrier, shipment và route event ngay trên trang admin của Shipping service.

Chạy riêng:

```bash
cd services/shipping_service
python manage.py migrate
python manage.py runserver 127.0.0.1:8007
```

## Luồng chính của website

Website được route từ `aiecommerce2/urls.py`:

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ecommerce_ai.urls')),
]
```

Toàn bộ route phía người dùng nằm trong `ecommerce_ai/urls.py`:

| URL | View | Chức năng |
| --- | --- | --- |
| `/` | `home` | Trang chủ, hiển thị danh sách sản phẩm |
| `/product/<product_id>/` | `product_detail` | Trang chi tiết sản phẩm |
| `/cart/` | `cart` | Trang giỏ hàng |
| `/checkout/` | `checkout` | Trang nhập thông tin thanh toán |
| `/checkout/success/<order_id>/` | `checkout_success` | Xác nhận đơn hàng đã tạo |
| `/api/chat/` | `chat_api` | API chatbot AI |
| `/api/cart/add/` | `cart_add` | API thêm sản phẩm vào giỏ |
| `/api/cart/remove/` | `cart_remove` | API xóa sản phẩm khỏi giỏ |
| `/api/cart/update/` | `cart_update` | API cập nhật số lượng sản phẩm |

## Dữ liệu sản phẩm

Sản phẩm hiện được lưu trong database Django qua model `Product`, liên kết với model `Category`. Dữ liệu mẫu ban đầu được seed bằng migration `ecommerce_ai/migrations/0002_seed_initial_catalog.py`.

Mỗi sản phẩm có các thông tin:

- `id`
- `name`
- `category`
- `price`
- `original_price`
- `icon`
- `color`
- `short_desc`
- `description`
- `features`
- `rating`
- `reviews`
- `stock`

Website hiện có 4 sản phẩm mẫu:

- `Quantum Audio Pro`
- `DevStation X1`
- `Vision X Content Kit`
- `LifeTracker Smartwatch`

Các sản phẩm có thể được quản lý trong Django Admin. `ProductAdmin` hỗ trợ lọc theo danh mục/trạng thái, tìm kiếm theo tên/mô tả, chỉnh nhanh giá, tồn kho và trạng thái hiển thị.

## Model dữ liệu bán hàng

File `ecommerce_ai/models.py` định nghĩa 4 model chính:

- `Category`: danh mục sản phẩm.
- `Product`: sản phẩm điện tử, giá bán, giá gốc, tồn kho, mô tả, tính năng, rating.
- `Order`: thông tin khách hàng, địa chỉ giao hàng, subtotal, tax, total và trạng thái đơn.
- `OrderItem`: từng dòng sản phẩm trong đơn hàng, lưu snapshot tên sản phẩm, đơn giá, số lượng và thành tiền.

Khi checkout thành công, hệ thống tạo `Order`, tạo các `OrderItem`, trừ tồn kho sản phẩm và xóa giỏ hàng khỏi session.

## Giỏ hàng

Giỏ hàng được lưu bằng Django session, không lưu trong database.

Các helper chính trong `ecommerce_ai/views.py`:

- `get_cart(request)`: lấy giỏ hàng từ session.
- `save_cart(request, cart)`: lưu giỏ hàng vào session.
- `cart_count(cart)`: tính tổng số lượng sản phẩm trong giỏ.
- `cart_totals(cart)`: tạo danh sách item, tính subtotal, tax và total.

Dữ liệu giỏ hàng có dạng dictionary:

```python
{
    "1": 2,
    "3": 1
}
```

Trong đó key là `product_id` dạng chuỗi, value là số lượng.

Thuế được tính cố định là `8%`:

```python
tax = round(subtotal * 0.08, 2)
total = round(subtotal + tax, 2)
```

## API giỏ hàng

Các API giỏ hàng đều nhận request `POST` với JSON body.

### Thêm sản phẩm

Endpoint:

```text
POST /api/cart/add/
```

Body:

```json
{
  "product_id": 1,
  "quantity": 1
}
```

Response thành công:

```json
{
  "success": true,
  "cart_count": 1
}
```

### Xóa sản phẩm

Endpoint:

```text
POST /api/cart/remove/
```

Body:

```json
{
  "product_id": 1
}
```

Response trả về lại tổng tiền mới:

```json
{
  "success": true,
  "cart_count": 0,
  "subtotal": 0,
  "tax": 0.0,
  "total": 0.0
}
```

### Cập nhật số lượng

Endpoint:

```text
POST /api/cart/update/
```

Body:

```json
{
  "product_id": 1,
  "quantity": 3
}
```

Nếu `quantity <= 0`, sản phẩm sẽ bị xóa khỏi giỏ.

## Giao diện người dùng

Các template nằm trong `ecommerce_ai/templates/ecommerce_ai/`.

### `index.html`

Trang chủ hiển thị danh sách sản phẩm dạng card. Mỗi card có icon Font Awesome, tên sản phẩm, mô tả ngắn, giá, giá gốc và nút thêm vào giỏ.

Trang này cũng chứa chatbot nổi ở góc dưới bên phải. Chatbot gửi request đến:

```text
POST /api/chat/
```

### `product_detail.html`

Trang chi tiết sản phẩm hiển thị:

- Breadcrumb
- Hình/icon sản phẩm
- Category
- Rating
- Giá và giá gốc
- Số tiền tiết kiệm
- Mô tả dài
- Danh sách tính năng
- Bộ chọn số lượng
- Nút thêm vào giỏ
- Danh sách sản phẩm liên quan

### `cart.html`

Trang giỏ hàng hiển thị:

- Danh sách sản phẩm đã thêm
- Nút tăng/giảm số lượng
- Nút xóa sản phẩm
- Subtotal
- Tax 8%
- Total
- Nút chuyển sang checkout

JavaScript trong trang gọi các API `/api/cart/update/` và `/api/cart/remove/` để cập nhật giỏ hàng không cần reload toàn bộ trang.

### `checkout.html`

Trang checkout gồm:

- Form nhập thông tin khách hàng.
- Tóm tắt đơn hàng.
- Nút `Place Order`.

Form checkout gửi `POST` về view `checkout`. Nếu dữ liệu hợp lệ và tồn kho đủ, hệ thống tạo đơn hàng thật trong database. Project hiện chưa tích hợp cổng thanh toán online, nên trạng thái mặc định của đơn là `pending`.

### `checkout_success.html`

Trang xác nhận đặt hàng thành công. URL nhận `order_id`, tải đơn hàng từ database và hiển thị mã đơn cùng tổng tiền.

## Chatbot AI và RAG

Chatbot được tích hợp qua `rag_chat.py` và endpoint `chat_api` trong `ecommerce_ai/views.py`.

### Luồng hoạt động

1. Người dùng nhập câu hỏi ở chatbot trên trang chủ.
2. JavaScript gửi request đến `/api/chat/`.
3. View `chat_api` gọi `get_chain()`.
4. `get_chain()` lazy-load module `rag_chat`.
5. `rag_chat.setup_rag()` kết nối Neo4j và tạo `GraphCypherQAChain`.
6. Câu hỏi được đưa vào chain bằng `rag_module.ask_question(chain, message)`.
7. Kết quả được trả về frontend dưới dạng JSON.

### Cấu hình RAG

Trong `rag_chat.py`, hệ thống dùng:

- `Neo4jGraph` để kết nối graph database.
- `ChatGroq` làm LLM.
- Model Groq: `llama-3.3-70b-versatile`.
- `GraphCypherQAChain` để sinh và chạy Cypher query trên Neo4j.

Các biến môi trường được dùng:

```text
NEO4J_URI
NEO4J_USER
NEO4J_PASSWORD
GROQ_API_KEY
```

Nếu chưa cấu hình `GROQ_API_KEY` hoặc Neo4j chưa chạy, `/api/chat/` sẽ trả lỗi:

```text
RAG system is not initialized. Ensure GROQ_API_KEY is configured and Neo4j is running.
```

## Neo4j Knowledge Graph

File `setup_neo4j.py` dùng dataset `data_user500.csv` để tạo graph trong Neo4j.

### Node

Graph có 2 loại node:

- `User`
- `Product`

### Relationship

Relationship được tạo dựa trên cột `action`:

- `view` thành `VIEWED`
- `click` thành `CLICKED`
- `add_to_cart` thành `ADDED_TO_CART`

Mỗi relationship có thuộc tính:

```text
timestamp
```

### Index

Script tạo index:

```cypher
CREATE INDEX user_id_idx IF NOT EXISTS FOR (u:User) ON (u.id)
CREATE INDEX product_id_idx IF NOT EXISTS FOR (p:Product) ON (p.id)
```

### Cách nạp dữ liệu vào Neo4j

Chạy Neo4j trước:

```bash
docker-compose up -d neo4j
```

Sau đó chạy:

```bash
python setup_neo4j.py
```

Script sẽ:

1. Kết nối Neo4j.
2. Đọc `data_user500.csv`.
3. Xóa dữ liệu graph cũ.
4. Tạo index.
5. Nạp user, product và relationship mới.

## Dataset hành vi người dùng

File `generate_data.py` sinh dataset giả lập cho hệ thống đề xuất.

Thông số dataset:

- 500 users: `U001` đến `U500`.
- 50 products: `P001` đến `P050`.
- Mỗi user có đúng 8 hành vi.
- Tổng cộng 4.000 dòng dữ liệu.
- Các action gồm:
  - `view`
  - `click`
  - `add_to_cart`

Trọng số action ban đầu:

```python
action_weights = [0.6, 0.3, 0.1]
```

Script có thêm logic mô phỏng hành vi tự nhiên:

- Sau `view`, user có xác suất chuyển sang `click`.
- Sau `click`, user có xác suất chuyển sang `add_to_cart`.

Chạy tạo lại dataset:

```bash
python generate_data.py
```

Kết quả được ghi vào:

```text
data_user500.csv
```

## Huấn luyện mô hình dự đoán hành vi

File `train_models.py` đọc `data_user500.csv` và huấn luyện 3 mô hình sequence:

- `RNNModel`
- `LSTMModel`
- `BiLSTMModel`

Mục tiêu là dùng 7 hành vi đầu của mỗi user để dự đoán hành vi thứ 8.

### Quy trình xử lý

1. Đọc CSV bằng Pandas.
2. Sort theo `user_id` và `timestamp`.
3. Encode action bằng `LabelEncoder`.
4. Gom từng user thành sequence.
5. Lấy 7 action đầu làm input.
6. Lấy action thứ 8 làm label.
7. Chia train/test với `test_size=0.2`.
8. Huấn luyện 30 epoch.
9. Đánh giá bằng accuracy, precision, recall và F1 score.
10. Lưu model tốt nhất vào `model_best.pth`.
11. Lưu biểu đồ vào `evaluation_plots.png`.

### Tham số model

```python
embed_dim = 16
hidden_dim = 32
epochs = 30
batch_size = 16
learning_rate = 0.005
```

Chạy huấn luyện:

```bash
python train_models.py
```

Lưu ý: `train_models.py` cần PyTorch (`torch`). Trong `Dockerfile`, torch được cài riêng bằng:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

Tuy nhiên `requirements.txt` hiện chưa liệt kê `torch`, nên nếu chạy local bạn cần cài thêm PyTorch thủ công.

## Cấu hình Django

File cấu hình chính là `aiecommerce2/settings.py`.

Một số cấu hình quan trọng:

```python
DEBUG = False
ALLOWED_HOSTS = ['*']
```

App đã cài:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'ecommerce_ai',
]
```

Database đang dùng SQLite:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Template được cấu hình để đọc từ:

```python
'DIRS': [BASE_DIR / 'templates']
```

và vẫn bật:

```python
'APP_DIRS': True
```

Do đó Django cũng đọc được template trong `ecommerce_ai/templates/ecommerce_ai/`.

## Chạy project local

### 1. Tạo môi trường ảo

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 2. Cài dependencies

```bash
pip install -r requirements.txt
```

Nếu muốn chạy phần huấn luyện model:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### 3. Chạy migrate

```bash
python manage.py migrate
```

### 4. Chạy Django server

```bash
python manage.py runserver
```

Mở trình duyệt tại:

```text
http://127.0.0.1:8000/
```

## Chạy bằng Docker Compose

Build và chạy toàn bộ:

```bash
docker-compose up --build
```

Django app chạy tại:

```text
http://localhost:8000/
```

Catalog service chạy tại:

```text
http://localhost:8001/
```

Order service chạy tại:

```text
http://localhost:8002/
```

User service chạy tại:

```text
http://localhost:8003/
```

AI service chạy tại:

```text
http://localhost:8004/
```

Payment service chạy tại:

```text
http://localhost:8005/
```

Product/Inventory service chạy tại:

```text
http://localhost:8006/
```

Shipping service chạy tại:

```text
http://localhost:8007/
```

Neo4j Browser chạy tại:

```text
http://localhost:7474/
```

Thông tin đăng nhập Neo4j mặc định trong `docker-compose.yml`:

```text
username: neo4j
password: password
```

Sau khi Neo4j chạy, nạp dữ liệu:

```bash
python setup_neo4j.py
```

Nếu chạy script từ host mà Neo4j đang chạy trong Docker, cấu hình mặc định `bolt://localhost:7687` là phù hợp. Nếu chạy script trong container web, URI nên là:

```text
bolt://neo4j:7687
```

## Biến môi trường

Các biến môi trường liên quan đến Neo4j và Groq:

```text
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
GROQ_API_KEY=your-groq-api-key
```

Các biến môi trường liên quan đến microservices:

```text
USE_MICROSERVICES=1
CATALOG_SERVICE_URL=http://catalog:8001
ORDER_SERVICE_URL=http://orders:8002
USER_SERVICE_URL=http://users:8003
AI_SERVICE_URL=http://ai:8004
PAYMENT_SERVICE_URL=http://payments:8005
PRODUCT_SERVICE_URL=http://products:8006
SHIPPING_SERVICE_URL=http://shipping:8007
```

Trong `docker-compose.yml`, các biến này được truyền vào service `web`.

Lưu ý bảo mật: không nên hardcode API key thật trong repository. Nên chuyển `GROQ_API_KEY`, `SECRET_KEY` và mật khẩu database sang file `.env` hoặc secret manager.

## Báo cáo và artifact

Codebase có một số file kết quả/phụ trợ:

- `BaoCao_HeThongDeXuat.tex`: báo cáo LaTeX về hệ thống đề xuất.
- `data_user500.csv`: dataset đã sinh sẵn.
- `model_best.pth`: trọng số model tốt nhất.
- `evaluation_plots.png`: biểu đồ quá trình huấn luyện.
- `db.sqlite3`: database SQLite local của Django.

## Những điểm cần chú ý trong codebase hiện tại

- Checkout đã lưu order thật nhưng chưa tích hợp thanh toán online.
- Cart vẫn lưu trong session, phù hợp cho demo hoặc cửa hàng nhỏ; nếu cần cart đa thiết bị thì nên chuyển sang model `Cart`/`CartItem`.
- `DEBUG = False` nhưng `ALLOWED_HOSTS = ['*']`; khi deploy thật nên cấu hình host cụ thể.
- `SECRET_KEY` đang hardcode trong `settings.py`; nên chuyển sang biến môi trường.
- `docker-compose.yml` đang chứa giá trị `GROQ_API_KEY`; nên thay bằng `.env`.
- `GraphCypherQAChain` đang bật `allow_dangerous_requests=True`; chỉ nên dùng khi kiểm soát rõ môi trường Neo4j và quyền truy cập.
- `requirements.txt` chưa có `torch`, trong khi `train_models.py` phụ thuộc vào PyTorch.
- Một số comment tiếng Việt trong `Dockerfile` đang bị lỗi encoding hiển thị.
- Trong `cart.html` có dòng CSS `background: rgba5,(1 23, 42, 0.85);` có vẻ là lỗi gõ nhầm và có thể khiến style navbar không đúng.

## Hướng phát triển tiếp theo

- Thêm model `Customer` hoặc dùng `django.contrib.auth` để khách hàng đăng nhập và xem lịch sử đơn.
- Thêm authentication cho user.
- Lưu lịch sử hành vi thật của người dùng thay vì chỉ dùng CSV giả lập.
- Kết nối model đề xuất với giao diện sản phẩm.
- Thêm test cho cart API, checkout flow và chat API.
- Thêm `.env.example` và loại bỏ secret khỏi source code.
- Tách CSS/JavaScript ra file static để dễ bảo trì.
