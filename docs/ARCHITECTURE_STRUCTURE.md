# KIẾN TRÚC VÀ CẤU TRÚC THƯ MỤC PYTHON

## TỔNG QUAN KIẾN TRÚC

### Clean Architecture với Domain-Driven Design (DDD)

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│                    (API / Controllers)                       │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    Application Layer                         │
│           (Services / Use Cases / DTOs)                      │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                      Domain Layer                            │
│        (Models / Entities / Value Objects / Events)          │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                  Infrastructure Layer                        │
│      (Repositories / External Services / Database)           │
└─────────────────────────────────────────────────────────────┘
```

**Dependency Rule:** 
- Inner layers không biết outer layers
- Outer layers depend vào inner layers
- Domain layer là center, không dependency nào cả

---

## CẤU TRÚC THƯ MỤC CHI TIẾT

```
ecommerce/
│
├── domain/                         # Domain Layer - Core Business Logic
│   ├── __init__.py
│   │
│   ├── models/                     # Domain Models (Entities & Value Objects)
│   │   ├── __init__.py
│   │   ├── user/
│   │   │   ├── __init__.py
│   │   │   ├── user.py             # User Entity
│   │   │   ├── email.py            # Email Value Object
│   │   │   ├── password.py         # Password Value Object
│   │   │   └── user_role.py        # UserRole Enum
│   │   │
│   │   ├── product/
│   │   │   ├── __init__.py
│   │   │   ├── product.py          # Product Entity
│   │   │   ├── price.py            # Price Value Object
│   │   │   └── stock.py            # Stock Value Object
│   │   │
│   │   ├── order/
│   │   │   ├── __init__.py
│   │   │   ├── order.py            # Order Aggregate Root
│   │   │   ├── order_item.py       # OrderItem Entity
│   │   │   ├── order_status.py     # OrderStatus Enum
│   │   │   └── shipping_address.py # ShippingAddress Value Object
│   │   │
│   │   ├── payment/
│   │   │   ├── __init__.py
│   │   │   ├── payment.py          # Payment Entity
│   │   │   ├── payment_method.py   # PaymentMethod Enum
│   │   │   └── payment_status.py   # PaymentStatus Enum
│   │   │
│   │   ├── coupon/
│   │   │   ├── __init__.py
│   │   │   └── coupon.py           # Coupon Entity
│   │   │
│   │   ├── review/
│   │   │   ├── __init__.py
│   │   │   ├── review.py           # Review Entity
│   │   │   └── rating.py           # Rating Value Object
│   │   │
│   │   ├── notification/
│   │   │   ├── __init__.py
│   │   │   └── notification.py     # Notification Entity
│   │   │
│   │   └── shared/                 # Shared Value Objects
│   │       ├── __init__.py
│   │       ├── money.py            # Money Value Object
│   │       ├── entity_id.py        # Base Entity ID
│   │       └── date_range.py       # DateRange Value Object
│   │
│   ├── events/                     # Domain Events
│   │   ├── __init__.py
│   │   ├── base.py                 # Base Domain Event
│   │   ├── user_events.py          # UserRegistered, UserAuthenticated, etc.
│   │   ├── product_events.py       # ProductCreated, StockReserved, etc.
│   │   ├── order_events.py         # OrderCreated, OrderPaid, etc.
│   │   ├── payment_events.py       # PaymentCompleted, PaymentFailed, etc.
│   │   └── notification_events.py  # NotificationSent, etc.
│   │
│   ├── services/                   # Domain Services (Pure Business Logic)
│   │   ├── __init__.py
│   │   ├── order_calculator.py     # Tax, discount calculations
│   │   ├── stock_manager.py        # Stock reservation logic
│   │   └── analytics_calculator.py # Metrics calculations
│   │
│   ├── exceptions/                 # Domain Exceptions
│   │   ├── __init__.py
│   │   ├── base.py                 # Base Domain Exception
│   │   ├── user_exceptions.py      # InvalidEmailException, etc.
│   │   ├── product_exceptions.py   # InsufficientStockException, etc.
│   │   ├── order_exceptions.py     # InvalidOrderStateException, etc.
│   │   └── payment_exceptions.py   # PaymentFailedException, etc.
│   │
│   └── interfaces/                 # Repository Interfaces (Ports)
│       ├── __init__.py
│       ├── user_repository.py      # IUserRepository
│       ├── product_repository.py   # IProductRepository
│       ├── order_repository.py     # IOrderRepository
│       ├── payment_repository.py   # IPaymentRepository
│       ├── coupon_repository.py    # ICouponRepository
│       ├── review_repository.py    # IReviewRepository
│       └── unit_of_work.py         # IUnitOfWork
│
├── application/                    # Application Layer - Use Cases
│   ├── __init__.py
│   │
│   ├── dtos/                       # Data Transfer Objects
│   │   ├── __init__.py
│   │   ├── user_dtos.py            # RegisterUserDto, LoginDto, UserProfileDto
│   │   ├── product_dtos.py         # CreateProductDto, ProductDto
│   │   ├── order_dtos.py           # CreateOrderDto, OrderDto
│   │   ├── payment_dtos.py         # ProcessPaymentDto, PaymentDto
│   │   ├── coupon_dtos.py          # CouponDto, ApplyCouponDto
│   │   └── review_dtos.py          # CreateReviewDto, ReviewDto
│   │
│   ├── services/                   # Application Services (Use Cases)
│   │   ├── __init__.py
│   │   ├── user_service.py         # User use cases
│   │   ├── product_service.py      # Product use cases
│   │   ├── order_service.py        # Order use cases
│   │   ├── payment_service.py      # Payment use cases
│   │   ├── coupon_service.py       # Coupon use cases
│   │   ├── review_service.py       # Review use cases
│   │   ├── notification_service.py # Notification use cases
│   │   └── analytics_service.py    # Analytics/Reporting use cases
│   │
│   ├── validators/                 # Application-level Validation
│   │   ├── __init__.py
│   │   ├── user_validator.py       # Validate RegisterUserDto, etc.
│   │   ├── product_validator.py    # Validate CreateProductDto, etc.
│   │   ├── order_validator.py      # Validate CreateOrderDto, etc.
│   │   └── base_validator.py       # Base validation utilities
│   │
│   ├── handlers/                   # Event Handlers
│   │   ├── __init__.py
│   │   ├── user_event_handlers.py  # Handle UserRegistered → Send welcome email
│   │   ├── order_event_handlers.py # Handle OrderCreated → Send confirmation
│   │   └── payment_event_handlers.py # Handle PaymentCompleted → Update order
│   │
│   └── exceptions/                 # Application Exceptions
│       ├── __init__.py
│       ├── validation_exception.py
│       ├── resource_not_found_exception.py
│       └── unauthorized_exception.py
│
├── infrastructure/                 # Infrastructure Layer - External Concerns
│   ├── __init__.py
│   │
│   ├── persistence/                # Database Implementation
│   │   ├── __init__.py
│   │   ├── database.py             # Database connection management
│   │   ├── unit_of_work.py         # UnitOfWork implementation
│   │   │
│   │   ├── repositories/           # Repository Implementations
│   │   │   ├── __init__.py
│   │   │   ├── sqlite_user_repository.py
│   │   │   ├── sqlite_product_repository.py
│   │   │   ├── sqlite_order_repository.py
│   │   │   ├── sqlite_payment_repository.py
│   │   │   ├── sqlite_coupon_repository.py
│   │   │   └── sqlite_review_repository.py
│   │   │
│   │   └── migrations/             # Database Migrations
│   │       ├── __init__.py
│   │       ├── v001_initial_schema.py
│   │       └── v002_add_notifications.py
│   │
│   ├── external/                   # External Service Integrations
│   │   ├── __init__.py
│   │   ├── email/
│   │   │   ├── __init__.py
│   │   │   ├── email_sender.py     # IEmailSender interface
│   │   │   ├── smtp_email_sender.py # SMTP implementation
│   │   │   └── mock_email_sender.py # Mock for testing
│   │   │
│   │   ├── payment/
│   │   │   ├── __init__.py
│   │   │   ├── payment_processor.py # IPaymentProcessor interface
│   │   │   ├── balance_payment_processor.py
│   │   │   └── mock_payment_processor.py
│   │   │
│   │   └── notification/
│   │       ├── __init__.py
│   │       ├── notification_sender.py # INotificationSender interface
│   │       └── console_notification_sender.py
│   │
│   ├── security/                   # Security Infrastructure
│   │   ├── __init__.py
│   │   ├── password_hasher.py      # IPasswordHasher interface
│   │   ├── bcrypt_hasher.py        # Bcrypt implementation
│   │   ├── jwt_service.py          # JWT token generation/validation
│   │   └── authorization_service.py # RBAC implementation
│   │
│   ├── event_bus/                  # Event Bus Implementation
│   │   ├── __init__.py
│   │   ├── event_bus.py            # IEventBus interface
│   │   ├── in_memory_event_bus.py  # In-memory implementation
│   │   └── message_queue_event_bus.py # Message queue (future)
│   │
│   └── logging/                    # Logging Infrastructure
│       ├── __init__.py
│       ├── logger.py               # ILogger interface
│       ├── console_logger.py       # Console implementation
│       ├── file_logger.py          # File implementation
│       └── null_logger.py          # Null object for testing
│
├── presentation/                   # Presentation Layer (Optional - API/Web)
│   ├── __init__.py
│   ├── api/                        # REST API
│   │   ├── __init__.py
│   │   ├── controllers/
│   │   │   ├── __init__.py
│   │   │   ├── user_controller.py
│   │   │   ├── product_controller.py
│   │   │   ├── order_controller.py
│   │   │   └── admin_controller.py
│   │   │
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── authentication.py
│   │       └── error_handler.py
│   │
│   └── cli/                        # Command-line Interface (Alternative)
│       ├── __init__.py
│       └── commands.py
│
├── shared/                         # Shared Utilities (Cross-cutting)
│   ├── __init__.py
│   ├── utils/                      # General Utilities
│   │   ├── __init__.py
│   │   ├── date_utils.py           # Date/time helpers
│   │   ├── string_utils.py         # String manipulation
│   │   └── validation_utils.py     # Common validation functions
│   │
│   └── constants/                  # Application Constants
│       ├── __init__.py
│       └── config.py               # Configuration constants
│
├── tests/                          # Test Suite
│   ├── __init__.py
│   │
│   ├── unit/                       # Unit Tests
│   │   ├── __init__.py
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── models/
│   │   │   │   ├── test_user.py
│   │   │   │   ├── test_product.py
│   │   │   │   ├── test_order.py
│   │   │   │   └── test_payment.py
│   │   │   │
│   │   │   └── services/
│   │   │       ├── test_order_calculator.py
│   │   │       └── test_stock_manager.py
│   │   │
│   │   └── application/
│   │       ├── __init__.py
│   │       ├── services/
│   │       │   ├── test_user_service.py
│   │       │   ├── test_product_service.py
│   │       │   ├── test_order_service.py
│   │       │   └── test_payment_service.py
│   │       │
│   │       └── validators/
│   │           └── test_user_validator.py
│   │
│   ├── integration/                # Integration Tests
│   │   ├── __init__.py
│   │   ├── repositories/
│   │   │   ├── test_user_repository.py
│   │   │   ├── test_product_repository.py
│   │   │   └── test_order_repository.py
│   │   │
│   │   └── services/
│   │       ├── test_order_workflow.py
│   │       └── test_payment_workflow.py
│   │
│   ├── e2e/                        # End-to-End Tests
│   │   ├── __init__.py
│   │   ├── test_user_registration_flow.py
│   │   ├── test_order_creation_flow.py
│   │   └── test_payment_flow.py
│   │
│   ├── fixtures/                   # Test Fixtures
│   │   ├── __init__.py
│   │   ├── user_fixtures.py        # User test data
│   │   ├── product_fixtures.py     # Product test data
│   │   ├── order_fixtures.py       # Order test data
│   │   └── factories.py            # Factory pattern for test objects
│   │
│   └── mocks/                      # Mock Objects
│       ├── __init__.py
│       ├── mock_repositories.py    # In-memory repository mocks
│       ├── mock_email_sender.py
│       └── mock_payment_processor.py
│
├── config/                         # Configuration Files
│   ├── __init__.py
│   ├── development.py              # Development settings
│   ├── testing.py                  # Testing settings
│   ├── production.py               # Production settings
│   └── settings.py                 # Base settings
│
├── scripts/                        # Utility Scripts
│   ├── seed_database.py            # Seed initial data
│   ├── migrate_database.py         # Run migrations
│   └── run_tests.py                # Test runner
│
├── main.py                         # Application Entry Point
├── requirements.txt                # Python dependencies
├── requirements-dev.txt            # Development dependencies
├── setup.py                        # Package setup
├── pytest.ini                      # Pytest configuration
├── .env.example                    # Environment variables template
└── README.md                       # Project documentation
```

---

## GIẢI THÍCH VAI TRÒ TỪNG LAYER

### 1. **domain/** - Domain Layer (Core)

**Vai trò:** Chứa business logic thuần túy, không biết về infrastructure

**Components:**

#### **models/**
- **Entity:** Object có identity (User, Product, Order)
- **Value Object:** Object không có identity, immutable (Email, Money, Rating)
- **Aggregate:** Cluster của entities với 1 root (Order + OrderItems)
- **Đặc điểm:**
  - Chứa business rules và validations
  - Self-contained, không dependency external
  - Rich domain model với behaviors

#### **events/**
- Domain events phát sinh khi state change
- Immutable objects
- Trigger side effects (email, notifications)
- **Ví dụ:** `UserRegistered`, `OrderCreated`, `PaymentCompleted`

#### **services/**
- Domain services cho logic không thuộc về 1 entity
- Stateless, pure functions
- **Ví dụ:** Calculate tax, calculate discount, reserve stock

#### **interfaces/**
- Repository interfaces (Ports trong Hexagonal Architecture)
- Định nghĩa contracts cho infrastructure
- Domain không biết implementation

#### **exceptions/**
- Business rule violations
- Domain-specific errors
- **Ví dụ:** `InsufficientStockException`, `InvalidEmailException`

**Nguyên tắc:**
- ❌ Không import từ application, infrastructure, presentation
- ❌ Không biết về database, HTTP, email
- ✅ Chỉ chứa pure business logic

---

### 2. **application/** - Application Layer

**Vai trò:** Orchestrate use cases, coordinate domain objects

**Components:**

#### **services/**
- Use case implementations
- Orchestrate domain objects, repositories, events
- Transaction boundaries
- **Ví dụ:** 
  - `UserService.register_user()`: Validate → Create User → Save → Send email
  - `OrderService.create_order()`: Reserve stock → Apply coupon → Calculate → Save → Notify

#### **dtos/**
- Data Transfer Objects
- Input/Output cho services
- Decouple domain từ presentation
- Validation schemas
- **Không chứa business logic**

#### **validators/**
- Application-level validation
- Input validation cho DTOs
- Cross-entity validation
- Authorization checks
- **Khác domain validation:** Focus vào workflow validation

#### **handlers/**
- Event handlers (subscribers)
- React to domain events
- Trigger side effects
- **Ví dụ:** UserRegistered → Send welcome email

#### **exceptions/**
- Application-level errors
- Validation failures
- Resource not found
- Authorization failures

**Nguyên tắc:**
- ✅ Depend on domain (entities, interfaces)
- ❌ Không depend vào infrastructure implementations
- ✅ Define interfaces cho external services
- ✅ Stateless services

---

### 3. **infrastructure/** - Infrastructure Layer

**Vai trò:** Technical implementations, external integrations

**Components:**

#### **persistence/**
- **repositories/**: Implement domain repository interfaces
- **database.py**: Connection management, pooling
- **unit_of_work.py**: Transaction management
- **migrations/**: Database schema changes

**Đặc điểm:**
- Map domain objects ↔ database rows
- Handle SQL, ORM
- Connection lifecycle

#### **external/**
- **email/**: SMTP integration
- **payment/**: Payment gateway integration
- **notification/**: SMS, Push notifications
- Mock implementations cho testing

#### **security/**
- Password hashing (bcrypt)
- JWT token management
- Authorization/RBAC
- Encryption utilities

#### **event_bus/**
- Event publishing/subscription
- In-memory (sync) hoặc message queue (async)
- Event routing

#### **logging/**
- Structured logging
- File, console, remote logging
- Log correlation

**Nguyên tắc:**
- ✅ Implement domain interfaces
- ✅ Depend on domain abstractions
- ❌ Domain KHÔNG depend vào infrastructure
- ✅ Swappable implementations

---

### 4. **presentation/** - Presentation Layer (Optional)

**Vai trò:** User interface - REST API, CLI, Web

**Components:**

#### **api/controllers/**
- HTTP request handlers
- Map HTTP ↔ DTOs
- Call application services
- Return HTTP responses

#### **api/middleware/**
- Authentication (JWT validation)
- Error handling
- CORS, rate limiting
- Request logging

#### **cli/**
- Command-line interface
- Interactive shell
- Admin tools

**Nguyên tắc:**
- ✅ Thin layer, minimal logic
- ✅ Depend on application services
- ❌ Không depend trực tiếp vào domain
- ✅ Handle HTTP-specific concerns

---

### 5. **shared/** - Shared Utilities

**Vai trò:** Cross-cutting utilities, không specific cho layer nào

**Components:**

#### **utils/**
- Date/time utilities
- String formatting
- Common validation functions
- Helper functions

#### **constants/**
- Application constants
- Configuration values
- Enum definitions

**Nguyên tắc:**
- ✅ Pure functions, stateless
- ✅ No business logic
- ✅ Reusable across all layers
- ❌ Minimal, tránh "utils hell"

---

### 6. **tests/** - Test Suite

**Vai trò:** Comprehensive testing cho all layers

**Structure:**

#### **unit/**
- Test isolated units (entities, value objects, services)
- Mock all dependencies
- Fast, deterministic
- **Coverage:** Domain models, application services

#### **integration/**
- Test component interactions
- Real repositories với test database
- Real external services (hoặc test doubles)
- **Coverage:** Repository implementations, workflows

#### **e2e/**
- Test complete user flows
- Real infrastructure components
- **Coverage:** Critical business paths

#### **fixtures/**
- Factory pattern cho test data
- Shared test data builders
- **Ví dụ:** `UserFactory.create()`, `OrderFactory.create_with_items()`

#### **mocks/**
- In-memory repository implementations
- Mock external services
- Reusable test doubles

**Testing Strategy:**
- **Unit tests:** 90%+ coverage cho domain, application
- **Integration tests:** 80%+ coverage cho repositories, workflows
- **E2E tests:** Critical paths only
- **Test pyramid:** Many unit → Some integration → Few E2E

---

## ƯU ĐIỂM KIẾN TRÚC

### Testability

✅ **Dependency Injection:**
- Tất cả dependencies qua constructor
- Easy mock/stub

✅ **Interface-based:**
- Repository interfaces
- Service interfaces
- Swap implementations

✅ **In-memory implementations:**
- Test mà không cần database
- Fast, isolated tests

✅ **No global state:**
- No singletons
- No static variables
- Parallel test execution

### Maintainability

✅ **Clear separation:**
- Business logic isolated trong domain
- Infrastructure swappable
- Easy locate code

✅ **Single Responsibility:**
- Mỗi class có 1 reason to change
- Small, focused modules

✅ **Open/Closed:**
- Extend bằng new classes
- Không modify existing code

✅ **Low coupling:**
- Layers communicate qua interfaces
- Change infrastructure không affect domain

### Scalability

✅ **Modular:**
- Mỗi domain có thể extract thành microservice
- Clear boundaries

✅ **Stateless services:**
- Horizontal scaling
- No shared state

✅ **Async-ready:**
- Event-driven architecture
- Background processing via events

---

## DEPENDENCY FLOW

```
┌──────────────────┐
│   Presentation   │
│   (Controllers)  │
└────────┬─────────┘
         │ depends on
         ▼
