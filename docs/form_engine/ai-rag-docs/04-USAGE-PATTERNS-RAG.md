# Usage Patterns - AI/RAG Optimized

## Document Metadata

- **Document Type**: Implementation Guide
- **Version**: 1.1-RAG
- **Date**: 2026-02-21
- **Status**: Production Ready
- **Purpose**: Common usage patterns and integration examples
- **Related**: 01-ARCHITECTURE-RAG.md, 03-JSON-SCHEMA-SPEC-RAG.md, 05-LAYOUT-STANDARDS-RAG.md

---

## Basic Integration

### Pattern 1: Simple Form

```typescript
import { FormEngine } from './FormEngine';
import type { FormSchema } from './types/schema.types';

function ContactForm() {
  const schema: FormSchema = {
    formId: 'contact',
    metadata: {
      version: '1.0',
      name: 'Contact Form',
      lastUpdated: '2026-02-14'
    },
    sections: [
      {
        id: 'info',
        title: 'Contact Information',
        fields: [
          {
            id: 'name',
            type: 'text',
            label: 'Name',
            validation: { required: true }
          },
          {
            id: 'email',
            type: 'email',
            label: 'Email',
            validation: { required: true, email: true }
          }
        ]
      }
    ]
  };

  const handleSubmit = (data: any) => {
    console.log('Form data:', data);
    // Send to API
  };

  return <FormEngine schema={schema} onSubmit={handleSubmit} />;
}
```

---

### Pattern 2: Load Schema from API

```typescript
import { useState, useEffect } from 'react';
import { FormEngine } from './FormEngine';

function DynamicForm() {
  const [schema, setSchema] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/forms/contact-form')
      .then(res => res.json())
      .then(data => {
        setSchema(data);
        setLoading(false);
      })
      .catch(err => console.error('Failed to load schema:', err));
  }, []);

  const handleSubmit = async (data: any) => {
    const response = await fetch('/api/forms/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (response.ok) {
      alert('Form submitted successfully!');
    }
  };

  if (loading) return <div>Loading form...</div>;
  if (!schema) return <div>Failed to load form</div>;

  return <FormEngine schema={schema} onSubmit={handleSubmit} />;
}
```

---

### Pattern 3: Pre-fill with Initial Data

`FormEngine` does not expose an `initialData` prop. To prefill values, map API data into
`field.defaultValue` before rendering.

```typescript
function EditUserForm({ userId }: { userId: string }) {
  const [schema, setSchema] = useState(null);

  const applyPrefillValues = (schemaData: any, values: Record<string, unknown>) => ({
    ...schemaData,
    sections: schemaData.sections.map((section: any) => ({
      ...section,
      fields: section.fields.map((field: any) => ({
        ...field,
        defaultValue: values[field.id] ?? field.defaultValue
      }))
    }))
  });

  useEffect(() => {
    // Load schema and user data in parallel
    Promise.all([
      fetch('/api/forms/user-profile').then(r => r.json()),
      fetch(`/api/users/${userId}`).then(r => r.json())
    ]).then(([schemaData, userData]) => {
      const prefillValues = {
        firstName: userData.first_name,
        lastName: userData.last_name,
        email: userData.email,
        phone: userData.phone
      };

      setSchema(applyPrefillValues(schemaData, prefillValues));
    });
  }, [userId]);

  const handleSubmit = async (data: any) => {
    await fetch(`/api/users/${userId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
  };

  if (!schema) return <div>Loading...</div>;

  // Force remount when userId changes so new schema defaultValue values are reapplied
  return <FormEngine key={userId} schema={schema} onSubmit={handleSubmit} />;
}
```

---

## Conditional Logic Patterns

### Pattern 4: Show/Hide Sections

```json
{
  "logic": {
    "conditionalVisibility": [
      {
        "targetField": "business-info",
        "showWhen": {
          "field": "userType",
          "operator": "equals",
          "value": "business"
        }
      }
    ]
  },
  "sections": [
    {
      "id": "type-selection",
      "fields": [
        {
          "id": "userType",
          "type": "radio",
          "label": "Account Type",
          "options": [
            { "value": "personal", "label": "Personal" },
            { "value": "business", "label": "Business" }
          ],
          "defaultValue": "personal"
        }
      ]
    },
    {
      "id": "business-info",
      "title": "Business Information",
      "fields": [
        {
          "id": "companyName",
          "type": "text",
          "label": "Company Name",
          "validation": { "required": true }
        }
      ]
    }
  ]
}
```

---

### Pattern 5: Complex Nested Conditions

```json
{
  "logic": {
    "conditionalVisibility": [
      {
        "targetField": "discount-section",
        "showWhen": {
          "operator": "and",
          "conditions": [
            {
              "field": "membershipType",
              "operator": "equals",
              "value": "premium"
            },
            {
              "operator": "or",
              "conditions": [
                {
                  "field": "totalAmount",
                  "operator": "greaterThan",
                  "value": 1000
                },
                {
                  "field": "hasPromoCode",
                  "operator": "equals",
                  "value": true
                }
              ]
            }
          ]
        }
      }
    ]
  }
}
```

---

## Validation Patterns

### Pattern 6: Multi-Rule Validation

```json
{
  "id": "password",
  "type": "text",
  "label": "Password",
  "validation": {
    "required": true,
    "minLength": 8,
    "maxLength": 50,
    "pattern": "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$",
    "errorMessage": "Password must be 8-50 characters with uppercase, lowercase, number, and special character"
  }
}
```

---

### Pattern 7: Custom Validator

```typescript
import { ValidationEngine } from './core/ValidationEngine';

