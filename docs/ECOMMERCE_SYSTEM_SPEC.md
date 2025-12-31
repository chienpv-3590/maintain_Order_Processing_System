# E-COMMERCE SYSTEM SPECIFICATION

## DOMAIN MODEL

### 1. USER DOMAIN

#### Trách nhiệm
- Quản lý vòng đời người dùng (đăng ký, xác thực, phân quyền)
- Lưu trữ thông tin cá nhân và credentials
- Quản lý vai trò (Customer, VIP, Admin)
- Quản lý số dư tài khoản

#### Domain Logic
**Entities:**
- `User`
  - Properties: id, name, email, role, balance, created_at
  - Behaviors:
    - `register()`: Validate email format, password strength
    - `authenticate()`: Verify credentials
    - `hasRole(role)`: Check authorization
    - `deductBalance(amount)`: Validate sufficient balance, update balance
    - `addBalance(amount)`: Validate amount > 0, update balance

**Value Objects:**
- `Email`: Validate format, immutable
- `Password`: Hash with strong algorithm (bcrypt/argon2), validate strength
- `UserRole`: Enum (CUSTOMER, VIP, ADMIN)
- `Money`: Amount with currency, validation

**Domain Events:**
- `UserRegistered`
- `UserAuthenticated`
- `BalanceUpdated`

**Business Rules:**
- Email phải unique trong hệ thống
- Password tối thiểu 8 ký tự, chứa chữ hoa, chữ thường, số, ký tự đặc biệt
- Balance không được âm
- VIP users có quyền thanh toán bằng balance
- Admin có full permissions

#### Application Service
**UserService:**
- `registerUser(RegisterUserDto)`: Validate → Create User → Persist → Emit UserRegistered event
- `authenticateUser(LoginDto)`: Validate credentials → Create session → Return token
- `getUserProfile(userId)`: Fetch user data → Map to DTO
- `updateUserRole(userId, role)`: Check admin permission → Update role
- `addUserBalance(userId, amount)`: Check admin permission → Validate amount → Update balance → Emit event

**DTOs:**
- `RegisterUserDto`: name, email, password
- `LoginDto`: email, password
- `UserProfileDto`: id, name, email, role, balance
- `UpdateBalanceDto`: userId, amount

#### Infrastructure
**Repositories:**
- `UserRepository` (Interface)
  - `save(user)`: Persist user entity
  - `findById(id)`: Retrieve by ID
  - `findByEmail(email)`: Retrieve by email
  - `update(user)`: Update existing user
  - `existsByEmail(email)`: Check uniqueness

**Implementations:**
- `SqliteUserRepository`: Concrete implementation using SQLite
- `InMemoryUserRepository`: For testing

**External Services:**
- `PasswordHasher` (Interface)
  - `hash(password, salt)`: Hash password
  - `verify(password, hash)`: Verify password
- `BcryptPasswordHasher`: Production implementation
- `MockPasswordHasher`: Test implementation

---

### 2. PRODUCT DOMAIN

#### Trách nhiệm
- Quản lý catalog sản phẩm
- Quản lý inventory (stock)
- Phân loại sản phẩm
- Quản lý giá

#### Domain Logic
**Entities:**
- `Product`
  - Properties: id, name, price, stock, category
  - Behaviors:
    - `updatePrice(newPrice)`: Validate price > 0
    - `addStock(quantity)`: Validate quantity ≥ 0, update stock
    - `reserveStock(quantity)`: Check availability, reserve stock
    - `releaseStock(quantity)`: Release reserved stock
    - `isAvailable(quantity)`: Check if stock sufficient

**Value Objects:**
- `ProductName`: Non-empty string, max length
- `Price`: Must be > 0, with precision
- `Stock`: Non-negative integer
- `Category`: String or enum

**Domain Events:**
- `ProductCreated`
- `ProductPriceUpdated`
- `StockReserved`
- `StockReleased`
- `LowStockAlert` (when stock < threshold)

