# Form Engine Architecture - AI/RAG Optimized

## Document Metadata

- **Document Type**: Technical Architecture Specification
- **Version**: 2.2-RAG
- **Date**: 2026-02-21
- **Status**: Production Ready (Core), Enhancement Phase (UI + Tests + Layout)
- **Purpose**: Complete architectural reference for AI agents and RAG systems
- **Source**: Consolidated from ARCHITECTURE.md and related documentation
- **Related**: 05-LAYOUT-STANDARDS-RAG.md

---

## Executive Summary

### System Overview

Form Engine is an **enterprise-grade, JSON-driven dynamic form generation system** for React applications. The system enables complete form definition through JSON schemas without hardcoding, supporting conditional logic, advanced validation, and API-driven dropdown lookups.

### Key Capabilities

- Zero hardcoding - all forms defined via JSON schemas
- Conditional field logic (show/hide/disable based on other fields)
- Advanced validation with built-in and custom validators
- Async API lookups with caching mechanism
- 12-column grid layout system with responsive breakpoints
- Type-safe TypeScript implementation
- Framework-agnostic core engines
- Production-ready with comprehensive unit tests

### Core Principles

1. **UI/Backend Separation**: Frontend doesn't know database structure
2. **Runtime Configuration**: Form changes through JSON without rebuilds
3. **Declarative Design**: All rules described in JSON
4. **Reusability**: Same engines across different forms
5. **Framework Agnostic Core**: Engines not tied to React

---

## System Architecture

### Architectural Layers

```
┌─────────────────────────────────────────────┐
│         React UI Layer                      │
│  (FormEngine, FieldRenderer, Hooks)         │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│      Framework-Agnostic Core                │
│  (ValidationEngine, LogicEngine,            │
│   LookupService)                            │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│         JSON Schema Definition               │
│  (Metadata, Fields, Logic, Validations)     │
└─────────────────────────────────────────────┘
```

### Project Structure

```
apps/form-engine/
├── src/
│   ├── core/                    # Framework-agnostic engines
│   │   ├── ValidationEngine.ts  # Field validation logic
│   │   ├── LogicEngine.ts       # Conditional logic processor
│   │   └── LookupService.ts     # API caching service
│   │
│   ├── hooks/                   # React integration hooks
│   │   ├── useFormEngine.ts     # Main form state management
│   │   ├── useValidation.ts     # Field validation wrapper
│   │   └── useLookup.ts         # Lookup data fetching
│   │
│   ├── types/                   # TypeScript type definitions
│   │   ├── schema.types.ts      # JSON schema types
│   │   ├── validation.types.ts  # Validation rule types
│   │   └── logic.types.ts       # Conditional logic types
│   │
│   ├── utils/                   # Utility functions
│   │   ├── errorFormatter.ts    # Error message formatting
│   │   ├── formDataTransformer.ts # Data transformation
│   │   ├── schemaParser.ts      # JSON parsing utilities
│   │   └── templateMerger.ts    # Template + override merging
│   │
│   ├── FormEngine.tsx           # Main orchestrator component
│   ├── FieldRenderer.tsx        # Field type to component mapper
│   ├── Section.tsx              # Section rendering component
│   └── ErrorSummary.tsx         # Error display component
│
├── schemas/                     # Example JSON schemas
│   ├── fizicko-lice.json       # Individual person form
│   ├── pravno-lice.json        # Legal entity form
│   └── insurance-v5.json       # Complex insurance form
│
├── tests/                       # Unit test suite
│   ├── ValidationEngine.test.ts # Validation tests (9KB)
│   ├── LogicEngine.test.ts      # Logic tests (5.8KB)
│   └── LookupService.test.ts    # Lookup tests (6KB)
│
└── docs/                        # Documentation
    └── ai-rag-docs/            # AI-optimized documentation
```

---

## Core Components

### 1. ValidationEngine

**Location**: `src/core/ValidationEngine.ts` (7.7KB)
**Purpose**: Centralized field and form validation
**Status**: ✅ Production Ready (100% implemented, 95% test coverage)

#### Built-in Validators

- `required` - mandatory field validation
- `pattern` - regex pattern matching
- `minLength` / `maxLength` - string length constraints
- `min` / `max` - numeric range validation
- `email` - email format validation
- `phone` - phone number format validation

#### Custom Validators

- `jmbgChecksum` - Serbian national ID validation with checksum
- `pibChecksum` - Serbian tax ID validation with checksum

#### API Interface

