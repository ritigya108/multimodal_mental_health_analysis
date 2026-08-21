# 🚀 URGENT: Quick Start & Dataset Access

## How to Run the Frontend RIGHT NOW

### Step 1: Open Terminal and Navigate to Project
```bash
cd /Users/vishwachi/Desktop/mental-health-ai/frontend
```

### Step 2: Install Dependencies (First Time Only)
```bash
npm install
```
This will take 2-3 minutes. Wait for it to complete.

### Step 3: Start the Frontend
```bash
npm start
```

The frontend will automatically open in your browser at: **http://localhost:3000**

If it doesn't open automatically, manually open your browser and go to: http://localhost:3000

### Step 4: Start Backend (In a New Terminal)
```bash
# Open a NEW terminal window
cd /Users/vishwachi/Desktop/mental-health-ai/backend

# Create virtual environment (first time only)
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Run the backend
python main.py
```

Backend will run at: **http://localhost:8000**

---

## 🚨 URGENT: Getting DAIC-WOZ Dataset TODAY

### ⚠️ CRITICAL INFORMATION
**The DAIC-WOZ dataset is NOT publicly available and requires approval, which typically takes 1-3 business days.**

However, here are your options to get data TODAY:

### Option 1: Request Expedited Access (BEST OPTION)
1. **Go to**: https://dcapswoz.ict.usc.edu/
2. **Fill the form** with:
   - Your institutional email (university/research)
   - Research purpose: "Mental health analysis research project"
   - Urgency note: "Time-sensitive research deadline"
3. **Email directly**: dcapswoz@ict.usc.edu
   - Subject: "Urgent DAIC-WOZ Dataset Access Request"
   - Explain your deadline
   - Provide your form submission details
4. **Call USC SAIL Lab** (if available): Check their website for contact

### Option 2: Use Alternative Datasets (IMMEDIATE ACCESS)

#### A. RAVDESS Dataset (Emotional Speech & Video)
- **Link**: https://zenodo.org/record/1188976
- **Access**: Immediate download
- **Content**: Audio and video of emotional expressions
- **Size**: ~24 actors, 7 emotions
- **Format**: Similar to DAIC-WOZ structure

#### B. IEMOCAP Dataset
- **Link**: https://sail.usc.edu/iemocap/
- **Access**: Request form (faster approval)
- **Content**: Emotional speech and video
- **Size**: ~12 hours of data

#### C. AVEC 2013/2014 Datasets
- **Link**: https://avec2014-db.sspnet.eu/
- **Access**: Request form
- **Content**: Depression detection data
- **Similar to**: DAIC-WOZ

#### D. YouTube Depression Dataset (PUBLIC)
- **Link**: Search "depression detection dataset github"
- **Access**: Immediate
- **Content**: Public YouTube videos with labels
- **Note**: Less controlled than DAIC-WOZ

### Option 3: Use Sample/Mock Data (FOR TESTING)

Create sample data to test your system:

```bash
cd /Users/vishwachi/Desktop/mental-health-ai
mkdir -p data/sample
```

I can help you create mock data that mimics DAIC-WOZ structure for testing.

### Option 4: Contact Researchers

Email researchers who have published papers using DAIC-WOZ:
- Ask if they can share preprocessed features (not raw data)
- Explain your urgent timeline
- Offer collaboration/co-authorship

**Search**: "DAIC-WOZ depression detection" on Google Scholar
**Recent papers**: Check 2022-2024 publications

### Option 5: IEEE Dataport (CHECK NOW)
- **Link**: https://ieee-dataport.org/
- **Search**: "depression detection" or "mental health"
- Some researchers upload processed versions

---

## 📧 Email Template for Urgent Request

```
Subject: Urgent DAIC-WOZ Dataset Access Request - Research Deadline

Dear DAIC-WOZ Team,

I am [Your Name], a [student/researcher] at [Your Institution], working on a 
multimodal mental health analysis project for [course/research].

I have submitted the Data Use Agreement form and urgently need access to the 
DAIC-WOZ dataset due to a project deadline of [date].

My research focuses on:
- Multimodal depression detection
- Audio, video, and text analysis
- Mental health AI applications

I understand the importance of data privacy and will strictly adhere to all 
usage guidelines. I would greatly appreciate expedited review of my request.

Form submission details:
- Email: [your email]
- Institution: [your institution]
- Date submitted: [today's date]

Thank you for your consideration.

Best regards,
[Your Name]
[Your Contact Information]
```

---

## 🎯 What You Can Do RIGHT NOW

### 1. Test Frontend Without Dataset (5 minutes)
```bash
cd /Users/vishwachi/Desktop/mental-health-ai/frontend
npm install
npm start
```
The frontend has **mock data** built-in for testing!

### 2. Submit Dataset Request (10 minutes)
- Go to https://dcapswoz.ict.usc.edu/
- Fill out the form
- Send urgent email to dcapswoz@ict.usc.edu

### 3. Download Alternative Dataset (30 minutes)
- RAVDESS: https://zenodo.org/record/1188976
- Download and extract
- Adapt cleaning script for this format

### 4. Create Mock Data (1 hour)
I can help you create realistic mock data that matches DAIC-WOZ structure for immediate testing.

---

## 🔧 Frontend Testing Without Real Data

The frontend I created has **built-in mock data** so you can test it immediately:

1. Start the frontend (as shown above)
2. Go to "Multimodal Analysis" page
3. Click "Analyze Mental Health Indicators" button
4. You'll see sample results with:
   - Audio analysis
   - Video analysis
   - Text analysis
   - Combined risk assessment

This lets you test the UI while waiting for real data!

---

## 📞 Emergency Contacts

### DAIC-WOZ Dataset
- **Email**: dcapswoz@ict.usc.edu
- **Website**: https://dcapswoz.ict.usc.edu/
- **USC SAIL Lab**: https://sail.usc.edu/

### Alternative Support
- **AVEC Challenge**: avec-workshop@googlegroups.com
- **IEEE Dataport**: support@ieee.org

---

## ⏰ Timeline Expectations

| Action | Time Required |
|--------|---------------|
| Frontend setup | 5 minutes |
| Backend setup | 10 minutes |
| DAIC-WOZ approval | 1-3 business days |
| Alternative dataset | 30 minutes - 2 hours |
| Mock data creation | 1 hour |

---

## 🎬 Quick Commands Summary

```bash
# Terminal 1: Frontend
cd /Users/vishwachi/Desktop/mental-health-ai/frontend
npm install
npm start

# Terminal 2: Backend
cd /Users/vishwachi/Desktop/mental-health-ai/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py

# Browser
# Open: http://localhost:3000
```

---

## 💡 Pro Tips

1. **Use mock data first** - Test your system while waiting for real data
2. **Submit request NOW** - Even if it takes days, start the process
3. **Try RAVDESS** - It's immediately available and similar structure
4. **Email researchers** - They might share preprocessed features
5. **Document everything** - Keep track of what you try

---

## ❓ Need Help?

If you encounter any issues:

1. **Frontend won't start**: 
   - Delete `node_modules` folder
   - Run `npm install` again

2. **Backend errors**:
   - Make sure virtual environment is activated
   - Check Python version: `python3 --version` (need 3.8+)

3. **Dataset access denied**:
   - Try alternative datasets
   - Use mock data for now
   - Contact me for help creating sample data

---

**Remember**: The frontend works with mock data RIGHT NOW, so you can start testing immediately while waiting for the real dataset!

Good luck! 🚀