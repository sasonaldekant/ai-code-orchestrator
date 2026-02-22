# ValidationEngine - AI/RAG Optimized Guide

## Document Metadata

- **Document Type**: Technical Implementation Guide
- **Version**: 1.2-RAG
- **Date**: 2026-02-21
- **Status**: Production Ready
- **Purpose**: Complete validation system reference for AI agents
- **Related**: 01-ARCHITECTURE-RAG.md, 05-LAYOUT-STANDARDS-RAG.md

---

## Overview

### Purpose

ValidationEngine provides centralized field and form validation with declarative JSON rules, built-in validators, custom validators, and cross-field validation support.

### Key Features

- Declarative validation via JSON schema
- 8+ built-in validators (required, pattern, email, phone, etc.)
- Custom validator registration system
- Serbian-specific validators (JMBG, PIB)
- Cross-field validation support
- Localized error messages
- Type-safe TypeScript implementation

---

## Core API

### ValidationEngine Class

**Location**: `src/core/ValidationEngine.ts`

```typescript
class ValidationEngine {
  // Validate single field
  validateField(value: any, rules: ValidationRules): ValidationResult;

  // Register custom validator
  registerCustomValidator(name: string, fn: ValidatorFunction): void;
}

interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

interface ValidationRules {
  required?: boolean;
  pattern?: string; // Regex pattern
  minLength?: number;
  maxLength?: number;
  min?: number; // For numbers
  max?: number; // For numbers
  email?: boolean;
  phone?: boolean;
  errorMessage?: string; // Custom message
  custom?: {
    rule: string; // Custom validator name
    errorMessage: string;
  };
}
```

### Usage Example

```typescript
import { ValidationEngine } from './core/ValidationEngine';

const engine = new ValidationEngine();

// Validate email field
const result = engine.validateField('user@example.com', {
  required: true,
  email: true,
  errorMessage: 'Valid email required',
});

if (!result.isValid) {
  console.error('Errors:', result.errors);
}
```

---

## Built-in Validators

### 1. Required Validator

**Purpose**: Ensures field has a value
**JSON Definition**:

```json
{
  "id": "name",
  "validation": {
    "required": true,
    "errorMessage": "Name is required"
  }
}
```

**Validation Logic**:

- Empty strings → Invalid
- null/undefined → Invalid
- Empty arrays → Invalid
- All other values → Valid

---

### 2. Pattern Validator (Regex)

**Purpose**: Regex pattern matching
**JSON Definition**:

```json
{
  "id": "jmbg",
  "validation": {
    "pattern": "^[0-9]{13}$",
    "errorMessage": "JMBG must be exactly 13 digits"
  }
}
```

**Common Patterns**:

```typescript
// Serbian JMBG (13 digits)
'^[0-9]{13}$';

// Serbian PIB (9 digits)
'^[0-9]{9}$';

// Letters only (including Serbian characters)
'^[a-žA-Ž\\s-]+$';

// Postal code (5 digits)
'^[0-9]{5}$';

// Alphanumeric
'^[a-zA-Z0-9]+$';
```

---

### 3. String Length Validators

**Purpose**: Min/max string length constraints
**JSON Definition**:

```json
{
  "id": "firstName",
  "validation": {
    "minLength": 2,
    "maxLength": 50,
    "errorMessage": "Name must be between 2 and 50 characters"
  }
}
```

**Validation Logic**:

- Counts actual string length
- Applies to string values only
- Ignored for non-string types

---

### 4. Numeric Range Validators

**Purpose**: Min/max numeric value constraints
**JSON Definition**:

```json
{
  "id": "age",
  "type": "number",
  "validation": {
    "min": 18,
    "max": 100,
    "errorMessage": "Age must be between 18 and 100"
  }
}
```

**Validation Logic**:

- Converts value to number
- Checks numeric range
- NaN values fail validation

---

### 5. Email Validator

**Purpose**: Email format validation
**JSON Definition**:

```json
{
  "id": "email",
  "type": "email",
  "validation": {
    "required": true,
    "email": true,
    "errorMessage": "Enter a valid email address"
  }
}
```

