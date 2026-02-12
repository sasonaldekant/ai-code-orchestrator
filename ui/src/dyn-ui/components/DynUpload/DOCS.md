# DynUpload Documentation

## 📌 Overview

**Category:** Molecule / Form
**Status:** Stable

`DynUpload` is a flexible file upload component that supports drag-and-drop, multiple file selection, and provides immediate visual feedback for selected files. It integrates cleanly with standard form fields and supports constraints like file type filtering and size limits.

## 🛠 Usage

### Basic File Drop

```tsx
import { DynUpload } from '@dyn-ui/react';

function MyForm() {
  const handleUpload = (files: File[]) => {
    console.log('Selected files:', files);
  };

  return (
    <DynUpload
      label="Upload Documents"
      description="Drag and drop or click to select PDF files"
      accept=".pdf"
      onUpload={handleUpload}
      multiple
    />
  );
}
```

### Controlled File List

```tsx
<DynUpload
  fileList={myFiles}
  onFileListChange={(newList) => setMyFiles(newList)}
  maxSize={5 * 1024 * 1024} // 5MB
  showFileList={true}
/>
```

## ⚙️ Properties (API)

### DynUpload Props

| Prop           | Type                      | Default | Description                                       | Required |
| :------------- | :------------------------ | :------ | :------------------------------------------------ | :------: |
| `onUpload`     | `(files: File[]) => void` | -       | Callback triggered when files are chosen.         |    No    |
| `accept`       | `string`                  | -       | Permitted file extensions (e.g., `.png, .jpg`).   |    No    |
| `multiple`     | `boolean`                 | `false` | Enable multi-selection.                           |    No    |
| `maxSize`      | `number`                  | -       | Maximum allowed bytes per file.                   |    No    |
| `label`        | `ReactNode`               | -       | Primary instruction text in the drop zone.        |    No    |
| `description`  | `ReactNode`               | -       | Secondary text (e.g., "Max size 2MB").            |    No    |
| `disabled`     | `boolean`                 | `false` | Disables interaction and greys out the UI.        |    No    |
| `showFileList` | `boolean`                 | `true`  | Automatically renders the list of selected files. |    No    |
| `fileList`     | `DynUploadFile[]`         | -       | Manual state management for file tracking.        |    No    |
| `error`        | `boolean`                 | `false` | Toggles the error visual state.                   |    No    |
| `errorMessage` | `string`                  | -       | Specific text to display when `error` is true.    |    No    |

## 🎨 Design Tokens

- **Dropzone BG**: `--dyn-upload-dropzone-bg`
- **Dash Border**: `--dyn-upload-border-dash`
- **Active Border**: `--dyn-upload-border-active` (on drag over)
- **File Text**: `--dyn-upload-file-text`

## ♿ Accessibility (A11y)

- **Input**: Uses a hidden `<input type="file">` for native OS file picking.
- **Keyboard**:
  - The dropzone is focusable and can be triggered via `Enter` or `Space`.
  - File removal buttons in the list are accessible via `Tab`.
- **States**: Uses `aria-invalid` and `aria-disabled` correctly.

## 📝 Best Practices

- ✅ Always specify `accept` to prevent users from picking unsupported files.
- ✅ Use `description` to inform users about `maxSize` limits.
- ✅ Enable `multiple` only when it makes sense for the backend processing.
- ❌ Don't rely solely on client-side `maxSize`; always verify on the server.
- ❌ Avoid using `showFileList={false}` unless you are rendering your own custom file list elsewhere.
- ❌ Don't use a dropzone if the interaction area is smaller than 100x100px.
