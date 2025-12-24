Execute a comprehensive Test-Driven Development (TDD) workflow with strict red-green-refactor discipline:

[Extended thinking: This workflow enforces test-first development through coordinated agent orchestration. Each phase of the TDD cycle is strictly enforced with fail-first verification, incremental implementation, and continuous refactoring. The workflow supports both single test and test suite approaches with configurable coverage thresholds.]

## Configuration

### Coverage Thresholds
- Minimum line coverage: 80%
- Minimum branch coverage: 75%
- Critical path coverage: 100%

### Refactoring Triggers
- Cyclomatic complexity > 10
- Method length > 20 lines
- Class length > 200 lines
- Duplicate code blocks > 3 lines

## Phase 1: Test Specification and Design

### 1. Requirements Analysis
- Use Task tool with subagent_type="backend-development::architect-review"
- Prompt: "Analyze requirements for: $ARGUMENTS. Define acceptance criteria, identify edge cases, and create test scenarios. Output a comprehensive test specification."
- Output: Test specification, acceptance criteria, edge case matrix
- Validation: Ensure all requirements have corresponding test scenarios

### 2. Test Architecture Design
- Use Task tool with subagent_type="backend-development::test-automator"
- Prompt: "Design test architecture for: $ARGUMENTS based on test specification. Define test structure, fixtures, mocks, and test data strategy. Ensure testability and maintainability."
- Output: Test architecture, fixture design, mock strategy
- Validation: Architecture supports isolated, fast, reliable tests

## Phase 2: RED - Write Failing Tests

### 3. Write Unit Tests (Failing)
- Use Task tool with subagent_type="backend-development::test-automator"
- Prompt: "Write FAILING unit tests for: $ARGUMENTS. Tests must fail initially. Include edge cases, error scenarios, and happy paths. DO NOT implement production code."
- Output: Failing unit tests, test documentation
- **CRITICAL**: Verify all tests fail with expected error messages

### 4. Verify Test Failure
- Use Task tool with subagent_type="codebase-cleanup::code-reviewer"
- Prompt: "Verify that all tests for: $ARGUMENTS are failing correctly. Ensure failures are for the right reasons (missing implementation, not test errors). Confirm no false positives."
- Output: Test failure verification report
- **GATE**: Do not proceed until all tests fail appropriately

### Core Requirements

1. **Test Structure**
   - Framework-appropriate setup (Jest/pytest/JUnit/Go/RSpec)
   - Arrange-Act-Assert pattern
   - should_X_when_Y naming convention
   - Isolated fixtures with no interdependencies

2. **Behavior Coverage**
   - Happy path scenarios
   - Edge cases (empty, null, boundary values)
   - Error handling and exceptions
   - Concurrent access (if applicable)

3. **Failure Verification**
   - Tests MUST fail when run
   - Failures for RIGHT reasons (not syntax/import errors)
   - Meaningful diagnostic error messages
   - No cascading failures

4. **Test Categories**
   - Unit: Isolated component behavior
   - Integration: Component interaction
   - Contract: API/interface contracts
   - Property: Mathematical invariants

### Framework Patterns

**JavaScript/TypeScript (Jest/Vitest)**
- Mock dependencies with `vi.fn()` or `jest.fn()`
- Use `@testing-library` for React components
- Property tests with `fast-check`

**Python (pytest)**
- Fixtures with appropriate scopes
- Parametrize for multiple test cases
- Hypothesis for property-based tests

**Go**
- Table-driven tests with subtests
- `t.Parallel()` for parallel execution
- Use `testify/assert` for cleaner assertions

**Ruby (RSpec)**
- `let` for lazy loading, `let!` for eager
- Contexts for different scenarios
- Shared examples for common behavior

## Validation

After generation:
1. Run tests - confirm they fail
2. Verify helpful failure messages
3. Check test independence
4. Ensure comprehensive coverage

## Example (Minimal)

