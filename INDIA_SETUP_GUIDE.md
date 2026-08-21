# 🇮🇳 Multimodal Mental Health Analysis - India Setup Guide

## 🎯 Important: This is a React Web Application (NOT Streamlit)

We have created a **modern React web application** with:
- ✅ React frontend (not Streamlit)
- ✅ FastAPI backend
- ✅ Material-UI components
- ✅ Professional web interface
- ✅ Multimodal analysis capabilities

The `streamlit-app/` folder in your project is from the old version. **We're using the React web app in the `frontend/` folder.**

---

## 🚀 Quick Start for India

### Step 1: Install Prerequisites

#### For Ubuntu/Debian (Most Indian Universities)
```bash
# Update system
sudo apt-get update

# Install Python 3.10
sudo apt-get install -y python3.10 python3-pip python3-venv

# Install Node.js and npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install audio/video dependencies
sudo apt-get install -y ffmpeg portaudio19-dev libsndfile1

# Verify installations
python3 --version
node --version
npm --version
```

#### For macOS (if using Mac)
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.10 node ffmpeg portaudio libsndfile
```

### Step 2: Run the React Web Application

#### Terminal 1: Start Backend
```bash
cd /Users/vishwachi/Desktop/mental-health-ai/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Run FastAPI backend
python main.py
```

Backend will run at: **http://localhost:8000**

#### Terminal 2: Start React Frontend
```bash
cd /Users/vishwachi/Desktop/mental-health-ai/frontend

# Install Node packages (first time only)
npm install

# Start React development server
npm start
```

Frontend will open at: **http://localhost:3000**

---

## 🇮🇳 DAIC-WOZ Dataset Access from India

### Official Method (Recommended)
1. **Website**: https://dcapswoz.ict.usc.edu/
2. **Email**: dcapswoz@ict.usc.edu
3. **Requirements**:
   - Use your college/university email (.edu or .ac.in)
   - Mention your institution name
   - State research purpose
   - Approval time: 1-3 business days

### Email Template for Indian Students
```
Subject: DAIC-WOZ Dataset Access Request - Indian Research Institution

Dear DAIC-WOZ Team,

I am [Your Name], a [B.Tech/M.Tech/PhD] student at [Your College/University], 
India, working on a multimodal mental health analysis project.

Institution: [Your College Name]
Email: [your.email@college.ac.in]
Research Focus: Multimodal depression detection using audio, video, and text

I have read and agree to the Data Use Agreement terms. I will use the dataset 
solely for academic research and will not redistribute it.

Thank you for your consideration.

Best regards,
[Your Name]
[Roll Number]
[Department]
[College Name, City, India]
```

### Alternative Datasets Available in India

#### 1. RAVDESS (Immediate Access)
- **Link**: https://zenodo.org/record/1188976
- **No approval needed** - Download directly
- **Size**: ~24 GB
- **Content**: Audio and video of emotional expressions
- **Good for**: Testing your system immediately

#### 2. Indian Datasets
- **IIIT-H Emotion Dataset**: Contact IIIT Hyderabad
- **IIT Datasets**: Check with IIT research labs
- **NPTEL Resources**: Some datasets available through NPTEL

#### 3. Public Datasets
- **YouTube Depression Dataset**: Available on GitHub
- **Kaggle Datasets**: Search "mental health" or "emotion detection"

---

## 💻 System Requirements for India

### Minimum Requirements
- **RAM**: 8GB (16GB recommended)
- **Storage**: 100GB free space
- **Internet**: Stable connection for downloads
- **OS**: Ubuntu 20.04+ / macOS / Windows 10+

### Recommended Setup
- **RAM**: 16GB
- **Storage**: 200GB SSD
- **GPU**: NVIDIA GPU (optional, for faster processing)
- **Internet**: Broadband connection

---

## 🌐 Network Configuration for India

### If Behind College/University Proxy

#### Configure npm proxy
```bash
npm config set proxy http://proxy.college.edu:port
npm config set https-proxy http://proxy.college.edu:port
```

#### Configure pip proxy
```bash
pip install --proxy http://proxy.college.edu:port package_name
```

#### Or use environment variables
```bash
export HTTP_PROXY=http://proxy.college.edu:port
export HTTPS_PROXY=http://proxy.college.edu:port
```

### If Facing Slow Downloads

#### Use Indian mirrors for npm
```bash
npm config set registry https://registry.npmmirror.com
```

#### Use Indian PyPI mirror
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package_name
```

---

## 📱 Indian Mental Health Resources

### Crisis Helplines
- **NIMHANS Helpline**: 080-46110007
- **Vandrevala Foundation**: 1860-2662-345 / 1800-2333-330
- **iCall**: 9152987821
- **AASRA**: 91-22-27546669

### Organizations
- **NIMHANS**: National Institute of Mental Health and Neuro Sciences, Bangalore
- **TISS**: Tata Institute of Social Sciences, Mumbai
- **SCARF**: Schizophrenia Research Foundation, Chennai

---

## 🎓 For Indian Students/Researchers

### Academic Use
- ✅ Use institutional email for dataset requests
- ✅ Mention your guide/supervisor name
- ✅ State if it's for B.Tech/M.Tech project or PhD research
- ✅ Get approval from your department if required

### Project Documentation
- Document in IEEE format (common in India)
- Include literature review from Indian journals
- Cite Indian mental health statistics
- Consider cultural context in analysis

