# DESIGN PATTERNS CHO E-COMMERCE SYSTEM

## TỔNG QUAN

Design patterns được chọn dựa trên:
- ✅ Giải quyết vấn đề cụ thể trong spaghetti code
- ✅ Tăng testability và maintainability
- ✅ Tuân thủ SOLID principles
- ✅ Phù hợp với Clean Architecture

---

## 1. REPOSITORY PATTERN

### Áp dụng ở đâu

**Domain Layer - Interfaces:**
```
domain/interfaces/
├── user_repository.py          # IUserRepository
├── product_repository.py       # IProductRepository
├── order_repository.py         # IOrderRepository
├── payment_repository.py       # IPaymentRepository
└── coupon_repository.py        # ICouponRepository
```

**Infrastructure Layer - Implementations:**
```
infrastructure/persistence/repositories/
├── sqlite_user_repository.py       # Concrete implementation
├── sqlite_product_repository.py
└── sqlite_order_repository.py
```

**Application Layer - Usage:**
```
application/services/
├── user_service.py             # Inject IUserRepository
├── order_service.py            # Inject IOrderRepository, IProductRepository
└── payment_service.py          # Inject IPaymentRepository
```

### Vì sao phù hợp

✅ **Separation of Concerns:**
- Data access logic tách khỏi business logic
- Domain không biết về database implementation

✅ **Testability:**
- Easy mock repositories trong unit tests
- Có thể dùng in-memory repository cho testing
- Không cần database khi test business logic

✅ **Flexibility:**
- Swap database (SQLite → PostgreSQL → MongoDB)
- Không affect business logic
- Multiple implementations (production, testing, caching)

✅ **SOLID Compliance:**
- **S:** Repository chỉ lo data access
- **D:** Depend on abstraction (interface), không phải concrete

### Giải quyết vấn đề gì trong code cũ

❌ **Vấn đề cũ:**
```python
# Trong do_everything() - SQL scattered everywhere
db.execute("SELECT * FROM users WHERE email = ?", (email,))
db.execute("INSERT INTO users VALUES (...)")
db.execute("UPDATE products SET stock = stock - ?")
```

**Hậu quả:**
- Business logic lẫn lộn với SQL
- Không thể test mà không có database
- Thay đổi database schema phá vỡ nhiều nơi
- Duplicate SQL queries

✅ **Giải pháp với Repository:**
```python
# Interface (domain/interfaces/user_repository.py)
class IUserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None:
        pass
    
    @abstractmethod
    def find_by_email(self, email: Email) -> Optional[User]:
        pass
    
    @abstractmethod
    def exists_by_email(self, email: Email) -> bool:
        pass

# Implementation (infrastructure/persistence/repositories/sqlite_user_repository.py)
class SqliteUserRepository(IUserRepository):
    def __init__(self, database: Database):
        self._db = database
    
    def save(self, user: User) -> None:
        self._db.execute(
            "INSERT INTO users (id, name, email, password, role, balance) VALUES (?, ?, ?, ?, ?, ?)",
            (user.id, user.name, user.email.value, user.password.hash, user.role.value, user.balance.amount)
        )
    
    def find_by_email(self, email: Email) -> Optional[User]:
        row = self._db.execute(
            "SELECT * FROM users WHERE email = ?", 
            (email.value,)
        ).fetchone()
        if row:
            return self._map_to_entity(row)
        return None

# Usage in Service (application/services/user_service.py)
class UserService:
    def __init__(self, user_repository: IUserRepository):
        self._user_repository = user_repository
    
    def register_user(self, dto: RegisterUserDto) -> UserProfileDto:
        email = Email(dto.email)
        
        if self._user_repository.exists_by_email(email):
            raise EmailAlreadyExistsException()
        
        user = User.register(dto.name, email, dto.password)
        self._user_repository.save(user)
        return self._map_to_dto(user)
```

**Lợi ích:**
- ✅ Business logic clean, không có SQL
- ✅ Test service với mock repository
- ✅ Thay đổi database không affect service
- ✅ Reuse queries, không duplicate

### Testing với Repository Pattern

```python
# tests/unit/application/services/test_user_service.py
class TestUserService:
    def test_register_user_success(self):
        # Arrange
        mock_repo = Mock(IUserRepository)
        mock_repo.exists_by_email.return_value = False
        service = UserService(mock_repo)
        dto = RegisterUserDto("John", "john@test.com", "password123")
        
        # Act
        result = service.register_user(dto)
        
        # Assert
        assert result.name == "John"
        mock_repo.save.assert_called_once()
```