**Business Rules:**
- Price phải > 0
- Stock không được âm
- Không thể reserve stock > available
- Chỉ admin mới có quyền thêm/sửa products

#### Application Service
**ProductService:**
- `createProduct(CreateProductDto)`: Check admin → Validate → Create Product → Persist
- `updateProduct(productId, UpdateProductDto)`: Check admin → Validate → Update → Persist
- `getProductById(productId)`: Fetch → Map to DTO
- `searchProducts(query)`: Search by name/category → Return list
- `getAllProducts()`: Get all active products
- `updateStock(productId, quantity)`: Check admin → Update stock

**DTOs:**
- `CreateProductDto`: name, price, stock, category
- `UpdateProductDto`: name?, price?, stock?, category?
- `ProductDto`: id, name, price, stock, category
- `ProductSearchDto`: query, category?, priceRange?

#### Infrastructure
**Repositories:**
- `ProductRepository` (Interface)
  - `save(product)`: Persist product
  - `findById(id)`: Retrieve by ID
  - `findAll()`: Get all products
  - `searchByNameOrCategory(query)`: Search products
  - `update(product)`: Update product

**Implementations:**
- `SqliteProductRepository`
- `InMemoryProductRepository`

---

### 3. ORDER DOMAIN

#### Trách nhiệm
- Quản lý đơn hàng
- Xử lý order lifecycle
- Tính toán giá trị đơn hàng
- Quản lý order items

#### Domain Logic
**Entities:**
- `Order`
  - Properties: id, userId, orderItems, subtotal, discount, tax, total, status, shippingAddress, createdAt
  - Behaviors:
    - `addItem(product, quantity)`: Validate product availability → Add to items → Recalculate total
    - `removeItem(itemId)`: Remove item → Recalculate total
    - `applyCoupon(coupon)`: Validate coupon → Calculate discount → Recalculate total
    - `calculateTax(taxRate)`: Calculate tax based on subtotal - discount
    - `calculateTotal()`: subtotal - discount + tax
    - `updateStatus(newStatus)`: Validate state transition
    - `canCancel()`: Check if order can be cancelled

- `OrderItem`
  - Properties: productId, productName, price, quantity, subtotal
  - Behaviors:
    - `calculateSubtotal()`: price * quantity

**Value Objects:**
- `OrderId`: Unique identifier
- `OrderStatus`: Enum (PENDING_PAYMENT, PAID, PROCESSING, SHIPPED, DELIVERED, CANCELLED)
- `ShippingAddress`: Street, city, country, zipCode
- `Money`: For amounts
- `TaxRate`: Percentage value

**Aggregates:**
- `Order` là aggregate root
- `OrderItem` là entity trong aggregate

**Domain Events:**
- `OrderCreated`
- `OrderPaid`
- `OrderStatusUpdated`
- `OrderCancelled`
- `OrderDelivered`

**Business Rules:**
- Order phải có ít nhất 1 item
- Total = (subtotal - discount) + tax
- Tax rate = 10%
- Status transition rules:
  - PENDING_PAYMENT → PAID hoặc CANCELLED
  - PAID → PROCESSING
  - PROCESSING → SHIPPED
  - SHIPPED → DELIVERED
  - Không thể cancel sau khi SHIPPED
- VIP users có thể thanh toán bằng balance
- Phải có shipping address hợp lệ

#### Application Service
**OrderService:**
- `createOrder(CreateOrderDto)`: 
  - Validate user authenticated
  - Validate items availability
  - Reserve product stock
  - Apply coupon if exists
  - Calculate totals
  - Create order
  - Process payment if VIP
  - Emit OrderCreated event
  - Return order summary

- `getOrderById(orderId, userId)`: 
  - Validate ownership or admin
  - Fetch order
  - Map to DTO

- `getUserOrders(userId)`: Get all orders for user

- `updateOrderStatus(orderId, status)`:
  - Check admin permission
  - Validate status transition
  - Update status
  - Emit event

- `cancelOrder(orderId, userId)`:
  - Validate ownership
  - Check if cancellable
  - Release stock
  - Update status
  - Emit event

