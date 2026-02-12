# DynTextArea Documentation

## 📌 Overview

**Category:** Molecule / Form
**Status:** Stable

`DynTextArea` is a multi-line text input component designed for long-form user input. It provides built-in support for character counting, automatic height adjustment (auto-resize), and seamless integration with the `useDynFieldValidation` system. It utilizes `DynFieldContainer` to ensure a consistent look and feel across the entire form ecosystem.

## 🛠 Usage

### Basic Usage

```tsx
import { DynTextArea } from '@dyn-ui/react';

function UserBio() {
  return (
    <DynTextArea
      label="Short Biography"
      placeholder="Tell us about yourself..."
      rows={5}
      showCount
      maxLength={250}
    />
  );
}
```

### Auto-Resizing Textarea

The `autoResize` feature allows the textarea to grow vertically as the user types, up to a specified `maxRows`.

```tsx
<DynTextArea label="Comments" autoResize maxRows={12} rows={3} />
```

## ⚙️ Properties (API)

### DynTextArea Props

| Prop           | Type                      | Default      | Description                                    | Required |
| :------------- | :------------------------ | :----------- | :--------------------------------------------- | :------: |
| `name`         | `string`                  | -            | Technical name of the field.                   |    No    |
| `label`        | `string`                  | -            | User-facing label shown above the input.       |    No    |
| `value`        | `string`                  | -            | Controlled value of the textarea.              |    No    |
| `placeholder`  | `string`                  | -            | Hint text shown when the input is empty.       |    No    |
| `rows`         | `number`                  | `4`          | Initial number of visible text lines.          |    No    |
| `cols`         | `number`                  | -            | Number of visible columns.                     |    No    |
| `autoResize`   | `boolean`                 | `false`      | Automatically expands height based on content. |    No    |
| `maxRows`      | `number`                  | `10`         | Maximum growth limit for `autoResize`.         |    No    |
| `showCount`    | `boolean`                 | `false`      | Displays the current character count.          |    No    |
| `maxLength`    | `number`                  | -            | Enforces a maximum character limit.            |    No    |
| `resize`       | `DynTextAreaResize`       | `'vertical'` | Controls manual resize handle behavior.        |    No    |
| `disabled`     | `boolean`                 | `false`      | Prevents user input and interaction.           |    No    |
| `readonly`     | `boolean`                 | `false`      | Value is visible but cannot be edited.         |    No    |
| `required`     | `boolean`                 | `false`      | Marks the field as mandatory with an asterisk. |    No    |
| `help`         | `string`                  | -            | Helper text displayed below the field.         |    No    |
| `errorMessage` | `string`                  | -            | Custom error message text.                     |    No    |
| `validation`   | `DynValidationRule[]`     | -            | List of rules for the validation system.       |    No    |
| `onChange`     | `(value: string) => void` | -            | Triggered whenever the text content changes.   |    No    |

## 🔌 Technical Reference (Ref)

The `DynTextAreaRef` allows imperative interactions with the underlying DOM element:

- `getValue()` / `setValue(val)`: Direct state management.
- `focus()` / `blur()`: Manual focus control.
- `validate()`: Triggers the field validation manually.
- `clear()`: Wipes the content and resets validation status.
- `getElement()`: Returns the raw `<textarea>` HTML element.

## 🎨 Design Tokens

- **Input BG**: `--dyn-input-bg`
- **Border Focus**: `--dyn-input-border-focus`
- **Text Color**: `--dyn-input-text`
- **Error Accent**: `--dyn-color-danger`

## ♿ Accessibility (A11y)

- **Semantic HTML**: Uses the native `<textarea>` tag for built-in keyboard support.
- **Labels**: Correctly linked via `htmlFor` and `id` in the `DynFieldContainer`.
- **States**:
  - `aria-invalid` reflects current validation errors.
  - `aria-required` signifies mandatory input for screen readers.
- **Support**: Character count is marked as `aria-hidden` as it is often redundant when `maxLength` and `aria-describedby` are properly configured.

## 📝 Best Practices

- ✅ Use `autoResize` for a modern "chat-like" or "notes" experience.
- ✅ Always provide a meaningful `label` even if `placeholder` is present.
- ✅ Set a reasonable `maxRows` to prevent the textarea from taking over the entire screen.
- ❌ Don't use `showCount` if there is no character limit as it adds visual noise.
- ❌ Avoid `resize="both"` in fixed-width layouts as it may break the container.
- ❌ Don't use a textarea for short phrases like names or emails (use `DynInput`).
