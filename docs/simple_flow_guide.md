# GraphRAG: Simple Flow Example 🎮

Let me show you **exactly** what happens with your **dino-game** code!

---

## 📥 Step 1: You Give Me a GitHub Link

```
https://github.com/Vasu7389/react-project-ideas/tree/master/day006/dino-game
```

---

## 📂 Step 2: I Download Your Code

Your file: **`src/App.js`**

```javascript
import "./App.css";
import Dino from "./components/Dino/Dino";

function App() {
  return (
    <div className="App">
      <Dino />
    </div>
  );
}

export default App;
```

I save it as: **`ragtest/input/src_App.js.txt`**

But I add special headers:
```
START FILE: src/App.js
LANGUAGE: js
-----------------------------------
import "./App.css";
import Dino from "./components/Dino/Dino";
...
```

---

## 🤖 Step 3: AI Reads Your Code

The AI looks at `src/App.js` and thinks:

> "I see a **FILE** called `src/App.js`"
> 
> "I see a **FUNCTION** called `App`"
> 
> "I see it **IMPORTS** something called `Dino`"

---

## 💾 Step 4: AI Creates Nodes (Entities)

The AI creates **3 nodes**:

| Node Name | Type | Description |
|-----------|------|-------------|
| `SRC_APP_JS` | FILE | File located at src/App.js |
| `APP` | FUNCTION | Function App in src/App.js |
| `DINO` | CLASS | Component Dino imported in src/App.js |

These are saved in: **`ragtest/output/entities.parquet`**

---

## 🔗 Step 5: AI Creates Connections (Relationships)

The AI creates **2 connections**:

| From | To | Why | Strength |
|------|----|----|----------|
| `SRC_APP_JS` | `DINO` | src/App.js imports Dino | 8 |
| `APP` | `SRC_APP_JS` | App is defined in src/App.js | 10 |

These are saved in: **`ragtest/output/relationships.parquet`**

---

## 🌐 Step 6: Backend Prepares the Graph

When you visit `http://127.0.0.1:8000/api/graph`, the backend reads the files and creates JSON:

```json
{
  "nodes": [
    {"id": "SRC_APP_JS", "name": "SRC_APP_JS", "type": "FILE"},
    {"id": "APP", "name": "APP", "type": "FUNCTION"},
    {"id": "DINO", "name": "DINO", "type": "CLASS"}
  ],
  "links": [
    {"source": "SRC_APP_JS", "target": "DINO"},
    {"source": "APP", "target": "SRC_APP_JS"}
  ]
}
```

---

## 🎨 Step 7: Frontend Draws the Graph

The frontend sees:
- **3 circles** (nodes): `SRC_APP_JS`, `APP`, `DINO`
- **2 lines** (links): connecting them

**How it connects**:
- Link says `"source": "SRC_APP_JS"` → Find node with `"id": "SRC_APP_JS"` ✅
- Link says `"target": "DINO"` → Find node with `"id": "DINO"` ✅
- Draw a line between them!

---

## 🖼️ Visual Result

```
    [SRC_APP_JS]
       /      \
      /        \
   [APP]    [DINO]
```

**Meaning**:
- The **file** `src/App.js` imports **Dino**
- The **function** `App` is inside the **file** `src/App.js`

---

## 🔍 Real Data from Your System

### Your Actual Nodes (from `entities.parquet`):
```
SRC_APP_JS          → FILE
APP                 → FUNCTION
DINO                → CLASS
SRC_COMPONENTS_DINO → FILE
```

### Your Actual Connections (from `relationships.parquet`):
```
SRC_APP_JS → DINO           (imports)
APP → SRC_APP_JS            (defined in)
DINO → SRC_COMPONENTS_DINO  (defined in)
```

---

## 🎯 Summary: The Magic Formula

```
GitHub Code
    ↓
Download & Add Headers
    ↓
AI Reads Code
    ↓
AI Creates: Nodes (entities.parquet) + Connections (relationships.parquet)
    ↓
Backend Reads Files → Creates JSON
    ↓
Frontend Draws Graph
```

**Key Point**: The `id` in nodes **MUST MATCH** the `source`/`target` in links!

Example:
- Node: `{"id": "DINO"}`
- Link: `{"source": "SRC_APP_JS", "target": "DINO"}` ← This `"DINO"` matches!

---

---

## 🔄 How Files Are Processed (Your Question!)

### Does AI read all files together or one by one?

**Answer: CHUNKS, not whole files!**

Here's what actually happens:

### Step 1: Files → Chunks
Your 3 files are broken into **small pieces** (chunks):

**Settings** ([`settings.yaml`](file:///c:/Users/202317/.gemini/antigravity/scratch/GrapgRagMain/ragtest/settings.yaml#L46-L49)):
```yaml
chunks:
  size: 1200        # Each chunk = 1200 characters
  overlap: 100      # Chunks overlap by 100 characters
```

**Example**:
- `src/App.js` (259 chars) → **1 chunk**
- `src/components/Dino/Dino.js` (1583 chars) → **2 chunks**
- `src/index.js` (342 chars) → **1 chunk**

**Total: 4 chunks** (not 3 files!)

### Step 2: AI Processes Chunks in Parallel

**Configuration** ([`settings.yaml`](file:///c:/Users/202317/.gemini/antigravity/scratch/GrapgRagMain/ragtest/settings.yaml#L17)):
```yaml
concurrent_requests: 25  # Process up to 25 chunks at the same time!
```

**What this means**:
```
Chunk 1 (App.js)           → AI #1 → Finds: SRC_APP_JS, APP, DINO
Chunk 2 (Dino.js part 1)   → AI #2 → Finds: DINO, RENDER
Chunk 3 (Dino.js part 2)   → AI #3 → Finds: COMPONENTDIDMOUNT
Chunk 4 (index.js)         → AI #4 → Finds: SRC_INDEX_JS, REACTDOM
```

**All 4 run at the SAME TIME!** ⚡

### Step 3: Merge Results

After all chunks finish, GraphRAG **combines** the entities:
- If Chunk 1 found `DINO` and Chunk 2 also found `DINO` → Merge into 1 entity
- All relationships are collected together

### Visual Timeline

```
Time 0s:  Start processing
          ↓
Time 1s:  [Chunk 1] [Chunk 2] [Chunk 3] [Chunk 4]  ← All running in parallel
          ↓         ↓         ↓         ↓
Time 5s:  Results merge → entities.parquet + relationships.parquet
```

### Why Chunks Instead of Whole Files?

1. **Large Files**: A 10,000-line file would be too big for the AI to read at once
2. **Speed**: Parallel processing = faster
3. **Cost**: Smaller chunks = cheaper API calls

### Your Actual Processing

Looking at your logs, you had:
- **3 files** → **Split into chunks** → **Processed in parallel**
- Progress: `1/3`, `2/3`, `3/3` (these are chunk batches, not individual files!)

---

## ✅ That's It!

Now you can:
1. **Ask questions**: "How does App.js work?"
2. **See the graph**: Visual connections between files/functions
3. **Understand code**: Without reading every file!

**Bonus**: The system processes files **in parallel** (not one-by-one), making it super fast! ⚡
