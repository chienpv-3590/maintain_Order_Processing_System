# 📋 CODE REVIEW: OrderService Module

## ✅ ĐIỂM MẠNH

### 1. **Separation of Responsibilities - TỐT (8/10)**
- ✅ Service layer tách biệt khỏi domain và infrastructure
- ✅ DTOs tách biệt data transfer
- ✅ Exceptions có hierarchy rõ ràng
- ✅ Repositories abstract data access

### 2. **SOLID Principles - TUÂN THỦ TỐT (7/10)**

#### ✅ Single Responsibility Principle
- Service tập trung vào orchestration
- Mỗi exception có 1 mục đích cụ thể

#### ✅ Open/Closed Principle  
- Mở rộng qua interfaces (IRepository)
- Có thể thêm repository implementations mà không sửa service

#### ✅ Liskov Substitution Principle
- Interfaces có thể swap implementations
- Mock dễ dàng trong tests

#### ✅ Interface Segregation Principle
- Repositories tách biệt: IOrderRepository, IProductRepository, ICouponRepository, IUserRepository
- Không có fat interface

#### ✅ Dependency Inversion Principle
- Service depends on abstractions (interfaces)
- Constructor injection rõ ràng

### 3. **Design Patterns - ÁP DỤNG ĐÚNG (8/10)**

✅ **Repository Pattern**: Tách data access hoàn toàn  
✅ **Dependency Injection**: Constructor-based, testable  
✅ **DTO Pattern**: Clean data transfer, validation separation  
✅ **Exception-based Error Handling**: Thay vì return codes

### 4. **Testability - RẤT DỄ TEST (9/10)**

✅ Pure dependency injection  
✅ No global state  
✅ No static methods  
✅ Clear inputs/outputs  
✅ Fixtures dễ setup  
✅ 100% mock được dependencies

---

## 🔴 VẤN ĐỀ NGHIÊM TRỌNG

### **1. VI PHẠM SRP - `create_order()` làm quá nhiều việc (210 lines)**

**Vấn đề**: God Method anti-pattern
```python
def create_order(self, dto):
    # Validate ✓
    # Check stock ✓
    # Calculate pricing ✓
    # Apply coupon ✓
    # Process payment ✓
    # Generate ID ✓
    # Save order ✓
    # Build response ✓
    # TOO MANY RESPONSIBILITIES!
```

**Hậu quả**:
- Khó maintain
- Khó đọc
- Khó test từng phần
- Vi phạm Single Responsibility

**Điểm**: 3/10

---

### **2. THIẾU Transaction Management - CRITICAL**

**Vấn đề**: Race condition và data inconsistency
```python
# Line 130: Stock được trừ
self._product_repository.update_stock(product_id, -quantity)

# Line 160: Coupon usage được increment  
self._coupon_repository.increment_usage(code)

# Line 185: User balance được trừ
self._user_repository.update_balance(user_id, -total)

# Line 200: Order được save
self._order_repository.save(order_data)

# ❌ NẾU save() FAIL → Stock đã mất, balance đã trừ, coupon đã dùng!
```

**Giải pháp cần thiết**:
```python
# Unit of Work pattern
with self._unit_of_work:
    # All operations here
    self._unit_of_work.commit()  # Atomic
```

**Điểm**: 2/10 (Critical bug)

---

### **3. BUSINESS LOGIC RÒ RỈ VÀO APPLICATION LAYER**

**Vấn đề**: Tax calculation thuộc Domain, không phải Application Service
```python
# ❌ Application service KHÔNG NÊN biết cách tính tax
TAX_RATE = Decimal("0.1")
tax = taxable_amount * self.TAX_RATE

# ❌ Application service KHÔNG NÊN biết cách tính discount
discount = subtotal * (discount_percentage / Decimal("100"))
```

**Đúng**: Tạo Domain Service
```python
# domain/services/pricing_service.py
class PricingService:
    def calculate_tax(self, amount: Decimal) -> Decimal:
        return amount * self.TAX_RATE
    
    def calculate_discount(self, subtotal: Decimal, percentage: int) -> Decimal:
        return subtotal * (Decimal(percentage) / Decimal("100"))
```