const engine = new ValidationEngine();

// Register custom validator
engine.registerCustomValidator('uniqueUsername', async (value: string) => {
  const response = await fetch(`/api/validate/username?value=${value}`);
  const { isAvailable } = await response.json();
  return isAvailable;
});
```

**Schema:**

```json
{
  "id": "username",
  "type": "text",
  "label": "Username",
  "validation": {
    "required": true,
    "minLength": 3,
    "maxLength": 20,
    "custom": {
      "rule": "uniqueUsername",
      "errorMessage": "Username is already taken"
    }
  }
}
```

---

## Lookup Integration Patterns

### Pattern 8: Simple API Lookup

```json
{
  "lookups": {
    "countries": {
      "endpoint": "/api/lookups/countries",
      "cache": true,
      "cacheTTL": 86400
    }
  },
  "sections": [
    {
      "id": "location",
      "fields": [
        {
          "id": "country",
          "type": "dropdown",
          "label": "Country",
          "lookupRef": "countries"
        }
      ]
    }
  ]
}
```

---

### Pattern 9: Cascading Dropdowns

```json
{
  "lookups": {
    "cities": {
      "endpoint": "/api/lookups/cities",
      "cache": true
    }
  },
  "sections": [
    {
      "id": "location",
      "fields": [
        {
          "id": "country",
          "type": "dropdown",
          "label": "Country",
          "lookupRef": "countries"
        },
        {
          "id": "city",
          "type": "dropdown",
          "label": "City",
          "lookupRef": "cities",
          "logic": {
            "disabled": {
              "when": {
                "field": "country",
                "operator": "isEmpty"
              }
            }
          }
        }
      ]
    }
  ]
}
```

**Dynamic lookup with params:**

```typescript
const service = new LookupService();
const cities = await service.getLookup('cities', {
  country: formData.country,
});
```

---

## Template System Patterns

### Pattern 10: Base Template + Overrides

**Base Template** (`schemas/base-contact.json`):

```json
{
  "formId": "contact-base",
  "sections": [
    {
      "id": "info",
      "title": "Contact Information",
      "fields": [
        {
          "id": "name",
          "type": "text",
          "label": "Name"
        },
        {
          "id": "email",
          "type": "email",
          "label": "Email"
        }
      ]
    }
  ]
}
```

**API Override:**

```json
{
  "templateRef": "contact-base",
  "overrides": {
    "sections[0].title": "Personal Contact Details",
    "sections[0].fields[0].label": "Full Name"
  }
}
```

**Merge:**

```typescript
import { mergeTemplateWithOverrides } from './utils/templateMerger';
import baseTemplate from './schemas/base-contact.json';

const apiResponse = await fetch('/api/forms/contact');
const apiData = await apiResponse.json();

