# How to Push Your Code to GitHub

## Quick Method (Recommended)

1. **Close this terminal**
2. **Open a NEW PowerShell/Terminal** (so Git is recognized)
3. Navigate to your project:
   ```powershell
   cd c:\Users\202317\.gemini\antigravity\scratch\GrapgRagMain
   ```
4. Run the push script:
   ```powershell
   .\push_to_github.bat
   ```

## Manual Method (If script fails)

Open a **NEW terminal** and run these commands one by one:

```bash
cd c:\Users\202317\.gemini\antigravity\scratch\GrapgRagMain

git init
git add .
git commit -m "Initial commit: GraphRAG Codebase Analysis Tool"
git branch -M main
git remote add origin git@github.com:Subha9932/GraphRag.git
git push -u origin main
```

## ⚠️ Authentication Required

You'll need to authenticate with GitHub. Choose one:

### Option 1: HTTPS (Easier)
Change the remote URL:
```bash
git remote set-url origin https://github.com/Subha9932/GraphRag.git
git push -u origin main
```
Then enter your GitHub username and **Personal Access Token** (not password).

### Option 2: SSH (More Secure)
1. Generate SSH key:
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```
2. Copy public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
3. Add to GitHub: Settings → SSH Keys → New SSH Key
4. Push:
   ```bash
   git push -u origin main
   ```

## ✅ Verify Success

After pushing, visit: https://github.com/Subha9932/GraphRag

You should see your code with the README displayed!
