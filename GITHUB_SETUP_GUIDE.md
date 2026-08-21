# 🐙 GitHub Setup Guide - Push & Clone

## 📤 PART 1: Push to GitHub (From Your Mac)

### Step 1: Create GitHub Repository

1. **Go to**: https://github.com
2. **Login** to your account
3. **Click** the "+" icon (top right) → "New repository"
4. **Fill in**:
   - Repository name: `multimodal-mental-health-analysis`
   - Description: `Multimodal Depression Detection using CNN, LSTM, and Deep Learning`
   - Visibility: **Public** (so teammates can access) or **Private** (invite teammates)
   - ❌ **DO NOT** check "Initialize with README" (we already have files)
5. **Click** "Create repository"

### Step 2: Initialize Git in Your Project

Open Terminal and run:

```bash
# Navigate to project
cd /Users/vishwachi/Desktop/mental-health-ai

# Initialize git (if not already done)
git init

# Check status
git status
```

### Step 3: Create .gitignore File

```bash
# Create .gitignore to exclude unnecessary files
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/
.pytest_cache/
.coverage

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnp/
.pnp.js
build/
.DS_Store

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Database
*.db
*.sqlite
*.sqlite3

# Environment
.env
.env.local
.env.*.local

# OS
.DS_Store
Thumbs.db

# Data (don't upload large datasets)
data/raw/
data/cleaned/
*.wav
*.mp4
*.avi

# Models (large files)
models/
*.pth
*.pt
*.h5
*.pkl

# Logs
logs/
*.log
EOF
```

### Step 4: Add All Files to Git

```bash
# Add all files
git add .

# Check what will be committed
git status

# Commit with message
git commit -m "Initial commit: Multimodal mental health analysis ML project"
```

### Step 5: Connect to GitHub and Push

```bash
# Add remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/multimodal-mental-health-analysis.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

**Enter your GitHub credentials when prompted.**

### Step 6: Verify Upload

1. Go to: `https://github.com/YOUR_USERNAME/multimodal-mental-health-analysis`
2. You should see all your files!

---

## 👥 PART 2: Add Teammates as Collaborators

### For Private Repository:

1. Go to your repository on GitHub
2. Click **"Settings"** tab
3. Click **"Collaborators"** in left sidebar
4. Click **"Add people"**
5. Enter teammate's GitHub username or email
6. Click **"Add [username] to this repository"**
7. They'll receive an invitation email

### For Public Repository:

- Anyone can clone it!
- Share the link: `https://github.com/YOUR_USERNAME/multimodal-mental-health-analysis`

---

## 💻 PART 3: Clone on Windows (For Your Teammates)

### Prerequisites on Windows:

1. **Install Git for Windows**:
   - Download: https://git-scm.com/download/win
   - Run installer, use default settings
   - Verify: Open Command Prompt, type `git --version`

2. **Install Python 3.10+**:
   - Download: https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH" during installation
   - Verify: `python --version`

3. **Install Node.js 16+**:
   - Download: https://nodejs.org/
   - Use LTS version
   - Verify: `node --version` and `npm --version`

### Step 1: Clone Repository

Open **Command Prompt** or **PowerShell**:

```bash
# Navigate to desired location (e.g., Desktop)
cd C:\Users\YourName\Desktop

# Clone repository (replace YOUR_USERNAME)
git clone https://github.com/YOUR_USERNAME/multimodal-mental-health-analysis.git

# Enter the project
cd multimodal-mental-health-analysis
```

### Step 2: Setup Backend (Windows)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install packages
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Setup Frontend (Windows)

Open **NEW Command Prompt** window:

```bash
# Navigate to frontend
cd C:\Users\YourName\Desktop\multimodal-mental-health-analysis\frontend

# Install packages
npm install
```

### Step 4: Run on Windows

**Terminal 1 (Backend)**:
```bash
cd C:\Users\YourName\Desktop\multimodal-mental-health-analysis\backend
venv\Scripts\activate
python main.py
```

**Terminal 2 (Frontend)**:
```bash
cd C:\Users\YourName\Desktop\multimodal-mental-health-analysis\frontend
npm start
```

**Access**: http://localhost:3000

---

## 🔄 PART 4: Keeping Project Updated

### When You Make Changes (Mac):

```bash
cd /Users/vishwachi/Desktop/mental-health-ai

# Check what changed
git status

# Add changes
git add .

# Commit with descriptive message
git commit -m "Added new feature: XYZ"

# Push to GitHub
git push origin main
```

### When Teammates Want Latest Code (Windows/Mac):