```typescript
class ValidationEngine {
  validateField(value: any, rules: ValidationRules): ValidationResult;
  registerCustomValidator(name: string, fn: ValidatorFunction): void;
}

interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

interface ValidationRules {
  required?: boolean;
  pattern?: string;
  minLength?: number;
  maxLength?: number;
  min?: number;
  max?: number;
  errorMessage?: string;
  custom?: { rule: string; errorMessage: string };
}
```

#### Usage Example

```typescript
const engine = new ValidationEngine();
const result = engine.validateField('12345', {
  required: true,
  pattern: '^[0-9]{13}$',
  errorMessage: 'JMBG must be 13 digits',
});
// result = { isValid: false, errors: ['JMBG must be 13 digits'] }
```

---

### 2. LogicEngine

**Location**: `src/core/LogicEngine.ts` (6.6KB)
**Purpose**: Conditional field visibility, disabled state, and required state
**Status**: ✅ Production Ready (100% implemented, 90% test coverage)

#### Supported Operators

- `equals` / `notEquals` - equality comparison
- `greaterThan` / `lessThan` - numeric comparison
- `contains` / `startsWith` - string operations
- `isEmpty` / `isNotEmpty` - empty state checks
- `and` / `or` - nested logical conditions

#### API Interface

```typescript
class LogicEngine {
  evaluateVisibility(
    logic: LogicRule | undefined,
    formData: Record<string, any>,
  ): boolean;

  evaluateDisabled(
    logic: LogicRule | undefined,
    formData: Record<string, any>,
  ): boolean;

  evaluateRequired(
    logic: LogicRule | undefined,
    formData: Record<string, any>,
  ): boolean;
}

interface Condition {
  field: string;
  operator:
    | 'equals'
    | 'notEquals'
    | 'greaterThan'
    | 'lessThan'
    | 'contains'
    | 'isEmpty'
    | 'isNotEmpty';
  value?: any;
  and?: Condition[];
  or?: Condition[];
}
```

#### Usage Example

```typescript
const engine = new LogicEngine();
const isVisible = engine.evaluateVisibility(
  {
    visible: {
      when: {
        field: 'userType',
        operator: 'equals',
        value: 'business',
      },
    },
  },
  { userType: 'business' },
);
// isVisible = true
```

---

### 3. LookupService

**Location**: `src/core/LookupService.ts` (5KB)
**Purpose**: API-driven dropdown population with caching
**Status**: ✅ Production Ready (100% implemented, 85% test coverage)

#### Features

- In-memory Map-based cache
- TTL validation (default 1 hour)
- Request deduplication for concurrent requests
- Manual cache invalidation

#### API Interface

```typescript
class LookupService {
  async getLookup(
    ref: string,
    params?: Record<string, any>,
  ): Promise<LookupOption[]>;

  invalidate(ref: string): void;
  clearAll(): void;
}

interface CacheEntry {
  data: any;
  timestamp: number;
  ttl: number; // seconds
}
```

#### Usage Example

```typescript
const service = new LookupService();
// First call: fetches from API
const cities = await service.getLookup('cities', { country: 'RS' });
// Second call: returns from cache
const cities2 = await service.getLookup('cities', { country: 'RS' });
```

---

## JSON Schema Specification

### Root Schema Structure

```typescript
interface FormSchema {
  formId: string; // Unique identifier
  metadata: {
    version: string; // Schema version (e.g., "5.0")
    name: string; // Human-readable name
    description?: string; // Optional description
    lastUpdated: string; // ISO date string
  };
  sections: Section[]; // Form sections array
  logic?: {
    conditionalVisibility?: ConditionalRule[];
    conditionalRequired?: ConditionalRule[];
    conditionalDisabled?: ConditionalRule[];
  };
  lookups?: Record<string, LookupDefinition>;
  templateRef?: string; // Optional base template reference
  overrides?: Record<string, any>; // Template override values
}
```

### Section Structure

```typescript
interface Section {
  id: string; // Unique section identifier
  title?: string; // Display title
  description?: string; // Optional description
  fields: Field[]; // Array of form fields
  logic?: {
    visible?: { when: Condition }; // Conditional visibility
  };
}
```

### Field Structure

```typescript
interface Field {
  id: string; // Unique field identifier
  type: FieldType; // Field type (see below)
  label: string; // Display label
  placeholder?: string; // Input placeholder
  defaultValue?: any; // Default value
  validation?: ValidationRules; // Validation rules
  logic?: {
    visible?: { when: Condition }; // Field-level visibility
    disabled?: { when: Condition }; // Disabled state logic
    required?: { when: Condition }; // Conditional required
  };
  'ui:layout'?: {
    // Layout positioning (see 05-LAYOUT-STANDARDS-RAG.md)
    colSpan?: 'full' | 'half' | 'third' | 'quarter'; // Grid column span
    row?: number; // Optional row hint
  };
  lookupRef?: string; // Lookup service reference
  options?: Option[]; // Static options (radio/checkbox)
}

type FieldType =
  | 'text'
  | 'number'
  | 'email'
  | 'tel'
  | 'date'
  | 'dropdown'
  | 'radio'
  | 'checkbox'
  | 'textarea';
```