```typescript
// auth.service.test.ts
describe('AuthService', () => {
  let authService: AuthService;
  let mockUserRepo: jest.Mocked<UserRepository>;

  beforeEach(() => {
    mockUserRepo = { findByEmail: jest.fn() } as any;
    authService = new AuthService(mockUserRepo);
  });

  it('should_return_token_when_valid_credentials', async () => {
    const user = { id: '1', email: 'test@example.com', passwordHash: 'hashed' };
    mockUserRepo.findByEmail.mockResolvedValue(user);

    const result = await authService.authenticate('test@example.com', 'pass');

    expect(result.success).toBe(true);
    expect(result.token).toBeDefined();
  });

  it('should_fail_when_user_not_found', async () => {
    mockUserRepo.findByEmail.mockResolvedValue(null);

    const result = await authService.authenticate('none@example.com', 'pass');

    expect(result.success).toBe(false);
    expect(result.error).toBe('INVALID_CREDENTIALS');
  });
});
```

Test requirements: $ARGUMENTS

## Phase 3: GREEN - Make Tests Pass

### 5. Minimal Implementation
- Use Task tool with subagent_type="backend-development::backend-architect"
- Prompt: "Implement MINIMAL code to make tests pass for: $ARGUMENTS. Focus only on making tests green. Do not add extra features or optimizations. Keep it simple."
- Output: Minimal working implementation
- Constraint: No code beyond what's needed to pass tests

### 6. Verify Test Success
- Use Task tool with subagent_type="backend-development::test-automator"
- Prompt: "Run all tests for: $ARGUMENTS and verify they pass. Check test coverage metrics. Ensure no tests were accidentally broken."
- Output: Test execution report, coverage metrics
- **GATE**: All tests must pass before proceeding

### 7. Code Structure Guidelines

- Write the minimal code that could possibly work
- Avoid adding functionality not required by tests
- Use simple data structures initially
- Defer architectural decisions until refactor phase
- Keep methods/functions small and focused
- Don't add error handling unless tests require it

### 8. Language-Specific Patterns

- **JavaScript/TypeScript**: Simple functions, avoid classes initially
- **Python**: Functions before classes, simple returns
- **Java**: Minimal class structure, no patterns yet
- **C#**: Basic implementations, no interfaces yet
- **Go**: Simple functions, defer goroutines/channels
- **Ruby**: Procedural before object-oriented when possible

### 9. Progressive Implementation

- Make first test pass with simplest possible code
- Run tests after each change to verify progress
- Add just enough code for next failing test
- Resist urge to implement beyond test requirements
- Keep track of technical debt for refactor phase
- Document assumptions and shortcuts taken

### 10. Common Green Phase Techniques

- Hard-coded returns for initial tests
- Simple if/else for limited test cases
- Basic loops only when iteration tests require
- Minimal data structures (arrays before complex objects)
- In-memory storage before database integration
- Synchronous before asynchronous implementation

### Best Practices

- Embrace "good enough" for this phase
- Speed over perfection (perfection comes in refactor)
- Make it work, then make it right, then make it fast
- Trust that refactoring phase will improve code
- Keep changes small and incremental
- Celebrate reaching green state!

## Complete Implementation Examples

### Example 1: Minimal → Production-Ready (User Service)

**Test Requirements:**
```typescript
describe('UserService', () => {
  it('should create a new user', async () => {
    const user = await userService.create({ email: 'test@example.com', name: 'Test' });
    expect(user.id).toBeDefined();
    expect(user.email).toBe('test@example.com');
  });

  it('should find user by email', async () => {
    await userService.create({ email: 'test@example.com', name: 'Test' });
    const user = await userService.findByEmail('test@example.com');
    expect(user).toBeDefined();
  });
});
```

**Stage 1: Fake It (Minimal)**
```typescript
class UserService {
  create(data: { email: string; name: string }) {
    return { id: '123', email: data.email, name: data.name };
  }

  findByEmail(email: string) {
    return { id: '123', email: email, name: 'Test' };
  }
}
```
*Tests pass. Implementation is obviously fake but validates test structure.*

**Stage 2: Simple Real Implementation**
```typescript
class UserService {
  private users: Map<string, User> = new Map();
  private nextId = 1;

  create(data: { email: string; name: string }) {
    const user = { id: String(this.nextId++), ...data };
    this.users.set(user.email, user);
    return user;
  }

  findByEmail(email: string) {
    return this.users.get(email) || null;
  }
}
```
*In-memory storage. Tests pass. Good enough for green phase.*