┌──────────────────┐
│   Application    │
│    (Services)    │────────┐
└────────┬─────────┘        │ implements
         │ depends on        │
         ▼                   ▼
┌──────────────────┐   ┌──────────────────┐
│     Domain       │   │  Infrastructure  │
│  (Models/Logic)  │◄──│  (Repositories)  │
└──────────────────┘   └──────────────────┘
         ▲                      │
         │ defines interface    │
         └──────────────────────┘
```

**Key Points:**
- Domain defines interfaces
- Infrastructure implements interfaces
- Application depends on domain interfaces
- Infrastructure depends on domain
- Domain depends on NOTHING

---

## CONFIGURATION & DEPENDENCY INJECTION

### Dependency Container Setup

```
# main.py hoặc container.py

1. Load configuration từ environment
2. Initialize infrastructure:
   - Database connection
   - Password hasher
   - Email sender
   - Payment processor
   - Event bus
   - Logger

3. Initialize repositories:
   - Inject database connection
   - UserRepository, ProductRepository, etc.

4. Initialize application services:
   - Inject repositories
   - Inject external services
   - Inject event bus
   - UserService, OrderService, etc.

5. Initialize controllers (nếu có):
   - Inject application services

6. Wire up event handlers:
   - Subscribe handlers to event bus