---

## 2. SERVICE LAYER PATTERN

### Áp dụng ở đâu

**Application Layer:**
```
application/services/
├── user_service.py             # User use cases
├── product_service.py          # Product use cases
├── order_service.py            # Order use cases
├── payment_service.py          # Payment use cases
└── notification_service.py     # Notification use cases
```

**Domain Layer (Domain Services):**
```
domain/services/
├── order_calculator.py         # Tax, discount calculation
├── stock_manager.py            # Stock reservation logic
└── analytics_calculator.py     # Metrics calculation
```

### Vì sao phù hợp

✅ **Use Case Encapsulation:**
- Mỗi service method = 1 use case
- Clear entry points cho business operations
- Transaction boundaries rõ ràng

✅ **Orchestration:**
- Coordinate multiple domain objects
- Manage repositories, events, external services
- Handle cross-cutting concerns (logging, transactions)

✅ **Separation:**
- Application services: workflow orchestration
- Domain services: pure business logic calculations
- Clear responsibility division

✅ **Testability:**
- Test use cases end-to-end
- Mock dependencies easily
- Integration tests straightforward

### Giải quyết vấn đề gì trong code cũ

❌ **Vấn đề cũ:**
```python
# God method - do_everything()
def do_everything(self, action, data=None):
    if action == "register":
        # 30 lines of logic
        # Validation
        # Database access
        # Email sending
        # Logging
    elif action == "login":
        # 20 lines
    elif action == "create_order":
        # 80 lines
        # Stock validation
        # Coupon application
        # Tax calculation
        # Payment processing
        # Email notification
```

**Hậu quả:**
- 300+ lines trong 1 method
- Không thể test riêng từng use case
- Khó maintain và debug
- Violation of Single Responsibility

✅ **Giải pháp với Service Layer:**

**Application Service (Workflow Orchestration):**
```python
# application/services/order_service.py
class OrderService:
    def __init__(
        self,
        order_repository: IOrderRepository,
        product_repository: IProductRepository,
        coupon_repository: ICouponRepository,
        stock_manager: StockManager,
        order_calculator: OrderCalculator,
        event_bus: IEventBus,
        unit_of_work: IUnitOfWork,
        logger: ILogger
    ):
        self._order_repository = order_repository
        self._product_repository = product_repository
        self._coupon_repository = coupon_repository
        self._stock_manager = stock_manager
        self._order_calculator = order_calculator
        self._event_bus = event_bus
        self._unit_of_work = unit_of_work
        self._logger = logger
    
    def create_order(self, dto: CreateOrderDto, user_id: UserId) -> OrderDto:
        """
        Use case: Create new order
        
        Steps:
        1. Validate products availability
        2. Reserve stock
        3. Apply coupon if provided
        4. Calculate totals (tax, discount)
        5. Create order entity
        6. Save to database
        7. Publish event
        8. Return order summary
        """
        try:
            self._unit_of_work.begin()
            
            # 1. Validate & fetch products
            products = self._validate_and_fetch_products(dto.items)
            
            # 2. Reserve stock (Domain Service)
            self._stock_manager.reserve_stock(products, dto.items)
            
            # 3. Create order entity (Domain)
            order = Order.create(user_id, dto.shipping_address)
            
            # 4. Add items to order
            for item_dto, product in zip(dto.items, products):
                order.add_item(product, item_dto.quantity)
            
            # 5. Apply coupon if provided
            if dto.coupon_code:
                coupon = self._coupon_repository.find_by_code(dto.coupon_code)
                if coupon and coupon.is_valid():
                    discount = coupon.calculate_discount(order.subtotal)
                    order.apply_discount(discount, dto.coupon_code)
                    coupon.use()
                    self._coupon_repository.update(coupon)
            
            # 6. Calculate tax (Domain Service)
            tax = self._order_calculator.calculate_tax(order.subtotal, order.discount)
            order.apply_tax(tax)
            
            # 7. Save order
            self._order_repository.save(order)
            
            # 8. Commit transaction
            self._unit_of_work.commit()
            
            # 9. Publish event (async side effects)
            self._event_bus.publish(OrderCreated(order.id, user_id, order.total))
            
            # 10. Log
            self._logger.info(f"Order created: {order.id}", {"user_id": user_id, "total": order.total})
            
            # 11. Return DTO
            return self._map_to_dto(order)
            
        except Exception as e:
            self._unit_of_work.rollback()
            self._logger.error(f"Failed to create order", e, {"user_id": user_id})
            raise
    
    def _validate_and_fetch_products(self, items: List[OrderItemDto]) -> List[Product]:
        products = []
        for item in items:
            product = self._product_repository.find_by_id(item.product_id)
            if not product:
                raise ProductNotFoundException(item.product_id)
            if not product.is_available(item.quantity):
                raise InsufficientStockException(product.name, product.stock)
            products.append(product)
        return products
```