**Stage 3: Production-Ready (Refactor Phase)**
```typescript
class UserService {
  constructor(private db: Database) {}

  async create(data: { email: string; name: string }) {
    const existing = await this.db.query('SELECT * FROM users WHERE email = ?', [data.email]);
    if (existing) throw new Error('User exists');

    const id = await this.db.insert('users', data);
    return { id, ...data };
  }

  async findByEmail(email: string) {
    return this.db.queryOne('SELECT * FROM users WHERE email = ?', [email]);
  }
}
```
*Database integration, error handling, validation - saved for refactor phase.*

### Example 2: API-First Implementation (Express)

**Test Requirements:**
```javascript
describe('POST /api/tasks', () => {
  it('should create task and return 201', async () => {
    const res = await request(app)
      .post('/api/tasks')
      .send({ title: 'Test Task' });

    expect(res.status).toBe(201);
    expect(res.body.id).toBeDefined();
    expect(res.body.title).toBe('Test Task');
  });
});
```

**Stage 1: Hardcoded Response**
```javascript
app.post('/api/tasks', (req, res) => {
  res.status(201).json({ id: '1', title: req.body.title });
});
```
*Tests pass immediately. No logic needed yet.*

**Stage 2: Simple Logic**
```javascript
let tasks = [];
let nextId = 1;

app.post('/api/tasks', (req, res) => {
  const task = { id: String(nextId++), title: req.body.title };
  tasks.push(task);
  res.status(201).json(task);
});
```
*Minimal state management. Ready for more tests.*

**Stage 3: Layered Architecture (Refactor)**
```javascript
// Controller
app.post('/api/tasks', async (req, res) => {
  try {
    const task = await taskService.create(req.body);
    res.status(201).json(task);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Service layer
class TaskService {
  constructor(private repository: TaskRepository) {}

  async create(data: CreateTaskDto): Promise<Task> {
    this.validate(data);
    return this.repository.save(data);
  }
}
```
*Proper separation of concerns added during refactor phase.*

### Example 3: Database Integration (Django)

**Test Requirements:**
```python
def test_product_creation():
    product = Product.objects.create(name="Widget", price=9.99)
    assert product.id is not None
    assert product.name == "Widget"

def test_product_price_validation():
    with pytest.raises(ValidationError):
        Product.objects.create(name="Widget", price=-1)
```

**Stage 1: Model Only**
```python
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
```
*First test passes. Second test fails - validation not implemented.*

**Stage 2: Add Validation**
```python
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        if self.price < 0:
            raise ValidationError("Price cannot be negative")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
```
*All tests pass. Minimal validation logic added.*

**Stage 3: Rich Domain Model (Refactor)**
```python
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=['category', '-created_at'])]

    def clean(self):
        if self.price < 0:
            raise ValidationError("Price cannot be negative")
        if self.price > 10000:
            raise ValidationError("Price exceeds maximum")

    def apply_discount(self, percentage: float) -> Decimal:
        return self.price * (1 - percentage / 100)
```
*Additional features, indexes, business logic added when needed.*

### Example 4: React Component Implementation

**Test Requirements:**
```typescript
describe('UserProfile', () => {
  it('should display user name', () => {
    render(<UserProfile user={{ name: 'John', email: 'john@test.com' }} />);
    expect(screen.getByText('John')).toBeInTheDocument();
  });

  it('should display email', () => {
    render(<UserProfile user={{ name: 'John', email: 'john@test.com' }} />);
    expect(screen.getByText('john@test.com')).toBeInTheDocument();
  });
});
```

**Stage 1: Minimal JSX**
```typescript
interface UserProfileProps {
  user: { name: string; email: string };
}

const UserProfile: React.FC<UserProfileProps> = ({ user }) => (
  <div>
    <div>{user.name}</div>
    <div>{user.email}</div>
  </div>
);
```
*Tests pass. No styling, no structure.*