**DTOs:**
- `CreateOrderDto`: userId, items[], shippingAddress, couponCode?
- `OrderItemDto`: productId, quantity
- `OrderDto`: id, userId, items, subtotal, discount, tax, total, status, shippingAddress, createdAt
- `OrderSummaryDto`: orderId, total, status, breakdown
- `UpdateOrderStatusDto`: orderId, status

#### Infrastructure
**Repositories:**
- `OrderRepository` (Interface)
  - `save(order)`: Persist order
  - `findById(id)`: Get order by ID
  - `findByUserId(userId)`: Get user's orders
  - `findAll()`: Get all orders (admin)
  - `update(order)`: Update order

**Implementations:**
- `SqliteOrderRepository`
- `InMemoryOrderRepository`

---

### 4. PAYMENT DOMAIN

#### Trách nhiệm
- Xử lý thanh toán
- Quản lý payment methods
- Tích hợp payment gateways
- Xử lý refunds

#### Domain Logic
**Entities:**
- `Payment`
  - Properties: id, orderId, amount, method, status, transactionId, createdAt
  - Behaviors:
    - `process()`: Execute payment
    - `confirm()`: Mark as successful
    - `fail(reason)`: Mark as failed
    - `refund(amount)`: Process refund

**Value Objects:**
- `PaymentMethod`: Enum (BALANCE, CREDIT_CARD, PAYPAL, etc.)
- `PaymentStatus`: Enum (PENDING, PROCESSING, COMPLETED, FAILED, REFUNDED)
- `Money`: Amount

**Domain Events:**
- `PaymentInitiated`
- `PaymentCompleted`
- `PaymentFailed`
- `PaymentRefunded`

**Business Rules:**
- Payment amount phải match order total
- Balance payment chỉ cho VIP users
- Balance payment phải check sufficient funds
- Payment failed không affect stock (đã reserved)
- Refund chỉ cho completed payments

#### Application Service
**PaymentService:**
- `processPayment(ProcessPaymentDto)`:
  - Validate order exists
  - Validate payment amount matches order
  - Select payment processor
  - Process payment
  - Update order status if successful
  - Emit events

- `processBalancePayment(orderId, userId)`:
  - Validate VIP user
  - Check sufficient balance
  - Deduct balance
  - Create payment record
  - Update order status

- `refundPayment(paymentId)`:
  - Check admin permission
  - Validate payment status
  - Process refund
  - Release stock
  - Update order

**DTOs:**
- `ProcessPaymentDto`: orderId, paymentMethod
- `PaymentDto`: id, orderId, amount, method, status, transactionId

#### Infrastructure
**Payment Processors:**
- `PaymentProcessor` (Interface)
  - `process(amount, method)`: Process payment
  - `refund(transactionId, amount)`: Refund payment

**Implementations:**
- `BalancePaymentProcessor`: Internal balance
- `MockPaymentProcessor`: For testing

**Repositories:**
- `PaymentRepository` (Interface)
  - `save(payment)`: Persist payment
  - `findById(id)`: Get payment
  - `findByOrderId(orderId)`: Get order payments

---

### 5. COUPON DOMAIN

#### Trách nhiệm
- Quản lý mã giảm giá
- Validate coupon usage
- Track usage limits

#### Domain Logic
**Entities:**
- `Coupon`
  - Properties: code, discountPercentage, usedCount, maxUses
  - Behaviors:
    - `isValid()`: Check if not expired and usage < max
    - `use()`: Increment usage count
    - `calculateDiscount(amount)`: Calculate discount amount
    - `canBeUsed()`: Check availability

**Value Objects:**
- `CouponCode`: Uppercase alphanumeric string
- `DiscountPercentage`: 0-100
- `UsageLimit`: Positive integer

**Domain Events:**
- `CouponCreated`
- `CouponUsed`
- `CouponExpired`

