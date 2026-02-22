# Form Engine - AI/RAG Optimized Documentation

## Overview

This folder contains **AI-optimized documentation** specifically structured for AI agents and Retrieval-Augmented Generation (RAG) systems. Each document has been:

- ✅ **Verified for factual accuracy** - All content cross-referenced with source code
- ✅ **Structured for AI consumption** - Clear headings, metadata, and semantic structure
- ✅ **Consolidated and deduplicated** - Single source of truth per topic
- ✅ **Enhanced with examples** - Practical code examples and JSON schemas
- ✅ **Optimized for chunking** - Suitable section sizes for vector embeddings

---

## Document Index

### 01-ARCHITECTURE-RAG.md

**Purpose**: Complete system architecture reference
**Topics**:

- System overview and capabilities
- Architectural layers and project structure
- Core components (ValidationEngine, LogicEngine, LookupService)
- JSON schema specification overview
- Architectural decisions and rationale
- Implementation status and roadmap
- Performance and security considerations

**Use for**: Understanding overall system design, component relationships, and technical decisions.

---

### 02-VALIDATION-GUIDE-RAG.md

**Purpose**: Complete validation system reference
**Topics**:

- ValidationEngine API and core methods
- Built-in validators (required, pattern, email, phone, etc.)
- Serbian-specific validators (JMBG, PIB)
- Custom validator registration
- Cross-field validation
- Validation timing and error handling
- Common validation patterns

**Use for**: Implementing field validation, creating custom validators, understanding validation logic.

---

### 03-JSON-SCHEMA-SPEC-RAG.md

**Purpose**: Complete JSON schema structure reference
**Topics**:

- Root schema structure (FormSchema)
- Metadata and section definitions
- Field types and properties
- Validation rules structure
- Field logic (conditional visibility, disabled, required)
- Lookup definitions and configuration
- Complete example schemas

**Use for**: Creating or modifying JSON schemas, understanding schema structure, defining forms.

---

### 04-USAGE-PATTERNS-RAG.md

**Purpose**: Common integration patterns and examples
**Topics**:

- Basic React integration
- Loading schemas from API
- Pre-filling forms with data
- Conditional logic patterns
- Validation patterns
- Lookup integration
- Template system usage
- Error handling patterns
- Performance optimization

**Use for**: Implementing specific features, integration examples, troubleshooting common scenarios.

---

### 05-LAYOUT-STANDARDS-RAG.md

**Purpose**: GUI layout standards and grid system reference
**Topics**:

- Form width standards (max-width tokens)
- 12-column grid system and colSpan positioning
- Spacing tokens (column gap, row gap, section gap)
- Component sizing and WCAG 2.1 AA accessibility
- Responsive breakpoints and behavior
- JSON Schema `ui:layout` integration pattern
- CSS variable mapping for grid layout

**Use for**: Defining field layout in JSON schemas, understanding grid positioning, responsive design rules, form width constraints.

---

## Quick Navigation by Topic

### Architecture & Design

- System Overview → `01-ARCHITECTURE-RAG.md` § Executive Summary
- Component Structure → `01-ARCHITECTURE-RAG.md` § Core Components
- Design Decisions → `01-ARCHITECTURE-RAG.md` § Architectural Decisions

### Validation

- Validation API → `02-VALIDATION-GUIDE-RAG.md` § Core API
- Built-in Rules → `02-VALIDATION-GUIDE-RAG.md` § Built-in Validators
- Custom Validators → `02-VALIDATION-GUIDE-RAG.md` § Custom Validators
- Error Messages → `02-VALIDATION-GUIDE-RAG.md` § Error Handling

### Schema Definition

- Schema Structure → `03-JSON-SCHEMA-SPEC-RAG.md` § Schema Structure Overview
- Field Types → `03-JSON-SCHEMA-SPEC-RAG.md` § Field Structure
- Conditional Logic → `03-JSON-SCHEMA-SPEC-RAG.md` § Field Logic
- Complete Examples → `03-JSON-SCHEMA-SPEC-RAG.md` § Complete Example Schema

### Layout & Grid

- Form Width Standards → `05-LAYOUT-STANDARDS-RAG.md` § Form Width Standards
- Grid & colSpan → `05-LAYOUT-STANDARDS-RAG.md` § Grid System
- Responsive Breakpoints → `05-LAYOUT-STANDARDS-RAG.md` § Responsive Behavior
- CSS Variable Mapping → `05-LAYOUT-STANDARDS-RAG.md` § CSS Variable Mapping

### Implementation

- Basic Setup → `04-USAGE-PATTERNS-RAG.md` § Pattern 1: Simple Form
- API Integration → `04-USAGE-PATTERNS-RAG.md` § Pattern 2: Load Schema from API
- Conditional Fields → `04-USAGE-PATTERNS-RAG.md` § Pattern 4: Show/Hide Sections
- Lookups → `04-USAGE-PATTERNS-RAG.md` § Pattern 8: Simple API Lookup

---

## Document Structure Convention

All documents follow this consistent structure:

```markdown
# Title - AI/RAG Optimized

## Document Metadata

- Document Type: [type]
- Version: [version]
- Date: [date]
- Status: [status]
- Purpose: [purpose]
- Related: [related docs]

## Content Sections

[Hierarchical sections with clear headings]

## Key Takeaways for AI Agents

[Summary of critical information]

**End of Document**
```

---

## Metadata Summary

| Document                   | Type                 | Version | Status     | Size  |
| -------------------------- | -------------------- | ------- | ---------- | ----- |
| 01-ARCHITECTURE-RAG.md     | Technical Spec       | 2.2-RAG | Production | ~19KB |
| 02-VALIDATION-GUIDE-RAG.md | Implementation Guide | 1.2-RAG | Production | ~13KB |
| 03-JSON-SCHEMA-SPEC-RAG.md | Technical Spec       | 1.1-RAG | Production | ~11KB |
| 04-USAGE-PATTERNS-RAG.md   | Implementation Guide | 1.1-RAG | Production | ~13KB |
| 05-LAYOUT-STANDARDS-RAG.md | Technical Spec       | 1.0-RAG | Production | ~3KB  |

**Total Documentation Size**: ~59KB  
**Estimated RAG Chunks** (1KB avg): ~59 chunks  
**Last Updated**: 2026-02-21

---

## Usage Guidelines for AI Agents

### Query Routing

**Architecture Questions** → Route to `01-ARCHITECTURE-RAG.md`

- "How does the system work?"
- "What are the core components?"
- "Why was [decision] made?"

**Validation Questions** → Route to `02-VALIDATION-GUIDE-RAG.md`

- "How do I validate [field type]?"
- "What validators are available?"
- "How do I create custom validator?"

**Schema Questions** → Route to `03-JSON-SCHEMA-SPEC-RAG.md`

- "What's the schema structure?"
- "How do I define [field type]?"
- "What properties does [object] have?"

**Implementation Questions** → Route to `04-USAGE-PATTERNS-RAG.md`

- "How do I implement [feature]?"
- "Show me example of [pattern]?"
- "How do I integrate with [X]?"

**Layout & Grid Questions** → Route to `05-LAYOUT-STANDARDS-RAG.md`

- "How wide should the form be?"
- "How do I make two fields side-by-side?"
- "What is colSpan and how do I use it?"
- "How does responsive layout work?"
- "What are the grid spacing tokens?"

### Chunking Strategy

Recommended for vector databases:

1. **Chunk by h2 sections** (##) - optimal semantic units
2. **Include document metadata** in each chunk for context
3. **Maintain code examples** intact - don't split mid-example
4. **Preserve tables** as complete units
5. **Overlap** 1-2 sentences between chunks for continuity

### Embedding Metadata

Include in vector metadata:

```json
{
  "document": "01-ARCHITECTURE-RAG.md",
  "section": "ValidationEngine",
  "doc_type": "technical_spec",
  "version": "2.1-RAG",
  "status": "production",
  "topics": ["validation", "api", "core-component"]
}
```

---

## Verification Status

### Content Accuracy

- ✅ All code examples tested and verified
- ✅ API interfaces match source code
- ✅ JSON schemas validated against implementation
- ✅ File paths and locations verified
- ✅ Test coverage numbers confirmed
- ✅ Implementation status accurate as of 2026-02-21

### Coverage Completeness

- ✅ All core engines documented
- ✅ All field types covered
- ✅ All validators documented
- ✅ Common patterns included
- ✅ Layout standards and grid system documented
- ⚠️ React component tests not yet implemented (noted in docs)
- ⚠️ Cross-field validation format still evolving (noted in docs)
- ⚠️ Layout engine support (ValidationEngine colSpan, FieldContainer grid) pending implementation

---

## Source Documentation Reference

These AI-optimized documents consolidate and enhance:

- `../ARCHITECTURE.md` (original architecture doc)
- `../USAGE_GUIDE.md` (original usage guide)
- `../VALIDATION_GUIDE.md` (original validation guide)
- Source code documentation in `src/` folder
- Unit tests in `tests/` folder

**Advantage of RAG Docs**:

- Single, authoritative version per topic
- Structured for AI comprehension
- Enhanced with practical examples
- Factually verified against source
- Optimized for vector search and retrieval

---

## Maintenance

### Update Triggers

- New features added to codebase
- API changes in core engines
- Schema structure changes
- New validators or field types
- Architectural decisions

### Update Process

1. Verify changes in source code
2. Update relevant document sections
3. Test all code examples
4. Validate JSON schemas
5. Update version numbers and dates
6. Re-verify factual accuracy

### Version History

- **2.2-RAG** (2026-02-21): Added 05-LAYOUT-STANDARDS-RAG.md, cross-references across all documents
- **2.1-RAG** (2026-02-14): Initial AI-optimized documentation set

---

## Contact & Contributions

For questions about this documentation:

- Check source code: `apps/form-engine/src/`
- Run tests: `pnpm test`
- Review examples: `apps/form-engine/schemas/`

To contribute improvements:

1. Verify factual accuracy against source
2. Maintain document structure convention
3. Include practical examples
4. Test all code samples
5. Update metadata and version

---

**End of Documentation Index**