```bash
# Navigate to project
cd multimodal-mental-health-analysis

# Pull latest changes
git pull origin main

# If backend changed, reinstall packages
cd backend
# Mac: source venv/bin/activate
# Windows: venv\Scripts\activate
pip install -r requirements.txt

# If frontend changed, reinstall packages
cd frontend
npm install
```

---

## 🌿 PART 5: Working with Branches (Team Collaboration)

### Create Feature Branch:

```bash
# Create and switch to new branch
git checkout -b feature/your-feature-name

# Make changes, then commit
git add .
git commit -m "Implemented feature XYZ"

# Push branch to GitHub
git push origin feature/your-feature-name
```

### Merge Branch (After Review):

```bash
# Switch to main branch
git checkout main

# Pull latest changes
git pull origin main

# Merge your feature branch
git merge feature/your-feature-name

# Push to GitHub
git push origin main
```

---

## 📋 PART 6: Quick Reference Commands

### Common Git Commands:

```bash
# Check status
git status

# See commit history
git log --oneline

# See changes
git diff

# Undo changes (before commit)
git checkout -- filename

# Create branch
git branch branch-name

# Switch branch
git checkout branch-name

# Delete branch
git branch -d branch-name

# Pull latest
git pull origin main

# Push changes
git push origin main
```

---

## 🚨 Troubleshooting

### Problem 1: "Permission denied (publickey)"

**Solution**: Use HTTPS instead of SSH
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/multimodal-mental-health-analysis.git
```

### Problem 2: "Failed to push some refs"

**Solution**: Pull first, then push
```bash
git pull origin main --rebase
git push origin main
```

### Problem 3: Merge conflicts

**Solution**:
1. Open conflicted files
2. Look for `<<<<<<<`, `=======`, `>>>>>>>`
3. Edit to keep desired changes
4. Remove conflict markers
5. `git add .` and `git commit`

### Problem 4: Large files error

**Solution**: Don't commit large files
```bash
# Remove from git (keep local file)
git rm --cached large-file.wav

# Add to .gitignore
echo "*.wav" >> .gitignore

# Commit
git add .gitignore
git commit -m "Ignore large audio files"
```

---

## 📝 README.md for GitHub

Create a good README for your repository:

```bash
cat > README.md << 'EOF'
# 🧠 Multimodal Mental Health Analysis

AI-powered depression detection using multimodal deep learning (CNN, LSTM, BiLSTM).

## 🎯 Features

- **Audio Analysis**: CNN for acoustic feature extraction
- **Facial Analysis**: CNN for expression recognition
- **Text Analysis**: BiLSTM for linguistic patterns
- **Multimodal Fusion**: Attention-based feature combination
- **Web Interface**: React + FastAPI

## 📊 Results

- **Accuracy**: 87%
- **RMSE**: 0.168
- **F1-Score**: 0.82

## 🚀 Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

Access: http://localhost:3000

## 📚 Documentation

- [How to Run](HOW_TO_RUN.md)
- [Presentation Guide](PROJECT_PRESENTATION_GUIDE.md)
- [Dataset Guide](DAIC_WOZ_DATASET_GUIDE.md)
- [India Setup](INDIA_SETUP_GUIDE.md)

## 🤝 Team

- [Your Name]
- [Teammate 1]
- [Teammate 2]

## 📄 License

MIT License - Academic Project

## 🙏 Acknowledgments

- DAIC-WOZ Dataset
- USC SAIL Lab
EOF
```

Then commit and push:
```bash
git add README.md
git commit -m "Added README"
git push origin main
```

---

## ✅ Complete Workflow Summary

### Initial Setup (You - Mac):
```bash
cd /Users/vishwachi/Desktop/mental-health-ai
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/multimodal-mental-health-analysis.git
git push -u origin main
```

### Clone (Teammates - Windows):
```bash
cd C:\Users\YourName\Desktop
git clone https://github.com/YOUR_USERNAME/multimodal-mental-health-analysis.git
cd multimodal-mental-health-analysis
```

### Update (Anyone):
```bash
git pull origin main
```

### Make Changes (Anyone):
```bash
git add .
git commit -m "Description of changes"
git push origin main
```

---

## 🎓 Best Practices for Team

1. **Always pull before starting work**: `git pull origin main`
2. **Commit often** with clear messages
3. **Don't commit large files** (datasets, models)
4. **Use branches** for new features
5. **Review code** before merging
6. **Document changes** in commit messages
7. **Keep .gitignore updated**

---

## 📞 Need Help?

- **Git Documentation**: https://git-scm.com/doc
- **GitHub Guides**: https://guides.github.com/
- **Git Cheat Sheet**: https://education.github.com/git-cheat-sheet-education.pdf

---

**Your project is now ready for team collaboration! 🚀**