# GitHub Push with Personal Access Token (OAuth)

## 📋 Step 1: Create Personal Access Token

I've opened the GitHub token creation page in your browser. Now:

1. **Note**: Enter `GraphRag Push Token`
2. **Expiration**: Choose `90 days` (or your preference)
3. **Select scopes**: ✅ Check **`repo`** (full control of private repositories)
4. Scroll down and click **"Generate token"**
5. **IMPORTANT**: Copy the token immediately (it won't be shown again!)
   - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## 🚀 Step 2: Push Your Code

### Option A: Using the Script (Recommended)

1. Open a **NEW PowerShell**
2. Run:
   ```powershell
   cd c:\Users\202317\.gemini\antigravity\scratch\GrapgRagMain
   .\push_to_github.bat
   ```
3. When prompted:
   - **Username**: `Subha9932`
   - **Password**: Paste your token (ghp_xxx...)

### Option B: Manual Commands

Open a **NEW PowerShell** and run:

```powershell
cd c:\Users\202317\.gemini\antigravity\scratch\GrapgRagMain

git init
git add .
git commit -m "Initial commit: GraphRAG Codebase Analysis Tool"
git branch -M main
git remote add origin https://github.com/Subha9932/GraphRag.git
git push -u origin main
```

When prompted:
- **Username**: `Subha9932`
- **Password**: [Paste your token]

---

## 💾 Save Your Token (Optional)

To avoid entering the token every time:

```powershell
git config --global credential.helper store
```

Next time you push, Git will remember your credentials.

---

## ✅ Verify Success

After pushing, visit: **https://github.com/Subha9932/GraphRag**

You should see your complete GraphRAG project! 🎉

---

## 🔧 Troubleshooting

**Error: "remote origin already exists"**
```powershell
git remote remove origin
git remote add origin https://github.com/Subha9932/GraphRag.git
```

**Error: "repository not found"**
- Make sure the repository exists on GitHub
- Check your username is correct: `Subha9932`
