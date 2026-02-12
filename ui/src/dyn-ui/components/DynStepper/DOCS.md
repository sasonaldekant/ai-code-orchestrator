# DynStepper Documentation

## 📌 Overview

**Category:** Organism / Navigation  
**Status:** Stable

`DynStepper` is a premium navigation component designed to manage multi-step workflows. It breaks down complex tasks into manageable chunks, providing clear progress indicators and intuitive navigation.

Whether you're building a multi-page registration form, a checkout process, or a complex wizard, `DynStepper` offers the flexibility of multiple visual themes and robust state management.

## 🛠 Usage

### Basic Numbered Stepper (Uncontrolled)

For simple wizards where state management is internal.

```tsx
import { DynStepper } from '@dyn-ui/react';

const steps = [
  { id: '1', title: 'Account', content: <AccountForm /> },
  { id: '2', title: 'Preferences', content: <PrefsForm /> },
  { id: '3', title: 'Verify', content: <CodeForm /> },
];

<DynStepper steps={steps} defaultActiveStep={0} />;
```

### Controlled Execution with Validation

Best for enterprise forms where each step must be validated before moving forward.

```tsx
function RegistrationWizard() {
  const [active, setActive] = useState(0);
  const stepperRef = useRef<DynStepperRef>(null);

  const handleNext = async () => {
    const isStepValid = await validateMyForm(active);
    if (isStepValid) {
      stepperRef.current?.nextStep();
    }
  };

  return (
    <DynStack gap="lg">
      <DynStepper
        ref={stepperRef}
        steps={steps}
        activeStep={active}
        onChange={(index) => setActive(index)}
        linear={true}
      />
      <DynButton onClick={handleNext}>Continue</DynButton>
    </DynStack>
  );
}
```

## ⚙️ Properties (API)

### DynStepperProps

Defines the configuration for the main Stepper component.

| Prop                | Type                            | Default        | Description                                            |
| :------------------ | :------------------------------ | :------------- | :----------------------------------------------------- |
| `steps`             | `StepItem[]`                    | `[]`           | **Required.** Array of step configurations.            |
| `activeStep`        | `number`                        | -              | Current 0-based index of the active step (Controlled). |
| `defaultActiveStep` | `number`                        | `0`            | Initial active step index (Uncontrolled).              |
| `value`             | `string \| number`              | -              | **Deprecated.** Use `activeStep`.                      |
| `defaultValue`      | `string \| number`              | `0`            | **Deprecated.** Use `defaultActiveStep`.               |
| `onChange`          | `(val, step, index) => void`    | -              | Callback triggered when active step changes.           |
| `orientation`       | `'horizontal' \| 'vertical'`    | `'horizontal'` | Layout direction of the step list.                     |
| `variant`           | `StepperVariant`                | `'numbered'`   | Visual theme (`numbered`, `dots`, `progress`, `tabs`). |
| `size`              | `'sm' \| 'md' \| 'lg'`          | `'md'`         | Scale of indicators and typography.                    |
| `linear`            | `boolean`                       | `true`         | Prevents skip-ahead navigation.                        |
| `showLabels`        | `boolean`                       | `true`         | Show/hide step titles.                                 |
| `showDescription`   | `boolean`                       | `false`        | Show/hide step subtitles.                              |
| `clickableSteps`    | `boolean`                       | `true`         | Allow clicking headers to navigate.                    |
| `renderStepContent` | `(step, index) => Node`         | -              | Override panel rendering.                              |
| `renderStepIcon`    | `(step, index, active) => Node` | -              | Override indicator rendering.                          |
| `id`                | `string`                        | -              | Unique identifier.                                     |
| `stepClassName`     | `string`                        | -              | CSS class for step items.                              |
| `contentClassName`  | `string`                        | -              | CSS class for the content container.                   |

### StepItem

Properties for individual step entries in the `steps` array.