**Stage 2: Basic Structure**
```typescript
const UserProfile: React.FC<UserProfileProps> = ({ user }) => (
  <div className="user-profile">
    <h2>{user.name}</h2>
    <p>{user.email}</p>
  </div>
);
```
*Added semantic HTML, className for styling hook.*

**Stage 3: Production Component (Refactor)**
```typescript
const UserProfile: React.FC<UserProfileProps> = ({ user }) => {
  const [isEditing, setIsEditing] = useState(false);

  return (
    <div className="user-profile" role="article" aria-label="User profile">
      <header>
        <h2>{user.name}</h2>
        <button onClick={() => setIsEditing(true)} aria-label="Edit profile">
          Edit
        </button>
      </header>
      <section>
        <p>{user.email}</p>
        {user.bio && <p>{user.bio}</p>}
      </section>
    </div>
  );
};
```
*Accessibility, interaction, additional features added incrementally.*

## Decision Frameworks

### Framework 1: Fake vs. Real Implementation

**When to Fake It:**
- First test for a new feature
- Complex external dependencies (payment gateways, APIs)
- Implementation approach is still uncertain
- Need to validate test structure first
- Time pressure to see all tests green

**When to Go Real:**
- Second or third test reveals pattern
- Implementation is obvious and simple
- Faking would be more complex than real code
- Need to test integration points
- Tests explicitly require real behavior

**Decision Matrix:**
```
Complexity Low     | High
         ↓         | ↓
Simple   → REAL    | FAKE first, real later
Complex  → REAL    | FAKE, evaluate alternatives
```

### Framework 2: Complexity Trade-off Analysis

**Simplicity Score Calculation:**
```
Score = (Lines of Code) + (Cyclomatic Complexity × 2) + (Dependencies × 3)

< 20  → Simple enough, implement directly
20-50 → Consider simpler alternative
> 50  → Defer complexity to refactor phase
```

**Example Evaluation:**
```typescript
// Option A: Direct implementation (Score: 45)
function calculateShipping(weight: number, distance: number, express: boolean): number {
  let base = weight * 0.5 + distance * 0.1;
  if (express) base *= 2;
  if (weight > 50) base += 10;
  if (distance > 1000) base += 20;
  return base;
}

// Option B: Simplest for green phase (Score: 15)
function calculateShipping(weight: number, distance: number, express: boolean): number {
  return express ? 50 : 25; // Fake it until more tests drive real logic
}
```
*Choose Option B for green phase, evolve to Option A as tests require.*

### Framework 3: Performance Consideration Timing

**Green Phase: Focus on Correctness**
```
❌ Avoid:
- Caching strategies
- Database query optimization
- Algorithmic complexity improvements
- Premature memory optimization

✓ Accept:
- O(n²) if it makes code simpler
- Multiple database queries
- Synchronous operations
- Inefficient but clear algorithms
```

**When Performance Matters in Green Phase:**
1. Performance is explicit test requirement
2. Implementation would cause timeout in test suite
3. Memory leak would crash tests
4. Resource exhaustion prevents testing

**Performance Testing Integration:**
```typescript
// Add performance test AFTER functional tests pass
describe('Performance', () => {
  it('should handle 1000 users within 100ms', () => {
    const start = Date.now();
    for (let i = 0; i < 1000; i++) {
      userService.create({ email: `user${i}@test.com`, name: `User ${i}` });
    }
    expect(Date.now() - start).toBeLessThan(100);
  });
});
```

## Framework-Specific Patterns

### React Patterns

**Simple Component → Hooks → Context:**
```typescript
// Green Phase: Props only
const Counter = ({ count, onIncrement }) => (
  <button onClick={onIncrement}>{count}</button>
);

// Refactor: Add hooks
const Counter = () => {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
};

// Refactor: Extract to context
const Counter = () => {
  const { count, increment } = useCounter();
  return <button onClick={increment}>{count}</button>;
};
```

### Django Patterns

**Function View → Class View → Generic View:**
```python
# Green Phase: Simple function
def product_list(request):
    products = Product.objects.all()
    return JsonResponse({'products': list(products.values())})

# Refactor: Class-based view
class ProductListView(View):
    def get(self, request):
        products = Product.objects.all()
        return JsonResponse({'products': list(products.values())})

# Refactor: Generic view
class ProductListView(ListView):
    model = Product
    context_object_name = 'products'
```

