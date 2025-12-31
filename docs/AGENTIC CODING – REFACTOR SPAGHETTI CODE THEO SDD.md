I. THÔNG TIN CHUNG

Bài toán: Refactor hệ thống E-commerce Order Processing System (spaghetti code)

Công cụ sử dụng: GitHub Copilot (Copilot Chat / Copilot Workspace)

Phương pháp: Spec Driven Development (SDD)

Ngôn ngữ: Python

Mục tiêu:

Refactor code theo kiến trúc rõ ràng, dễ maintain

Áp dụng Design Patterns phù hợp

Đảm bảo testability và chất lượng code

II. PHẦN 1 – CÁC PROMPTS ĐÃ SỬ DỤNG (THEO QUY TRÌNH SDD)

Nguyên tắc thực hiện

Mỗi prompt chỉ giải quyết một bước trong SDD

Không refactor khi chưa có Spec & Design

1. Prompt phân tích code hiện tại (SDD – Discovery)
Phân tích file Python hiện tại như một hệ thống E-commerce chạy production.

Yêu cầu:
- Chỉ ra các vấn đề về:
  + Kiến trúc
  + SOLID
  + Global state
  + Coupling / cohesion
  + Security
  + Testability
- Phân loại mức độ nghiêm trọng (Critical / High / Medium / Low)

Ràng buộc:
- Không refactor
- Không đề xuất solution
- Chỉ phân tích


Mục đích:
Khoanh vùng toàn bộ vấn đề trước khi chỉnh sửa code.

2. Prompt viết SPEC hệ thống (SDD – Specification)
Dựa trên code hiện tại, hãy viết SPEC cho hệ thống E-commerce.

Yêu cầu:
- Xác định domain chính: User, Product, Order, Payment, Coupon, Notification
- Mô tả trách nhiệm từng domain
- Phân tách rõ:
  + Domain logic
  + Application service
  + Infrastructure
- Định hướng:
  + Dễ test
  + Không dùng global variable
  + Tuân thủ SOLID

Không viết code.


Mục đích:
Khóa phạm vi bài toán, tránh AI tự suy diễn nghiệp vụ.

3. Prompt thiết kế kiến trúc & cấu trúc thư mục (SDD – Design)
Đề xuất kiến trúc và cấu trúc thư mục Python cho hệ thống theo SPEC.

Yêu cầu:
- Có các layer:
  models / repositories / services / validators / utils / tests
- Giải thích ngắn gọn vai trò mỗi layer
- Ưu tiên testability và maintainability

Không viết code chi tiết.


Mục đích:
Khóa kiến trúc trước khi triển khai code.

4. Prompt chọn Design Patterns (SDD – Design Decision)
Chọn các Design Pattern phù hợp cho hệ thống.

Với mỗi pattern:
- Áp dụng ở đâu
- Vì sao phù hợp
- Giải quyết vấn đề gì trong code cũ

Gợi ý:
Repository, Service Layer, Strategy (discount/payment), Dependency Injection


Mục đích:
Mọi quyết định thiết kế đều có lý do rõ ràng.

5. Prompt tạo cấu trúc project (Copilot Workspace)
Tạo cấu trúc thư mục Python cho hệ thống E-commerce như đã thiết kế.

Yêu cầu:
- Chỉ tạo folder và file rỗng
- Đúng chuẩn Python package (__init__.py)
- Chưa viết logic


Mục đích:
Chuẩn bị nền tảng trước khi refactor.

6. Prompt refactor từng module (SDD – Implementation)
Refactor logic tạo order từ file cũ sang OrderService.

Yêu cầu:
- Không dùng global variable
- Không truy cập DB trực tiếp trong controller
- Nhận repository và payment service qua constructor
- Ném exception thay vì return dict lỗi


Mục đích:
Refactor từng phần nhỏ, kiểm soát rủi ro.

7. Prompt viết Unit Test (SDD – Verification)
Viết unit test bằng pytest cho service hiện tại.

Yêu cầu:
- Test happy path
- Test input không hợp lệ
- Test unauthorized
- Test out-of-stock
- Mock database và email
- Không phụ thuộc global state


Mục đích:
Xác minh hệ thống đúng nghiệp vụ và dễ bảo trì.

8. Prompt review kết quả (SDD – Validation)
Review file / module hiện tại.

Đánh giá:
- Code đã tách đúng responsibility chưa?
- Có vi phạm SOLID không?
- Design Pattern dùng đúng chưa?
- Có khó test không?

Đề xuất cải tiến nếu có.


Mục đích:
Đảm bảo chất lượng cuối cùng trước khi kết thúc bài.

III. PHẦN 2 – MÔ TẢ CHI TIẾT QUY TRÌNH GIẢI BÀI
1. Tiếp cận bài toán

Thay vì refactor trực tiếp spaghetti code, tôi áp dụng Spec Driven Development (SDD) nhằm:

Tránh refactor cảm tính

Tránh việc AI tự “đoán nghiệp vụ”

Kiểm soát chất lượng thiết kế ngay từ đầu

2. Các bước thực hiện
Bước 1: Phân tích & đóng băng vấn đề

Sử dụng Copilot Chat để phân tích code

Không chỉnh sửa code ở bước này

Ghi nhận các vấn đề lớn: global state, God method, vi phạm SOLID

Bước 2: Viết SPEC

Xác định rõ domain và trách nhiệm

Tách domain logic khỏi hạ tầng

Định nghĩa yêu cầu phi chức năng (testability, maintainability)

Bước 3: Thiết kế kiến trúc

Áp dụng layered architecture

Tách models – repositories – services

Chuẩn bị cho unit test ngay từ đầu

Bước 4: Chọn Design Patterns

Repository Pattern để tách DB

Service Layer cho business logic

Strategy Pattern cho discount & payment

Dependency Injection để giảm coupling, dễ test

Bước 5: Refactor từng phần nhỏ

Không refactor toàn bộ một lần

Refactor theo từng module

Mỗi module đều tuân thủ spec đã định nghĩa

Bước 6: Viết unit test

Test cả happy path và edge cases

Mock các dependency bên ngoài

Đảm bảo coverage ≥ 80%

Bước 7: Review & đánh giá

Kiểm tra lại SOLID

Đánh giá khả năng mở rộng

Ghi nhận các cải tiến có thể thực hiện trong tương lai