**Điểm**: 4/10

---

### **4. COUPLING VỚI USER ROLE LOGIC**

**Vấn đề**: Service layer biết quá nhiều về business rules
```python
# ❌ Application service KHÔNG NÊN biết logic VIP
if user and user['role'] == 'vip':
    if user_balance >= final_total:
        # Process payment
```

**Giải pháp**: Strategy Pattern
```python
payment_strategy = PaymentStrategyFactory.get_strategy(user)
payment_result = payment_strategy.process(amount, user)
```

**Điểm**: 5/10

---

### **5. THIẾU DOMAIN EVENTS**

**Vấn đề**: Không có cách nào notify các hệ thống khác khi order được tạo

**Cần**: Event-Driven Architecture
```python
# Publish event sau khi order created
event = OrderCreated(order_id, user_id, total, items)
self._event_bus.publish(event)

# Other services subscribe:
# - EmailService → send confirmation
# - AnalyticsService → track revenue
# - NotificationService → push notification
# - InventoryService → update warehouse
```

**Điểm**: 5/10

---

### **6. KHÔNG HANDLE PARTIAL FAILURES**

**Vấn đề**: 
```python
for item in items:
    self._product_repository.update_stock(...)  # Item 1 success
    # ❌ Error on item 2 → Item 1 stock already decreased!
```

**Cần**: Either commit all or rollback all

**Điểm**: 3/10

---

### **7. ID GENERATION KHÔNG AN TOÀN**

```python
def _generate_order_id(self) -> int:
    return int(datetime.now().timestamp() * 1000)
    # ❌ Collision risk in distributed systems
    # ❌ Không đảm bảo uniqueness
```

**Điểm**: 4/10

---

## 📊 TỔNG KẾT ĐÁNH GIÁ

| Tiêu chí | Điểm | Mức độ |
|----------|------|--------|
| Separation of Concerns | 8/10 | ✅ Tốt |
| Single Responsibility | 3/10 | 🔴 Kém |
| SOLID Principles | 7/10 | ✅ Khá tốt |
| Design Patterns | 8/10 | ✅ Tốt |
| Testability | 9/10 | ✅ Rất tốt |
| Transaction Safety | 2/10 | 🔴 Nguy hiểm |
| Domain Logic Placement | 4/10 | ⚠️ Trung bình |
| Event-Driven | 5/10 | ⚠️ Trung bình |
| Error Handling | 7/10 | ✅ Khá tốt |
| **TỔNG ĐIỂM** | **53/90** | ⚠️ **CẦN CẢI THIỆN** |

---

## 🎯 ĐỀ XUẤT CẢI TIẾN (Ưu tiên)

### Priority 1: CRITICAL (Phải làm ngay)

#### ✅ **1. Implement Unit of Work Pattern**
```python
# infrastructure/persistence/unit_of_work.py
class SqliteUnitOfWork(IUnitOfWork):
    def __init__(self, connection):
        self._connection = connection
        self._transaction = None
    
    def __enter__(self):
        self._transaction = self._connection.begin()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._transaction.rollback()
        return False
    
    def commit(self):
        self._transaction.commit()
    
    def rollback(self):
        self._transaction.rollback()

# Usage in OrderService
def create_order(self, dto):
    with self._unit_of_work:
        # All operations
        self._unit_of_work.commit()  # Atomic!
```

#### ✅ **2. Extract Method - Tách `create_order()` thành nhiều methods nhỏ**
```python
def create_order(self, dto):
    with self._unit_of_work:
        self._validate_input(dto)
        reservation = self._reserve_inventory(dto.items)
        pricing = self._calculate_pricing(reservation, dto.coupon_code)
        payment = self._process_payment(dto.user_id, pricing)
        order_id = self._save_order(dto, pricing, payment)
        self._publish_events(order_id, dto, pricing)
        self._unit_of_work.commit()
        return self._build_response(order_id, pricing, payment)
```

