# 🚀 HOW TO RUN - Step by Step Guide

## ⚡ Quick Start (Copy-Paste These Commands)

### Step 1: Open Terminal and Navigate to Project
```bash
cd /Users/vishwachi/Desktop/mental-health-ai
```

---

## 🔧 BACKEND SETUP (Do This First)

### Step 2: Go to Backend Folder
```bash
cd backend
```

### Step 3: Create Virtual Environment (First Time Only)
```bash
python3 -m venv venv
```
**Wait**: This takes 1-2 minutes

### Step 4: Activate Virtual Environment
```bash
source venv/bin/activate
```
**You should see** `(venv)` at the start of your terminal line

### Step 5: Install Python Packages (First Time Only)
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
**Wait**: This takes 3-5 minutes

### Step 6: Start Backend Server
```bash
python main.py
```

**✅ SUCCESS**: You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Keep this terminal open!** Backend is now running.

---

## 💻 FRONTEND SETUP (Open New Terminal)

### Step 7: Open NEW Terminal Window
Press `Cmd + T` (Mac) or open new terminal window

### Step 8: Go to Frontend Folder
```bash
cd /Users/vishwachi/Desktop/mental-health-ai/frontend
```

### Step 9: Install Node Packages (First Time Only)
```bash
npm install
```
**Wait**: This takes 2-3 minutes

### Step 10: Start Frontend Server
```bash
npm start
```

**✅ SUCCESS**: Browser will automatically open to `http://localhost:3000`

If it doesn't open automatically, manually open browser and go to:
```
http://localhost:3000
```

---

## 🎉 YOU'RE DONE!

You should now see:
- ✅ Backend running at: http://localhost:8000
- ✅ Frontend running at: http://localhost:3000
- ✅ Web application open in browser

---

## 📱 Using the Application

1. **Navigate** to "Multimodal Analysis" in the sidebar
2. **Upload** audio, video, or enter text
3. **Click** "Analyze Mental Health Indicators"
4. **View** results with charts and recommendations

---

## 🛑 How to Stop

### Stop Frontend:
In the frontend terminal, press: `Ctrl + C`

### Stop Backend:
In the backend terminal, press: `Ctrl + C`

### Deactivate Virtual Environment:
```bash
deactivate
```

---

## 🔄 Running Again (Next Time)

### Terminal 1 (Backend):
```bash
cd /Users/vishwachi/Desktop/mental-health-ai/backend
source venv/bin/activate
python main.py
```

### Terminal 2 (Frontend):
```bash
cd /Users/vishwachi/Desktop/mental-health-ai/frontend
npm start
```

**That's it!** No need to install packages again.

---

## ❌ Troubleshooting

### Problem 1: "python3: command not found"
**Solution**: Install Python 3
```bash
# Mac
brew install python@3.10

# Ubuntu
sudo apt-get install python3.10
```

### Problem 2: "npm: command not found"
**Solution**: Install Node.js
```bash
# Mac
brew install node

# Ubuntu
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Problem 3: "Port 8000 already in use"
**Solution**: Kill the process
```bash
# Find process
lsof -ti:8000

# Kill it
kill -9 $(lsof -ti:8000)

# Or use different port
# In backend/main.py, change port to 8080
```

### Problem 4: "Port 3000 already in use"
**Solution**: 
```bash
# Kill process
kill -9 $(lsof -ti:3000)

# Or when prompted, press 'Y' to use different port
```

### Problem 5: "Module not found" errors
**Solution**: Reinstall packages
```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules
npm install
```

### Problem 6: Virtual environment won't activate
**Solution**: 
```bash
# Delete and recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📊 Verify Everything is Working

### Check Backend:
Open browser to: http://localhost:8000/health

You should see:
```json
{
  "status": "healthy",
  "timestamp": "2024-..."
}
```

### Check Frontend:
Open browser to: http://localhost:3000

You should see the MindCare application with navigation menu.

---

## 🎯 Complete Command Summary

```bash
# ============================================
# FIRST TIME SETUP (Do Once)
# ============================================

# Backend Setup
cd /Users/vishwachi/Desktop/mental-health-ai/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Frontend Setup (New Terminal)
cd /Users/vishwachi/Desktop/mental-health-ai/frontend
npm install

# ============================================
# RUNNING THE APPLICATION (Every Time)
# ============================================

# Terminal 1: Backend
cd /Users/vishwachi/Desktop/mental-health-ai/backend
source venv/bin/activate
python main.py

# Terminal 2: Frontend
cd /Users/vishwachi/Desktop/mental-health-ai/frontend
npm start

# ============================================
# ACCESS
# ============================================
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

---

## 🎓 For Presentation/Demo

### Before Demo:
1. Start backend (Terminal 1)
2. Start frontend (Terminal 2)
3. Open browser to http://localhost:3000
4. Navigate to "Multimodal Analysis"
5. Keep it ready

### During Demo:
1. Show the interface
2. Upload sample audio/video/text
3. Click "Analyze"
4. Show results with charts
5. Explain the multimodal analysis

---

## 💡 Pro Tips

1. **Always start backend first**, then frontend
2. **Keep both terminals open** while using the app
3. **Use Cmd+T** to open new terminal tabs (Mac)
4. **Check http://localhost:8000/docs** for API documentation
5. **The app has mock data** - works without real dataset

---

## 📞 Still Having Issues?

1. Check if Python 3.8+ is installed: `python3 --version`
2. Check if Node.js 16+ is installed: `node --version`
3. Check if ports 8000 and 3000 are free
4. Try restarting your computer
5. Delete `venv` and `node_modules`, reinstall everything

---

## ✅ Success Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Backend virtual environment created
- [ ] Backend packages installed
- [ ] Frontend packages installed
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Browser opens to http://localhost:3000
- [ ] Can navigate to "Multimodal Analysis"
- [ ] Can see the interface

---

**That's it! You're ready to run your ML project! 🚀**

If you see the web interface, everything is working correctly!