---
title: Code Examples
type: examples
category: reference
version: 1.0.0
last_updated: 2026-02-13
---

# DynUI Code Examples

> **Real-world implementation patterns**

## 📝 Forms

### Example 1: Login Form

```tsx
import { DynBox, DynInput, DynButton, DynFieldContainer, DynCheckbox } from '@dyn-ui/react';

function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    // Login logic
    setLoading(false);
  };

  return (
    <DynBox
      as="form"
      onSubmit={handleSubmit}
      gap="md"
      direction="vertical"
      style={{ maxWidth: '400px' }}
    >
      <h2>Sign In</h2>

      <DynFieldContainer label="Email" required>
        <DynInput
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={setEmail}
          size="md"
          required
        />
      </DynFieldContainer>

      <DynFieldContainer label="Password" required>
        <DynInput
          type="password"
          value={password}
          onChange={setPassword}
          size="md"
          required
        />
      </DynFieldContainer>

      <DynCheckbox
        checked={remember}
        onChange={setRemember}
        color="primary"
      >
        Remember me
      </DynCheckbox>

      <DynButton
        type="submit"
        color="primary"
        size="md"
        loading={loading}
        style={{ width: '100%' }}
      >
        Sign In
      </DynButton>
    </DynBox>
  );
}
```

### Example 2: Multi-Step Registration

```tsx
import { DynBox, DynStepper, DynButton, DynInput, DynSelect, DynFieldContainer } from '@dyn-ui/react';

function RegistrationWizard() {
  const [step, setStep] = useState(0);
  
  const steps = [
    { label: 'Personal Info', key: 'personal' },
    { label: 'Account Details', key: 'account' },
    { label: 'Preferences', key: 'preferences' }
  ];

  const renderStep = () => {
    switch (step) {
      case 0:
        return (
          <DynBox gap="md" direction="vertical">
            <DynFieldContainer label="First Name" required>
              <DynInput size="md" />
            </DynFieldContainer>
            <DynFieldContainer label="Last Name" required>
              <DynInput size="md" />
            </DynFieldContainer>
          </DynBox>
        );
      case 1:
        return (
          <DynBox gap="md" direction="vertical">
            <DynFieldContainer label="Email" required>
              <DynInput type="email" size="md" />
            </DynFieldContainer>
            <DynFieldContainer label="Password" required>
              <DynInput type="password" size="md" />
            </DynFieldContainer>
          </DynBox>
        );
      case 2:
        return (
          <DynBox gap="md" direction="vertical">
            <DynFieldContainer label="Role">
              <DynSelect
                size="md"
                options={[
                  { value: 'dev', label: 'Developer' },
                  { value: 'designer', label: 'Designer' }
                ]}
              />
            </DynFieldContainer>
          </DynBox>
        );
    }
  };

  return (
    <DynBox gap="lg" direction="vertical" style={{ maxWidth: '600px' }}>
      <DynStepper steps={steps} currentStep={step} />
      
      {renderStep()}
      
      <DynBox display="flex" justify="between">
        <DynButton
          variant="outline"
          onClick={() => setStep(step - 1)}
          disabled={step === 0}
        >
          Back
        </DynButton>
        <DynButton
          color="primary"
          onClick={() => setStep(step + 1)}
        >
          {step === steps.length - 1 ? 'Submit' : 'Next'}
        </DynButton>
      </DynBox>
    </DynBox>
  );
}
```

## 🎴 Layouts

### Example 3: Dashboard Grid

```tsx
import { DynGrid, DynBox, DynProgress, DynBadge } from '@dyn-ui/react';

function Dashboard() {
  const metrics = [
    { label: 'Revenue', value: '$45,231', change: '+12%', status: 'success' },
    { label: 'Users', value: '1,234', change: '+5%', status: 'success' },
    { label: 'Orders', value: '456', change: '-2%', status: 'danger' },
    { label: 'Conversion', value: '3.2%', change: '+0.5%', status: 'success' }
  ];

  return (
    <DynGrid
      columns={{ mobile: 1, tablet: 2, desktop: 4 }}
      gap="md"
    >
      {metrics.map((metric) => (
        <DynBox
          key={metric.label}
          padding="md"
          gap="sm"
          direction="vertical"
          style={{
            backgroundColor: 'var(--dyn-color-surface)',
            borderRadius: 'var(--dyn-border-radius-md)',
            border: '1px solid var(--dyn-color-border)'
          }}
        >
          <span style={{ 
            fontSize: 'var(--dyn-font-size-sm)',
            color: 'var(--dyn-color-text-secondary)'
          }}>
            {metric.label}
          </span>
          <DynBox display="flex" align="center" justify="between">
            <span style={{ 
              fontSize: 'var(--dyn-font-size-3xl)',
              fontWeight: 'var(--dyn-font-weight-bold)'
            }}>
              {metric.value}
            </span>
            <DynBadge 
              color={metric.status as any} 
              size="sm"
            >
              {metric.change}
            </DynBadge>
          </DynBox>
        </DynBox>
      ))}
    </DynGrid>
  );
}
```