### Express Patterns

**Inline → Middleware → Service Layer:**
```javascript
// Green Phase: Inline logic
app.post('/api/users', (req, res) => {
  const user = { id: Date.now(), ...req.body };
  users.push(user);
  res.json(user);
});

// Refactor: Extract middleware
app.post('/api/users', validateUser, (req, res) => {
  const user = userService.create(req.body);
  res.json(user);
});

// Refactor: Full layering
app.post('/api/users',
  validateUser,
  asyncHandler(userController.create)
);
```

## Refactoring Resistance Patterns

### Pattern 1: Test Anchor Points

Keep tests green during refactoring by maintaining interface contracts:

```typescript
// Original implementation (tests green)
function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// Refactoring: Add tax calculation (keep interface)
function calculateTotal(items: Item[]): number {
  const subtotal = items.reduce((sum, item) => sum + item.price, 0);
  const tax = subtotal * 0.1;
  return subtotal + tax;
}

// Tests still green because return type/behavior unchanged
```

### Pattern 2: Parallel Implementation

Run old and new implementations side by side:

```python
def process_order(order):
    # Old implementation (tests depend on this)
    result_old = legacy_process(order)

    # New implementation (testing in parallel)
    result_new = new_process(order)

    # Verify they match
    assert result_old == result_new, "Implementation mismatch"

    return result_old  # Keep tests green
```

### Pattern 3: Feature Flags for Refactoring

```javascript
class PaymentService {
  processPayment(amount) {
    if (config.USE_NEW_PAYMENT_PROCESSOR) {
      return this.newPaymentProcessor(amount);
    }
    return this.legacyPaymentProcessor(amount);
  }
}
```

## Performance-First Green Phase Strategies

### Strategy 1: Type-Driven Development

Use types to guide minimal implementation:

```typescript
// Types define contract
interface UserRepository {
  findById(id: string): Promise<User | null>;
  save(user: User): Promise<void>;
}

// Green phase: In-memory implementation
class InMemoryUserRepository implements UserRepository {
  private users = new Map<string, User>();

  async findById(id: string) {
    return this.users.get(id) || null;
  }

  async save(user: User) {
    this.users.set(user.id, user);
  }
}

// Refactor: Database implementation (same interface)
class DatabaseUserRepository implements UserRepository {
  constructor(private db: Database) {}

  async findById(id: string) {
    return this.db.query('SELECT * FROM users WHERE id = ?', [id]);
  }

  async save(user: User) {
    await this.db.insert('users', user);
  }
}
```

### Strategy 2: Contract Testing Integration

```typescript
// Define contract
const userServiceContract = {
  create: {
    input: { email: 'string', name: 'string' },
    output: { id: 'string', email: 'string', name: 'string' }
  }
};

// Green phase: Implementation matches contract
class UserService {
  create(data: { email: string; name: string }) {
    return { id: '123', ...data }; // Minimal but contract-compliant
  }
}

// Contract test ensures compliance
describe('UserService Contract', () => {
  it('should match create contract', () => {
    const result = userService.create({ email: 'test@test.com', name: 'Test' });
    expect(typeof result.id).toBe('string');
    expect(typeof result.email).toBe('string');
    expect(typeof result.name).toBe('string');
  });
});
```

### Strategy 3: Continuous Refactoring Workflow

**Micro-Refactoring During Green Phase:**

```python
# Test passes with this
def calculate_discount(price, customer_type):
    if customer_type == 'premium':
        return price * 0.8
    return price

# Immediate micro-refactor (tests still green)
DISCOUNT_RATES = {
    'premium': 0.8,
    'standard': 1.0
}

def calculate_discount(price, customer_type):
    rate = DISCOUNT_RATES.get(customer_type, 1.0)
    return price * rate
```

**Safe Refactoring Checklist:**
- ✓ Tests green before refactoring
- ✓ Change one thing at a time
- ✓ Run tests after each change
- ✓ Commit after each successful refactor
- ✓ No behavior changes, only structure

