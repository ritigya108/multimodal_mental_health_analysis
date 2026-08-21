# DAIC-WOZ Dataset Download and Setup Guide

## Overview
The DAIC-WOZ (Distress Analysis Interview Corpus - Wizard of Oz) dataset is a multimodal dataset for depression detection containing audio, video, and text data from clinical interviews.

## Dataset Information
- **Full Name**: Distress Analysis Interview Corpus - Wizard of Oz
- **Purpose**: Depression detection and mental health analysis
- **Modalities**: Audio, Video, Text transcripts, Facial features
- **Size**: ~135 participants (train: 107, dev: 35, test: 47)
- **Labels**: PHQ-8 depression scores (0-24)

## Download Methods

### Method 1: Official USC SAIL Website (Recommended)
The DAIC-WOZ dataset is NOT available on Kaggle. You must request it from the official source.

**Steps:**
1. Visit the USC SAIL website: https://dcapswoz.ict.usc.edu/
2. Click on "Request Database Access"
3. Fill out the Data Use Agreement form with:
   - Your name and affiliation
   - Email address (use institutional email if possible)
   - Research purpose
   - Intended use of the data
4. Submit the form and wait for approval (usually 1-3 business days)
5. You'll receive an email with download instructions and credentials
6. Download the dataset using the provided link

**Important Notes:**
- You MUST sign a Data Use Agreement
- The dataset is for research purposes only
- Cannot be redistributed or shared
- Must cite the original paper in publications

### Method 2: Alternative Sources (If Available)

#### IEEE Dataport
Some researchers have uploaded processed versions:
1. Visit: https://ieee-dataport.org/
2. Search for "DAIC-WOZ" or "depression detection"
3. Check if any processed versions are available
4. Follow their download instructions

#### Research Collaborations
- Contact researchers who have published papers using DAIC-WOZ
- Ask if they can share preprocessed features (not raw data)
- Join research groups working on mental health AI

## Dataset Structure After Download

```
DAIC-WOZ/
├── train_split_Depression_AVEC2017.csv    # Training labels
├── dev_split_Depression_AVEC2017.csv      # Development labels
├── test_split_Depression_AVEC2017.csv     # Test labels (no PHQ scores)
├── train/
│   ├── 300_P/
│   │   ├── 300_AUDIO.wav          # Audio recording (~20 min)
│   │   ├── 300_TRANSCRIPT.csv     # Text transcript with timestamps
│   │   ├── 300_CLNF_features.txt  # Facial features (OpenFace)
│   │   ├── 300_CLNF_AUs.txt       # Action Units
│   │   └── 300_P.mp4              # Video file
│   ├── 301_P/
│   ├── 302_P/
│   └── ... (107 participants)
├── dev/
│   └── ... (35 participants)
└── test/
    └── ... (47 participants)
```

## File Descriptions

### 1. Audio Files (*.wav)
- **Format**: WAV, 16-bit PCM
- **Sample Rate**: 16 kHz (typically)
- **Duration**: 7-33 minutes per interview
- **Content**: Clinical interview between participant and virtual interviewer (Ellie)

### 2. Transcript Files (*_TRANSCRIPT.csv)
- **Format**: CSV with tab separator
- **Columns**:
  - `start_time`: Start timestamp (seconds)
  - `stop_time`: End timestamp (seconds)
  - `speaker`: "Participant" or "Ellie"
  - `value`: Spoken text

### 3. Facial Feature Files (*_CLNF_features.txt)
- **Extracted using**: OpenFace 2.0
- **Features**:
  - 68 facial landmarks (x, y coordinates)
  - Head pose (6 DOF: Tx, Ty, Tz, Rx, Ry, Rz)
  - Gaze direction
  - 17 Action Units (AU intensities)
  - Face detection confidence

### 4. Video Files (*.mp4)
- **Resolution**: 640x480 or similar
- **Frame Rate**: 30 fps
- **Content**: Participant's face during interview

