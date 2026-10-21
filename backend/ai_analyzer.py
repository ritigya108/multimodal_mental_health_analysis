from transformers import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import numpy as np
from typing import Dict, List, Tuple

class MentalHealthAnalyzer:
    """AI-powered mental health text analysis"""
    
    def __init__(self):
        # Initialize sentiment analyzers
        self.vader = SentimentIntensityAnalyzer()
        
        # Load transformer model for more advanced analysis
        # Using a mental health specific model or general sentiment model
        try:
            self.transformer_sentiment = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
        except Exception as e:
            print(f"Warning: Could not load transformer model: {e}")
            self.transformer_sentiment = None
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Comprehensive sentiment analysis using multiple methods
        Returns: dict with sentiment scores and labels
        """
        results = {}
        
        # VADER Analysis (good for social media text)
        vader_scores = self.vader.polarity_scores(text)
        results['vader'] = vader_scores
        
        # TextBlob Analysis
        blob = TextBlob(text)
        results['textblob'] = {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        }
        
        # Transformer Analysis
        if self.transformer_sentiment:
            try:
                transformer_result = self.transformer_sentiment(text[:512])[0]
                results['transformer'] = transformer_result
            except Exception as e:
                print(f"Transformer analysis failed: {e}")
                results['transformer'] = None
        
        # Aggregate sentiment
        overall_sentiment = self._aggregate_sentiment(results)
        results['overall'] = overall_sentiment
        
        return results
    
    def _aggregate_sentiment(self, results: Dict) -> Dict:
        """Aggregate multiple sentiment scores into overall assessment"""
        
        # Extract scores
        vader_compound = results['vader']['compound']
        textblob_polarity = results['textblob']['polarity']
        
        # Average the scores
        avg_score = (vader_compound + textblob_polarity) / 2
        
        # Determine label
        if avg_score >= 0.05:
            label = "positive"
        elif avg_score <= -0.05:
            label = "negative"
        else:
            label = "neutral"
        
        # Determine intensity
        intensity = abs(avg_score)
        if intensity >= 0.6:
            intensity_label = "strong"
        elif intensity >= 0.3:
            intensity_label = "moderate"
        else:
            intensity_label = "mild"
        
        return {
            'score': float(avg_score),
            'label': label,
            'intensity': intensity_label,
            'confidence': float(intensity)
        }
    
    def detect_crisis_keywords(self, text: str) -> Dict:
        """
        Detect crisis-related keywords and phrases
        Returns: dict with risk indicators
        """
        text_lower = text.lower()
        
        # Crisis keywords (this is a simplified version)
        crisis_keywords = {
            'high_risk': [
                'suicide', 'kill myself', 'end my life', 'want to die',
                'no reason to live', 'better off dead', 'harm myself'
            ],
            'medium_risk': [
                'hopeless', 'worthless', 'can\'t go on', 'give up',
                'no point', 'unbearable', 'can\'t take it'
            ],
            'low_risk': [
                'sad', 'depressed', 'anxious', 'worried', 'stressed',
                'overwhelmed', 'tired', 'exhausted'
            ]
        }
        
        detected = {
            'high_risk': [],
            'medium_risk': [],
            'low_risk': []
        }
        
        for risk_level, keywords in crisis_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected[risk_level].append(keyword)
        
        # Determine overall risk level
        if detected['high_risk']:
            risk_level = 'critical'
        elif detected['medium_risk']:
            risk_level = 'high'
        elif detected['low_risk']:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk_level': risk_level,
            'detected_keywords': detected,
            'requires_immediate_attention': len(detected['high_risk']) > 0
        }
    
    def assess_mental_health_risk(
        self,
        recent_entries: List[str],
        mood_scores: List[int]
    ) -> Dict:
        """
        Assess overall mental health risk based on recent data
        """
        if not recent_entries and not mood_scores:
            return {
                'risk_level': 'unknown',
                'score': 0,
                'factors': [],
                'recommendations': []
            }
        
        risk_factors = []
        risk_score = 0
        
        # Analyze sentiment trends
        if recent_entries:
            sentiments = [self.analyze_sentiment(entry) for entry in recent_entries]
            avg_sentiment = np.mean([s['overall']['score'] for s in sentiments])
            
            if avg_sentiment < -0.3:
                risk_factors.append("Consistently negative sentiment in journal entries")
                risk_score += 30
            
            # Check for crisis keywords
            for entry in recent_entries:
                crisis_check = self.detect_crisis_keywords(entry)
                if crisis_check['requires_immediate_attention']:
                    risk_factors.append("Crisis keywords detected")
                    risk_score += 50
                    break
        
        # Analyze mood trends
        if mood_scores:
            avg_mood = np.mean(mood_scores)
            mood_trend = np.polyfit(range(len(mood_scores)), mood_scores, 1)[0]
            
            if avg_mood < 4:
                risk_factors.append("Low average mood score")
                risk_score += 20
            
            if mood_trend < -0.5:
                risk_factors.append("Declining mood trend")
                risk_score += 25
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = 'critical'
        elif risk_score >= 50:
            risk_level = 'high'
        elif risk_score >= 30:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_level, risk_factors)
        
        return {
            'risk_level': risk_level,
            'score': risk_score,
            'factors': risk_factors,
            'recommendations': recommendations
        }
    
    def _generate_recommendations(
        self,
        risk_level: str,
        factors: List[str]
    ) -> List[str]:
        """Generate personalized recommendations based on risk assessment"""
        
        recommendations = []
        
        if risk_level == 'critical':
            recommendations.extend([
                "⚠️ URGENT: Please contact a mental health professional immediately",
                "Call National Suicide Prevention Lifeline: 988 (US) or your local emergency number",
                "Reach out to a trusted friend or family member right now",
                "Go to the nearest emergency room if you're in immediate danger"
            ])
        elif risk_level == 'high':
            recommendations.extend([
                "Schedule an appointment with a mental health professional this week",
                "Contact your therapist or counselor if you have one",
                "Reach out to a trusted friend or family member",
                "Consider calling a mental health hotline for support"
            ])
        elif risk_level == 'medium':
            recommendations.extend([
                "Consider scheduling a check-in with a mental health professional",
                "Practice daily self-care activities",
                "Maintain regular sleep schedule",
                "Engage in physical exercise (even a short walk helps)",
                "Connect with supportive friends or family"
            ])
        else:  # low risk
            recommendations.extend([
                "Continue your current self-care practices",
                "Maintain healthy sleep and exercise routines",
                "Practice mindfulness or meditation",
                "Stay connected with your support network",
                "Keep journaling to track your mental health"
            ])
        
        return recommendations

# Initialize global analyzer instance
analyzer = MentalHealthAnalyzer()


