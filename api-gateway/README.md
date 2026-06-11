# API Gateway Map

Thư mục này mô tả các API chính của hệ thống microservices Nexus Store. File này có thể dùng như tài liệu gateway hoặc làm cơ sở viết cấu hình Nginx/Kong/Traefik sau này.

## Gateway Ports

| Service | Internal URL | Public Prefix |
| --- | --- | --- |
| Storefront/BFF | `http://web:8000` | `/` |
| Catalog Service | `http://catalog:8001` | `/catalog/` |
| Order Service | `http://orders:8002` | `/orders/` |
| User Service | `http://users:8003` | `/users/` |
| AI Service | `http://ai:8004` | `/ai/` |
| Payment Service | `http://payments:8005` | `/payments/` |
| Product/Inventory Service | `http://products:8006` | `/products/` |
| Shipping Service | `http://shipping:8007` | `/shipping/` |

## Storefront/BFF APIs

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Trang chủ cửa hàng |
| GET | `/product/<id>/` | Chi tiết sản phẩm |
| GET | `/cart/` | Trang giỏ hàng |
| GET/POST | `/checkout/` | Checkout |
| GET | `/checkout/success/<order_id>/` | Xác nhận đơn hàng |
| GET/POST | `/login/` | Đăng nhập frontend |
| GET/POST | `/register/` | Đăng ký frontend |
| GET | `/account/` | Trang tài khoản |
| GET | `/logout/` | Đăng xuất |
| POST | `/api/cart/add/` | Thêm sản phẩm vào giỏ |
| POST | `/api/cart/update/` | Cập nhật giỏ |
| POST | `/api/cart/remove/` | Xóa khỏi giỏ |
| POST | `/api/chat/` | Chatbot endpoint qua BFF |

## Catalog Service APIs

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health/` | Health check |
| GET | `/api/categories/` | Danh sách danh mục |
| GET | `/api/products/` | Danh sách sản phẩm bán |
| GET | `/api/products/<id>/` | Chi tiết sản phẩm bán |
| POST | `/api/stock/reserve/` | Reserve/trừ tồn kho catalog |

## Order Service APIs

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health/` | Health check |
| POST | `/api/orders/` | Tạo đơn hàng |
| GET | `/api/orders/<id>/` | Chi tiết đơn hàng |

## User Service APIs

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health/` | Health check |
| GET | `/api/users/` | Danh sách user |
| POST | `/api/users/` | Đăng ký user |
| POST | `/api/users/login/` | Đăng nhập user |
| GET | `/api/users/<id>/` | Hồ sơ user |
| PATCH/PUT | `/api/users/<id>/` | Cập nhật user |

## AI Service APIs

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health/` | Health check |
| POST | `/api/chat/` | Hỏi chatbot/RAG |

## Payment Service APIs

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health/` | Health check |
| POST | `/api/payments/` | Tạo payment |
| GET | `/api/payments/<id>/` | Chi tiết payment |
| POST | `/api/payments/<id>/confirm/` | Xác nhận payment thành công |
| POST | `/api/payments/<id>/fail/` | Đánh dấu payment thất bại |

## Product/Inventory Service APIs

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health/` | Health check |
| GET | `/api/warehouses/` | Danh sách kho |
| POST | `/api/warehouses/` | Tạo kho |
| GET | `/api/inventory/` | Danh sách hàng hóa trong kho |
| POST | `/api/inventory/` | Tạo item tồn kho |
| GET | `/api/inventory/<id>/` | Chi tiết item tồn kho |
| POST | `/api/inventory/<id>/adjust/` | Điều chỉnh tồn kho |
| POST | `/api/inventory/<id>/reserve/` | Reserve hàng hóa |
| POST | `/api/inventory/<id>/release/` | Hoàn reserve hàng hóa |
| GET | `/api/movements/` | Lịch sử stock movement |

## Shipping Service APIs

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health/` | Health check |
| GET | `/api/carriers/` | Danh sách đối tác vận chuyển |
| POST | `/api/carriers/` | Tạo đối tác vận chuyển |
| GET | `/api/shipments/` | Danh sách shipment |
| POST | `/api/shipments/` | Tạo shipment |
| GET | `/api/shipments/<id>/` | Chi tiết shipment/lộ trình |
| POST | `/api/shipments/<id>/assign/` | Gán đối tác vận chuyển |
| POST | `/api/shipments/<id>/events/` | Thêm sự kiện lộ trình/trạng thái |
