# Walkthrough: Phase 13 - Database Content Ingestion 🗄️

## Overview

We have enabled the RAG system to ingest actual **data rows** from your database, not just the schema. This allows the AI to answer questions like _"What is the price of product X?"_ or _"Who is the user with email Y?"_.

## 🎯 Features Implemented

### 1. Hybrid Ingestion Engine (`DatabaseContentIngester`)

We implemented a flexible ingester that supports two modes:

#### Mode A: Direct SQL Connection 🔌

- Connects directly to MS SQL Server using `pyodbc`.
- Executes a custom SQL query (default: `SELECT * FROM Table`).
- Converts each row into a semantic document.
- **Best for:** Live environments, frequent updates, automation.

#### Mode B: JSON File Import 📂

- Fallback mode for secure/offline environments.
- Reads a JSON file containing a list of objects (rows).
- **Best for:** Ad-hoc ingestion, testing, restricted implementation.

### 2. Frontend Interface (`IngestionPanel`)

- Updated the **Ingestion Panel** with a new **"Database Content"** ingestion type.
- **Dynamic Form:**
  - Selecting "Direct SQL" shows inputs for Connection String and Query.
  - Selecting "JSON File" shows input for File Path.
- **Target Table:** Allows specifying the table name (e.g., `Products`) to tag the data correctly.

### 3. Backend API (`POST /admin/ingest/content`)

- New endpoint verifying input and routing to the correct ingestion logic.

## 📸 Usage

1.  Navigate to **Admin Panel** > **Ingestion**.
2.  Select **"Database Content"**.
3.  Choose your mode:
    - **SQL**: Enter connection string (e.g., `Driver={ODBC Driver 17 for SQL Server};Server=myServer;...`) and Table Name.
    - **JSON**: Enter the path to your exported JSON file (e.g., `E:\exports\products.json`).
4.  Click **"Ingest Knowledge"**.
5.  Validates and chunks the data into the vector store.

## 🚀 Next Steps

- Add "Scheduled Re-ingestion" for SQL mode.
- Add "Column selection" UI to ignore sensitive fields (like passwords).