### 5. Label Files (*.csv)
- **Columns**:
  - `Participant_ID`: Unique identifier
  - `PHQ8_Score`: Depression score (0-24)
  - `PHQ8_Binary`: 0 (no depression) or 1 (depression, score ≥ 10)
  - `Gender`: Male/Female

## Citation

If you use this dataset, you MUST cite:

```bibtex
@inproceedings{gratch2014distress,
  title={The distress analysis interview corpus of human and computer interviews},
  author={Gratch, Jonathan and Artstein, Ron and Lucas, Gale M and Stratou, Giota and Scherer, Stefan and Nazarian, Angela and Wood, Rachel and Boberg, Jill and DeVault, David and Marsella, Stacy and others},
  booktitle={LREC},
  pages={3123--3128},
  year={2014}
}
```

## Data Statistics

### Training Set
- Total participants: 107
- Depressed (PHQ-8 ≥ 10): 31 (29%)
- Non-depressed (PHQ-8 < 10): 76 (71%)

### Development Set
- Total participants: 35
- Depressed: 10 (29%)
- Non-depressed: 25 (71%)

### Test Set
- Total participants: 47
- Labels: Not publicly available (for competition)

## Preprocessing Requirements

After downloading, you'll need to:

1. **Audio Processing**
   - Resample to consistent sample rate (16 kHz)
   - Remove silence
   - Normalize volume
   - Extract acoustic features (MFCC, prosody, etc.)

2. **Text Processing**
   - Clean transcripts (remove fillers, normalize)
   - Extract linguistic features
   - Apply sentiment analysis
   - Identify key questions/responses

3. **Video/Facial Processing**
   - Validate OpenFace features
   - Handle missing frames
   - Normalize features
   - Extract temporal patterns

4. **Temporal Alignment**
   - Align audio, text, and video by timestamps
   - Create synchronized segments
   - Handle missing modalities

## Storage Requirements

- **Raw Dataset**: ~50-100 GB
- **Processed Features**: ~5-10 GB
- **Recommended**: 150+ GB free space for processing

## Legal and Ethical Considerations

⚠️ **IMPORTANT**:
- This dataset contains sensitive mental health data
- Must comply with IRB/ethics board requirements
- Cannot share or redistribute the dataset
- Must ensure data security and privacy
- Use only for approved research purposes
- Follow HIPAA/GDPR guidelines if applicable

## Troubleshooting

### Issue: Cannot Download from USC SAIL
**Solution**: 
- Ensure you've signed the Data Use Agreement
- Check your email (including spam folder)
- Contact: dcapswoz@ict.usc.edu

### Issue: Missing Files in Dataset
**Solution**:
- Some participants may have incomplete data
- Document missing modalities
- Use only complete samples or apply imputation

### Issue: Large File Sizes
**Solution**:
- Download in batches
- Use compression
- Consider cloud storage (AWS, Google Cloud)

## Alternative Datasets

If you cannot access DAIC-WOZ, consider:

1. **E-DAIC** (Extended DAIC)
   - Similar structure, more participants
   - Request from USC SAIL

2. **AVEC Datasets**
   - AVEC 2013, 2014, 2016, 2017, 2019
   - Various mental health tasks
   - Available through competitions

3. **MODMA Dataset**
   - Multimodal depression dataset
   - Chinese language
   - Available on request

4. **D-Vlog Dataset**
   - YouTube vlogs with depression labels
   - Publicly available
   - Less controlled than DAIC-WOZ

## Next Steps

After obtaining the dataset:

1. ✅ Verify data integrity
2. ✅ Run quality checks (see data_cleaning_guide.md)
3. ✅ Preprocess all modalities
4. ✅ Extract features
5. ✅ Create train/dev/test splits
6. ✅ Build multimodal models
7. ✅ Evaluate and validate

## Support

For dataset-specific questions:
- Email: dcapswoz@ict.usc.edu
- USC SAIL Lab: https://sail.usc.edu/

For technical implementation:
- Refer to: data_cleaning_guide.md
- Check: clean_audio.py and clean_text.py scripts

---

**Remember**: This is sensitive mental health data. Handle with care and respect for participants' privacy.