## Modern Development Practices (2024/2025)

### Type-Driven Development

**Python Type Hints:**
```python
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class User:
    id: str
    email: str
    name: str

class UserService:
    def create(self, email: str, name: str) -> User:
        return User(id="123", email=email, name=name)

    def find_by_email(self, email: str) -> Optional[User]:
        return None  # Minimal implementation
```

**TypeScript Strict Mode:**
```typescript
// Enable strict mode in tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}

// Implementation guided by types
interface CreateUserDto {
  email: string;
  name: string;
}

class UserService {
  create(data: CreateUserDto): User {
    // Type system enforces contract
    return { id: '123', email: data.email, name: data.name };
  }
}
```

### AI-Assisted Green Phase

**Using Copilot/AI Tools:**
1. Write test first (human-driven)
2. Let AI suggest minimal implementation
3. Verify suggestion passes tests
4. Accept if truly minimal, reject if over-engineered
5. Iterate with AI for refactoring phase

**AI Prompt Pattern:**
```
Given these failing tests:
[paste tests]

Provide the MINIMAL implementation that makes tests pass.
Do not add error handling, validation, or features beyond test requirements.
Focus on simplicity over completeness.
```

### Cloud-Native Patterns

**Local → Container → Cloud:**
```javascript
// Green Phase: Local implementation
class CacheService {
  private cache = new Map();

  get(key) { return this.cache.get(key); }
  set(key, value) { this.cache.set(key, value); }
}

// Refactor: Redis-compatible interface
class CacheService {
  constructor(private redis) {}

  async get(key) { return this.redis.get(key); }
  async set(key, value) { return this.redis.set(key, value); }
}

// Production: Distributed cache with fallback
class CacheService {
  constructor(private redis, private fallback) {}

  async get(key) {
    try {
      return await this.redis.get(key);
    } catch {
      return this.fallback.get(key);
    }
  }
}
```

### Observability-Driven Development

**Add observability hooks during green phase:**
```typescript
class OrderService {
  async createOrder(data: CreateOrderDto): Promise<Order> {
    console.log('[OrderService] Creating order', { data }); // Simple logging

    const order = { id: '123', ...data };

    console.log('[OrderService] Order created', { orderId: order.id }); // Success log

    return order;
  }
}

// Refactor: Structured logging
class OrderService {
  constructor(private logger: Logger) {}

  async createOrder(data: CreateOrderDto): Promise<Order> {
    this.logger.info('order.create.start', { data });

    const order = await this.repository.save(data);

    this.logger.info('order.create.success', {
      orderId: order.id,
      duration: Date.now() - start
    });

    return order;
  }
}
```

Tests to make pass: $ARGUMENTS

## Phase 4: REFACTOR - Improve Code Quality

### 11. Code Refactoring
- Use Task tool with subagent_type="codebase-cleanup::code-reviewer"
- Prompt: "Refactor implementation for: $ARGUMENTS while keeping tests green. Apply SOLID principles, remove duplication, improve naming, and optimize performance. Run tests after each refactoring."
- Output: Refactored code, refactoring report
- Constraint: Tests must remain green throughout

### 12. Test Refactoring
- Use Task tool with subagent_type="backend-development::test-automator"
- Prompt: "Refactor tests for: $ARGUMENTS. Remove test duplication, improve test names, extract common fixtures, and enhance test readability. Ensure tests still provide same coverage."
- Output: Refactored tests, improved test structure
- Validation: Coverage metrics unchanged or improved

## Core Process

**1. Pre-Assessment**
- Run tests to establish green baseline
- Analyze code smells and test coverage
- Document current performance metrics
- Create incremental refactoring plan

**2. Code Smell Detection**
- Duplicated code → Extract methods/classes
- Long methods → Decompose into focused functions
- Large classes → Split responsibilities
- Long parameter lists → Parameter objects
- Feature Envy → Move methods to appropriate classes
- Primitive Obsession → Value objects
- Switch statements → Polymorphism
- Dead code → Remove