| Prop          | Type                  | Description                                                    |
| :------------ | :-------------------- | :------------------------------------------------------------- |
| `id`          | `string`              | **Required.** Unique ID for the step.                          |
| `title`       | `string`              | Primary header text.                                           |
| `label`       | `string`              | Alias for `title`.                                             |
| `content`     | `ReactNode \| Fn`     | UI body. Can be a function: `(props) => Node`.                 |
| `description` | `string`              | Sub-label text.                                                |
| `icon`        | `string \| ReactNode` | Lucide icon name or custom element.                            |
| `completed`   | `boolean`             | Force success state.                                           |
| `error`       | `boolean`             | Force error state.                                             |
| `disabled`    | `boolean`             | Prevents interaction.                                          |
| `optional`    | `boolean`             | Displays an "(optional)" hint.                                 |
| `tooltip`     | `string`              | Native title attribute on the header button.                   |
| `validator`   | `(step) => boolean`   | Custom logic check before allowing navigation.                 |
| `status`      | `StepStatus`          | Manual status override (`active`, `completed`, `error`, etc.). |

## 🔌 Technical Reference (Types)

### Status & State Enums

The stepper uses specific keywords to determine visual states:

```typescript
export type StepStatus =
  | 'inactive'
  | 'active'
  | 'completed'
  | 'error'
  | 'disabled';
export type StepState = 'pending' | 'active' | 'completed' | 'error';
```

### Imperative API (`DynStepperRef`)

When using a `ref`, the following methods are available:

- `nextStep()`: Moves to the next available step. Returns `boolean` (success).
- `prevStep()`: Moves to the previous step. Returns `boolean` (success).
- `goToStep(index)`: Jumps to a specific index. Validates `linear` rules.
- `getCurrentStep()`: Returns the current 0-based index.
- `getStepData(index)`: Returns the `StepItem` for that index.
- `validateStep(index)`: Runs the `validator` (if any) and returns result.
- `completeStep(index)`: Marks a step as completed programmatically.
- `errorStep(index, hasError)`: Sets or clears the error state for a step.

### Advanced Props (`DynStepperAdvancedProps`)

Used for highly interactive or persisted wizards:

- `enableValidation`: Toggles integrated validation checks.
- `showProgress`: Shows an additional progress bar in supported variants.
- `animation`: Transition type (`none`, `fade`, `slide`).
- `persistState`: If true, saves the current step to local storage.
- `storageKey`: Key used for data persistence.

### Event Handlers (`StepEventHandlers`)

- `onNext`: Called before moving forward. Can block navigation by returning `false`.
- `onPrevious`: Called before moving backward.
- `onComplete`: Called when the final step is reached or completed.
- `onValidationError`: Called if a `validator` fails.

## 🎨 Design Tokens

- **Active Accent**: `--dyn-stepper-active-color`
- **Success Color**: `--dyn-stepper-success-color`
- **Error Color**: `--dyn-stepper-error-color`
- **Separator Line**: `--dyn-stepper-connector-color`
- **Indicator Rounding**: `--dyn-stepper-indicator-radius`

## ♿ Accessibility (A11y)

- **Landmarks**: Uses `<ol>` and `<li>` for semantic listing.
- **Roles**: Container is `role="group"` (default) or `role="tablist"` (tabs variant).
- **Keyboard Navigation**:
  - `ArrowRight`/`Down`: Navigate forward.
  - `ArrowLeft`/`Up`: Navigate backward.
  - `Home`/`End`: Jump to first/last steps.
- **ARIA Attributes**: Uses `aria-current="step"`, `aria-selected`, and `aria-invalid`.

## 📝 Best Practices

- ✅ Use `linear={true}` for onboarding or legal processes where sequence matters.
- ✅ Always provide `id` for steps to ensure stable DOM reconciliation.
- ✅ Use `clickableSteps={false}` for high-stakes flows to force use of "Next" buttons only.
- ❌ Don't nest Steppers within each other. If a step is complex, use `DynTabs` inside it instead.
- ❌ Avoid using `variant="progress"` if the user needs to jump between steps frequently.
