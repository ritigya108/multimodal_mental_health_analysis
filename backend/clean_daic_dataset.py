"""
DAIC-WOZ Dataset Cleaning Script
Processes audio, text, and facial features from the DAIC-WOZ dataset
"""

import os
import pandas as pd
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
import json
import re
from scipy import stats
from scipy.signal import wiener
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

class DAICDatasetCleaner:
    """Clean and preprocess DAIC-WOZ dataset"""
    
    def __init__(self, raw_data_dir, output_dir):
        self.raw_data_dir = Path(raw_data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / 'audio_features').mkdir(exist_ok=True)
        (self.output_dir / 'text_features').mkdir(exist_ok=True)
        (self.output_dir / 'facial_features').mkdir(exist_ok=True)
        (self.output_dir / 'processed_audio').mkdir(exist_ok=True)
        
        self.quality_report = {
            'total_participants': 0,
            'valid_participants': 0,
            'missing_audio': [],
            'missing_text': [],
            'missing_video': [],
            'low_quality_audio': [],
            'low_quality_video': [],
        }
    
    def check_audio_quality(self, audio_path):
        """Check audio file quality"""
        try:
            audio, sr = librosa.load(audio_path, sr=16000)
            duration = len(audio) / sr
            
            # Check for silence
            rms = librosa.feature.rms(y=audio)[0]
            silence_ratio = np.sum(rms < 0.01) / len(rms)
            
            # Check for clipping
            clipping_ratio = np.sum(np.abs(audio) > 0.99) / len(audio)
            
            return {
                'duration': duration,
                'silence_ratio': silence_ratio,
                'clipping_ratio': clipping_ratio,
                'valid': duration > 60 and silence_ratio < 0.5 and clipping_ratio < 0.01
            }
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def preprocess_audio(self, audio_path, output_path):
        """
        Preprocess audio file:
        - Resample to 16kHz
        - Remove silence
        - Normalize volume
        - Apply noise reduction
        """
        try:
            # Load audio
            audio, sr = librosa.load(audio_path, sr=None)
            
            # Resample to 16kHz
            if sr != 16000:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
                sr = 16000
            
            # Remove silence (threshold-based)
            intervals = librosa.effects.split(audio, top_db=20)
            audio_trimmed = np.concatenate([audio[start:end] for start, end in intervals])
            
            # Normalize volume
            audio_normalized = librosa.util.normalize(audio_trimmed)
            
            # Apply Wiener filter for noise reduction
            audio_denoised = wiener(audio_normalized)
            
            # Save processed audio
            sf.write(output_path, audio_denoised, sr)
            
            return True
        except Exception as e:
            print(f"Error preprocessing audio: {e}")
            return False
    
    def clean_transcript_text(self, text):
        """
        Clean transcript text:
        - Remove filler words
        - Normalize whitespace
        - Remove special characters
        """
        if pd.isna(text):
            return ""
        
        # Remove filler words
        fillers = ['um', 'uh', 'like', 'you know', 'i mean', 'sort of', 'kind of']
        for filler in fillers:
            text = re.sub(r'\b' + filler + r'\b', '', text, flags=re.IGNORECASE)
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        # Lowercase and strip
        text = text.lower().strip()
        
        return text
    
    def process_transcript(self, transcript_path):
        """Process transcript CSV file"""
        try:
            df = pd.read_csv(transcript_path, sep='\t')
            
            # Clean text
            df['text_cleaned'] = df['value'].apply(self.clean_transcript_text)
            
            # Remove empty responses
            df = df[df['text_cleaned'].str.len() > 0]
            
            # Filter only participant responses
            df_participant = df[df['speaker'] == 'Participant'].copy()
            
            return df_participant
        except Exception as e:
            print(f"Error processing transcript: {e}")
            return None
    
    def validate_openface_data(self, openface_path):
        """Validate OpenFace extracted features"""
        try:
            df = pd.read_csv(openface_path)
            
            # Check for required columns
            required_cols = ['timestamp', 'confidence', 'success']
            if not all(col in df.columns for col in required_cols):
                return False, "Missing required columns"
            
            # Check success rate
            success_rate = df['success'].mean()
            avg_confidence = df['confidence'].mean()
            
            if success_rate < 0.8 or avg_confidence < 0.9:
                return False, f"Low quality: success={success_rate:.2f}, confidence={avg_confidence:.2f}"
            
            return True, "Valid"
        except Exception as e:
            return False, str(e)
    
    def clean_facial_features(self, openface_df):
        """
        Clean OpenFace facial features:
        - Remove low confidence frames
        - Handle missing values
        - Normalize features
        - Remove outliers
        """
        try:
            # Filter by confidence and success
            df_clean = openface_df[
                (openface_df['confidence'] > 0.9) & 
                (openface_df['success'] == 1)
            ].copy()
            
            # Select relevant features
            au_cols = [col for col in df_clean.columns if col.startswith('AU') and col.endswith('_r')]
            pose_cols = [col for col in df_clean.columns if col.startswith('pose_')]
            gaze_cols = [col for col in df_clean.columns if col.startswith('gaze_')]
            
            feature_cols = ['timestamp'] + au_cols + pose_cols + gaze_cols
            df_features = df_clean[feature_cols]
            
            # Handle missing values (interpolation)
            df_features = df_features.interpolate(method='linear', limit_direction='both')
            
            # Remove outliers (Z-score method)
            numeric_cols = au_cols + pose_cols + gaze_cols
            z_scores = np.abs(stats.zscore(df_features[numeric_cols]))
            df_features = df_features[(z_scores < 3).all(axis=1)]
            
            # Normalize features (0-1 range)
            scaler = MinMaxScaler()
            df_features[numeric_cols] = scaler.fit_transform(df_features[numeric_cols])
            
            return df_features
        except Exception as e:
            print(f"Error cleaning facial features: {e}")
            return None
    
    def extract_audio_features(self, audio_path):
        """Extract acoustic features from audio"""
        try:
            audio, sr = librosa.load(audio_path, sr=16000)
            
            # Extract features
            features = {}
            
            # MFCCs
            mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            features['mfcc_mean'] = np.mean(mfccs, axis=1)
            features['mfcc_std'] = np.std(mfccs, axis=1)
            
            # Pitch
            pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            features['pitch_mean'] = np.mean(pitch_values) if pitch_values else 0
            features['pitch_std'] = np.std(pitch_values) if pitch_values else 0
            
            # Energy
            rms = librosa.feature.rms(y=audio)[0]
            features['energy_mean'] = np.mean(rms)
            features['energy_std'] = np.std(rms)
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio)[0]
            features['zcr_mean'] = np.mean(zcr)
            features['zcr_std'] = np.std(zcr)
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            features['spectral_centroid_mean'] = np.mean(spectral_centroids)
            features['spectral_centroid_std'] = np.std(spectral_centroids)
            
            return features
        except Exception as e:
            print(f"Error extracting audio features: {e}")
            return None
    
    def process_participant(self, participant_id, split='train'):
        """Process all data for a single participant"""
        print(f"Processing participant {participant_id}...")
        
        participant_folder = self.raw_data_dir / split / f"{participant_id}_P"
        
        if not participant_folder.exists():
            print(f"Folder not found: {participant_folder}")
            return False
        
        # File paths
        audio_file = participant_folder / f"{participant_id}_AUDIO.wav"
        transcript_file = participant_folder / f"{participant_id}_TRANSCRIPT.csv"
        openface_file = participant_folder / f"{participant_id}_CLNF_features.txt"
        
        # Check for missing files
        missing = []
        if not audio_file.exists():
            missing.append('audio')
        if not transcript_file.exists():
            missing.append('transcript')
        if not openface_file.exists():
            missing.append('openface')
        
        if missing:
            print(f"Missing files for {participant_id}: {missing}")
            for m in missing:
                self.quality_report[f'missing_{m}'].append(participant_id)
            return False
        
        # Process audio
        audio_quality = self.check_audio_quality(audio_file)
        if not audio_quality['valid']:
            print(f"Low quality audio for {participant_id}")
            self.quality_report['low_quality_audio'].append(participant_id)
            return False
        
        # Preprocess audio
        processed_audio_path = self.output_dir / 'processed_audio' / f"{participant_id}.wav"
        if not self.preprocess_audio(audio_file, processed_audio_path):
            return False
        
        # Extract audio features
        audio_features = self.extract_audio_features(processed_audio_path)
        if audio_features:
            np.save(
                self.output_dir / 'audio_features' / f"{participant_id}.npy",
                audio_features
            )
        
        # Process transcript
        transcript_df = self.process_transcript(transcript_file)
        if transcript_df is not None:
            transcript_df.to_csv(
                self.output_dir / 'text_features' / f"{participant_id}.csv",
                index=False
            )
        
        # Process facial features
        if openface_file.exists():
            valid, msg = self.validate_openface_data(openface_file)
            if valid:
                openface_df = pd.read_csv(openface_file)
                facial_features = self.clean_facial_features(openface_df)
                if facial_features is not None:
                    facial_features.to_csv(
                        self.output_dir / 'facial_features' / f"{participant_id}.csv",
                        index=False
                    )
            else:
                print(f"Invalid OpenFace data for {participant_id}: {msg}")
                self.quality_report['low_quality_video'].append(participant_id)
        
        self.quality_report['valid_participants'] += 1
        return True
    
    def process_dataset(self, split='train'):
        """Process entire dataset split"""
        split_dir = self.raw_data_dir / split
        
        if not split_dir.exists():
            print(f"Split directory not found: {split_dir}")
            return
        
        # Get all participant folders
        participant_folders = [f for f in split_dir.iterdir() if f.is_dir() and f.name.endswith('_P')]
        
        self.quality_report['total_participants'] = len(participant_folders)
        
        print(f"Processing {len(participant_folders)} participants from {split} split...")
        
        for folder in participant_folders:
            participant_id = folder.name.split('_')[0]
            self.process_participant(participant_id, split)
        
        # Save quality report
        report_path = self.output_dir / f'quality_report_{split}.json'
        with open(report_path, 'w') as f:
            json.dump(self.quality_report, f, indent=2)
        
        print(f"\nProcessing complete!")
        print(f"Total participants: {self.quality_report['total_participants']}")
        print(f"Valid participants: {self.quality_report['valid_participants']}")
        print(f"Quality report saved to: {report_path}")


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean DAIC-WOZ dataset')
    parser.add_argument('--raw_dir', type=str, required=True, help='Path to raw DAIC-WOZ data')
    parser.add_argument('--output_dir', type=str, required=True, help='Path to output directory')
    parser.add_argument('--split', type=str, default='train', choices=['train', 'dev', 'test'], help='Dataset split to process')
    
    args = parser.parse_args()
    
    # Create cleaner instance
    cleaner = DAICDatasetCleaner(args.raw_dir, args.output_dir)
    
    # Process dataset
    cleaner.process_dataset(args.split)


if __name__ == '__main__':
    main()

# Made with Bob