### Complete Example Schema

```json
{
  "formId": "contact-form",
  "metadata": {
    "version": "1.0",
    "name": "Contact Form",
    "lastUpdated": "2026-02-14"
  },
  "sections": [
    {
      "id": "personal",
      "title": "Personal Information",
      "fields": [
        {
          "id": "firstName",
          "type": "text",
          "label": "First Name",
          "validation": {
            "required": true,
            "minLength": 2,
            "maxLength": 50,
            "pattern": "^[a-zA-Z\\s-]+$",
            "errorMessage": "Name must contain only letters"
          }
        },
        {
          "id": "email",
          "type": "email",
          "label": "Email Address",
          "validation": {
            "required": true,
            "errorMessage": "Valid email is required"
          }
        }
      ]
    }
  ]
}
```

---

## Architectural Decisions

### Decision 1: UI Meta-Schema vs Direct DB Mapping

**Decision**: Use UI Meta-Schema approach
**Rationale**:

- Complete control over UI presentation
- Backend database changes don't affect frontend
- Version control and schema evolution easier
- Multi-client support (different views per client)

### Decision 2: Template System - Hybrid Approach

**Decision**: Base templates + Runtime overrides
**Implementation**:

1. Static base templates stored in `schemas/` folder
2. API returns override object for customization
3. `templateMerger` utility combines base + overrides
4. Final schema passed to FormEngine

**Example**:

```typescript
import { mergeTemplateWithOverrides } from './utils/templateMerger';
import baseTemplate from './schemas/fizicko-lice.json';

const apiOverrides = {
  'sections[0].fields[0].label': 'Full Name with Middle Initial',
};

const finalSchema = mergeTemplateWithOverrides(baseTemplate, apiOverrides);
```

### Decision 3: Centralized Validation Engine

**Decision**: Separate ValidationEngine with JSON declarations
**Rationale**:

- Validation rules defined once in JSON
- Reusable across all field types
- Easy to test in isolation
- Custom validators pluggable

### Decision 4: API Lookups with Local Cache

**Decision**: Lazy loading + in-memory cache
**Rationale**:

- Reduces initial load time
- Minimizes API calls
- Supports offline operation
- TTL ensures data freshness

### Decision 5: JSON Logic Rules

**Decision**: Declarative rules in JSON processed by LogicEngine
**Rationale**:

- Backend controls business logic
- No UI code changes for logic updates
- Testable and maintainable
- Clear audit trail of rule changes

---

## Implementation Status

### Completed (Production Ready)

| Component        | Status | Test Coverage | Notes                      |
| ---------------- | ------ | ------------- | -------------------------- |
| ValidationEngine | ✅     | 95%           | All validators implemented |
| LogicEngine      | ✅     | 90%           | All operators supported    |
| LookupService    | ✅     | 85%           | Cache + API working        |
| useFormEngine    | ✅     | -             | Hook implemented           |
| FormEngine       | ✅     | -             | Main component ready       |
| FieldRenderer    | ✅     | -             | All field types mapped     |
| templateMerger   | ✅     | -             | Base + override merging    |

### Partially Implemented

| Feature                | Status | What Exists                      | What's Missing                                      |
| ---------------------- | ------ | -------------------------------- | --------------------------------------------------- |
| Template System        | 60%    | Merger utility                   | API integration                                     |
| Cross-field Validation | 30%    | Engine support                   | JSON schema format                                  |
| Layout/Grid Support    | 40%    | Token definitions, standards doc | Engine colSpan support, FieldContainer grid classes |
| React Component Tests  | 0%     | -                                | All hooks/components                                |

### Planned Features

| Feature                    | Priority | ETA     |
| -------------------------- | -------- | ------- |
| API Contract Documentation | High     | Q1 2026 |
| React Component Tests      | High     | Q1 2026 |
| Multi-step Wizard          | Low      | Q3 2026 |
| i18n Support               | Low      | Q4 2026 |

---

## Integration Patterns

### React Application Integration

