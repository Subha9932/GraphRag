# GraphRAG Search Methods: Local vs Global vs Community

## 🎯 The Three Search Methods Explained

GraphRAG offers **3 different ways** to search your code. Each is designed for different types of questions.

---

## 1️⃣ LOCAL Search (Currently Used ✅)

### **What It Does:**
Searches for **specific, detailed information** about particular entities and their immediate relationships.

### **Think of it as:**
🔍 **Zooming in** on a specific part of the code

### **Visual Representation:**
```
Your Codebase (Knowledge Graph):

        [User]
          ↓
    [AuthController] ←─ LOCAL SEARCH FOCUSES HERE
          ↓
    [UserService]
          ↓
    [Database]

LOCAL search finds:
- AuthController details
- Its direct connections
- Specific implementation
```

### **Best For:**
- ✅ "How does the login function work?"
- ✅ "What does authenticate() do?"
- ✅ "Where is the JWT token generated?"
- ✅ "How is password validation implemented?"

### **Example Query & Response:**

**Query:** "How does login work?"

**LOCAL Search Process:**
```
1. Find entities matching "login"
   → AuthController.login()
   → UserService.authenticate()
   
2. Get immediate neighbors
   → JWT token generation
   → Password validation
   → Database queries
   
3. Return detailed information
```

**Response:**
```markdown
## Login Implementation

The login function is implemented in `AuthController.login()`:

```python
@app.post("/auth/login")
async def login(credentials: LoginRequest):
    # Validate input
    if not credentials.email or not credentials.password:
        raise ValueError("Missing credentials")
    
    # Authenticate user
    user = await user_service.authenticate(
        credentials.email, 
        credentials.password
    )
    
    # Generate JWT token
    token = jwt.encode(
        {"user_id": user.id, "exp": datetime.now() + timedelta(hours=24)},
        SECRET_KEY
    )
    
    return {"token": token}
```

The process:
1. Receives credentials via POST request
2. Validates input format
3. Calls UserService.authenticate() to check password
4. Generates JWT token with 24-hour expiration
5. Returns token to client
```

**Characteristics:**
- ⚡ **Fast** (searches small subgraph)
- 📊 **Detailed** (code-level information)
- 🎯 **Precise** (focused on specific entities)

---

## 2️⃣ GLOBAL Search (Not Currently Used ❌)

### **What It Does:**
Searches across **the entire codebase** using high-level community summaries to answer broad questions.

### **Think of it as:**
🌍 **Zooming out** to see the big picture

### **Visual Representation:**
```
Your Codebase (Knowledge Graph):

┌─────────────────────────────────────┐
│  ENTIRE CODEBASE                    │
│                                     │
│  ┌──────────┐  ┌──────────┐       │
│  │  Auth    │  │   API    │       │
│  │ Module   │  │ Module   │       │
│  └──────────┘  └──────────┘       │
│                                     │
│  ┌──────────┐  ┌──────────┐       │
│  │ Database │  │ Frontend │       │
│  │ Module   │  │ Module   │       │
│  └──────────┘  └──────────┘       │
└─────────────────────────────────────┘
     ↑
GLOBAL search looks at ALL communities
```

### **Best For:**
- ✅ "What is the overall architecture?"
- ✅ "What are the main components?"
- ✅ "How is the system organized?"
- ✅ "What technologies are used?"

### **Example Query & Response:**

**Query:** "What is the overall architecture?"

**GLOBAL Search Process:**
```
1. Look at all community summaries
   → Authentication community
   → API community
   → Database community
   → Frontend community
   
2. Aggregate high-level information
   
3. Return architectural overview
```

**Response:**
```markdown
## System Architecture Overview

The system follows a **3-tier architecture**:

### 1. Frontend Layer
- **Technology**: React with TypeScript
- **Purpose**: User interface and client-side logic
- **Components**: 
  - Authentication UI
  - Dashboard
  - API client

### 2. Backend Layer
- **Technology**: FastAPI (Python)
- **Purpose**: Business logic and API endpoints
- **Modules**:
  - Authentication service
  - User management
  - Data processing
  - API routing

### 3. Data Layer
- **Technology**: PostgreSQL
- **Purpose**: Persistent storage
- **Components**:
  - User database
  - Session storage
  - Application data

### Communication Flow
```
Frontend (React) 
    ↓ HTTP/REST
Backend (FastAPI)
    ↓ SQL
Database (PostgreSQL)
```

### Key Design Patterns
- RESTful API design
- JWT-based authentication
- MVC architecture
```

**Characteristics:**
- 🐌 **Slower** (processes entire graph)
- 📈 **Broad** (high-level overview)
- 🌐 **Comprehensive** (covers all areas)

---

## 3️⃣ COMMUNITY Search (Not Currently Used ❌)

### **What It Does:**
Searches within **specific communities/modules** of related code.

### **Think of it as:**
🎯 **Zooming to a specific module** (between local and global)