**Domain Service (Pure Business Logic):**
```python
# domain/services/order_calculator.py
class OrderCalculator:
    """Pure business logic - no dependencies"""
    
    def __init__(self, tax_rate: Decimal = Decimal("0.1")):
        self._tax_rate = tax_rate
    
    def calculate_tax(self, subtotal: Money, discount: Money) -> Money:
        """Calculate tax on discounted amount"""
        taxable_amount = subtotal.subtract(discount)
        tax_amount = taxable_amount.multiply(self._tax_rate)
        return Money(tax_amount.amount)
    
    def calculate_total(self, subtotal: Money, discount: Money, tax: Money) -> Money:
        """Calculate final total"""
        return subtotal.subtract(discount).add(tax)
```

**Lợi ích:**
- ✅ Mỗi method < 30 lines, clear purpose
- ✅ Easy test từng use case
- ✅ Transaction boundaries explicit
- ✅ Logging, error handling centralized
- ✅ Domain services reusable

---

## 3. STRATEGY PATTERN

### Áp dụng ở đâu

#### 3A. Payment Strategy

**Interfaces:**
```
infrastructure/external/payment/
├── payment_processor.py        # IPaymentProcessor interface
├── balance_payment_processor.py    # Strategy 1
├── credit_card_processor.py        # Strategy 2
├── paypal_processor.py             # Strategy 3
└── mock_payment_processor.py       # Strategy 4 (testing)
```

**Usage:**
```
application/services/payment_service.py
```

#### 3B. Discount Strategy

**Interfaces:**
```
domain/services/discount/
├── discount_strategy.py        # IDiscountStrategy interface
├── percentage_discount.py      # Strategy 1
├── fixed_amount_discount.py    # Strategy 2
└── free_shipping_discount.py   # Strategy 3
```

#### 3C. Notification Strategy

**Interfaces:**
```
infrastructure/external/notification/
├── notification_sender.py      # INotificationSender interface
├── email_sender.py             # Strategy 1
├── sms_sender.py               # Strategy 2
└── push_notification_sender.py # Strategy 3
```

### Vì sao phù hợp

✅ **Algorithm Encapsulation:**
- Mỗi strategy = 1 algorithm/behavior
- Dễ add strategy mới mà không modify existing code

✅ **Runtime Selection:**
- Chọn strategy based on context (user role, payment method, etc.)
- Flexibility cao

✅ **Open/Closed Principle:**
- Open for extension (new strategies)
- Closed for modification (existing code)

✅ **Testability:**
- Test mỗi strategy isolated
- Mock strategies dễ dàng

### Giải quyết vấn đề gì trong code cũ

❌ **Vấn đề cũ - Payment Processing:**
```python
# Trong create_order()
if current_user["role"] == "vip":
    if current_user["balance"] >= final_total:
        db.execute("UPDATE users SET balance = balance - ? WHERE id = ?", ...)
        payment_status = "paid_with_balance"
    else:
        payment_status = "pending_payment"
else:
    payment_status = "pending_payment"
    # TODO: Credit card processing?
    # TODO: PayPal integration?
```

**Hậu quả:**
- Payment logic hardcoded trong order creation
- Thêm payment method phải modify existing code
- Không thể test payment logic riêng
- Violation of Open/Closed Principle

✅ **Giải pháp với Strategy Pattern:**

**1. Payment Strategy Interface:**
```python
# infrastructure/external/payment/payment_processor.py
class IPaymentProcessor(ABC):
    @abstractmethod
    def process(self, amount: Money, order_id: OrderId) -> PaymentResult:
        """Process payment and return result"""
        pass
    
    @abstractmethod
    def can_process(self, payment_method: PaymentMethod, user: User) -> bool:
        """Check if this processor can handle the payment"""
        pass

class PaymentResult:
    def __init__(self, success: bool, transaction_id: Optional[str], message: str):
        self.success = success
        self.transaction_id = transaction_id
        self.message = message
```