```typescript
import { FormEngine } from './FormEngine';
import type { FormSchema } from './types/schema.types';

function App() {
  const [schema, setSchema] = useState<FormSchema | null>(null);

  useEffect(() => {
    // Load schema from API or import
    fetch('/api/forms/contact-form')
      .then(res => res.json())
      .then(setSchema);
  }, []);

  const handleSubmit = (data: any) => {
    console.log('Form data:', data);
    // Send to backend API
  };

  if (!schema) return <div>Loading...</div>;

  return (
    <FormEngine
      schema={schema}
      onSubmit={handleSubmit}
      initialData={{ /* pre-fill values */ }}
    />
  );
}
```

### Custom Field Type Extension

`FieldRenderer` currently does **not** expose a runtime registration API.
To add a new field type (e.g. `richtext`), extend the `switch (field.type)`
branch in `src/FieldRenderer.tsx` and add the corresponding schema type.

```typescript
// src/FieldRenderer.tsx (inside switch field.type)
case 'richtext':
  return (
    <RichTextEditor
      id={field.id}
      value={value}
      onChange={(val) => onChange(val)}
      onBlur={onBlur}
      disabled={disabled}
    />
  );
```

### Custom Validator Registration

```typescript
import { ValidationEngine } from './core/ValidationEngine';

const engine = new ValidationEngine();

engine.registerCustomValidator('uniqueUsername', async (value) => {
  const response = await fetch(`/api/validate/username?value=${value}`);
  const { isAvailable } = await response.json();
  return isAvailable;
});
```

---

## Performance Considerations

### Optimization Strategies

1. **Conditional Rendering**: Hidden fields not rendered in DOM
2. **Lookup Caching**: API calls minimized via LookupService cache
3. **Lazy Validation**: Validation on blur, not on every keystroke
4. **Request Deduplication**: Concurrent lookup requests merged
5. **Memoization**: React.memo on FieldRenderer and Section components

### Performance Metrics

- **Initial Render**: < 100ms for 50-field form
- **Field Validation**: < 5ms per field
- **Logic Evaluation**: < 2ms per condition
- **Lookup Cache Hit**: < 1ms
- **Lookup Cache Miss**: depends on API (typically 100-500ms)

---

## Security Considerations

### Client-Side Validation

- All client validation is for UX only
- Backend must re-validate all inputs
- Never trust client-side data

### XSS Prevention

- User input sanitized before display
- Error messages escaped
- HTML not allowed in field values

### API Security

- Lookup endpoints require authentication
- Rate limiting on validation endpoints
- CORS properly configured

---

## Testing Strategy

### Unit Tests

- **ValidationEngine.test.ts** (9KB): All validators tested
- **LogicEngine.test.ts** (5.8KB): All operators tested
- **LookupService.test.ts** (6KB): Cache and API tested

### Integration Tests (Planned)

- End-to-end form flow
- Conditional logic scenarios
- Lookup service integration
- Multi-section forms

### Test Coverage Goals

- Core Engines: 90%+ ✅ Achieved
- React Hooks: 85%+ ⏳ Pending
- UI Components: 80%+ ⏳ Pending
- Overall: 85%+ (currently 30%)

---

## Future Enhancements

### Phase 4: Advanced Features

1. Cross-field validation JSON format
2. Async validators (username availability)
3. Computed fields (automatic calculations)
4. Field dependency graphs

### Phase 5: Extended Capabilities

1. Multi-step wizard forms
2. Dynamic field arrays (repeatable sections)
3. File upload fields
4. Rich text editor integration
5. Internationalization (i18n)

---

## Key Takeaways for AI Agents

### System Capabilities

1. **JSON-Driven**: All form structure defined in JSON schemas
2. **Type-Safe**: Full TypeScript support throughout
3. **Modular**: Core engines independent of React
4. **Extensible**: Custom validators and field types supported
5. **Production Ready**: Core functionality complete and tested

### Integration Points

1. **Schema Definition**: Start with JSON schema structure
2. **Custom Validation**: Use ValidationEngine.registerCustomValidator()
3. **Field Types**: Extend via FieldRenderer.registerFieldType()
4. **API Lookups**: Configure in schema lookups section
5. **Conditional Logic**: Define in schema logic section
6. **Layout & Grid**: Use `ui:layout` with `colSpan` for field positioning (see 05-LAYOUT-STANDARDS-RAG.md)

### Common Patterns

1. Load schema from API at runtime
2. Merge base template with API overrides
3. Pass schema to FormEngine component
4. Handle submit callback for form data
5. Pre-fill with initialData prop

---

## Document Version History

- **2.2-RAG** (2026-02-21): Added layout/grid references, `ui:layout` in Field interface
- **2.1-RAG** (2026-02-14): AI-optimized version for RAG systems
- **2.0** (2026-01-31): Consolidated architecture documentation
- **1.0** (2026-01-15): Initial architecture document

---

**End of Document**
