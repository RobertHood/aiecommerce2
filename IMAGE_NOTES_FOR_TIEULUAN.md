# Checklist ảnh cần capture cho tiểu luận

File LaTeX chính: `TieuLuan_Ecommerce_Microservices_Project.tex`

Các ảnh dưới đây tương ứng với các placeholder `TODO: Chèn ảnh` trong file LaTeX.

1. Context Map của hệ thống
   - Gợi ý: vẽ sơ đồ các bounded context gồm Storefront, Catalog, Order, User, Payment, Product/Inventory, Shipping, AI.

2. Product và Inventory Admin
   - Capture admin của Catalog Service và Product/Inventory Service.
   - Nên có `Category`, `Product`, `Warehouse`, `InventoryItem`, `StockMovement`.

3. Trang đăng ký, đăng nhập và tài khoản
   - URL: `/register/`, `/login/`, `/account/`.

4. Trang giỏ hàng
   - URL: `/cart/` sau khi thêm sản phẩm.

5. Payment Service Admin
   - Capture danh sách `Payment` sau khi checkout hoặc tạo payment API.

6. Shipping Service Admin
   - Capture `Carrier`, `Shipment`, `RouteEvent`.

7. Sequence diagram luồng mua hàng
   - Tự vẽ Browser -> Storefront -> Catalog -> Order -> Payment -> Shipping.

8. Class diagram tổng thể
   - Tự vẽ từ các model trong từng service:
   - Catalog: `Category`, `Product`
   - User: `Customer`
   - Order: `Order`, `OrderItem`
   - Payment: `Payment`
   - Product/Inventory: `Warehouse`, `InventoryItem`, `StockMovement`
   - Shipping: `Carrier`, `Shipment`, `RouteEvent`
   - AI: `ChatLog`

9. Chatbot trên trang chủ
   - Capture widget chatbot và một câu hỏi mẫu.

10. Biểu đồ huấn luyện model
   - Dùng ảnh `evaluation_plots.png`.

11. Neo4j Browser hiển thị graph
   - Capture sau khi chạy `setup_neo4j.py`.

12. Kiến trúc tổng thể hệ thống
   - Capture hoặc tự vẽ từ `docker-compose.yml`, gồm web, catalog, orders, users, ai, payments, products, shipping, neo4j.

13. Cấu trúc thư mục project
   - Capture cây thư mục trong IDE, đặc biệt `services/` và `api-gateway/`.

14. API Gateway README
   - Capture `api-gateway/README.md` hoặc `api-gateway/nginx.conf`.

15. Docker Compose chạy toàn bộ hệ thống
   - Capture Docker Desktop hoặc terminal khi các container đang chạy.

16. Sequence diagram checkout
   - Tự vẽ theo luồng:
   - Browser -> Storefront: POST `/checkout/`
   - Storefront -> Order Service: POST `/api/orders/`
   - Order Service -> Catalog Service: POST `/api/stock/reserve/`
   - Storefront -> Payment Service: POST `/api/payments/`
   - Storefront -> Browser: redirect `/checkout/success/<id>/`