**3. Design Patterns**
- Apply Creational (Factory, Builder, Singleton)
- Apply Structural (Adapter, Facade, Decorator)
- Apply Behavioral (Strategy, Observer, Command)
- Apply Domain (Repository, Service, Value Objects)
- Use patterns only where they add clear value

**4. SOLID Principles**
- Single Responsibility: One reason to change
- Open/Closed: Open for extension, closed for modification
- Liskov Substitution: Subtypes substitutable
- Interface Segregation: Small, focused interfaces
- Dependency Inversion: Depend on abstractions

**5. Refactoring Techniques**
- Extract Method/Variable/Interface
- Inline unnecessary indirection
- Rename for clarity
- Move Method/Field to appropriate classes
- Replace Magic Numbers with constants
- Encapsulate fields
- Replace Conditional with Polymorphism
- Introduce Null Object

**6. Performance Optimization**
- Profile to identify bottlenecks
- Optimize algorithms and data structures
- Implement caching where beneficial
- Reduce database queries (N+1 elimination)
- Lazy loading and pagination
- Always measure before and after

**7. Incremental Steps**
- Make small, atomic changes
- Run tests after each modification
- Commit after each successful refactoring
- Keep refactoring separate from behavior changes
- Use scaffolding when needed

**8. Architecture Evolution**
- Layer separation and dependency management
- Module boundaries and interface definition
- Event-driven patterns for decoupling
- Database access pattern optimization

**9. Safety Verification**
- Run full test suite after each change
- Performance regression testing
- Mutation testing for test effectiveness
- Rollback plan for major changes

**10. Advanced Patterns**
- Strangler Fig: Gradual legacy replacement
- Branch by Abstraction: Large-scale changes
- Parallel Change: Expand-contract pattern
- Mikado Method: Dependency graph navigation

## Output Requirements

- Refactored code with improvements applied
- Test results (all green)
- Before/after metrics comparison
- Applied refactoring techniques list
- Performance improvement measurements
- Remaining technical debt assessment

## Safety Checklist

Before committing:
- ✓ All tests pass (100% green)
- ✓ No functionality regression
- ✓ Performance metrics acceptable
- ✓ Code coverage maintained/improved
- ✓ Documentation updated

## Recovery Protocol

If tests fail:
- Immediately revert last change
- Identify breaking refactoring
- Apply smaller incremental changes
- Use version control for safe experimentation

## Example: Extract Method Pattern

**Before:**
```typescript
class OrderProcessor {
  processOrder(order: Order): ProcessResult {
    // Validation
    if (!order.customerId || order.items.length === 0) {
      return { success: false, error: "Invalid order" };
    }

    // Calculate totals
    let subtotal = 0;
    for (const item of order.items) {
      subtotal += item.price * item.quantity;
    }
    let total = subtotal + (subtotal * 0.08) + (subtotal > 100 ? 0 : 15);

    // Process payment...
    // Update inventory...
    // Send confirmation...
  }
}
```

**After:**
```typescript
class OrderProcessor {
  async processOrder(order: Order): Promise<ProcessResult> {
    const validation = this.validateOrder(order);
    if (!validation.isValid) return ProcessResult.failure(validation.error);

    const orderTotal = OrderTotal.calculate(order);
    const inventoryCheck = await this.inventoryService.checkAvailability(order.items);
    if (!inventoryCheck.available) return ProcessResult.failure(inventoryCheck.reason);

    await this.paymentService.processPayment(order.paymentMethod, orderTotal.total);
    await this.inventoryService.reserveItems(order.items);
    await this.notificationService.sendOrderConfirmation(order, orderTotal);

    return ProcessResult.success(order.id, orderTotal.total);
  }

  private validateOrder(order: Order): ValidationResult {
    if (!order.customerId) return ValidationResult.invalid("Customer ID required");
    if (order.items.length === 0) return ValidationResult.invalid("Order must contain items");
    return ValidationResult.valid();
  }
}
```

**Applied:** Extract Method, Value Objects, Dependency Injection, Async patterns

Code to refactor: $ARGUMENTS"

## Phase 5: Integration and System Tests

