# E-Commerce Order Processing System

A refactored e-commerce order processing system following Clean Architecture and Domain-Driven Design principles.

## 🏗️ Architecture

This project demonstrates the transformation of spaghetti code into a well-architected system using:

- **Clean Architecture** (Domain, Application, Infrastructure, Presentation layers)
- **Domain-Driven Design** (Aggregates, Entities, Value Objects, Domain Events)
- **SOLID Principles**
- **Design Patterns** (Repository, Service Layer, Strategy, Dependency Injection, Factory, Unit of Work, Observer, Builder)

## 📁 Project Structure

```
ecommerce/
├── domain/                    # Domain Layer (Business Logic)
│   ├── aggregates/           # Aggregate Roots
│   ├── entities/             # Domain Entities
│   ├── events/               # Domain Events
│   ├── exceptions/           # Domain Exceptions
│   ├── interfaces/           # Repository Interfaces
│   ├── services/             # Domain Services
│   └── value_objects/        # Value Objects
│
├── application/              # Application Layer (Use Cases)
│   ├── dtos/                # Data Transfer Objects
│   ├── exceptions/          # Application Exceptions
│   ├── handlers/            # Event Handlers
│   ├── services/            # Application Services
│   ├── strategies/          # Strategy Pattern Implementations
│   └── validators/          # Input Validators
│
├── infrastructure/          # Infrastructure Layer
│   ├── event_bus/          # Event Bus Implementation
│   ├── logging/            # Logging Services
│   ├── persistence/        # Database Implementation
│   └── security/           # Security Services
│
├── presentation/           # Presentation Layer
│   └── cli/               # Command Line Interface
│
├── tests/                 # Test Suite
│   ├── unit/             # Unit Tests
│   ├── integration/      # Integration Tests
│   └── e2e/             # End-to-End Tests
│
└── docs/                 # Documentation
    ├── ARCHITECTURE.md
    ├── DESIGN_PATTERNS.md
    ├── SPEC.md
    └── CODE_REVIEW_ORDERSERVICE.md
```

## ✨ Features

### Implemented Services

1. **OrderService** - Order creation and management
2. **UserService** - User registration, authentication, profile management
3. **ProductService** - Product catalog management
4. **PaymentService** - Payment processing (balance, credit card, PayPal)
5. **CouponService** - Coupon validation and management
6. **ReviewService** - Product reviews and ratings
7. **NotificationService** - Email notifications
8. **AnalyticsService** - Sales reporting and analytics

### Key Improvements Over Original Code

- ✅ No global variables
- ✅ Dependency Injection throughout
- ✅ Exception-based error handling
- ✅ Repository pattern for data access
- ✅ Event-driven architecture
- ✅ Type hints for better IDE support
- ✅ Comprehensive unit tests
- ✅ SOLID principles compliance

## 🧪 Testing

The project includes comprehensive unit tests with:
- Mock dependencies (no database required)
- Happy path testing
- Validation testing
- Authorization testing
- Edge case testing

Run tests:
```bash
pytest tests/unit/application/services/test_order_service.py -v
```

Test Coverage:
- ✅ 8/8 tests passing for OrderService
- ✅ Happy path scenarios
- ✅ Input validation
- ✅ Out-of-stock scenarios
- ✅ Coupon validation
- ✅ All tests isolated (no global state)

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip
- virtualenv (recommended)

### Installation

1. Clone the repository:
```bash
git clone git@github.com:chienpv-3590/maintain_Order_Processing_System.git
cd maintain_Order_Processing_System
```

2. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run tests:
```bash
pytest -v
```

## 📚 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Design Patterns](docs/DESIGN_PATTERNS.md)
- [System Specification](docs/SPEC.md)
- [Code Review](docs/CODE_REVIEW_ORDERSERVICE.md)
- [Refactored Example](docs/REFACTORED_ORDER_SERVICE.py)

## 🛠️ Technology Stack

- **Language**: Python 3.10+
- **Testing**: pytest, pytest-mock, pytest-cov
- **Security**: bcrypt (password hashing)
- **Database**: SQLite (with repository abstraction)
- **Architecture**: Clean Architecture + DDD

## 📈 Code Quality

### SOLID Principles Compliance
- ✅ Single Responsibility Principle
- ✅ Open/Closed Principle
- ✅ Liskov Substitution Principle
- ✅ Interface Segregation Principle
- ✅ Dependency Inversion Principle

### Design Patterns Used
- Repository Pattern
- Service Layer Pattern
- Strategy Pattern
- Dependency Injection
- Factory Pattern
- Unit of Work Pattern (proposed)
- Observer Pattern (Event Bus)
- Builder Pattern (DTOs)

## 🔄 Refactoring Journey

This project demonstrates the transformation from:

**Before** (exam_spaghetti_code.py):
- 345 lines of procedural code
- Global variables everywhere
- God method `do_everything()`
- Direct SQL queries
- MD5 password hashing
- No separation of concerns

**After** (ecommerce/):
- 55 directories, 184+ files
- Clean Architecture layers
- SOLID principles
- Design patterns
- Type-safe DTOs
- Repository pattern
- Bcrypt password hashing
- Comprehensive test suite

## 🤝 Contributing

This is an educational project demonstrating refactoring techniques. Feel free to:
- Study the code structure
- Learn from the design patterns
- Compare with the original spaghetti code
- Suggest improvements via issues

## 📝 License

This project is for educational purposes.

## 👨‍💻 Author

Refactored from spaghetti code to Clean Architecture + DDD as a demonstration of software engineering best practices.

---

**Note**: This project is a refactoring exercise showing how to transform legacy code into a maintainable, testable, and extensible system following industry best practices.