### Collaboration
- Connect with NIMHANS researchers
- Join Indian AI/ML communities
- Participate in hackathons (Smart India Hackathon, etc.)

---

## 🔧 Common Issues in India & Solutions

### Issue 1: Slow npm install
**Solution**: Use Indian mirror or download offline
```bash
npm config set registry https://registry.npmmirror.com
npm install
```

### Issue 2: pip install fails
**Solution**: Use Indian PyPI mirror
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

### Issue 3: Port 8000 already in use
**Solution**: Change port in backend
```bash
# In backend/main.py, change port to 8080
uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
```

### Issue 4: Permission denied errors
**Solution**: Use sudo or fix permissions
```bash
sudo chown -R $USER:$USER /Users/vishwachi/Desktop/mental-health-ai
```

### Issue 5: College firewall blocking
**Solution**: 
- Use mobile hotspot for initial setup
- Request IT department to whitelist required domains
- Use VPN if allowed

---

## 💰 Cost Considerations for India

### Free Tier Options
- **Frontend Hosting**: Netlify, Vercel (Free)
- **Backend Hosting**: Render, Railway (Free tier)
- **Database**: MongoDB Atlas (Free 512MB)
- **Storage**: Google Drive, Dropbox (Free)

### Paid Options (Budget-friendly)
- **DigitalOcean**: ₹400/month (~$5)
- **AWS Free Tier**: 12 months free
- **Google Cloud**: ₹300 credit for new users
- **Azure**: ₹13,300 credit for students

---

## 🎯 Project Timeline for Indian Academic Calendar

### Semester Project (4 months)
- **Month 1**: Setup, literature review, dataset acquisition
- **Month 2**: Data cleaning, preprocessing
- **Month 3**: Model development, frontend integration
- **Month 4**: Testing, documentation, presentation

### Final Year Project (6-8 months)
- **Months 1-2**: Research, setup, dataset
- **Months 3-4**: Implementation
- **Months 5-6**: Testing, optimization
- **Months 7-8**: Documentation, paper writing, defense

---

## 📊 What We've Built (React Web App)

### Frontend (React + Material-UI)
- ✅ Modern, responsive web interface
- ✅ Audio upload and analysis
- ✅ Video upload and facial analysis
- ✅ Text input and sentiment analysis
- ✅ Interactive charts and visualizations
- ✅ Real-time results display

### Backend (FastAPI + Python)
- ✅ RESTful API endpoints
- ✅ Audio processing (librosa)
- ✅ Video processing (OpenCV)
- ✅ NLP analysis (NLTK, spaCy)
- ✅ ML models integration
- ✅ Database support

### NOT Using Streamlit
- ❌ We're NOT using Streamlit
- ✅ We're using React (professional web framework)
- ✅ Better for production deployment
- ✅ More customizable
- ✅ Industry-standard approach

---

## 🚀 Running the Web Application

### Development Mode (For Testing)
```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 2: Frontend
cd frontend
npm start

# Access at: http://localhost:3000
```

### Production Build (For Deployment)
```bash
# Build frontend
cd frontend
npm run build

# Serve with backend
cd ../backend
# Configure to serve static files from frontend/build
```

---

## 📚 Resources for Indian Students

### Learning Resources
- **NPTEL Courses**: AI, ML, Deep Learning
- **IIT Lectures**: YouTube channels
- **Indian AI Communities**: 
  - Analytics Vidhya
  - Machine Hack
  - Kaggle India

### Datasets
- **Indian Government Data**: data.gov.in
- **Healthcare Data**: NDHM (National Digital Health Mission)
- **Research Papers**: Indian journals, IEEE Xplore

### Competitions
- **Smart India Hackathon**
- **TechGig Code Gladiators**
- **HackerEarth Challenges**
- **Kaggle Competitions**

---

## 🎓 Academic Requirements

### For B.Tech/M.Tech Projects
- Literature review (15-20 papers)
- System design and architecture
- Implementation details
- Results and analysis
- Future scope
- IEEE format documentation

### For PhD Research
- Comprehensive literature survey
- Novel contribution
- Extensive experimentation
- Statistical validation
- Publication in conferences/journals

---

## 📞 Support Contacts

### Technical Issues
- **Your College IT Department**
- **Online Communities**: Stack Overflow, Reddit r/india
- **GitHub Issues**: Create issue in project repository

### Dataset Access
- **DAIC-WOZ**: dcapswoz@ict.usc.edu
- **Indian Datasets**: Contact respective institutions

---

## ✅ Quick Checklist

- [ ] Python 3.10+ installed
- [ ] Node.js 16+ installed
- [ ] Dependencies installed (npm install, pip install)
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Dataset request submitted
- [ ] Alternative dataset downloaded (RAVDESS)
- [ ] Project documentation started

---

## 🎯 Next Steps

1. **Today**: Setup environment, test with mock data
2. **This Week**: Submit dataset request, download RAVDESS
3. **Next Week**: Start data cleaning and preprocessing
4. **Month 1**: Complete implementation
5. **Month 2**: Testing and optimization
6. **Month 3**: Documentation and presentation

---

**Made for Indian students and researchers! 🇮🇳**

**Remember**: This is a React web application, not Streamlit. You have a professional, production-ready web interface!

For any questions, refer to the documentation or create an issue on GitHub.

Good luck with your project! 🚀