### 13. Write Integration Tests (Failing First)
- Use Task tool with subagent_type="backend-development::test-automator"
- Prompt: "Write FAILING integration tests for: $ARGUMENTS. Test component interactions, API contracts, and data flow. Tests must fail initially."
- Output: Failing integration tests
- Validation: Tests fail due to missing integration logic

### 14. Implement Integration
- Use Task tool with subagent_type="backend-development::backend-architect"
- Prompt: "Implement integration code for: $ARGUMENTS to make integration tests pass. Focus on component interaction and data flow."
- Output: Integration implementation
- Validation: All integration tests pass

## Phase 6: Continuous Improvement Cycle

### 15. Performance and Edge Case Tests
- Use Task tool with subagent_type="backend-development::test-automator"
- Prompt: "Add performance tests and additional edge case tests for: $ARGUMENTS. Include stress tests, boundary tests, and error recovery tests."
- Output: Extended test suite
- Metric: Increased test coverage and scenario coverage

### 12. Final Code Review
- Use Task tool with subagent_type="backend-development::architect-review"
- Prompt: "Perform comprehensive review of: $ARGUMENTS. Verify TDD process was followed, check code quality, test quality, and coverage. Suggest improvements."
- Output: Review report, improvement suggestions
- Action: Implement critical suggestions while maintaining green tests

## Incremental Development Mode

For test-by-test development:
1. Write ONE failing test
2. Make ONLY that test pass
3. Refactor if needed
4. Repeat for next test

Use this approach by adding `--incremental` flag to focus on one test at a time.

## Test Suite Mode

For comprehensive test suite development:
1. Write ALL tests for a feature/module (failing)
2. Implement code to pass ALL tests
3. Refactor entire module
4. Add integration tests

Use this approach by adding `--suite` flag for batch test development.

## Validation Checkpoints

### RED Phase Validation
- [ ] All tests written before implementation
- [ ] All tests fail with meaningful error messages
- [ ] Test failures are due to missing implementation
- [ ] No implementation leakage
- [ ] One behavior per test
- [ ] Meaningful test data (not 'foo'/'bar')
- [ ] No test passes accidentally

### GREEN Phase Validation
- [ ] All tests pass
- [ ] No extra code beyond test requirements
- [ ] Coverage meets minimum thresholds
- [ ] No test was modified to make it pass

### REFACTOR Phase Validation
- [ ] All tests still pass after refactoring
- [ ] Code complexity reduced
- [ ] Duplication eliminated
- [ ] Performance improved or maintained
- [ ] Test readability improved

## Coverage Reports

Generate coverage reports after each phase:
- Line coverage
- Branch coverage
- Function coverage
- Statement coverage

## Failure Recovery

If TDD discipline is broken:
1. **STOP** immediately
2. Identify which phase was violated
3. Rollback to last valid state
4. Resume from correct phase
5. Document lesson learned

## TDD Metrics Tracking

Track and report:
- Time in each phase (Red/Green/Refactor)
- Number of test-implementation cycles
- Coverage progression
- Refactoring frequency
- Defect escape rate

## Anti-Patterns to Avoid

- Writing implementation before tests
- Writing tests that already pass
- Skipping the refactor phase
- Writing multiple features without tests
- Modifying tests to make them pass
- Ignoring failing tests
- Writing tests after implementation
- Multiple responsibilities per test
- Brittle tests tied to specifics

## Edge Case Categories

- **Null/Empty**: undefined, null, empty string/array/object
- **Boundaries**: min/max values, single element, capacity limits
- **Special Cases**: Unicode, whitespace, special characters
- **State**: Invalid transitions, concurrent modifications
- **Errors**: Network failures, timeouts, permissions

## Success Criteria

- 100% of code written test-first
- All tests pass continuously
- Coverage exceeds thresholds
- Code complexity within limits
- Zero defects in covered code
- Clear test documentation
- Fast test execution (< 5 seconds for unit tests)

## Notes

- Enforce strict RED-GREEN-REFACTOR discipline
- Each phase must be completed before moving to next
- Tests are the specification
- If a test is hard to write, the design needs improvement
- Refactoring is NOT optional
- Keep test execution fast
- Tests should be independent and isolated

TDD implementation for: $ARGUMENTS