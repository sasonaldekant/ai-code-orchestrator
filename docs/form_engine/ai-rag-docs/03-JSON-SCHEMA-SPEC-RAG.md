# JSON Schema Specification - AI/RAG Optimized

## Document Metadata

- **Document Type**: Technical Specification
- **Version**: 1.1-RAG
- **Date**: 2026-02-21
- **Status**: Production Ready
- **Purpose**: Complete JSON schema reference for AI agents
- **Related**: 01-ARCHITECTURE-RAG.md, 05-LAYOUT-STANDARDS-RAG.md

---

## Schema Structure Overview

### Root Schema

```typescript
interface FormSchema {
  formId: string; // Unique form identifier
  metadata: FormMetadata; // Form metadata
  sections: Section[]; // Array of form sections
  logic?: LogicBlock; // Conditional logic rules
  lookups?: Record<string, LookupDefinition>; // API lookup definitions
  templateRef?: string; // Optional base template reference
  overrides?: Record<string, any>; // Template override values
}
```

---

## Metadata Structure

```typescript
interface FormMetadata {
  version: string; // Schema version (e.g., "5.0")
  name: string; // Human-readable form name
  description?: string; // Optional description
  lastUpdated: string; // ISO date string (e.g., "2026-02-14")
}
```

**Example**:

```json
{
  "metadata": {
    "version": "5.0",
    "name": "Insurance Person Entry Form",
    "description": "Form for entering insured person data",
    "lastUpdated": "2026-02-14"
  }
}
```

---

## Section Structure

```typescript
interface Section {
  id: string; // Unique section identifier
  title?: string; // Display title
  description?: string; // Optional section description
  fields: Field[]; // Array of fields
  logic?: {
    visible?: { when: Condition }; // Conditional visibility
  };
}
```

**Example**:

```json
{
  "sections": [
    {
      "id": "personal-info",
      "title": "Personal Information",
      "description": "Enter your personal details",
      "fields": [...],
      "logic": {
        "visible": {
          "when": {
            "field": "userType",
            "operator": "equals",
            "value": "individual"
          }
        }
      }
    }
  ]
}
```

---

## Field Structure

### Base Field Interface

```typescript
interface Field {
  id: string; // Unique field identifier
  type: FieldType; // Field type
  label: string; // Display label
  placeholder?: string; // Input placeholder text
  defaultValue?: any; // Default field value
  validation?: ValidationRules; // Validation rules
  logic?: FieldLogic; // Field-specific logic
  'ui:layout'?: UILayout; // Layout positioning (see 05-LAYOUT-STANDARDS-RAG.md)
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

### Field Layout (ui:layout)

The `ui:layout` property controls field positioning within the 12-column grid system. For full layout standards, see `05-LAYOUT-STANDARDS-RAG.md`.

```typescript
interface UILayout {
  colSpan?: 'full' | 'half' | 'third' | 'quarter'; // Grid column span
  row?: number; // Optional row hint
}
```

| colSpan     | Columns | Fields per Row | Recommended Usage                         |
| :---------- | :------ | :------------- | :---------------------------------------- |
| **full**    | 12      | 1              | Textarea, Address, Headers, Descriptions. |
| **half**    | 6       | 2              | First Name + Last Name, Email + Phone.    |
| **third**   | 4       | 3              | City + Zip + Country, Date + Time + User. |
| **quarter** | 3       | 4              | Short codes, Currency symbols, Numbers.   |

**Example**:

````json
{
  "id": "email",
  "type": "email",
  "label": "Email",
  "ui:layout": {
    "colSpan": "half",
    "row": 1
  }
}

### Field Types Reference

| Type | Description | Use Case | Example |
|------|-------------|----------|--------|
| `text` | Single-line text | Names, addresses | First Name |
| `number` | Numeric input | Age, quantities | Age: 25 |
| `email` | Email with validation | Email addresses | user@example.com |
| `tel` | Phone number | Phone numbers | +381 61 1234567 |
| `date` | Date picker | Birth dates, deadlines | 1990-01-15 |
| `textarea` | Multi-line text | Comments, descriptions | Long text |
| `dropdown` | Select dropdown | Countries, categories | Select option |
| `radio` | Radio button group | Yes/No, Gender | Male/Female |
| `checkbox` | Single checkbox | Accept terms | true/false |

---

## Validation Rules

```typescript
interface ValidationRules {
  required?: boolean;       // Field is mandatory
  pattern?: string;         // Regex pattern
  min?: number;            // Min value (numbers)
  max?: number;            // Max value (numbers)
  minLength?: number;      // Min string length
  maxLength?: number;      // Max string length
  email?: boolean;         // Email format validation
  phone?: boolean;         // Phone format validation
  errorMessage?: string;   // Custom error message
  custom?: {
    rule: string;          // Custom validator name
    errorMessage: string;  // Custom error message
    params?: any;          // Optional validator parameters
  };
}
````

**Example**:

```json
{
  "id": "email",
  "type": "email",
  "label": "Email Address",
  "validation": {
    "required": true,
    "email": true,
    "maxLength": 100,
    "errorMessage": "Enter a valid email (max 100 characters)"
  }
}
```