### **Visual Representation:**
```
Your Codebase (Knowledge Graph):

┌─────────────────────────────────────┐
│                                     │
│  ┌──────────────────────────┐      │
│  │  AUTHENTICATION COMMUNITY│ ←─── COMMUNITY SEARCH
│  │                          │      │
│  │  [AuthController]        │      │
│  │        ↓                 │      │
│  │  [UserService]           │      │
│  │        ↓                 │      │
│  │  [PasswordHasher]        │      │
│  │        ↓                 │      │
│  │  [JWTGenerator]          │      │
│  └──────────────────────────┘      │
│                                     │
│  [Other communities not searched]  │
└─────────────────────────────────────┘
```

### **Best For:**
- ✅ "How does the authentication module work?"
- ✅ "What's in the payment processing system?"
- ✅ "Explain the data validation layer"
- ✅ "How is the API routing organized?"

### **Example Query & Response:**

**Query:** "How does the authentication module work?"

**COMMUNITY Search Process:**
```
1. Identify "authentication" community
   → All auth-related entities
   
2. Search within that cluster
   → AuthController
   → UserService
   → PasswordHasher
   → JWTGenerator
   → SessionManager
   
3. Return module-level information
```

**Response:**
```markdown
## Authentication Module Architecture

The authentication system is organized into **5 main components**:

### 1. AuthController
**Purpose**: HTTP endpoint handling
**Responsibilities**:
- Receives login/logout requests
- Validates input format
- Returns responses to client

### 2. UserService
**Purpose**: Business logic
**Responsibilities**:
- User lookup in database
- Credential verification
- Account status checking

### 3. PasswordHasher
**Purpose**: Security
**Responsibilities**:
- Hash passwords with bcrypt
- Verify password hashes
- Salt generation

### 4. JWTGenerator
**Purpose**: Token management
**Responsibilities**:
- Create JWT tokens
- Sign tokens with secret key
- Set expiration times

### 5. SessionManager
**Purpose**: Session handling
**Responsibilities**:
- Store active sessions
- Validate session tokens
- Handle logout/expiration

### Data Flow
```
Client Request
    ↓
AuthController (validate input)
    ↓
UserService (check user exists)
    ↓
PasswordHasher (verify password)
    ↓
JWTGenerator (create token)
    ↓
SessionManager (store session)
    ↓
Response to Client
```

### Security Features
- Bcrypt password hashing (cost factor: 12)
- JWT tokens with HMAC-SHA256
- 24-hour session expiration
- Rate limiting on login attempts
```

**Characteristics:**
- ⚡ **Medium speed** (searches one community)
- 📊 **Module-level detail** (focused but comprehensive)
- 🎯 **Scoped** (limited to related entities)

---

## 📊 Comparison Table

| Feature | LOCAL | GLOBAL | COMMUNITY |
|---------|-------|--------|-----------|
| **Scope** | Single entity + neighbors | Entire codebase | One module/cluster |
| **Detail Level** | Very high (code-level) | Low (overview) | Medium (module-level) |
| **Speed** | Fast (⚡) | Slow (🐌) | Medium (⚡🐌) |
| **Best For** | Specific questions | Architecture questions | Module questions |
| **Example** | "How does X work?" | "What's the architecture?" | "How does auth module work?" |
| **Result Size** | Small, focused | Large, broad | Medium, scoped |

---

## 🎯 When to Use Each Method

### **Use LOCAL when:**
```
❓ "How does the login function work?"
❓ "What does authenticate() do?"
❓ "Where is the database connection created?"
❓ "How is error handling implemented in X?"

→ You need specific, detailed code-level information
```

### **Use GLOBAL when:**
```
❓ "What is the overall system architecture?"
❓ "What are all the main components?"
❓ "How is the codebase organized?"
❓ "What technologies and frameworks are used?"

→ You need a high-level overview
```

### **Use COMMUNITY when:**
```
❓ "How does the authentication module work?"
❓ "Explain the payment processing system"
❓ "What's in the data validation layer?"
❓ "How do all the API endpoints work together?"

→ You need module-level understanding
```

---

## 🔧 How to Change Search Method

**Current code** (in `agentic_copilot/graphs/graphrag_subgraph.py`):
```python
cmd = ["graphrag", "query", "--root", root_path, "--method", "local", "--query", query]
                                                    ^^^^^^^^
```

**To use GLOBAL:**
```python
cmd = ["graphrag", "query", "--root", root_path, "--method", "global", "--query", query]
```

**To use COMMUNITY:**
```python
cmd = ["graphrag", "query", "--root", root_path, "--method", "community", "--query", query]
```

---

## 💡 Real-World Analogy

Think of searching a **library**:

### **LOCAL Search** = 📖
"Find me the specific page about photosynthesis in this biology book"
- Very specific
- Detailed information
- Fast to find

### **GLOBAL Search** = 🏛️
"Give me an overview of everything in this library"
- Very broad
- General categories
- Takes time to survey everything

### **COMMUNITY Search** = 📚
"Tell me about all the biology books in the science section"
- Medium scope
- Related topics
- Focused on one area

---

## 🎯 Summary

**Current System Uses: LOCAL** ✅

**Why?**
- Most user questions are specific ("How does X work?")
- Provides detailed, code-level answers
- Fast and precise
- Best for day-to-day code exploration

**When to switch:**
- Use **GLOBAL** for architecture/overview questions
- Use **COMMUNITY** for module-level questions
- Use **LOCAL** for everything else (default)

For most use cases, **LOCAL is the right choice**! 🚀