**2. Concrete Strategies:**
```python
# infrastructure/external/payment/balance_payment_processor.py
class BalancePaymentProcessor(IPaymentProcessor):
    def __init__(self, user_repository: IUserRepository):
        self._user_repository = user_repository
    
    def can_process(self, payment_method: PaymentMethod, user: User) -> bool:
        return payment_method == PaymentMethod.BALANCE and user.is_vip()
    
    def process(self, amount: Money, order_id: OrderId) -> PaymentResult:
        user = self._user_repository.find_by_id(order_id.user_id)
        
        if not user.has_sufficient_balance(amount):
            return PaymentResult(False, None, "Insufficient balance")
        
        user.deduct_balance(amount)
        self._user_repository.update(user)
        
        return PaymentResult(True, f"BAL-{order_id.value}", "Paid with balance")


# infrastructure/external/payment/credit_card_processor.py
class CreditCardProcessor(IPaymentProcessor):
    def __init__(self, gateway: CreditCardGateway):
        self._gateway = gateway
    
    def can_process(self, payment_method: PaymentMethod, user: User) -> bool:
        return payment_method == PaymentMethod.CREDIT_CARD
    
    def process(self, amount: Money, order_id: OrderId) -> PaymentResult:
        # Call external payment gateway
        result = self._gateway.charge(amount, card_details)
        
        if result.success:
            return PaymentResult(True, result.transaction_id, "Payment successful")
        else:
            return PaymentResult(False, None, result.error_message)


# infrastructure/external/payment/paypal_processor.py
class PayPalProcessor(IPaymentProcessor):
    def __init__(self, paypal_client: PayPalClient):
        self._paypal_client = paypal_client
    
    def can_process(self, payment_method: PaymentMethod, user: User) -> bool:
        return payment_method == PaymentMethod.PAYPAL
    
    def process(self, amount: Money, order_id: OrderId) -> PaymentResult:
        # PayPal API integration
        result = self._paypal_client.create_payment(amount)
        return PaymentResult(True, result.payment_id, "PayPal payment initiated")
```

**3. Context (Payment Service):**
```python
# application/services/payment_service.py
class PaymentService:
    def __init__(self, payment_processors: List[IPaymentProcessor]):
        self._payment_processors = payment_processors
    
    def process_payment(self, dto: ProcessPaymentDto, user: User) -> PaymentDto:
        # Select appropriate strategy
        processor = self._select_processor(dto.payment_method, user)
        
        if not processor:
            raise UnsupportedPaymentMethodException(dto.payment_method)
        
        # Execute strategy
        result = processor.process(dto.amount, dto.order_id)
        
        # Create payment record
        payment = Payment.create(
            dto.order_id,
            dto.amount,
            dto.payment_method,
            result.transaction_id,
            PaymentStatus.COMPLETED if result.success else PaymentStatus.FAILED
        )
        
        self._payment_repository.save(payment)
        
        return self._map_to_dto(payment)
    
    def _select_processor(
        self, 
        payment_method: PaymentMethod, 
        user: User
    ) -> Optional[IPaymentProcessor]:
        for processor in self._payment_processors:
            if processor.can_process(payment_method, user):
                return processor
        return None
```

**4. Configuration (DI Container):**
```python
# Setup payment processors
payment_processors = [
    BalancePaymentProcessor(user_repository),
    CreditCardProcessor(credit_card_gateway),
    PayPalProcessor(paypal_client)
]

payment_service = PaymentService(payment_processors)
```

**Lợi ích:**
- ✅ Thêm payment method mới: chỉ tạo class mới, không modify existing
- ✅ Test mỗi processor isolated
- ✅ Runtime selection based on context
- ✅ Clear separation of algorithms

---

❌ **Vấn đề cũ - Discount Calculation:**
```python
# Hardcoded discount logic
if data.get("coupon_code"):
    coupon = db.execute("SELECT * FROM coupons WHERE code = ?", ...)
    if coupon:
        discount_amount = total * (coupon[1] / 100)  # Always percentage?
```

**Hậu quả:**
- Chỉ support percentage discount
- Fixed amount, buy-one-get-one không implement được
- Logic hardcoded

✅ **Giải pháp với Discount Strategy:**