---

## Field Logic

```typescript
interface FieldLogic {
  visible?: { when: Condition }; // Field visibility
  disabled?: { when: Condition }; // Field disabled state
  required?: { when: Condition }; // Conditional required
}

interface Condition {
  field: string; // Field ID to check
  operator: ConditionOperator; // Comparison operator
  value?: any; // Comparison value
  and?: Condition[]; // Nested AND conditions
  or?: Condition[]; // Nested OR conditions
}

type ConditionOperator =
  | 'equals'
  | 'notEquals'
  | 'greaterThan'
  | 'lessThan'
  | 'contains'
  | 'startsWith'
  | 'isEmpty'
  | 'isNotEmpty';
```

**Example - Conditional Visibility**:

```json
{
  "id": "companyName",
  "type": "text",
  "label": "Company Name",
  "logic": {
    "visible": {
      "when": {
        "field": "userType",
        "operator": "equals",
        "value": "business"
      }
    }
  }
}
```

---

## Dropdown Fields with Lookups

### Static Options

```json
{
  "id": "gender",
  "type": "radio",
  "label": "Gender",
  "options": [
    { "value": "M", "label": "Male" },
    { "value": "F", "label": "Female" },
    { "value": "O", "label": "Other" }
  ]
}
```

### Dynamic Lookup

```json
{
  "id": "city",
  "type": "dropdown",
  "label": "City",
  "lookupRef": "cities"
}
```

### Lookup Definition

```typescript
interface LookupDefinition {
  endpoint: string; // API endpoint URL
  method?: string; // HTTP method (default: GET)
  cache?: boolean; // Enable caching (default: true)
  cacheTTL?: number; // Cache TTL in seconds (default: 3600)
  params?: Record<string, any>; // Additional query params
}
```

```json
{
  "lookups": {
    "cities": {
      "endpoint": "/api/lookups/cities",
      "method": "GET",
      "cache": true,
      "cacheTTL": 3600,
      "params": { "country": "RS" }
    }
  }
}
```

---

## Logic Block (Form-Level)

```typescript
interface LogicBlock {
  conditionalVisibility?: ConditionalRule[];
  conditionalRequired?: ConditionalRule[];
  conditionalDisabled?: ConditionalRule[];
  crossFieldValidation?: CrossFieldRule[];
}

interface ConditionalRule {
  targetField: string; // Field/section ID to affect
  showWhen?: Condition; // Visibility condition
  requireWhen?: Condition; // Required condition
  disableWhen?: Condition; // Disabled condition
}
```

**Example**:

```json
{
  "logic": {
    "conditionalVisibility": [
      {
        "targetField": "business-section",
        "showWhen": {
          "field": "userType",
          "operator": "equals",
          "value": "business"
        }
      }
    ]
  }
}
```

---

## Complete Example Schema

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
          "placeholder": "Enter your first name",
          "ui:layout": { "colSpan": "half" },
          "validation": {
            "required": true,
            "minLength": 2,
            "maxLength": 50,
            "pattern": "^[a-zA-Z\\s-]+$",
            "errorMessage": "Name must be 2-50 letters only"
          }
        },
        {
          "id": "email",
          "type": "email",
          "label": "Email Address",
          "ui:layout": { "colSpan": "half" },
          "validation": {
            "required": true,
            "email": true,
            "errorMessage": "Valid email is required"
          }
        },
        {
          "id": "phone",
          "type": "tel",
          "label": "Phone Number",
          "validation": {
            "phone": true,
            "errorMessage": "Enter a valid phone number"
          }
        }
      ]
    },
    {
      "id": "business",
      "title": "Business Information",
      "logic": {
        "visible": {
          "when": {
            "field": "userType",
            "operator": "equals",
            "value": "business"
          }
        }
      },
      "fields": [
        {
          "id": "companyName",
          "type": "text",
          "label": "Company Name",
          "validation": {
            "required": true,
            "minLength": 2,
            "maxLength": 100
          }
        }
      ]
    }
  ],
  "lookups": {
    "cities": {
      "endpoint": "/api/lookups/cities",
      "cache": true,
      "cacheTTL": 3600
    }
  }
}
```

---

## Key Takeaways for AI Agents

### Schema Checklist

1. **formId**: Unique identifier (required)
2. **metadata**: Version, name, lastUpdated (required)
3. **sections**: At least one section (required)
4. **fields**: At least one field per section (required)
5. **logic**: Optional conditional rules
6. **lookups**: Optional API lookups

### Field Definition Essentials

1. **id**: Unique within form
2. **type**: Valid FieldType
3. **label**: User-visible text
4. **validation**: Rules object (optional but recommended)
5. **logic**: Conditional behavior (optional)
6. **ui:layout**: Grid positioning with `colSpan` (optional, see 05-LAYOUT-STANDARDS-RAG.md)

### Validation Best Practices

1. Always include `errorMessage` for clarity
2. Combine validators (e.g., required + email)
3. Use appropriate field types
4. Set reasonable length/range limits
5. Test regex patterns thoroughly

---

**End of Document**
