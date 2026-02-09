1. Ingest Domain Knowledge:

bash

# Ingest your database schema (C# EF Core)

python manage.py ingest database ./path/to/backend/Data

# Ingest your component library (React TypeScript)

python manage.py ingest component_library ./path/to/frontend/src/components 2. Run a Feature Request:

bash

# The orchestrator will plan, architect, implement, and test the feature

python manage.py run "Add a loyalty points summary to the checkout page" 3. Query Knowledge Base:

bash

# Ask questions about your ingested domain knowledge

python manage.py query "How does the Order entity relate to Customer?" 4. Check Costs:

bash

# View usage and cost reports

python manage.py cost