```python
# domain/services/discount/discount_strategy.py
class IDiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, order: Order) -> Money:
        pass

class PercentageDiscount(IDiscountStrategy):
    def __init__(self, percentage: Decimal):
        self._percentage = percentage
    
    def calculate(self, order: Order) -> Money:
        discount_amount = order.subtotal.multiply(self._percentage / 100)
        return Money(discount_amount.amount)

class FixedAmountDiscount(IDiscountStrategy):
    def __init__(self, amount: Money):
        self._amount = amount
    
    def calculate(self, order: Order) -> Money:
        # Don't exceed subtotal
        if self._amount.is_greater_than(order.subtotal):
            return order.subtotal
        return self._amount

class FreeShippingDiscount(IDiscountStrategy):
    def calculate(self, order: Order) -> Money:
        # Free shipping = return shipping cost as discount
        return order.shipping_cost

# Usage in Coupon entity
class Coupon:
    def __init__(self, code: str, strategy: IDiscountStrategy, max_uses: int):
        self.code = code
        self._strategy = strategy
        self.max_uses = max_uses
    
    def calculate_discount(self, order: Order) -> Money:
        return self._strategy.calculate(order)
```

---

❌ **Vấn đề cũ - Notification:**
```python
# Email only, hardcoded
try:
    msg = f"Welcome {data['name']}!"
    print(f"EMAIL SENT to {data['email']}: {msg}")
except:
    pass
```

✅ **Giải pháp với Notification Strategy:**

```python
# infrastructure/external/notification/notification_sender.py
class INotificationSender(ABC):
    @abstractmethod
    def send(self, recipient: str, message: str) -> bool:
        pass

class EmailSender(INotificationSender):
    def __init__(self, smtp_config: SMTPConfig):
        self._smtp = smtp_config
    
    def send(self, recipient: str, message: str) -> bool:
        # SMTP implementation
        pass

class SmsSender(INotificationSender):
    def __init__(self, sms_gateway: SmsGateway):
        self._gateway = sms_gateway
    
    def send(self, recipient: str, message: str) -> bool:
        # SMS gateway implementation
        pass

# Multi-channel notification
class NotificationService:
    def __init__(self, senders: List[INotificationSender]):
        self._senders = senders
    
    def send_welcome(self, user: User):
        message = f"Welcome {user.name}!"
        for sender in self._senders:  # Send via all channels
            sender.send(user.email.value, message)
```

---

## 4. DEPENDENCY INJECTION PATTERN

### Áp dụng ở đâu

**Toàn bộ hệ thống:**
- Application Services inject repositories
- Repositories inject database connection
- Services inject external services
- Controllers inject services

**DI Container:**
```
infrastructure/di/
├── container.py            # Service container
├── service_provider.py     # Service registration
└── config.py              # Configuration management
```

### Vì sao phù hợp

✅ **Loose Coupling:**
- Components không tạo dependencies trực tiếp
- Depend on abstractions (interfaces)

✅ **Testability:**
- Inject mocks trong tests
- No global state
- Isolated unit tests

✅ **Flexibility:**
- Swap implementations dễ dàng
- Configure for different environments

✅ **SOLID:**
- Dependency Inversion Principle
- Open/Closed Principle

### Giải quyết vấn đề gì trong code cũ

❌ **Vấn đề cũ:**
```python
# Global variables - tight coupling
db = None
email_server = None
current_user = None
order_counter = 1000

class EcommerceSystem:
    def __init__(self):
        global db, email_server  # Modify global state
        db = sqlite3.connect(":memory:")
        email_server = {"host": "smtp.fake.com"}
    
    def do_everything(self, action, data):
        global current_user  # Access global state
        # Use db directly - tight coupling
        db.execute("SELECT ...")
```

**Hậu quả:**
- ❌ Global state = không thể test parallel
- ❌ Không thể inject mock database
- ❌ Singleton pattern implicit (bad)
- ❌ Tight coupling với SQLite
- ❌ Không thể run multiple instances

✅ **Giải pháp với Dependency Injection:**

**1. Constructor Injection:**
```python
# application/services/user_service.py
class UserService:
    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher: IPasswordHasher,
        event_bus: IEventBus,
        logger: ILogger
    ):
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._event_bus = event_bus
        self._logger = logger
    
    def register_user(self, dto: RegisterUserDto) -> UserProfileDto:
        # Use injected dependencies
        email = Email(dto.email)
        
        if self._user_repository.exists_by_email(email):
            raise EmailAlreadyExistsException()
        
        password = Password.create(dto.password, self._password_hasher)
        user = User.register(dto.name, email, password)
        
        self._user_repository.save(user)
        self._event_bus.publish(UserRegistered(user.id))
        self._logger.info(f"User registered: {user.email.value}")
        
        return self._map_to_dto(user)
```

**2. DI Container:**
```python
# infrastructure/di/container.py
class Container:
    def __init__(self):
        self._services = {}
    
    def register(self, interface, implementation, singleton=False):
        self._services[interface] = {
            'implementation': implementation,
            'singleton': singleton,
            'instance': None
        }
    
    def resolve(self, interface):
        if interface not in self._services:
            raise DependencyNotRegisteredException(interface)
        
        service = self._services[interface]
        
        if service['singleton']:
            if service['instance'] is None:
                service['instance'] = service['implementation']()
            return service['instance']
        else:
            return service['implementation']()
```