**Business Rules:**
- Code phải unique
- Discount percentage: 0-100
- Usage không vượt quá max uses
- Một order chỉ dùng 1 coupon
- Discount không vượt quá order subtotal

#### Application Service
**CouponService:**
- `createCoupon(CreateCouponDto)`: Check admin → Create → Persist
- `validateCoupon(code)`: Check exists and valid
- `applyCoupon(code, amount)`: Validate → Calculate discount → Mark as used
- `getCouponUsage(code)`: Get usage statistics

**DTOs:**
- `CreateCouponDto`: code, discountPercentage, maxUses
- `CouponDto`: code, discountPercentage, usedCount, maxUses
- `ApplyCouponDto`: code, orderAmount

#### Infrastructure
**Repositories:**
- `CouponRepository` (Interface)
  - `save(coupon)`: Persist coupon
  - `findByCode(code)`: Get by code
  - `update(coupon)`: Update usage

**Implementations:**
- `SqliteCouponRepository`
- `InMemoryCouponRepository`

---

### 6. REVIEW DOMAIN

#### Trách nhiệm
- Quản lý đánh giá sản phẩm
- Validate quyền review (đã mua)
- Tính rating trung bình

#### Domain Logic
**Entities:**
- `Review`
  - Properties: id, productId, userId, rating, comment, createdAt
  - Behaviors:
    - `update(rating, comment)`: Update review
    - `isValidRating(rating)`: Check 1-5 range

**Value Objects:**
- `Rating`: Integer 1-5
- `Comment`: Non-empty string, max length

**Domain Events:**
- `ReviewCreated`
- `ReviewUpdated`
- `ReviewDeleted`

**Business Rules:**
- Rating: 1-5
- User phải purchase product mới được review
- Một user chỉ review 1 lần mỗi product
- Không review cancelled orders

#### Application Service
**ReviewService:**
- `createReview(CreateReviewDto)`:
  - Validate user purchased product
  - Check order status (not cancelled)
  - Check not already reviewed
  - Create review
  - Update product rating

- `getProductReviews(productId)`: Get all reviews for product
- `getUserReviews(userId)`: Get user's reviews
- `updateReview(reviewId, UpdateReviewDto)`: Update existing review
- `deleteReview(reviewId)`: Delete review

**DTOs:**
- `CreateReviewDto`: productId, userId, rating, comment
- `UpdateReviewDto`: rating?, comment?
- `ReviewDto`: id, productId, userName, rating, comment, createdAt

#### Infrastructure
**Repositories:**
- `ReviewRepository` (Interface)
  - `save(review)`: Persist review
  - `findByProductId(productId)`: Get product reviews
  - `findByUserId(userId)`: Get user reviews
  - `existsByUserAndProduct(userId, productId)`: Check duplicate
  - `update(review)`: Update review
  - `delete(reviewId)`: Delete review

---

### 7. NOTIFICATION DOMAIN

#### Trách nhiệm
- Gửi thông báo cho users
- Quản lý notification templates
- Support multiple channels (email, SMS, push)

#### Domain Logic
**Entities:**
- `Notification`
  - Properties: id, userId, type, channel, content, status, sentAt
  - Behaviors:
    - `send()`: Send notification
    - `markAsSent()`: Update status
    - `retry()`: Retry failed notification

**Value Objects:**
- `NotificationType`: Enum (WELCOME, ORDER_CONFIRMATION, ORDER_STATUS, etc.)
- `NotificationChannel`: Enum (EMAIL, SMS, PUSH)
- `NotificationStatus`: Enum (PENDING, SENT, FAILED)

**Domain Events:**
- `NotificationSent`
- `NotificationFailed`

**Business Rules:**
- Welcome email khi user register
- Order confirmation khi order created
- Status update khi order status changes
- Retry failed notifications max 3 times

#### Application Service
**NotificationService:**
- `sendWelcomeEmail(userId)`: Send welcome notification
- `sendOrderConfirmation(orderId, userId)`: Send order confirmation
- `sendOrderStatusUpdate(orderId, status)`: Notify status change
- `sendLowStockAlert(productId)`: Alert admin về low stock
- `retryFailedNotifications()`: Retry failed notifications