const finalSchema = mergeTemplateWithOverrides(baseTemplate, apiData.overrides);
```

---

## Error Handling Patterns

### Pattern 11: Schema Load Error

```typescript
function FormWithErrorHandling() {
  const [schema, setSchema] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/forms/contact')
      .then(res => {
        if (!res.ok) throw new Error('Failed to load form');
        return res.json();
      })
      .then(setSchema)
      .catch(err => {
        console.error('Schema load error:', err);
        setError(err.message);
      });
  }, []);

  if (error) {
    return (
      <div className="error">
        <h2>Error Loading Form</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>
          Retry
        </button>
      </div>
    );
  }

  if (!schema) return <div>Loading...</div>;

  return <FormEngine schema={schema} onSubmit={handleSubmit} />;
}
```

---

### Pattern 12: Submit Error Handling

```typescript
const handleSubmit = async (data: any) => {
  try {
    const response = await fetch('/api/forms/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Submit failed');
    }

    const result = await response.json();
    alert('Form submitted successfully!');
  } catch (error) {
    console.error('Submit error:', error);
    alert(`Error: ${error.message}`);
  }
};
```

---

## Performance Patterns

### Pattern 13: Lazy Schema Loading

```typescript
import { lazy, Suspense } from 'react';

const FormEngine = lazy(() => import('./FormEngine'));

function LazyForm() {
  const [schema, setSchema] = useState(null);

  return (
    <Suspense fallback={<div>Loading form engine...</div>}>
      {schema && <FormEngine schema={schema} onSubmit={handleSubmit} />}
    </Suspense>
  );
}
```

---

### Pattern 14: Optimized Lookup Caching

```typescript
import { LookupService } from './core/LookupService';

// Create singleton instance
const lookupService = new LookupService();

// Preload frequently used lookups
await Promise.all([
  lookupService.getLookup('countries'),
  lookupService.getLookup('currencies'),
  lookupService.getLookup('languages'),
]);

// Later usage hits cache
const countries = await lookupService.getLookup('countries'); // From cache
```

---

## Layout Patterns

### Pattern 15: Two-Column Layout

Use `ui:layout` with `colSpan` to place fields side-by-side on a 12-column grid. For full standards, see `05-LAYOUT-STANDARDS-RAG.md`.

```json
{
  "sections": [
    {
      "id": "personal",
      "title": "Personal Information",
      "fields": [
        {
          "id": "firstName",
          "type": "text",
          "label": "First Name",
          "ui:layout": { "colSpan": "half" },
          "validation": { "required": true }
        },
        {
          "id": "lastName",
          "type": "text",
          "label": "Last Name",
          "ui:layout": { "colSpan": "half" },
          "validation": { "required": true }
        },
        {
          "id": "city",
          "type": "text",
          "label": "City",
          "ui:layout": { "colSpan": "third" }
        },
        {
          "id": "zip",
          "type": "text",
          "label": "Zip Code",
          "ui:layout": { "colSpan": "third" }
        },
        {
          "id": "country",
          "type": "dropdown",
          "label": "Country",
          "ui:layout": { "colSpan": "third" },
          "lookupRef": "countries"
        },
        {
          "id": "notes",
          "type": "textarea",
          "label": "Additional Notes",
          "ui:layout": { "colSpan": "full" }
        }
      ]
    }
  ]
}
```

**Key Points**:

- `full` = 12 columns (textarea, headers)
- `half` = 6 columns (2 fields per row)
- `third` = 4 columns (3 fields per row)
- `quarter` = 3 columns (4 fields per row)
- On mobile (<768px), all fields collapse to `full` width

---

### Pattern 16: Form Width Control

Use form-level max-width tokens to constrain form width:

| Category | Token                        | Value | Use Case                 |
| :------- | :--------------------------- | :---- | :----------------------- |
| Narrow   | `dyn.form.maxWidth.narrow`   | 480px | Login, short forms       |
| Standard | `dyn.form.maxWidth.standard` | 720px | Business forms           |
| Wide     | `dyn.form.maxWidth.wide`     | 960px | Complex enterprise forms |
| Full     | `dyn.form.maxWidth.full`     | 100%  | Embedded forms           |

---

## Key Takeaways

### Common Integration Steps

1. Import FormEngine and types
2. Define or load schema
3. Create submit handler
4. Render FormEngine with schema and handler
5. Handle loading and error states

### Best Practices

1. **Always** validate on both client and server
2. **Load** schemas from API for runtime flexibility
3. **Cache** lookups to minimize API calls
4. **Pre-fill** forms by mapping API data to field `defaultValue` when editing
5. **Handle errors** gracefully with user feedback
6. **Use templates** for reusable base schemas
7. **Test** conditional logic thoroughly
8. **Monitor** performance with large forms
9. **Use `ui:layout`** with `colSpan` for optimal field arrangement (see 05-LAYOUT-STANDARDS-RAG.md)

---

**End of Document**