```

### Example Container (Conceptual)

```
container = {
    # Infrastructure
    'database': SQLiteDatabase(connection_string),
    'password_hasher': BcryptPasswordHasher(),
    'email_sender': SmtpEmailSender(config),
    'event_bus': InMemoryEventBus(),
    'logger': FileLogger(log_path),
    
    # Repositories
    'user_repository': SqliteUserRepository(database),
    'product_repository': SqliteProductRepository(database),
    'order_repository': SqliteOrderRepository(database),
    
    # Application Services
    'user_service': UserService(
        user_repository,
        password_hasher,
        event_bus,
        logger
    ),
    'order_service': OrderService(
        order_repository,
        product_repository,
        coupon_repository,
        event_bus,
        logger
    ),
    
    # Event Handlers
    'welcome_email_handler': WelcomeEmailHandler(email_sender),
    'order_confirmation_handler': OrderConfirmationHandler(email_sender)
}

# Register handlers
event_bus.subscribe(UserRegistered, welcome_email_handler.handle)
event_bus.subscribe(OrderCreated, order_confirmation_handler.handle)
```

---

## MIGRATION PATH (Từ Spaghetti Code)

### Step 1: Setup Structure
- Tạo folder structure
- Setup testing framework
- Configure dependency injection

### Step 2: Extract Domain Models
- User, Product, Order entities
- Email, Password, Money value objects
- Business rules vào domain

### Step 3: Create Repository Interfaces
- Define interfaces trong domain/interfaces
- Implement repositories trong infrastructure

### Step 4: Extract Application Services
- Move use cases từ `do_everything()` vào services
- Create DTOs
- Add validators

### Step 5: Implement Infrastructure
- Database repositories
- Email sender
- Password hasher
- Event bus

### Step 6: Write Tests
- Unit tests cho domain
- Integration tests cho services
- E2E tests cho critical paths

### Step 7: Wire Dependencies
- Setup DI container
- Configure for different environments

### Step 8: Add Presentation Layer (Optional)
- REST API controllers
- Error handling middleware

---

## BEST PRACTICES

### Code Organization

✅ **One class per file**
✅ **Max 200 lines per file**
✅ **Max 20 lines per function**
✅ **Descriptive names:** `create_order_with_coupon()` not `do_thing()`

### Testing

✅ **Test file naming:** `test_<module>.py`
✅ **Test class naming:** `Test<ClassName>`
✅ **Test method naming:** `test_<scenario>_<expected_result>()`
✅ **AAA pattern:** Arrange, Act, Assert
✅ **One assertion per test** (when possible)

### Dependencies

✅ **Explicit > Implicit**
✅ **Constructor injection > Property injection**
✅ **Interfaces > Concrete classes**
✅ **Composition > Inheritance**

### Error Handling

✅ **Specific exceptions**
✅ **Don't catch generic Exception**
✅ **Log errors with context**
✅ **Fail fast**

---

## TOOLS & LIBRARIES RECOMMENDATION

### Core
- **Python 3.11+**
- **Type hints:** mypy
- **Dataclasses:** Built-in or pydantic

### Testing
- **pytest:** Test framework
- **pytest-cov:** Coverage
- **faker:** Test data generation
- **factory_boy:** Test fixtures

### Infrastructure
- **SQLite/PostgreSQL:** Database
- **bcrypt:** Password hashing
- **PyJWT:** JWT tokens
- **python-dotenv:** Environment variables

### Quality
- **black:** Code formatting
- **flake8:** Linting
- **mypy:** Type checking
- **pylint:** Static analysis

### Optional
- **FastAPI:** REST API framework
- **SQLAlchemy:** ORM (if needed)
- **Celery:** Background tasks
- **Redis:** Caching, message queue

---

## SUMMARY

Kiến trúc này đảm bảo:

✅ **Testability:** 
- Mọi component testable isolated
- Mock dependencies dễ dàng
- Fast test execution

✅ **Maintainability:**
- Clear structure
- Single responsibility
- Easy to navigate
- Self-documenting code

✅ **Scalability:**
- Modular design
- Stateless services
- Event-driven
- Can extract to microservices

✅ **SOLID:**
- S: One responsibility per class
- O: Extend via new classes
- L: Interfaces substitutable
- I: Small, focused interfaces
- D: Depend on abstractions

✅ **Clean Architecture:**
- Domain không depend vào gì
- Infrastructure implements domain interfaces
- Application orchestrates use cases
- Clear dependency direction

Cấu trúc này transform spaghetti code thành professional, maintainable, testable e-commerce system.