**DTOs:**
- `NotificationDto`: userId, type, channel, content
- `SendNotificationDto`: recipients[], template, data

#### Infrastructure
**Notification Senders:**
- `NotificationSender` (Interface)
  - `send(notification)`: Send notification

**Implementations:**
- `EmailSender`: SMTP integration
- `SmsSender`: SMS gateway integration
- `MockNotificationSender`: For testing

**Repositories:**
- `NotificationRepository` (Interface)
  - `save(notification)`: Persist notification
  - `findPending()`: Get pending notifications
  - `findFailed()`: Get failed notifications
  - `update(notification)`: Update status

**Template Engine:**
- `NotificationTemplateEngine` (Interface)
  - `render(template, data)`: Render notification content

---

### 8. ANALYTICS DOMAIN

#### Trách nhiệm
- Tạo reports
- Tính toán metrics
- Aggregate data

#### Domain Logic
**Value Objects:**
- `DateRange`: startDate, endDate
- `SalesMetrics`: totalRevenue, totalOrders, averageOrderValue
- `ProductMetrics`: productId, name, quantitySold, revenue

**Domain Services:**
- `AnalyticsService`
  - `calculateSalesMetrics(dateRange)`: Tính metrics
  - `getTopProducts(limit, dateRange)`: Top selling products
  - `getUserStatistics()`: User growth metrics
  - `getRevenueByPeriod(period)`: Revenue breakdown

**Business Rules:**
- Chỉ admin mới access analytics
- Exclude cancelled orders khỏi revenue
- Top products based on quantity sold

#### Application Service
**ReportService:**
- `generateSalesReport(dateRange)`: Generate sales report
- `getAnalyticsDashboard()`: Get dashboard metrics
- `exportOrderReport(dateRange, format)`: Export report

**DTOs:**
- `SalesReportDto`: metrics, topProducts, revenueByDay
- `AnalyticsDashboardDto`: totalOrders, totalRevenue, totalUsers, topProducts

#### Infrastructure
**Repositories:**
- `AnalyticsRepository` (Interface)
  - `getOrderStatistics(dateRange)`: Get aggregated data
  - `getProductSales(dateRange)`: Product sales data
  - `getUserGrowth(dateRange)`: User growth data

---

## CROSS-CUTTING CONCERNS

### Authentication & Authorization

**AuthenticationService:**
- `authenticate(credentials)`: Verify credentials → Generate token
- `validateToken(token)`: Validate and extract user info
- `refreshToken(refreshToken)`: Generate new access token

**AuthorizationService:**
- `hasPermission(user, resource, action)`: Check permissions
- `isAdmin(user)`: Check admin role
- `isOwner(user, resource)`: Check ownership

**Implementations:**
- `JwtTokenService`: JWT-based authentication
- `MockAuthService`: For testing

### Logging

**Logger** (Interface)
- `info(message, context)`
- `error(message, error, context)`
- `warn(message, context)`
- `debug(message, context)`

**Implementations:**
- `FileLogger`: Log to file
- `ConsoleLogger`: Log to console
- `NullLogger`: For testing

### Event Bus

**EventBus** (Interface)
- `publish(event)`: Publish domain event
- `subscribe(eventType, handler)`: Subscribe to events

**Implementations:**
- `InMemoryEventBus`: Synchronous in-memory
- `MessageQueueEventBus`: Async message queue

### Transaction Management

**UnitOfWork** (Interface)
- `begin()`: Start transaction
- `commit()`: Commit transaction
- `rollback()`: Rollback transaction

**Implementations:**
- `SqliteUnitOfWork`
- `InMemoryUnitOfWork`

---

## ARCHITECTURE LAYERS

### 1. Domain Layer (Core)
- Entities, Value Objects, Aggregates
- Domain Services
- Domain Events
- Business Rules
- **Không dependency vào layer khác**
- Pure business logic

