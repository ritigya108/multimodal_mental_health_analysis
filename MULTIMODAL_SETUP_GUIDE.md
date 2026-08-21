# 🎭 Multimodal Mental Health Analysis - Complete Setup Guide

## Overview
This guide will help you set up the complete multimodal mental health analysis system with audio, video, and text processing capabilities using the DAIC-WOZ dataset.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Dataset Setup](#dataset-setup)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Data Cleaning](#data-cleaning)
6. [Running the Application](#running-the-application)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **OS**: macOS, Linux, or Windows 10+
- **RAM**: 16GB minimum (32GB recommended)
- **Storage**: 200GB free space
- **GPU**: NVIDIA GPU with CUDA support (optional but recommended)

### Software Requirements
- **Python**: 3.8 or higher
- **Node.js**: 16.x or higher
- **npm**: 8.x or higher
- **Git**: Latest version

### Install System Dependencies

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.10 node ffmpeg portaudio libsndfile
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y python3.10 python3-pip nodejs npm ffmpeg portaudio19-dev libsndfile1
```

#### Windows
```powershell
# Install Chocolatey if not already installed
# Then install dependencies
choco install python nodejs ffmpeg
```

---

## Dataset Setup

### Step 1: Request DAIC-WOZ Dataset

1. Visit: https://dcapswoz.ict.usc.edu/
2. Fill out the Data Use Agreement form
3. Wait for approval (1-3 business days)
4. Download the dataset using provided credentials

### Step 2: Organize Dataset

Create the following directory structure:

```
mental-health-ai/
├── data/
│   ├── raw/
│   │   ├── train/
│   │   │   ├── 300_P/
│   │   │   ├── 301_P/
│   │   │   └── ...
│   │   ├── dev/
│   │   └── test/
│   ├── cleaned/
│   └── labels/
│       ├── train_split_Depression_AVEC2017.csv
│       ├── dev_split_Depression_AVEC2017.csv
│       └── test_split_Depression_AVEC2017.csv
```

### Step 3: Extract Dataset

```bash
cd mental-health-ai
mkdir -p data/raw data/cleaned data/labels

# Extract downloaded files
unzip DAIC-WOZ.zip -d data/raw/

# Move label files
mv data/raw/*_split_Depression_AVEC2017.csv data/labels/
```

---

## Backend Setup

### Step 1: Create Virtual Environment

```bash
cd mental-health-ai/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### Step 2: Install Python Dependencies

```bash
# Install core dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install multimodal processing dependencies
pip install -r requirements_multimodal.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
nano .env
```

Add the following to `.env`:
```env
# Database
DATABASE_URL=sqlite:///./mental_health.db

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# CORS
CORS_ORIGINS=http://localhost:3000

# Data Paths
RAW_DATA_PATH=../data/raw
CLEANED_DATA_PATH=../data/cleaned
LABELS_PATH=../data/labels

# Model Settings
MODEL_CACHE_DIR=./models
USE_GPU=False

# Security (generate secure keys for production)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Step 4: Initialize Database

```bash
python -c "from database import init_db; init_db()"
```

---

## Frontend Setup

### Step 1: Install Node Dependencies

```bash
cd mental-health-ai/frontend

# Install dependencies
npm install

# Install additional charting libraries
npm install recharts @mui/icons-material
```

### Step 2: Configure Frontend

Create `.env` file in frontend directory:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

---

## Data Cleaning

### Step 1: Clean Training Data

```bash
cd mental-health-ai/backend

# Activate virtual environment if not already active
source venv/bin/activate

# Clean training split
python clean_daic_dataset.py \
  --raw_dir ../data/raw \
  --output_dir ../data/cleaned/train \
  --split train
```

### Step 2: Clean Development Data

```bash
python clean_daic_dataset.py \
  --raw_dir ../data/raw \
  --output_dir ../data/cleaned/dev \
  --split dev
```

### Step 3: Clean Test Data (if available)

```bash
python clean_daic_dataset.py \
  --raw_dir ../data/raw \
  --output_dir ../data/cleaned/test \
  --split test
```

### Step 4: Verify Cleaning Results

```bash
# Check quality reports
cat ../data/cleaned/train/quality_report_train.json
cat ../data/cleaned/dev/quality_report_dev.json
```

Expected output structure:
```json
{
  "total_participants": 107,
  "valid_participants": 95,
  "missing_audio": [],
  "missing_text": [],
  "missing_video": ["305", "312"],
  "low_quality_audio": ["308"],
  "low_quality_video": ["315", "320"]
}
```

---

## Running the Application

### Step 1: Start Backend Server

```bash
cd mental-health-ai/backend
source venv/bin/activate

# Start FastAPI server
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Step 2: Start Frontend Development Server

Open a new terminal:

```bash
cd mental-health-ai/frontend

# Start React development server
npm start
```

Frontend will be available at: http://localhost:3000

### Step 3: Access the Application

1. Open browser to http://localhost:3000
2. Navigate to "Multimodal Analysis" in the sidebar
3. Upload audio, video, or text for analysis

---

## Using the Multimodal Analysis Feature

### Upload Audio
1. Click "Upload Audio" button
2. Select a `.wav` or `.mp3` file
3. Supported formats: WAV, MP3, M4A, FLAC

### Upload Video
1. Click "Upload Video" button
2. Select a `.mp4` or `.avi` file
3. Supported formats: MP4, AVI, MOV

### Enter Text
1. Click "Enter Text" button
2. Type or paste text transcript
3. Minimum 50 characters recommended

### Analyze
1. Click "Analyze Mental Health Indicators"
2. Wait for processing (30-60 seconds)
3. View comprehensive results across all modalities

---

## Understanding the Results

### Overall Assessment
- **Risk Level**: Low, Moderate, or High
- **Confidence Score**: Model confidence (0-100%)
- **Radar Chart**: Scores across all modalities

### Audio Analysis
- **Pitch Variance**: Voice pitch variation
- **Speech Rate**: Words per minute
- **Pause Duration**: Length of pauses
- **Vocal Energy**: Voice intensity

### Video Analysis
- **Facial Expressions**: Emotion distribution
- **Gaze Patterns**: Eye contact behavior
- **Head Pose**: Head position and movement
- **Action Units**: Facial muscle movements

### Text Analysis
- **Sentiment Score**: Overall text sentiment
- **Key Themes**: Important words/topics
- **Linguistic Features**: Language patterns
- **First-Person Usage**: Self-reference frequency

### Timeline
- Shows how indicators change over time
- Helps identify patterns and trends

---

## Troubleshooting

### Backend Issues

#### Issue: Import errors for librosa/soundfile
```bash
# Solution: Install audio processing libraries
pip install librosa soundfile audioread

# macOS: Install portaudio
brew install portaudio

# Ubuntu: Install portaudio
sudo apt-get install portaudio19-dev
```

#### Issue: CUDA/GPU errors
```bash
# Solution: Install CPU-only version of PyTorch
pip uninstall torch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### Issue: Database connection errors
```bash
# Solution: Reinitialize database
rm mental_health.db
python -c "from database import init_db; init_db()"
```

### Frontend Issues

#### Issue: Module not found errors
```bash
# Solution: Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

#### Issue: CORS errors
```bash
# Solution: Check backend CORS settings in main.py
# Ensure frontend URL is in allow_origins list
```

#### Issue: API connection refused
```bash
# Solution: Verify backend is running
curl http://localhost:8000/health

# Check .env file has correct API_URL
```

### Data Cleaning Issues

#### Issue: Missing audio files
**Solution**: Some participants may have incomplete data. This is normal. The cleaning script will skip them and document in the quality report.

#### Issue: Low quality audio
**Solution**: Adjust quality thresholds in `clean_daic_dataset.py`:
```python
# Line ~50
'valid': duration > 60 and silence_ratio < 0.5 and clipping_ratio < 0.01
# Adjust these values as needed
```

#### Issue: Out of memory during processing
**Solution**: Process in smaller batches:
```bash
# Process specific participant IDs
python clean_daic_dataset.py --raw_dir ../data/raw --output_dir ../data/cleaned/train --split train --participant_ids 300,301,302
```

---

## Performance Optimization

### Backend Optimization

1. **Enable GPU Processing**
```python
# In .env file
USE_GPU=True
```

2. **Use Model Caching**
```python
# Models will be cached in MODEL_CACHE_DIR
# Subsequent loads will be faster
```

3. **Batch Processing**
```python
# Process multiple files at once
# Reduces overhead
```

### Frontend Optimization

1. **Enable Production Build**
```bash
npm run build
# Serve with static server
npx serve -s build
```

2. **Lazy Loading**
```javascript
// Components are already lazy-loaded
// No additional configuration needed
```

---

## Production Deployment

### Backend Deployment

1. **Use Production WSGI Server**
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. **Set Environment Variables**
```bash
export DEBUG=False
export SECRET_KEY=$(openssl rand -hex 32)
```

3. **Use PostgreSQL Database**
```bash
# Install PostgreSQL
# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost/mental_health
```

### Frontend Deployment

1. **Build for Production**
```bash
npm run build
```

2. **Deploy to Netlify/Vercel**
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod
```

---

## Security Considerations

⚠️ **IMPORTANT**: This application handles sensitive mental health data

1. **Use HTTPS in Production**
2. **Implement User Authentication**
3. **Encrypt Data at Rest**
4. **Follow HIPAA/GDPR Guidelines**
5. **Regular Security Audits**
6. **Secure API Keys**
7. **Rate Limiting**
8. **Input Validation**

---

## Additional Resources

### Documentation
- [DAIC-WOZ Dataset Guide](./DAIC_WOZ_DATASET_GUIDE.md)
- [Data Cleaning Guide](../data_cleaning_guide.md)
- [API Documentation](http://localhost:8000/docs)

### Research Papers
- Gratch et al. (2014) - DAIC-WOZ Dataset
- Valstar et al. (2016) - AVEC 2016 Challenge
- DeVault et al. (2014) - SimSensei Kiosk

### Support
- GitHub Issues: [Create Issue]
- Email: support@example.com
- Documentation: [Wiki]

---

## Next Steps

After setup:

1. ✅ Test with sample data
2. ✅ Train custom models
3. ✅ Fine-tune parameters
4. ✅ Add more features
5. ✅ Deploy to production
6. ✅ Monitor performance
7. ✅ Collect feedback
8. ✅ Iterate and improve

---

## License and Ethics

This project is for research and educational purposes. When using:

- ✅ Obtain proper consent
- ✅ Follow ethical guidelines
- ✅ Respect privacy
- ✅ Cite original work
- ✅ Use responsibly
- ✅ Seek professional guidance

**Remember**: This tool supports, but does not replace, professional mental health care.

---

**Made with ❤️ for mental health awareness**

For questions or issues, please refer to the documentation or create an issue on GitHub.