**Regex Pattern**: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`

**Validation Logic**:

- Checks for @ symbol
- Requires domain with extension
- Rejects whitespace

---

### 6. Phone Validator

**Purpose**: Phone number format validation (Serbian and international)
**JSON Definition**:

```json
{
  "id": "phone",
  "type": "tel",
  "validation": {
    "phone": true,
    "errorMessage": "Enter a valid phone number"
  }
}
```

**Supported Formats**:

```
0611234567              # Serbian mobile
+381611234567           # International format
011 123 4567            # Serbian landline with spaces
(011) 123-4567          # With parentheses and dash
```

---

## Custom Validators

### Serbian JMBG Validator

**Purpose**: Validates Serbian national ID with checksum
**Usage**:

```json
{
  "id": "jmbg",
  "validation": {
    "custom": {
      "rule": "jmbgChecksum",
      "errorMessage": "Invalid JMBG checksum"
    }
  }
}
```

**Validation Logic**:

1. Checks 13-digit format
2. Calculates checksum using algorithm
3. Verifies last digit matches checksum

---

### Serbian PIB Validator

**Purpose**: Validates Serbian tax ID with checksum
**Usage**:

```json
{
  "id": "pib",
  "validation": {
    "custom": {
      "rule": "pibChecksum",
      "errorMessage": "Invalid PIB checksum"
    }
  }
}
```

**Validation Logic**:

1. Checks 9-digit format
2. Calculates checksum using algorithm
3. Verifies last digit matches checksum

---

### Registering Custom Validators

```typescript
import { ValidationEngine } from './core/ValidationEngine';

const engine = new ValidationEngine();