### 2. Application Layer
- Application Services (Use Cases)
- DTOs
- Event Handlers
- Orchestration logic
- **Dependency:** Domain Layer
- **Không biết về Infrastructure**

### 3. Infrastructure Layer
- Repositories implementation
- External Services integration (Email, SMS, Payment)
- Database access
- File storage
- **Dependency:** Domain Layer (interfaces)

### 4. Presentation Layer (API/Web)
- Controllers/Handlers
- Request/Response models
- Validation
- **Dependency:** Application Layer

---

## DEPENDENCY INJECTION

### Service Container
Tất cả dependencies được inject qua constructor:

```
Controller → Application Service → Domain Service
                ↓
          Repository Interface
                ↓
          Repository Implementation
```

**Không sử dụng:**
- Global variables
- Static methods for dependencies
- Service locators
- New keyword trong business logic

**Sử dụng:**
- Constructor injection
- Interface-based dependencies
- Factory pattern cho complex object creation
- Dependency Inversion Principle

---

## TESTING STRATEGY

### Unit Tests
- Test Domain Entities và Value Objects isolated
- Test Domain Services với mock dependencies
- Test Application Services với mock repositories
- **Coverage target:** 90%+

### Integration Tests
- Test Application Services với real repositories
- Test Repository implementations với test database
- Test External Service integrations với mocks
- **Coverage target:** 80%+

### End-to-End Tests
- Test complete workflows (register → login → order → payment)
- Test với real infrastructure components
- **Coverage target:** Critical paths

### Test Fixtures
- Factory pattern cho test data
- Builder pattern cho complex objects
- Shared fixtures cho common scenarios

### Mocking Strategy
- Mock external dependencies (email, payment gateway)
- Use in-memory repositories cho unit tests
- Use test database cho integration tests
- Mock time-dependent functions (datetime.now)

---

## DESIGN PRINCIPLES

### SOLID Compliance

**Single Responsibility:**
- Mỗi class có 1 reason to change
- Separate concerns: UserService vs AuthenticationService
- Domain logic tách biệt khỏi infrastructure

**Open/Closed:**
- Extend behavior qua inheritance/composition
- New payment methods không modify existing code
- New notification channels không modify service

**Liskov Substitution:**
- All Repository implementations interchangeable
- Payment processors có thể swap
- Notification senders có thể swap

**Interface Segregation:**
- Small, focused interfaces
- Clients chỉ depend vào methods cần thiết
- Repository interfaces specific cho từng domain

**Dependency Inversion:**
- Depend on abstractions (interfaces)
- High-level modules không depend vào low-level
- Infrastructure implements domain interfaces

### Additional Principles