**3. Service Registration:**
```python
# main.py or setup.py
def configure_container(config: Config) -> Container:
    container = Container()
    
    # Infrastructure - Singletons
    container.register_singleton(
        IDatabase, 
        lambda: SQLiteDatabase(config.database_url)
    )
    container.register_singleton(
        IEventBus,
        lambda: InMemoryEventBus()
    )
    container.register_singleton(
        ILogger,
        lambda: FileLogger(config.log_path)
    )
    
    # Infrastructure - Transient
    container.register(
        IPasswordHasher,
        lambda: BcryptPasswordHasher()
    )
    
    # Repositories - Scoped (per request)
    container.register_scoped(
        IUserRepository,
        lambda: SqliteUserRepository(container.resolve(IDatabase))
    )
    container.register_scoped(
        IProductRepository,
        lambda: SqliteProductRepository(container.resolve(IDatabase))
    )
    container.register_scoped(
        IOrderRepository,
        lambda: SqliteOrderRepository(container.resolve(IDatabase))
    )
    
    # Application Services - Transient
    container.register(
        UserService,
        lambda: UserService(
            user_repository=container.resolve(IUserRepository),
            password_hasher=container.resolve(IPasswordHasher),
            event_bus=container.resolve(IEventBus),
            logger=container.resolve(ILogger)
        )
    )
    container.register(
        OrderService,
        lambda: OrderService(
            order_repository=container.resolve(IOrderRepository),
            product_repository=container.resolve(IProductRepository),
            coupon_repository=container.resolve(ICouponRepository),
            stock_manager=StockManager(),
            order_calculator=OrderCalculator(),
            event_bus=container.resolve(IEventBus),
            unit_of_work=container.resolve(IUnitOfWork),
            logger=container.resolve(ILogger)
        )
    )
    
    # Payment Processors - Strategy Pattern + DI
    container.register(
        IPaymentProcessor,
        lambda: [
            BalancePaymentProcessor(container.resolve(IUserRepository)),
            CreditCardProcessor(container.resolve(ICreditCardGateway)),
            PayPalProcessor(container.resolve(IPayPalClient))
        ]
    )
    
    return container
```

**4. Usage:**
```python
# Application startup
config = load_config()
container = configure_container(config)

# Resolve services
user_service = container.resolve(UserService)
order_service = container.resolve(OrderService)

# Use services
result = user_service.register_user(dto)
```

**5. Testing với DI:**
```python
# tests/unit/application/services/test_user_service.py
class TestUserService:
    def setup_method(self):
        # Inject mocks
        self.mock_user_repo = Mock(IUserRepository)
        self.mock_password_hasher = Mock(IPasswordHasher)
        self.mock_event_bus = Mock(IEventBus)
        self.mock_logger = Mock(ILogger)
        
        # Create service with mocks
        self.service = UserService(
            self.mock_user_repo,
            self.mock_password_hasher,
            self.mock_event_bus,
            self.mock_logger
        )
    
    def test_register_user_success(self):
        # Arrange
        self.mock_user_repo.exists_by_email.return_value = False
        dto = RegisterUserDto("John", "john@test.com", "password123")
        
        # Act
        result = self.service.register_user(dto)
        
        # Assert
        assert result.name == "John"
        self.mock_user_repo.save.assert_called_once()
        self.mock_event_bus.publish.assert_called_once()
```

**Lợi ích:**
- ✅ No global state
- ✅ Easy mock dependencies
- ✅ Testable in isolation
- ✅ Swap implementations (dev, test, prod)
- ✅ Lifecycle management (singleton, transient, scoped)

---

## 5. FACTORY PATTERN

### Áp dụng ở đâu

**Domain Layer:**
```
domain/factories/
├── user_factory.py         # Create User entities
├── order_factory.py        # Create Order aggregates
└── payment_factory.py      # Create Payment entities
```

**Testing:**
```
tests/fixtures/
└── factories.py            # Test data factories
```

### Vì sao phù hợp

✅ **Complex Object Creation:**
- Encapsulate creation logic
- Multiple construction steps
- Validation during creation

✅ **Testability:**
- Centralized test data creation
- Consistent test objects
- DRY in tests

✅ **Domain Logic:**
- Business rules enforced at creation
- Named constructors for clarity

