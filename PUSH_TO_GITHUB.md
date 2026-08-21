# 🚀 PUSH TO GITHUB - Simple Steps

## ⚠️ BEFORE YOU START

You need a GitHub account. If you don't have one:
1. Go to https://github.com
2. Click "Sign up"
3. Create account

---

## 📝 STEP 1: Create Repository on GitHub

### Do This First (On GitHub Website):

1. **Open browser** → Go to https://github.com
2. **Login** to your account
3. **Click** the **"+"** icon (top right corner)
4. **Click** "New repository"
5. **Fill in**:
   - Repository name: `mental-health-analysis`
   - Description: `Multimodal Depression Detection ML Project`
   - Choose: **Public** (so teammates can see)
   - ❌ **UNCHECK** "Add a README file"
   - ❌ **UNCHECK** "Add .gitignore"
   - ❌ **UNCHECK** "Choose a license"
6. **Click** "Create repository"

### After Creating:
You'll see a page with commands. **IGNORE THEM** for now.

**Copy your repository URL**. It looks like:
```
https://github.com/YOUR_USERNAME/mental-health-analysis.git
```

---

## 💻 STEP 2: Push Your Code

### Open Terminal and Run These Commands ONE BY ONE:

```bash
# 1. Go to your project
cd /Users/vishwachi/Desktop/mental-health-ai

# 2. Check if git is initialized (should say "On branch main")
git status

# 3. Add remote repository
# REPLACE "YOUR_USERNAME" with your actual GitHub username
git remote add origin https://github.com/YOUR_USERNAME/mental-health-analysis.git

# 4. Verify remote was added
git remote -v

# 5. Push to GitHub
git push -u origin main
```

### When Prompted:
- **Username**: Enter your GitHub username
- **Password**: Enter your GitHub password OR Personal Access Token

---

## 🔑 If Password Doesn't Work (Use Personal Access Token)

GitHub doesn't accept passwords anymore. You need a token:

### Create Token:
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: `mental-health-project`
4. Check: `repo` (all repo permissions)
5. Click "Generate token"
6. **COPY THE TOKEN** (you won't see it again!)

### Use Token as Password:
When terminal asks for password, paste the token instead.

---

## ✅ VERIFY IT WORKED

1. Go to: `https://github.com/YOUR_USERNAME/mental-health-analysis`
2. You should see all your files!
3. Refresh the page if needed

---

## 🎯 EXACT COMMANDS (Copy-Paste)

Replace `YOUR_USERNAME` with your GitHub username, then run:

```bash
cd /Users/vishwachi/Desktop/mental-health-ai
git remote add origin https://github.com/YOUR_USERNAME/mental-health-analysis.git
git push -u origin main
```

---

## 👥 SHARE WITH TEAMMATES

After pushing, share this link with your team:
```
https://github.com/YOUR_USERNAME/mental-health-analysis
```

They can clone it with:
```bash
git clone https://github.com/YOUR_USERNAME/mental-health-analysis.git
```

---

## 🔄 UPDATE CODE LATER

When you make changes:

```bash
cd /Users/vishwachi/Desktop/mental-health-ai
git add .
git commit -m "Updated XYZ"
git push origin main
```

---

## ❌ TROUBLESHOOTING

### Error: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/mental-health-analysis.git
```

### Error: "failed to push"
```bash
git pull origin main --rebase
git push origin main
```

### Error: "Permission denied"
Use Personal Access Token instead of password (see above)

---

## 📞 STILL NOT WORKING?

### Option 1: Use GitHub Desktop (Easier)
1. Download: https://desktop.github.com/
2. Install and login
3. Click "Add" → "Add existing repository"
4. Select: `/Users/vishwachi/Desktop/mental-health-ai`
5. Click "Publish repository"

### Option 2: Ask Me
Tell me the exact error message you're seeing.

---

## ✅ CHECKLIST

- [ ] Created GitHub account
- [ ] Created new repository on GitHub
- [ ] Copied repository URL
- [ ] Ran `git remote add origin` command
- [ ] Ran `git push -u origin main` command
- [ ] Entered username and token/password
- [ ] Verified files on GitHub website

---

**Once pushed, your teammates can access it! 🎉**