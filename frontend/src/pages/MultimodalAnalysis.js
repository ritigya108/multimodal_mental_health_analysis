import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Button,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Alert,
  Tabs,
  Tab,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  CloudUpload,
  AudioFile,
  VideoFile,
  TextFields,
  Psychology,
  TrendingUp,
  Warning,
  CheckCircle,
  Info,
} from '@mui/icons-material';
import { LineChart, Line, BarChart, Bar, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function MultimodalAnalysis() {
  const [activeTab, setActiveTab] = useState(0);
  const [audioFile, setAudioFile] = useState(null);
  const [videoFile, setVideoFile] = useState(null);
  const [textInput, setTextInput] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);

  // Handle file uploads
  const handleAudioUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('audio/')) {
      setAudioFile(file);
    }
  };

  const handleVideoUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('video/')) {
      setVideoFile(file);
    }
  };

  // Analyze multimodal data
  const handleAnalyze = async () => {
    setAnalyzing(true);
    
    // Simulate API call
    setTimeout(() => {
      setResults({
        overall_risk: 'moderate',
        confidence: 0.78,
        audio_analysis: {
          sentiment: 'negative',
          score: 0.35,
          features: {
            pitch_variance: 0.42,
            speech_rate: 0.68,
            pause_duration: 0.55,
            energy: 0.38,
          }
        },
        video_analysis: {
          facial_expressions: {
            sadness: 0.65,
            neutral: 0.25,
            happiness: 0.10,
          },
          gaze_patterns: 'avoidant',
          head_pose: 'downward',
          action_units: [1, 4, 6, 15, 17],
        },
        text_analysis: {
          sentiment: 'negative',
          score: 0.28,
          keywords: ['tired', 'difficult', 'struggle', 'alone'],
          linguistic_features: {
            first_person_pronouns: 0.82,
            negative_words: 0.45,
            cognitive_words: 0.35,
          }
        },
        recommendations: [
          'Consider professional consultation',
          'Practice mindfulness exercises',
          'Maintain regular sleep schedule',
          'Engage in social activities',
        ],
        risk_factors: [
          'Low vocal energy',
          'Negative sentiment in speech',
          'Reduced facial expressions',
          'Avoidant gaze patterns',
        ]
      });
      setAnalyzing(false);
    }, 3000);
  };

  // Mock data for visualizations
  const modalityScores = [
    { modality: 'Audio', score: 35, fullMark: 100 },
    { modality: 'Video', score: 42, fullMark: 100 },
    { modality: 'Text', score: 28, fullMark: 100 },
    { modality: 'Combined', score: 38, fullMark: 100 },
  ];

  const timelineData = [
    { time: '0-5s', audio: 40, video: 45, text: 35 },
    { time: '5-10s', audio: 38, video: 42, text: 30 },
    { time: '10-15s', audio: 35, video: 40, text: 28 },
    { time: '15-20s', audio: 32, video: 38, text: 25 },
  ];

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'low': return 'success';
      case 'moderate': return 'warning';
      case 'high': return 'error';
      default: return 'info';
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom fontWeight="bold">
          🎭 Multimodal Mental Health Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Upload audio, video, or text data for comprehensive AI-powered mental health assessment
        </Typography>
      </Box>

      {/* Upload Section */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Audio Upload */}
        <Grid item xs={12} md={4}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AudioFile sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                <Typography variant="h6">Audio Analysis</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Upload audio recording for voice analysis (prosody, pitch, energy)
              </Typography>
              <Button
                variant="outlined"
                component="label"
                fullWidth
                startIcon={<CloudUpload />}
              >
                Upload Audio
                <input
                  type="file"
                  hidden
                  accept="audio/*"
                  onChange={handleAudioUpload}
                />
              </Button>
              {audioFile && (
                <Chip
                  label={audioFile.name}
                  onDelete={() => setAudioFile(null)}
                  sx={{ mt: 2 }}
                  color="primary"
                />
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Video Upload */}
        <Grid item xs={12} md={4}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <VideoFile sx={{ fontSize: 40, color: 'secondary.main', mr: 2 }} />
                <Typography variant="h6">Video Analysis</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Upload video for facial expression and behavior analysis
              </Typography>
              <Button
                variant="outlined"
                component="label"
                fullWidth
                startIcon={<CloudUpload />}
              >
                Upload Video
                <input
                  type="file"
                  hidden
                  accept="video/*"
                  onChange={handleVideoUpload}
                />
              </Button>
              {videoFile && (
                <Chip
                  label={videoFile.name}
                  onDelete={() => setVideoFile(null)}
                  sx={{ mt: 2 }}
                  color="secondary"
                />
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Text Input */}
        <Grid item xs={12} md={4}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TextFields sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
                <Typography variant="h6">Text Analysis</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Enter text or transcript for linguistic analysis
              </Typography>
              <Button
                variant="outlined"
                fullWidth
                onClick={() => setActiveTab(1)}
              >
                Enter Text
              </Button>
              {textInput && (
                <Chip
                  label={`${textInput.length} characters`}
                  onDelete={() => setTextInput('')}
                  sx={{ mt: 2 }}
                  color="success"
                />
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Analyze Button */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Button
          variant="contained"
          size="large"
          startIcon={<Psychology />}
          onClick={handleAnalyze}
          disabled={!audioFile && !videoFile && !textInput}
          sx={{ px: 6, py: 1.5 }}
        >
          Analyze Mental Health Indicators
        </Button>
      </Box>

      {/* Loading */}
      {analyzing && (
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Analyzing multimodal data...
          </Typography>
          <LinearProgress sx={{ mb: 2 }} />
          <Typography variant="body2" color="text.secondary">
            Processing audio features, facial expressions, and linguistic patterns
          </Typography>
        </Paper>
      )}

      {/* Results Section */}
      {results && !analyzing && (
        <>
          {/* Overall Assessment */}
          <Paper sx={{ p: 3, mb: 4 }}>
            <Grid container spacing={3} alignItems="center">
              <Grid item xs={12} md={6}>
                <Typography variant="h5" gutterBottom>
                  Overall Assessment
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Chip
                    label={`Risk Level: ${results.overall_risk.toUpperCase()}`}
                    color={getRiskColor(results.overall_risk)}
                    size="large"
                  />
                  <Chip
                    label={`Confidence: ${(results.confidence * 100).toFixed(0)}%`}
                    variant="outlined"
                    size="large"
                  />
                </Box>
                <Alert severity={results.overall_risk === 'high' ? 'error' : 'warning'} sx={{ mt: 2 }}>
                  {results.overall_risk === 'high' 
                    ? 'High risk indicators detected. Professional consultation recommended.'
                    : 'Some concerning patterns detected. Consider monitoring and self-care practices.'}
                </Alert>
              </Grid>
              <Grid item xs={12} md={6}>
                <ResponsiveContainer width="100%" height={200}>
                  <RadarChart data={modalityScores}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="modality" />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} />
                    <Radar name="Score" dataKey="score" stroke="#6366f1" fill="#6366f1" fillOpacity={0.6} />
                  </RadarChart>
                </ResponsiveContainer>
              </Grid>
            </Grid>
          </Paper>

          {/* Detailed Results Tabs */}
          <Paper sx={{ mb: 4 }}>
            <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
              <Tab label="Audio Analysis" icon={<AudioFile />} />
              <Tab label="Video Analysis" icon={<VideoFile />} />
              <Tab label="Text Analysis" icon={<TextFields />} />
              <Tab label="Timeline" icon={<TrendingUp />} />
            </Tabs>

            <Box sx={{ p: 3 }}>
              {/* Audio Analysis Tab */}
              {activeTab === 0 && (
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="h6" gutterBottom>
                      Acoustic Features
                    </Typography>
                    <List>
                      <ListItem>
                        <ListItemText
                          primary="Pitch Variance"
                          secondary={`${(results.audio_analysis.features.pitch_variance * 100).toFixed(0)}% - Lower than normal`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Speech Rate"
                          secondary={`${(results.audio_analysis.features.speech_rate * 100).toFixed(0)}% - Moderate pace`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Pause Duration"
                          secondary={`${(results.audio_analysis.features.pause_duration * 100).toFixed(0)}% - Longer pauses detected`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Vocal Energy"
                          secondary={`${(results.audio_analysis.features.energy * 100).toFixed(0)}% - Low energy levels`}
                        />
                      </ListItem>
                    </List>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="h6" gutterBottom>
                      Sentiment Analysis
                    </Typography>
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Overall Sentiment: {results.audio_analysis.sentiment}
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={results.audio_analysis.score * 100}
                        color={results.audio_analysis.score < 0.4 ? 'error' : 'warning'}
                        sx={{ height: 10, borderRadius: 5 }}
                      />
                    </Box>
                    <Alert severity="info">
                      Voice analysis indicates potential signs of low mood based on prosodic features.
                    </Alert>
                  </Grid>
                </Grid>
              )}

              {/* Video Analysis Tab */}
              {activeTab === 1 && (
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="h6" gutterBottom>
                      Facial Expressions
                    </Typography>
                    <ResponsiveContainer width="100%" height={250}>
                      <BarChart data={[
                        { emotion: 'Sadness', value: results.video_analysis.facial_expressions.sadness * 100 },
                        { emotion: 'Neutral', value: results.video_analysis.facial_expressions.neutral * 100 },
                        { emotion: 'Happiness', value: results.video_analysis.facial_expressions.happiness * 100 },
                      ]}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="emotion" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="value" fill="#ec4899" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="h6" gutterBottom>
                      Behavioral Indicators
                    </Typography>
                    <List>
                      <ListItem>
                        <ListItemIcon>
                          <Warning color="warning" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Gaze Patterns"
                          secondary={`${results.video_analysis.gaze_patterns} - May indicate discomfort`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon>
                          <Info color="info" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Head Pose"
                          secondary={`${results.video_analysis.head_pose} - Possible low mood indicator`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon>
                          <CheckCircle color="success" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Active Action Units"
                          secondary={`AUs: ${results.video_analysis.action_units.join(', ')}`}
                        />
                      </ListItem>
                    </List>
                  </Grid>
                </Grid>
              )}

              {/* Text Analysis Tab */}
              {activeTab === 2 && (
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="h6" gutterBottom>
                      Linguistic Features
                    </Typography>
                    <List>
                      <ListItem>
                        <ListItemText
                          primary="First-Person Pronouns"
                          secondary={`${(results.text_analysis.linguistic_features.first_person_pronouns * 100).toFixed(0)}% - High self-focus`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Negative Words"
                          secondary={`${(results.text_analysis.linguistic_features.negative_words * 100).toFixed(0)}% - Elevated negative language`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Cognitive Words"
                          secondary={`${(results.text_analysis.linguistic_features.cognitive_words * 100).toFixed(0)}% - Moderate cognitive processing`}
                        />
                      </ListItem>
                    </List>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="h6" gutterBottom>
                      Key Themes
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
                      {results.text_analysis.keywords.map((keyword, idx) => (
                        <Chip key={idx} label={keyword} color="error" variant="outlined" />
                      ))}
                    </Box>
                    <Alert severity="warning">
                      Text analysis reveals concerning themes related to fatigue and isolation.
                    </Alert>
                  </Grid>
                </Grid>
              )}

              {/* Timeline Tab */}
              {activeTab === 3 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Temporal Analysis
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={timelineData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="audio" stroke="#6366f1" strokeWidth={2} />
                      <Line type="monotone" dataKey="video" stroke="#ec4899" strokeWidth={2} />
                      <Line type="monotone" dataKey="text" stroke="#10b981" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                    Shows sentiment scores across different modalities over time
                  </Typography>
                </Box>
              )}
            </Box>
          </Paper>

          {/* Recommendations */}
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom color="primary">
                  📋 Recommendations
                </Typography>
                <List>
                  {results.recommendations.map((rec, idx) => (
                    <ListItem key={idx}>
                      <ListItemIcon>
                        <CheckCircle color="success" />
                      </ListItemIcon>
                      <ListItemText primary={rec} />
                    </ListItem>
                  ))}
                </List>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom color="error">
                  ⚠️ Risk Factors Identified
                </Typography>
                <List>
                  {results.risk_factors.map((factor, idx) => (
                    <ListItem key={idx}>
                      <ListItemIcon>
                        <Warning color="warning" />
                      </ListItemIcon>
                      <ListItemText primary={factor} />
                    </ListItem>
                  ))}
                </List>
              </Paper>
            </Grid>
          </Grid>

          {/* Disclaimer */}
          <Alert severity="info" sx={{ mt: 4 }}>
            <Typography variant="body2">
              <strong>Important:</strong> This analysis is for informational purposes only and should not replace professional mental health assessment. 
              If you're experiencing mental health concerns, please consult with a qualified healthcare provider.
            </Typography>
          </Alert>
        </>
      )}
    </Container>
  );
}

export default MultimodalAnalysis;

// Made with Bob