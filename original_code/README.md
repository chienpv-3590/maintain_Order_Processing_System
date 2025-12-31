# Original Spaghetti Code

This directory contains the original spaghetti code that was refactored into the Clean Architecture system.

## File: exam_spaghetti_code.py

**Original Issues**:
- 345 lines of procedural code
- Global variables: `db`, `email_server`, `current_user`, `order_counter`, `logs`
- God method: `do_everything()` with 15+ actions
- Direct SQL queries embedded in business logic
- MD5 password hashing (insecure)
- No separation of concerns
- Error handling via dict returns instead of exceptions
- Tight coupling - impossible to test in isolation

**Refactored To**:
- Clean Architecture with 4 layers (Domain, Application, Infrastructure, Presentation)
- 55 directories, 184+ files
- SOLID principles compliance
- 8 specialized services
- Repository pattern for data access
- Dependency injection throughout
- Bcrypt password hashing
- Exception-based error handling
- 100% testable with mocks
- Event-driven architecture

## Comparison

| Aspect | Before (Spaghetti) | After (Clean Architecture) |
|--------|-------------------|---------------------------|
| Lines of code | 345 in 1 file | 4,458 across 203 files |
| Global state | ✅ Yes (6 globals) | ❌ No globals |
| Testability | ❌ Impossible | ✅ 100% mockable |
| Security | ❌ MD5 hashing | ✅ Bcrypt |
| Error handling | ❌ Dict returns | ✅ Exceptions |
| Separation of concerns | ❌ Everything in 1 file | ✅ Layered architecture |
| Design patterns | ❌ None | ✅ 8 patterns |
| SOLID compliance | ❌ 0/5 | ✅ 5/5 |
| Maintainability | 🔴 Very Low | 🟢 High |
| Extensibility | 🔴 Very Low | 🟢 High |

## Learning Points

This refactoring demonstrates:

1. **God Object Anti-Pattern** → Separated into focused services
2. **Global State** → Dependency Injection
3. **Procedural Code** → Object-Oriented with DDD
4. **No Abstractions** → Repository Pattern + Interfaces
5. **Spaghetti Logic** → Clean Architecture layers
6. **Hard to Test** → 100% unit test coverage possible
7. **Tight Coupling** → Loose coupling via interfaces
8. **No Events** → Event-driven architecture

See the refactored code in the parent directories for the improved implementation.