### Priority 2: HIGH (Nên làm sớm)

#### ✅ **3. Tạo Domain Services**
```python
# domain/services/pricing_service.py
class PricingService:
    def calculate_order_total(self, items, coupon_code):
        subtotal = self._calculate_subtotal(items)
        discount = self._calculate_discount(subtotal, coupon_code)
        tax = self._calculate_tax(subtotal - discount)
        return PricingResult(subtotal, discount, tax)

# domain/services/inventory_service.py  
class InventoryService:
    def reserve_items(self, items):
        # Validate and reserve stock
        # Return reservation or raise exception
```

#### ✅ **4. Strategy Pattern cho Payment**
```python
# application/strategies/payment_strategy.py
class VIPPaymentStrategy:
    def can_process(self, user, amount):
        return user['role'] == 'vip' and user['balance'] >= amount
    
    def process(self, user, amount):
        self._user_repo.update_balance(user['id'], -amount)
        return PaymentResult(status='paid')

class StandardPaymentStrategy:
    def process(self, user, amount):
        return PaymentResult(status='pending_payment')
```

#### ✅ **5. Add Domain Events**
```python
# domain/events/order_events.py
@dataclass
class OrderCreated(DomainEvent):
    order_id: int
    user_id: int
    total: Decimal
    items: List[dict]

# Publish in service
self._event_bus.publish(OrderCreated(...))

# Subscribers handle async
class EmailNotificationHandler:
    def handle(self, event: OrderCreated):
        self._email_service.send_order_confirmation(event)
```

### Priority 3: MEDIUM (Cải tiến dần)

#### ✅ **6. Value Objects cho domain concepts**
```python
# domain/value_objects/money.py
class Money:
    def __init__(self, amount: Decimal, currency: str = "USD"):
        self.amount = amount
        self.currency = currency
    
    def add_tax(self, rate: Decimal):
        return Money(self.amount * (1 + rate), self.currency)

# domain/value_objects/order_item.py
class OrderItem:
    def __init__(self, product_id, quantity, price):
        self._validate(product_id, quantity, price)
        self.product_id = product_id
        self.quantity = quantity
        self.price = Money(price)
    
    def calculate_subtotal(self):
        return Money(self.price.amount * self.quantity)
```

#### ✅ **7. Aggregate cho Order**
```python
# domain/aggregates/order.py
class Order:
    """Order Aggregate Root"""
    
    def __init__(self, order_id, user_id):
        self.id = order_id
        self.user_id = user_id
        self.items = []
        self.status = OrderStatus.PENDING
        self._events = []
    
    def add_item(self, item: OrderItem):
        self.items.append(item)
        self._events.append(OrderItemAdded(self.id, item))
    
    def confirm(self):
        if self.status != OrderStatus.PENDING:
            raise InvalidOrderStateException()
        self.status = OrderStatus.CONFIRMED
        self._events.append(OrderConfirmed(self.id))
```

---

## 📝 KẾT LUẬN

### ✅ **Code hiện tại là FUNCTIONAL** nhưng:

1. **Thiếu transaction safety** → Có thể mất data
2. **Method quá dài** → Khó maintain  
3. **Business logic rò rỉ** → Vi phạm Clean Architecture
4. **Không có events** → Khó mở rộng

### 🎯 **Ưu tiên làm**:

1. **Unit of Work** (ngay lập tức - critical)
2. **Extract methods** (tuần này)
3. **Domain Services** (tuần tới)
4. **Strategy Pattern** (sprint tới)
5. **Domain Events** (khi cần scale)

### 📈 **Sau khi refactor**:
- Transaction safe: 2/10 → 10/10
- SRP compliance: 3/10 → 9/10  
- Maintainability: 6/10 → 9/10
- Extensibility: 6/10 → 10/10

**Overall grade**: 53/90 → 85/90 ⭐

Xem file refactored example tại: [docs/REFACTORED_ORDER_SERVICE.py](docs/REFACTORED_ORDER_SERVICE.py)