### Giải quyết vấn đề gì

❌ **Vấn đề cũ:**
```python
# Scattered creation logic
user = {
    "id": user[0],
    "name": user[1],
    "email": user[2],
    "role": user[4],
    "balance": user[5]
}
```

✅ **Giải pháp:**

```python
# domain/models/user/user.py
class User:
    @staticmethod
    def register(name: str, email: Email, password: str) -> 'User':
        """Factory method for new user registration"""
        hashed_password = Password.create(password)
        return User(
            id=UserId.generate(),
            name=name,
            email=email,
            password=hashed_password,
            role=UserRole.CUSTOMER,
            balance=Money.zero(),
            created_at=datetime.now()
        )
    
    @staticmethod
    def create_admin(name: str, email: Email, password: str) -> 'User':
        """Factory method for admin creation"""
        user = User.register(name, email, password)
        user.role = UserRole.ADMIN
        return user

# tests/fixtures/factories.py
class UserFactory:
    @staticmethod
    def create_customer(
        name: str = "Test User",
        email: str = "test@example.com"
    ) -> User:
        return User.register(name, Email(email), "password123")
    
    @staticmethod
    def create_vip_with_balance(balance: Decimal = Decimal("1000")) -> User:
        user = UserFactory.create_customer()
        user.role = UserRole.VIP
        user.balance = Money(balance)
        return user
```

---

## 6. UNIT OF WORK PATTERN

### Áp dụng ở đâu

**Domain Interface:**
```
domain/interfaces/unit_of_work.py
```

**Infrastructure Implementation:**
```
infrastructure/persistence/unit_of_work.py
```

### Vì sao phù hợp

✅ **Transaction Management:**
- Atomic operations
- Rollback on failure
- Consistent state

✅ **Clean Business Logic:**
- Transaction boundaries explicit
- No database transaction code trong domain

### Giải quyết vấn đề gì

❌ **Vấn đề cũ:**
```python
# No transaction management
db.execute("UPDATE products SET stock = stock - ?", ...)
db.execute("INSERT INTO orders VALUES (...)")
db.commit()  # What if error between these?
```

✅ **Giải pháp:**

```python
# domain/interfaces/unit_of_work.py
class IUnitOfWork(ABC):
    @abstractmethod
    def begin(self):
        pass
    
    @abstractmethod
    def commit(self):
        pass
    
    @abstractmethod
    def rollback(self):
        pass

# infrastructure/persistence/unit_of_work.py
class SqliteUnitOfWork(IUnitOfWork):
    def __init__(self, connection):
        self._connection = connection
        self._transaction = None
    
    def begin(self):
        self._transaction = self._connection.begin()
    
    def commit(self):
        if self._transaction:
            self._transaction.commit()
    
    def rollback(self):
        if self._transaction:
            self._transaction.rollback()

# Usage in Service
class OrderService:
    def create_order(self, dto: CreateOrderDto) -> OrderDto:
        try:
            self._unit_of_work.begin()
            
            # Multiple operations
            self._stock_manager.reserve_stock(...)
            self._order_repository.save(order)
            self._coupon_repository.update(coupon)
            
            self._unit_of_work.commit()
            
        except Exception:
            self._unit_of_work.rollback()
            raise
```

---

## 7. OBSERVER PATTERN (Event-Driven)

### Áp dụng ở đâu

**Domain Events:**
```
domain/events/
```

**Event Bus:**
```
infrastructure/event_bus/
```

**Event Handlers:**
```
application/handlers/
```

### Vì sao phù hợp

✅ **Loose Coupling:**
- Publishers không biết subscribers
- Add handlers mà không modify domain

✅ **Async Side Effects:**
- Email sending
- Notifications
- Analytics updates

✅ **Separation of Concerns:**
- Domain focus on core logic
- Side effects handled separately

### Giải quyết vấn đề gì

❌ **Vấn đề cũ:**
```python
# Email sending trong business logic
db.execute("INSERT INTO users ...")
db.commit()
try:
    # Side effect mixed with core logic
    msg = f"Welcome {data['name']}!"
    print(f"EMAIL SENT to {data['email']}: {msg}")
except:
    pass  # Silent failure
```

✅ **Giải pháp:**

