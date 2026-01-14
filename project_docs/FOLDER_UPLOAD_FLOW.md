# 📂 Folder Upload & Analysis Flow

Here is exactly how the new **Local Folder Upload** system works, step-by-step.

---

## 1. The Frontend (React UI)

**File:** `simple_rag_app/frontend/src/App.jsx`

When you select "Folder Upload" and pick a folder:

1.  **Browser Selection**: The `<input type="file" webkitdirectory />` allows you to select a recursive directory.
2.  **Filtering (Client-Side)**: We do a quick check to skip `node_modules` or `.git` folders immediately to save bandwidth.
3.  **Packing**: All selected files are packed into a `FormData` object.
4.  **Sending**: The frontend sends a `POST` request to `http://localhost:8000/api/ingest/upload`.

```javascript
// frontend logic
const formData = new FormData();
for (let file of selectedFiles) {
    if (!file.path.includes("node_modules")) {
        formData.append('files', file);
    }
}
fetch('/api/ingest/upload', { method: 'POST', body: formData });
```

---

## 2. The Backend (Ingestion Agent) 🤖

**File:** `simple_rag_app/main.py` & `agents/ingestion_agent.py`

Instead of hardcoded rules, we now use an **AI Agent** to decide what to ingest.

### **Step A: Tech Stack Analysis** 🧠
1.  The Agent receives the list of all filenames in the uploaded folder.
2.  It sends this list to **GPT-4o-mini** with a prompt: *"Analyze this structure and identify the tech stack."*
3.  The LLM replies with a config:
    *   **Tech Stack**: e.g., "Salesforce Apex/LWC" or "React + Python".
    *   **Allowed Extensions**: e.g., `['.cls', '.trigger', '.js', '.xml']`.
    *   **Ignored Patterns**: e.g., `['node_modules', '__pycache__']`.

### **Step B: Dynamic Filtering** 🧹
The backend uses the Agent's config to filter files component-by-component.

*   **Salesforce Support**: Explicitly trained to find `.cls`, `.trigger`, `.page` files.
*   **Debug Logs**: We print the exact decision process to the terminal:
    *   `[DEBUG] File Summary Sent to LLM`
    *   `[DEBUG] Raw LLM Response`
    *   `Skipping unsupported extension: style.css`

### **Step C: Saving** 💾
Only the "Smart Filtered" files are saved to `ragtest/input`.

### **Step D: Indexing** ⚙️
We trigger `graphrag index` to build the knowledge graph from the clean data.

---

## 3. GraphRAG Settings

**File:** `ragtest/settings.yaml`

We made a critical change here:
```yaml
input:
  file_type: text
  file_pattern: ".*"  # <--- CHANGED: Allows .py, .js, etc.
```
By default, GraphRAG only sees `.txt` files. We changed this to `.*` so it accepts the code files we just uploaded.

---

## 🔄 The Complete Flow

```mermaid
graph TD
    A[User Selects Folder] -->|Browser| B[Frontend Filters (node_modules)]
    B -->|POST Upload| C[Backend API]
    C -->|Smart Filter| D{Is Code File?}
    D -->|No (.css, .exe)| E[Skip]
    D -->|Yes (.py, .js)| F[Save to /input]
    F --> G[Trigger GraphRAG Index]
    G --> H[Build Knowledge Graph]
    H --> I[Ready for Querying!]
```

---

## ✅ Why This is Better

1.  **No Git Needed**: You don't need to push to GitHub first.
2.  **Clean Data**: We strip out junk files (CSS, cache) so the AI focuses only on logic.
3.  **Fast**: Direct local transfer is faster than cloning.

You now have a **Local Code Analysis** engine running on your machine! 🚀
