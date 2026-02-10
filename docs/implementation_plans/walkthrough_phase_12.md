# Walkthrough: Phase 12 - Knowledge Graph Visualization 🕸️

## Overview

We have added a visualization layer to the Knowledge Graph, allowing you to interactively explore the codebase structure directly from the Admin Panel.

## 🎯 Features Implemented

### 1. Backend API (`api/admin_routes.py`)

- **`POST /admin/graph/build`**: Triggers a full scan of the codebase to build the graph in-memory.
- **`GET /admin/graph`**: Returns the graph nodes and edges in JSON format for the frontend.

### 2. Frontend Visualization (`ui/src/components/admin/GraphTab.tsx`)

- **Interactive Graph:** Uses `react-force-graph-2d` to render the network.
- **Node Types:**
  - 🔵 **File**: Represents source files.
  - 🟡 **Class**: Represents classes defined in files.
  - 🟢 **Function**: Represents functions.
  - ⚪ **Module**: Represents imported modules.
- **Features:**
  - Zoom/Pan interaction.
  - Node dragging.
  - Hover for details.
  - "Rebuild Graph" button to refresh data.

### 3. Integration (`AdminLayout.tsx`)

- Added a new **"Knowledge Graph"** tab to the Admin Sidebar.

## 📸 Usage

1.  Navigate to **Admin Panel** > **Knowledge Graph** tab.
2.  Click **"Rebuild Graph"** to scan the current codebase.
3.  Explore the graph by dragging nodes or zooming in to see relationships (Defines, Imports, etc.).

## 🚀 Future Enhancements

- **Filter by Type:** Toggle visibility of specific node types.
- **Search:** Find specific nodes in the graph.
- **Click-to-Nav:** Click a file node to open it in the editor (requires File Browser integration).