### Example 4: App Layout with Sidebar

```tsx
import { DynBox, DynAppbar, DynSidebar, DynContainer } from '@dyn-ui/react';

function AppLayout({ children }: { children: ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <DynBox style={{ minHeight: '100vh' }}>
      <DynAppbar
        logo={<Logo />}
        actions={<UserMenu />}
        onMenuClick={() => setSidebarOpen(!sidebarOpen)}
      />
      
      <DynBox display="flex" style={{ height: 'calc(100vh - 64px)' }}>
        <DynSidebar
          collapsed={!sidebarOpen}
          items={[
            { label: 'Dashboard', icon: <IconDashboard />, path: '/' },
            { label: 'Users', icon: <IconUsers />, path: '/users' },
            { label: 'Settings', icon: <IconSettings />, path: '/settings' }
          ]}
        />
        
        <DynBox
          style={{
            flex: 1,
            overflow: 'auto',
            backgroundColor: 'var(--dyn-color-background)'
          }}
        >
          <DynContainer padding="lg">
            {children}
          </DynContainer>
        </DynBox>
      </DynBox>
    </DynBox>
  );
}
```

## 📊 Data Display

### Example 5: User List with Actions

```tsx
import { DynTable, DynBox, DynButton, DynBadge, DynAvatar } from '@dyn-ui/react';

function UserList() {
  const users = [
    { id: 1, name: 'John Doe', email: 'john@example.com', role: 'Admin', status: 'active' },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'User', status: 'active' },
    { id: 3, name: 'Bob Johnson', email: 'bob@example.com', role: 'User', status: 'inactive' }
  ];

  return (
    <DynTable
      columns={[
        {
          key: 'name',
          label: 'User',
          sortable: true,
          render: (value, row) => (
            <DynBox display="flex" align="center" gap="sm">
              <DynAvatar size="sm" />
              <span>{value}</span>
            </DynBox>
          )
        },
        { key: 'email', label: 'Email' },
        {
          key: 'status',
          label: 'Status',
          render: (value) => (
            <DynBadge color={value === 'active' ? 'success' : 'info'} size="sm">
              {value}
            </DynBadge>
          )
        },
        {
          key: 'actions',
          label: 'Actions',
          render: (_, row) => (
            <DynBox display="flex" gap="xs">
              <DynButton size="sm" variant="outline">Edit</DynButton>
              <DynButton size="sm" variant="outline" color="danger">Delete</DynButton>
            </DynBox>
          )
        }
      ]}
      data={users}
      size="md"
      striped
      hoverable
    />
  );
}
```

## ⚙️ Complex Interactions

### Example 6: Modal Confirmation Dialog

```tsx
import { DynModal, DynButton, DynBox } from '@dyn-ui/react';

function DeleteConfirmation({ isOpen, onClose, onConfirm, itemName }: Props) {
  const [deleting, setDeleting] = useState(false);

  const handleConfirm = async () => {
    setDeleting(true);
    await onConfirm();
    setDeleting(false);
    onClose();
  };

  return (
    <DynModal
      open={isOpen}
      onClose={onClose}
      size="md"
      title="Confirm Deletion"
      actions={
        <DynBox display="flex" gap="sm" justify="end">
          <DynButton 
            variant="outline" 
            onClick={onClose}
            disabled={deleting}
          >
            Cancel
          </DynButton>
          <DynButton
            color="danger"
            onClick={handleConfirm}
            loading={deleting}
          >
            Delete
          </DynButton>
        </DynBox>
      }
    >
      <p>
        Are you sure you want to delete <strong>{itemName}</strong>? 
        This action cannot be undone.
      </p>
    </DynModal>
  );
}
```

## 🔗 Related Documentation

- [Quick Start](01-QUICK_START.md) - Getting started
- [Component Catalog](03-COMPONENT_CATALOG.md) - All components
- [Styling Guide](04-STYLING_GUIDE.md) - Styling patterns

---

**More examples**: Check individual component docs in `components/` folder.
