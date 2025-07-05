# Testing Vanilla JS & Alpine.js: The Smart Way

## The Problem with Vanilla JS Testing

Most developers think you can't easily test vanilla JavaScript or Alpine.js apps. They're wrong! The key is **extracting logic from the DOM**.

## Vanilla JavaScript Testing Strategy

### ❌ Hard to Test (Everything Mixed Together)
```javascript
// All in one file, mixed with DOM
document.getElementById('submit').addEventListener('click', async function() {
  const name = document.getElementById('name').value;
  if (!name.trim()) {
    alert('Name required!');
    return;
  }
  // ... complex validation and API calls mixed with DOM
});
```

### ✅ Easy to Test (Separated Concerns)
```javascript
// src/user-manager.js - Pure logic, no DOM
export class UserManager {
  validateUser(userData) {
    const errors = [];
    if (!userData.name?.trim()) errors.push('Name required');
    return { isValid: errors.length === 0, errors };
  }
  
  async saveUser(userData) {
    // API logic without DOM dependencies
  }
}

// main.js - DOM handling only
import { UserManager } from './src/user-manager.js';
const manager = new UserManager();

document.getElementById('submit').addEventListener('click', async function() {
  const userData = { name: document.getElementById('name').value };
  
  // Use testable function
  const validation = manager.validateUser(userData);
  if (!validation.isValid) {
    showErrors(validation.errors);
    return;
  }
  
  await manager.saveUser(userData);
});
```

## Alpine.js Testing Strategy

Alpine.js is actually **easier to test** than vanilla JS because Alpine encourages separating data from templates.

### ❌ Hard to Test (Logic in Alpine Directives)
```html
<div x-data="{
  name: '',
  async saveUser() {
    if (!this.name.trim()) {
      alert('Name required');
      return;
    }
    // Complex logic in template - can't test
  }
}">
```

### ✅ Easy to Test (Extract to Stores)
```javascript
// src/user-store.js - Testable Alpine store
export function createUserStore() {
  return {
    name: '',
    
    validateForm() {
      const errors = [];
      if (!this.name.trim()) errors.push('Name required');
      return { isValid: errors.length === 0, errors };
    },
    
    async saveUser() {
      const validation = this.validateForm();
      if (!validation.isValid) {
        this.error = validation.errors.join(', ');
        return false;
      }
      // ... API logic
    }
  };
}

// app.js
import { createUserStore } from './src/user-store.js';
Alpine.store('users', createUserStore());
```

```html
<!-- Template just calls store methods -->
<div x-data>
  <input x-model="$store.users.name">
  <button @click="$store.users.saveUser()">Save</button>
</div>
```

## What to Extract and Test

### 1. **Validation Logic** (High Priority)
```javascript
// Testable
validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Test
expect(manager.validateEmail('test@example.com')).toBe(true);
expect(manager.validateEmail('invalid')).toBe(false);
```

### 2. **Data Transformation** (High Priority)
```javascript
// Testable  
formatUserName(name) {
  return name.trim().split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

// Test
expect(manager.formatUserName('john doe')).toBe('John Doe');
```

### 3. **API Calls** (High Priority)
```javascript
// Testable
async fetchUsers() {
  const response = await fetch('/api/users');
  if (!response.ok) throw new Error('Failed to fetch');
  return response.json();
}

// Test (with mocked fetch)
fetch.mockResolvedValueOnce({
  ok: true,
  json: async () => [{ id: 1, name: 'John' }]
});

const users = await manager.fetchUsers();
expect(users).toEqual([{ id: 1, name: 'John' }]);
```

### 4. **Business Logic** (High Priority)
```javascript
// Testable
calculateTotal(items) {
  return items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
}

// Test
const items = [{ price: 10, quantity: 2 }, { price: 5, quantity: 3 }];
expect(manager.calculateTotal(items)).toBe(35);
```

### 5. **HTML Generation** (Medium Priority)
```javascript
// Testable
createUserHTML(user) {
  return `<div class="user">${this.escapeHTML(user.name)}</div>`;
}

// Test
const html = manager.createUserHTML({ name: 'John<script>' });
expect(html).not.toContain('<script>');
expect(html).toContain('John&lt;script&gt;');
```

## Testing Setup

### 1. Install Tools
```bash
npm install --save-dev vitest jsdom
```

### 2. Configure Vitest
```javascript
// vite.config.js
export default {
  test: {
    environment: 'jsdom',
    globals: true
  }
}
```

### 3. Mock Global Objects
```javascript
// In your tests
global.fetch = vi.fn();
global.window = { location: { origin: 'http://test' } };
```

## Testing Patterns

### Mock Fetch for API Tests
```javascript
test('should save user', async () => {
  fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({ id: 1, name: 'John' })
  });
  
  const result = await manager.saveUser({ name: 'John' });
  expect(result.id).toBe(1);
});
```

### Test Alpine Store Methods
```javascript
test('Alpine store validation', () => {
  const store = createUserStore();
  store.name = 'John Doe';
  
  const result = store.validateForm();
  expect(result.isValid).toBe(true);
});
```

### Test Error Handling
```javascript
test('should handle API errors', async () => {
  fetch.mockRejectedValueOnce(new Error('Network error'));
  
  await expect(manager.fetchUsers()).rejects.toThrow('Network error');
});
```

## Key Benefits

| ✅ With Extracted Logic | ❌ Without Extraction |
|-------------------------|----------------------|
| Fast unit tests | Only slow E2E tests |
| Easy debugging | Hard to isolate issues |
| Reliable tests | Flaky browser tests |
| Test-driven development | Manual testing only |
| Refactoring confidence | Fear of changes |

## Quick Start Checklist

1. ✅ **Extract validation** from form handlers
2. ✅ **Extract API calls** from event listeners  
3. ✅ **Extract data formatting** from display logic
4. ✅ **Create testable modules** (ES6 imports/exports)
5. ✅ **Mock external dependencies** (fetch, localStorage)
6. ✅ **Write focused unit tests** for each function
7. ✅ **Use integration tests** sparingly for workflows

## The Bottom Line

**Vanilla JS and Alpine.js are just as testable as React or Vue** - you just need to separate your concerns properly. Extract logic from the DOM, mock dependencies, and test your functions directly.

This approach gives you:
- ⚡ **Fast tests** (milliseconds, not seconds)
- 🎯 **Focused tests** (test specific functions)
- 🔧 **Easy debugging** (clear stack traces)
- 💯 **High confidence** (catch bugs before users do)

The secret is thinking of your JavaScript as **modules with functions**, not as **scripts that manipulate the DOM**.