// Register custom validator
engine.registerCustomValidator('strongPassword', (value: string) => {
  const hasUpper = /[A-Z]/.test(value);
  const hasLower = /[a-z]/.test(value);
  const hasNumber = /[0-9]/.test(value);
  const hasSpecial = /[!@#$%^&*]/.test(value);

  return hasUpper && hasLower && hasNumber && hasSpecial;
});
```

**Use in Schema**:

```json
{
  "id": "password",
  "validation": {
    "custom": {
      "rule": "strongPassword",
      "errorMessage": "Password must contain uppercase, lowercase, number, and special character"
    }
  }
}
```

---

## Validation Timing

### Configuration

```json
{
  "id": "email",
  "validation": {
    "email": true,
    "validateOn": "blur" // "blur" | "change" | "submit"
  }
}
```

### Options

| Value    | Description                      | Use Case             |
| -------- | -------------------------------- | -------------------- |
| `blur`   | Validates when field loses focus | **Default**, best UX |
| `change` | Validates on every keystroke     | Real-time feedback   |
| `submit` | Validates only on form submit    | Minimal interruption |

---

## Cross-Field Validation

### Concept

Validate relationships between multiple fields (e.g., "End Date must be after Start Date").

### JSON Definition

```json
{
  "logic": {
    "crossFieldValidation": [
      {
        "id": "date-range",
        "rule": {
          "field": "endDate",
          "operator": "greaterThan",
          "compareWith": "startDate"
        },
        "errorMessage": "End date must be after start date",
        "targetFields": ["endDate"]
      }
    ]
  }
}
```

### Supported Operators

- `greaterThan` / `lessThan` - Numeric/date comparison
- `equals` / `notEquals` - Equality check
- `contains` - String contains substring

---

## Error Handling

### Error Message Priority

1. **Custom `errorMessage`** in validation rule (highest priority)
2. **Default validator message** (built-in)
3. **Generic error message** (fallback)

### Error Message Examples

```json
{
  "validation": {
    "required": true,
    "minLength": 2,
    "errorMessage": "Name must be at least 2 characters" // Custom message
  }
}
```

Without custom message:

```
"This field is required"              // Default for required
"Minimum length is 2 characters"      // Default for minLength
```

---

## Validation Result Structure

```typescript
interface ValidationResult {
  isValid: boolean;           // Overall validation status
  errors: string[];           // Array of error messages
}

// Example result
{
  isValid: false,
  errors: [
    "Email is required",
    "Enter a valid email address"
  ]
}
```

---

## Integration with FormEngine

### Automatic Validation

FormEngine automatically validates fields using ValidationEngine:

```typescript
// User blurs field
handleFieldBlur(fieldId) {
  const field = schema.sections
    .flatMap(s => s.fields)
    .find(f => f.id === fieldId);

  if (field?.validation) {
    const result = validationEngine.validateField(
      formData[fieldId],
      field.validation
    );

    if (!result.isValid) {
      setErrors(prev => ({
        ...prev,
        [fieldId]: result.errors[0]
      }));
    }
  }
}
```

### Submit Validation

```typescript
handleSubmit(e) {
  e.preventDefault();

  const allFields = schema.sections.flatMap(s => s.fields);
  const newErrors = {};

  allFields.forEach(field => {
    if (field.validation) {
      const result = validationEngine.validateField(
        formData[field.id],
        field.validation
      );

      if (!result.isValid) {
        newErrors[field.id] = result.errors[0];
      }
    }
  });

  if (Object.keys(newErrors).length === 0) {
    onSubmit(formData);  // Valid, proceed
  } else {
    setErrors(newErrors);  // Show errors
  }
}
```

---

## Best Practices

### 1. Always Provide Error Messages

✅ **Good**:

```json
{
  "validation": {
    "required": true,
    "errorMessage": "Email address is required"
  }
}
```

❌ **Bad**:

```json
{
  "validation": {
    "required": true // Uses generic message
  }
}
```

### 2. Combine Validators

```json
{
  "validation": {
    "required": true,
    "email": true,
    "maxLength": 100,
    "errorMessage": "Enter a valid email (max 100 characters)"
  }
}
```

### 3. Use Appropriate Field Types

```json
// Email field
{ "id": "email", "type": "email", "validation": { "email": true } }

// Phone field
{ "id": "phone", "type": "tel", "validation": { "phone": true } }

// Number field
{ "id": "age", "type": "number", "validation": { "min": 18 } }
```

### 4. Validate on Blur (Default)

```json
{
  "validation": {
    "email": true,
    "validateOn": "blur" // Best UX - validates after user finishes
  }
}
```

### 5. Client + Server Validation

**Critical**: Client-side validation is for UX only.

- Always re-validate on server
- Never trust client-submitted data
- Use same validation rules on both sides

---

## Common Validation Patterns

### Required Text Field with Length

```json
{
  "id": "firstName",
  "type": "text",
  "label": "First Name",
  "validation": {
    "required": true,
    "minLength": 2,
    "maxLength": 50,
    "pattern": "^[a-žA-Ž\\s-]+$",
    "errorMessage": "Name must be 2-50 letters only"
  }
}
```

### Email with Required

```json
{
  "id": "email",
  "type": "email",
  "label": "Email",
  "validation": {
    "required": true,
    "email": true,
    "errorMessage": "Valid email is required"
  }
}
```

### Numeric Range

```json
{
  "id": "age",
  "type": "number",
  "label": "Age",
  "validation": {
    "required": true,
    "min": 18,
    "max": 100,
    "errorMessage": "Age must be between 18 and 100"
  }
}
```

### Serbian JMBG

```json
{
  "id": "jmbg",
  "type": "text",
  "label": "JMBG",
  "validation": {
    "required": true,
    "pattern": "^[0-9]{13}$",
    "custom": {
      "rule": "jmbgChecksum",
      "errorMessage": "Invalid JMBG"
    }
  }
}
```

---

## Testing

### Unit Test Coverage

**File**: `tests/ValidationEngine.test.ts` (9KB)
**Coverage**: 95%

**Test Cases**:

- ✅ Required validation (empty, null, undefined)
- ✅ Pattern matching (valid/invalid regex)
- ✅ String length (min/max boundaries)
- ✅ Numeric range (min/max boundaries)
- ✅ Email format (valid/invalid emails)
- ✅ Phone format (various formats)
- ✅ Custom validators (jmbg, pib)
- ✅ Error message handling

### Running Tests

```bash
pnpm test ValidationEngine
```

---

## Key Takeaways for AI Agents

### Quick Reference

1. **Location**: `src/core/ValidationEngine.ts`
2. **Main Method**: `validateField(value, rules)`
3. **Returns**: `{ isValid: boolean, errors: string[] }`
4. **Custom Validators**: Use `registerCustomValidator(name, fn)`
5. **JSON Config**: Define validation in field's `validation` object

### Common Use Cases

1. **Required Field**: `{ required: true }`
2. **Email**: `{ email: true }`
3. **Pattern**: `{ pattern: "regex_here" }`
4. **Length**: `{ minLength: X, maxLength: Y }`
5. **Range**: `{ min: X, max: Y }`
6. **Custom**: `{ custom: { rule: "validator_name" } }`

### Integration Points

1. Define validation rules in JSON schema
2. FormEngine calls ValidationEngine on blur/submit
3. Errors displayed via FieldRenderer
4. Custom validators registered at app init
5. Cross-field validation in schema logic section

---

**End of Document**