```python
# domain/events/user_events.py
@dataclass
class UserRegistered:
    user_id: UserId
    email: Email
    name: str
    timestamp: datetime

# application/handlers/user_event_handlers.py
class WelcomeEmailHandler:
    def __init__(self, email_sender: IEmailSender):
        self._email_sender = email_sender
    
    def handle(self, event: UserRegistered):
        message = f"Welcome {event.name}!"
        self._email_sender.send(event.email.value, message)

# application/services/user_service.py
class UserService:
    def register_user(self, dto: RegisterUserDto):
        user = User.register(dto.name, Email(dto.email), dto.password)
        self._user_repository.save(user)
        
        # Publish event - async handling
        self._event_bus.publish(
            UserRegistered(user.id, user.email, user.name, datetime.now())
        )

# Setup (DI Container)
event_bus.subscribe(UserRegistered, welcome_email_handler.handle)
```

---

## 8. BUILDER PATTERN

### Áp dụng ở đâu

**Testing:**
```
tests/fixtures/builders.py
```

**Complex DTOs:**
```
application/dtos/builders/
```

### Vì sao phù hợp

✅ **Test Data Construction:**
- Fluent interface
- Default values
- Partial construction

✅ **Complex Objects:**
- Step-by-step construction
- Validation at build time

### Giải pháp

```python
# tests/fixtures/builders.py
class OrderBuilder:
    def __init__(self):
        self._items = []
        self._shipping_address = "123 Main St"
        self._coupon_code = None
    
    def with_item(self, product_id: int, quantity: int):
        self._items.append({"product_id": product_id, "quantity": quantity})
        return self
    
    def with_coupon(self, code: str):
        self._coupon_code = code
        return self
    
    def build(self) -> CreateOrderDto:
        return CreateOrderDto(
            items=self._items,
            shipping_address=self._shipping_address,
            coupon_code=self._coupon_code
        )

# Usage in tests
order_dto = (OrderBuilder()
    .with_item(product_id=1, quantity=2)
    .with_item(product_id=2, quantity=1)
    .with_coupon("SAVE10")
    .build())
```

---

## TỔNG KẾT PATTERNS

| Pattern | Layer | Vấn đề giải quyết | SOLID |
|---------|-------|-------------------|-------|
| **Repository** | Infrastructure | SQL scattered, không testable | S, D |
| **Service Layer** | Application | God method, multiple responsibilities | S, O |
| **Strategy** | Infrastructure/Domain | Hardcoded algorithms, không extensible | O, D |
| **Dependency Injection** | All layers | Global state, tight coupling | D, O |
| **Factory** | Domain | Complex creation, scattered logic | S |
| **Unit of Work** | Infrastructure | Transaction management | S |
| **Observer (Events)** | All layers | Side effects mixed with logic | S, O |
| **Builder** | Testing | Complex test data creation | S |

---

## INTERACTION GIỮA CÁC PATTERNS

```
┌─────────────────────────────────────────────────────────────────┐
│                        Controller                                │
│                             │                                     │
│                             ▼                                     │
│                   [Dependency Injection]                         │
│                             │                                     │
│                             ▼                                     │
│                   ┌─────────────────┐                           │
│                   │  Service Layer  │ ◄── [Factory]             │
│                   │  (Use Cases)    │                           │
│                   └────────┬────────┘                           │
│                            │                                     │
│               ┌────────────┼────────────┐                       │
│               ▼            ▼            ▼                       │
│         [Repository]  [Strategy]   [Event Bus]                 │
│               │            │            │                       │
│               ▼            ▼            ▼                       │
│            Database    External     Handlers                    │
│                        Services                                 │
│               │                        │                        │
│               └────[Unit of Work]──────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## KẾT LUẬN

### So sánh Code Cũ vs Code Mới

| Aspect | Code Cũ | Code Mới với Patterns |
|--------|----------|----------------------|
| **Testability** | ❌ Không test được isolated | ✅ Mock dependencies, isolated tests |
| **Maintainability** | ❌ 300+ lines/method | ✅ <30 lines/method, clear purpose |
| **Extensibility** | ❌ Modify existing code | ✅ Add new classes (Open/Closed) |
| **Coupling** | ❌ Tight coupling, global state | ✅ Loose coupling, DI |
| **SOLID** | ❌ Violate all principles | ✅ Follow all principles |
| **Scalability** | ❌ Single instance only | ✅ Stateless, parallel execution |

### Patterns là Foundation

Design patterns không phải "nice to have" - chúng là **foundation** để:
- ✅ Transform spaghetti code thành clean architecture
- ✅ Enable testing (unit, integration, E2E)
- ✅ Support maintenance và evolution
- ✅ Enforce SOLID principles
- ✅ Scale system (technical và team)

Áp dụng patterns một cách có chọn lọc, phù hợp với context - **không over-engineer**, nhưng cũng không under-engineer.