**DRY (Don't Repeat Yourself):**
- Shared logic trong base classes/utilities
- Reusable Value Objects
- Common validation logic

**KISS (Keep It Simple):**
- Clear, readable code
- Avoid over-engineering
- Simple solutions preferred

**YAGNI (You Aren't Gonna Need It):**
- Implement features when needed
- No speculative coding
- Focus on current requirements

---

## ERROR HANDLING

### Domain Exceptions
- `InvalidEmailException`
- `InsufficientStockException`
- `InvalidOrderStateException`
- `UnauthorizedAccessException`
- `CouponExpiredException`

### Application Exceptions
- `ResourceNotFoundException`
- `ValidationException`
- `BusinessRuleViolationException`

### Infrastructure Exceptions
- `DatabaseException`
- `ExternalServiceException`
- `NetworkException`

**Strategy:**
- Domain layer throws domain exceptions
- Application layer catches và converts to DTOs
- Infrastructure layer throws infrastructure exceptions
- API layer converts to HTTP responses

---

## VALIDATION STRATEGY

### Domain Validation
- Value Objects self-validate
- Entities validate state transitions
- Business rules enforced in domain

### Application Validation
- Input DTOs validation
- Cross-entity validation
- Authorization checks

### Infrastructure Validation
- Schema validation
- Data type validation
- Constraint validation

---

## CONFIGURATION MANAGEMENT

**Externalize Configuration:**
- Database connection strings
- Email server settings
- Payment gateway credentials
- Tax rates
- Feature flags

**Environment-specific:**
- Development
- Testing
- Staging
- Production

**No hardcoded values:**
- URLs
- Credentials
- Business constants (configurable)

---

## SCALABILITY CONSIDERATIONS

### Stateless Services
- No shared mutable state
- Each request independent
- Horizontal scaling possible

### Caching Strategy
- Cache product catalog
- Cache user sessions
- Cache analytics data
- Invalidate on updates

### Async Processing
- Order confirmation emails async
- Analytics calculation async
- Notification sending async
- Use message queues

### Database Optimization
- Indexes on frequently queried fields
- Connection pooling
- Query optimization
- Pagination for large datasets

---

## SECURITY REQUIREMENTS

### Authentication
- Strong password hashing (bcrypt/argon2)
- Password strength validation
- Token-based authentication (JWT)
- Token expiration
- Refresh tokens

### Authorization
- Role-based access control (RBAC)
- Resource ownership validation
- Admin-only operations protected

### Data Protection
- Encrypt sensitive data at rest
- HTTPS for data in transit
- SQL injection prevention (parameterized queries)
- XSS prevention
- CSRF protection

### Input Validation
- Sanitize all inputs
- Validate types and formats
- Prevent injection attacks
- Limit input sizes

### Audit Logging
- Log authentication attempts
- Log administrative actions
- Log payment transactions
- Immutable audit trail

---

## MONITORING & OBSERVABILITY

### Logging
- Structured logging
- Log levels (DEBUG, INFO, WARN, ERROR)
- Correlation IDs for request tracing
- No sensitive data in logs

### Metrics
- Request count
- Response times
- Error rates
- Business metrics (orders, revenue)

### Health Checks
- Database connectivity
- External service availability
- System resources

### Alerting
- Low stock alerts
- Payment failures
- System errors
- Performance degradation

---

## DATA CONSISTENCY

### Transaction Boundaries
- Order creation = atomic transaction
- Stock reservation + order save
- Payment + order update
- Rollback on failure

### Eventual Consistency
- Notification sending (async)
- Analytics updates
- Cache invalidation

### Idempotency
- Retry-safe operations
- Duplicate order prevention
- Payment idempotency keys

---

## MIGRATION STRATEGY (From Current Code)

### Phase 1: Domain Modeling
1. Extract domain entities
2. Create value objects
3. Define domain events
4. Implement business rules

### Phase 2: Application Services
1. Create service interfaces
2. Implement use cases
3. Define DTOs
4. Add validation

### Phase 3: Infrastructure
1. Create repository interfaces
2. Implement repositories
3. Add external service integrations
4. Configure dependency injection

### Phase 4: Testing
1. Unit tests for domain
2. Integration tests for services
3. E2E tests for workflows
4. Performance tests

### Phase 5: Deployment
1. Database migration
2. Configuration setup
3. Monitoring setup
4. Gradual rollout

---

## SUCCESS METRICS

### Code Quality
- 80%+ test coverage
- Zero CRITICAL security issues
- < 5% code duplication
- Complexity score < 10

### Performance
- < 200ms average response time
- < 1% error rate
- 99.9% uptime
- Handle 1000 concurrent users

### Maintainability
- New feature time < 2 days
- Bug fix time < 4 hours
- Zero global state dependencies
- All SOLID principles enforced

---

## CONCLUSION

Specification này định nghĩa một E-commerce system:
- **Modular:** Tách biệt domains rõ ràng
- **Testable:** Dependency injection, interfaces
- **Secure:** Authentication, authorization, encryption
- **Scalable:** Stateless, async processing
- **Maintainable:** SOLID principles, clean architecture
- **Observable:** Logging, metrics, monitoring

Mỗi domain độc lập, có thể test và deploy riêng. Không có global state, không có tight coupling. Tuân thủ nghiêm ngặt SOLID và clean architecture principles.
