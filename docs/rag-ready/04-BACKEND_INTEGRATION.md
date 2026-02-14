# DynUI Backend Integration Map (Tier 4)

## 1. Overview
The DynUI Backend (`dyn-ui-backend`) serves as the dynamic configuration engine for the frontend. It manages component configurations, user-specific UI states, and domain models.

## 2. API Routing Map (Key Endpoints)

### **Component Management**
- `GET /api/components` - List all configured component instances.
- `GET /api/components/:id` - Get detailed configuration for a specific instance.
- `POST /api/components` - Create a new component configuration (e.g., a new Page or specialized Button).
- `PATCH /api/components/:id/properties` - Update the dynamic properties (JSON) of a component.

### **UI State & Layouts**
- `GET /api/layouts/:slug` - Fetch a predefined layout structure.
- `POST /api/layouts` - Save a new layout composition.

## 3. Data Models (Prisma Schema Reference)

### **ComponentConfiguration**
The central model for dynamic UI.
```prisma
model ComponentConfiguration {
  id         String   @id @default(uuid())
  name       String   // Internal name (e.g., "MainDashboardButton")
  type       String   // DynUI component type (e.g., "DynButton")
  properties Json     // Dynamic props: { "variant": "primary", "icon": "check" }
  createdAt  DateTime @default(now())
  updatedAt  DateTime @updatedAt
}
```

### **LayoutNode**
Defines the hierarchy of components.
```prisma
model LayoutNode {
  id          String   @id @default(uuid())
  componentId String
  parentId    String?
  order       Int
  config      Json
}
```

## 4. Implementation Protocol for Agents
1.  **Check Capability**: See if the feature can be handled by updating a `ComponentConfiguration` via API.
2.  **Verify Schema**: Open `packages/dyn-ui-backend/prisma/schema.prisma` for the source of truth on relationships.
3.  **Controller Pattern**: Follow the existing logic in `packages/dyn-ui-backend/src/api/controllers/ComponentController.ts` when implementing new backend-driven UI features.
