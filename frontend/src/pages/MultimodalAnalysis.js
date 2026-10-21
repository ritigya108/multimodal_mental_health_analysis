import React, { useState, useRef } from 'react';
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
  TextField,
  CircularProgress,
  Tooltip,
  IconButton,
  Snackbar,
} from '@mui/material';
import {
  CloudUpload,
  AudioFile,
  VideoFile,
  TextFields,
  Psychology,
  CheckCircle,
  Warning,
  Info,
  Delete,
  TrendingUp,
  HealthAndSafety,
  ErrorOutline,
} from '@mui/icons-material';
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RTooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import apiService from '../services/api';

// ── Helpers ──────────────────────────────────────────────────────────────────

const RISK_META = {
  low:      { color: '#10b981', bg: '#d1fae5', label: 'Low Risk',      icon: '🟢' },
  moderate: { color: '#f59e0b', bg: '#fef3c7', label: 'Moderate Risk', icon: '🟡' },
  high:     { color: '#ef4444', bg: '#fee2e2', label: 'High Risk',      icon: '🔴' },
  critical: { color: '#7c3aed', bg: '#ede9fe', label: 'Critical',       icon: '🚨' },
};

function getRisk(r) {
  return RISK_META[r] || RISK_META.low;
}

function FeatureBar({ label, value, max = 1, color = '#6366f1' }) {
  const pct = Math.min(100, Math.round((value / max) * 100));
  return (
    <Box sx={{ mb: 1.5 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
        <Typography variant="body2">{label}</Typography>
        <Typography variant="body2" fontWeight={600}>{pct}%</Typography>
      </Box>
      <LinearProgress
        variant="determinate"
        value={pct}
        sx={{
          height: 8,
          borderRadius: 4,
          backgroundColor: '#e5e7eb',
          '& .MuiLinearProgress-bar': { backgroundColor: color, borderRadius: 4 },
        }}
      />
    </Box>
  );
}

const SAMPLE_TEXTS = {
  '— select a sample —': '',
  'Low risk (positive)':
    'Today was actually a good day. I went for a walk in the morning and felt ' +
    'peaceful. I am grateful for my family and feeling motivated about my goals. ' +
    'Things are going well and I feel calm and content.',
  'Moderate risk':
    'I have been feeling a bit stressed and worried lately. Work has been difficult ' +
    'and I am tired most of the time. I sometimes feel alone and it is hard to ' +
    'concentrate. I hope things get better soon.',
  'High risk':
    'Everything feels hopeless. I am exhausted all the time and nothing seems ' +
    'worthwhile. I feel empty inside and I cannot stop crying. I am worthless ' +
    'and nobody would notice if I disappeared. I just want the pain to stop.',
  'Critical risk':
    'I want to die. I have been thinking about suicide for weeks. ' +
    'I feel there is no reason to live and I am better off dead. ' +
    'I cannot take it anymore. I have lost all hope.',
};

// ── Main component ────────────────────────────────────────────────────────────

function MultimodalAnalysis() {
  const [activeTab, setActiveTab]   = useState(0);
  const [audioFile, setAudioFile]   = useState(null);
  const [videoFile, setVideoFile]   = useState(null);
  const [textInput, setTextInput]   = useState('');
  const [sampleKey, setSampleKey]   = useState('— select a sample —');
  const [analyzing, setAnalyzing]   = useState(false);
  const [results, setResults]       = useState(null);
  const [error, setError]           = useState('');
  const [snack, setSnack]           = useState('');

  const audioRef = useRef();
  const videoRef = useRef();

  // ── File handlers ──────────────────────────────────────────────────────────
  const handleAudioChange = (e) => {
    const f = e.target.files[0];
    if (f) { setAudioFile(f); setSnack(`Audio loaded: ${f.name}`); }
    e.target.value = '';
  };
  const handleVideoChange = (e) => {
    const f = e.target.files[0];
    if (f) { setVideoFile(f); setSnack(`Video loaded: ${f.name}`); }
    e.target.value = '';
  };

  // ── Sample text loader ─────────────────────────────────────────────────────
  const handleSampleChange = (e) => {
    const key = e.target.value;
    setSampleKey(key);
    setTextInput(SAMPLE_TEXTS[key] || '');
  };

  // ── Analyse ────────────────────────────────────────────────────────────────
  const handleAnalyze = async () => {
    if (!textInput.trim()) {
      setError('Please enter some text before running the analysis.');
      return;
    }
    setError('');
    setResults(null);
    setAnalyzing(true);

    try {
      const data = await apiService.multimodalAnalyze(textInput.trim(), audioFile, videoFile);
      setResults(data);
      setActiveTab(0);
    } catch (err) {
      // FastAPI 422 detail is an array of objects [{type,loc,msg,input}] — stringify it
      const detail = err.response?.data?.detail;
      let msg;
      if (Array.isArray(detail)) {
        msg = detail.map((d) => d.msg || JSON.stringify(d)).join('; ');
      } else if (detail && typeof detail === 'object') {
        msg = JSON.stringify(detail);
      } else {
        msg = detail || err.message || 'Analysis failed. Is the backend running?';
      }
      setError(String(msg));
    } finally {
      setAnalyzing(false);
    }
  };

  // ── Derived values from results ────────────────────────────────────────────
  const risk        = results ? getRisk(results.risk_level) : null;
  const depPct      = results ? Math.round(results.depression_probability * 100) : 0;
  const lf          = results?.linguistic_features || {};
  const mw          = results?.modality_weights || {};
  const crisis      = results?.crisis_flags || {};
  const recs        = results?.recommendations || [];
  const modelUsed   = results?.model_used || 'heuristic';

  const modalityData = results
    ? Object.entries(mw)
        .filter(([, v]) => v > 0)
        .map(([k, v]) => ({ modality: k.charAt(0).toUpperCase() + k.slice(1), weight: Math.round(v * 100) }))
    : [];

  const phqGaugeData = results
    ? [
        { label: 'PHQ-8', value: results.phq8_estimate, fill: risk.color },
        { label: '', value: 24 - results.phq8_estimate, fill: '#e5e7eb' },
      ]
    : [];

  return (
    <Container maxWidth="xl" sx={{ mt: 3, mb: 6 }}>

      {/* ── Page header ────────────────────────────────────────────────── */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          🎭 Multimodal Mental Health Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Submit a text transcript (required) and optionally an audio or video file.
          The AI combines all available modalities to assess mental health indicators.
        </Typography>
      </Box>

      {/* ── Input section ───────────────────────────────────────────────── */}
      <Grid container spacing={3} sx={{ mb: 3 }}>

        {/* Text input (left, 2/3) */}
        <Grid item xs={12} md={8}>
          <Card elevation={1}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <TextFields sx={{ color: 'success.main' }} />
                <Typography variant="h6">Transcript / Text</Typography>
                <Chip label="Required" size="small" color="primary" sx={{ ml: 'auto' }} />
              </Box>

              {/* Sample selector */}
              <TextField
                select
                fullWidth
                size="small"
                label="Load a sample text"
                value={sampleKey}
                onChange={handleSampleChange}
                sx={{ mb: 2 }}
                SelectProps={{ native: true }}
              >
                {Object.keys(SAMPLE_TEXTS).map((k) => (
                  <option key={k} value={k}>{k}</option>
                ))}
              </TextField>

              <TextField
                multiline
                fullWidth
                minRows={7}
                maxRows={14}
                placeholder={
                  'Paste a conversation transcript, journal entry, or any text here…\n\n' +
                  'Example: "I have been feeling really down lately. Everything seems ' +
                  'overwhelming and I cannot find the energy to do things I used to enjoy."'
                }
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                variant="outlined"
              />
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                {textInput.split(/\s+/).filter(Boolean).length} words · {textInput.length} characters
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* File uploads (right, 1/3) */}
        <Grid item xs={12} md={4}>
          <Grid container direction="column" spacing={2} sx={{ height: '100%' }}>

            {/* Audio */}
            <Grid item>
              <Card elevation={1}>
                <CardContent sx={{ pb: '12px !important' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <AudioFile sx={{ color: 'primary.main' }} />
                    <Typography variant="subtitle1" fontWeight={600}>Audio</Typography>
                    <Chip label="Optional" size="small" variant="outlined" sx={{ ml: 'auto' }} />
                  </Box>
                  <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1.5 }}>
                    WAV · MP3 · M4A · FLAC · OGG
                  </Typography>

                  {audioFile ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip
                        label={audioFile.name.length > 22 ? audioFile.name.slice(0, 20) + '…' : audioFile.name}
                        color="primary"
                        variant="outlined"
                        size="small"
                        sx={{ flex: 1, overflow: 'hidden' }}
                      />
                      <Tooltip title="Remove audio">
                        <IconButton size="small" onClick={() => setAudioFile(null)}>
                          <Delete fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  ) : (
                    <Button
                      variant="outlined"
                      component="label"
                      fullWidth
                      size="small"
                      startIcon={<CloudUpload />}
                    >
                      Upload Audio
                      <input type="file" hidden accept="audio/*" ref={audioRef} onChange={handleAudioChange} />
                    </Button>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Video */}
            <Grid item>
              <Card elevation={1}>
                <CardContent sx={{ pb: '12px !important' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <VideoFile sx={{ color: 'secondary.main' }} />
                    <Typography variant="subtitle1" fontWeight={600}>Video</Typography>
                    <Chip label="Optional" size="small" variant="outlined" sx={{ ml: 'auto' }} />
                  </Box>
                  <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1.5 }}>
                    MP4 · AVI · MOV · MKV
                  </Typography>

                  {videoFile ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip
                        label={videoFile.name.length > 22 ? videoFile.name.slice(0, 20) + '…' : videoFile.name}
                        color="secondary"
                        variant="outlined"
                        size="small"
                        sx={{ flex: 1, overflow: 'hidden' }}
                      />
                      <Tooltip title="Remove video">
                        <IconButton size="small" onClick={() => setVideoFile(null)}>
                          <Delete fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  ) : (
                    <Button
                      variant="outlined"
                      component="label"
                      fullWidth
                      size="small"
                      startIcon={<CloudUpload />}
                    >
                      Upload Video
                      <input type="file" hidden accept="video/*" ref={videoRef} onChange={handleVideoChange} />
                    </Button>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Modalities active summary */}
            <Grid item>
              <Card elevation={1} sx={{ backgroundColor: 'background.default' }}>
                <CardContent sx={{ pb: '12px !important' }}>
                  <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1 }}>
                    Active modalities
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip label="Text" size="small" color={textInput.trim() ? 'success' : 'default'} />
                    <Chip label="Audio" size="small" color={audioFile ? 'primary' : 'default'} />
                    <Chip label="Video" size="small" color={videoFile ? 'secondary' : 'default'} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>
      </Grid>

      {/* ── Error ───────────────────────────────────────────────────────── */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {String(error)}
        </Alert>
      )}

      {/* ── Analyse button ───────────────────────────────────────────────── */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Button
          variant="contained"
          size="large"
          startIcon={analyzing ? <CircularProgress size={20} color="inherit" /> : <Psychology />}
          onClick={handleAnalyze}
          disabled={!textInput.trim() || analyzing}
          sx={{ px: 6, py: 1.5, fontSize: '1rem' }}
        >
          {analyzing ? 'Analysing…' : 'Run Multimodal Analysis'}
        </Button>
        {!textInput.trim() && (
          <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 1 }}>
            Enter text above to enable analysis
          </Typography>
        )}
      </Box>

      {/* ── Analysing progress bar ───────────────────────────────────────── */}
      {analyzing && (
        <Paper sx={{ p: 3, mb: 4, textAlign: 'center' }} elevation={1}>
          <LinearProgress sx={{ mb: 2, borderRadius: 2 }} />
          <Typography variant="body2" color="text.secondary">
            Extracting linguistic features · computing risk score · fusing modalities…
          </Typography>
        </Paper>
      )}

      {/* ══════════════════════════════════════════════════════════════════
          RESULTS
      ══════════════════════════════════════════════════════════════════ */}
      {results && !analyzing && (
        <>
          {/* ── Crisis banner ─────────────────────────────────────────── */}
          {crisis.high_risk_detected && (
            <Alert severity="error" icon={<ErrorOutline />} sx={{ mb: 3, fontSize: '1rem' }}>
              <strong>🚨 CRITICAL: Potential crisis language detected.</strong><br />
              Please contact a mental health professional immediately.<br />
              <strong>KIRAN: 1800-599-0019</strong> (India, free, 24/7) &nbsp;|&nbsp;
              iCall: 9152987821 &nbsp;|&nbsp; Vandrevala: 1860-2662-345
            </Alert>
          )}
          {!crisis.high_risk_detected && crisis.medium_risk_detected && (
            <Alert severity="warning" sx={{ mb: 3 }}>
              <strong>⚠️ Elevated distress signals detected.</strong> Consider reaching out to a
              mental health professional. KIRAN: 1800-599-0019 (free, 24/7)
            </Alert>
          )}

          {/* ── Top KPI row ───────────────────────────────────────────── */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            {/* Risk level */}
            <Grid item xs={12} sm={6} md={3}>
              <Paper
                elevation={0}
                sx={{
                  p: 2.5,
                  borderLeft: `5px solid ${risk.color}`,
                  backgroundColor: risk.bg,
                  height: '100%',
                }}
              >
                <Typography variant="caption" color="text.secondary" display="block">RISK LEVEL</Typography>
                <Typography variant="h5" fontWeight={700} sx={{ color: risk.color, mt: 0.5 }}>
                  {risk.icon} {risk.label}
                </Typography>
              </Paper>
            </Grid>

            {/* Depression probability */}
            <Grid item xs={12} sm={6} md={3}>
              <Paper elevation={0} sx={{ p: 2.5, border: '1px solid', borderColor: 'divider', height: '100%' }}>
                <Typography variant="caption" color="text.secondary" display="block">DEPRESSION PROBABILITY</Typography>
                <Typography variant="h5" fontWeight={700} sx={{ mt: 0.5 }}>
                  {depPct}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={depPct}
                  sx={{
                    mt: 1, height: 6, borderRadius: 3,
                    backgroundColor: '#e5e7eb',
                    '& .MuiLinearProgress-bar': { backgroundColor: risk.color },
                  }}
                />
              </Paper>
            </Grid>

            {/* PHQ-8 */}
            <Grid item xs={12} sm={6} md={3}>
              <Paper elevation={0} sx={{ p: 2.5, border: '1px solid', borderColor: 'divider', height: '100%' }}>
                <Typography variant="caption" color="text.secondary" display="block">PHQ-8 ESTIMATE</Typography>
                <Typography variant="h5" fontWeight={700} sx={{ mt: 0.5 }}>
                  {results.phq8_estimate} <Typography component="span" variant="body1" color="text.secondary">/ 24</Typography>
                </Typography>
                <Typography variant="caption" color="text.secondary">≥ 10 = moderate–severe</Typography>
              </Paper>
            </Grid>

            {/* Binary */}
            <Grid item xs={12} sm={6} md={3}>
              <Paper elevation={0} sx={{ p: 2.5, border: '1px solid', borderColor: 'divider', height: '100%' }}>
                <Typography variant="caption" color="text.secondary" display="block">CLASSIFICATION</Typography>
                <Typography variant="h5" fontWeight={700} sx={{ mt: 0.5 }}>
                  {results.binary_prediction === 1 ? '🔴 Depressed' : '🟢 Not Depressed'}
                </Typography>
                <Chip
                  label={`Model: ${modelUsed}`}
                  size="small"
                  variant="outlined"
                  sx={{ mt: 1 }}
                />
              </Paper>
            </Grid>
          </Grid>

          {/* ── Charts row ────────────────────────────────────────────── */}
          <Grid container spacing={3} sx={{ mb: 3 }}>

            {/* Modality contribution radar */}
            <Grid item xs={12} md={5}>
              <Paper elevation={1} sx={{ p: 2.5, height: '100%' }}>
                <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                  Modality Contribution
                </Typography>
                {modalityData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={220}>
                    <RadarChart data={modalityData} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="modality" />
                      <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />
                      <Radar
                        name="Weight"
                        dataKey="weight"
                        stroke="#6366f1"
                        fill="#6366f1"
                        fillOpacity={0.55}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                ) : (
                  <Typography variant="body2" color="text.secondary">No modality data.</Typography>
                )}
              </Paper>
            </Grid>

            {/* PHQ-8 bar */}
            <Grid item xs={12} md={7}>
              <Paper elevation={1} sx={{ p: 2.5, height: '100%' }}>
                <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                  PHQ-8 Score Breakdown
                </Typography>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart
                    data={[
                      { label: 'Estimated Score', value: results.phq8_estimate, fill: risk.color },
                      { label: 'Remaining', value: Math.max(0, 24 - results.phq8_estimate), fill: '#e5e7eb' },
                      { label: 'Threshold (10)', value: 10, fill: '#f59e0b' },
                    ]}
                    margin={{ top: 10, right: 20, bottom: 10, left: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                    <YAxis domain={[0, 24]} tick={{ fontSize: 12 }} />
                    <RTooltip />
                    <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                      {[
                        { fill: risk.color },
                        { fill: '#e5e7eb' },
                        { fill: '#f59e0b' },
                      ].map((entry, i) => (
                        <Cell key={i} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>
          </Grid>

          {/* ── Detailed tabs ─────────────────────────────────────────── */}
          <Paper elevation={1} sx={{ mb: 3 }}>
            <Tabs
              value={activeTab}
              onChange={(_, v) => setActiveTab(v)}
              sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}
            >
              <Tab label="Text Analysis" icon={<TextFields />} iconPosition="start" />
              <Tab label="Modality Weights" icon={<TrendingUp />} iconPosition="start" />
              <Tab label="Audio / Video" icon={<AudioFile />} iconPosition="start" />
            </Tabs>

            <Box sx={{ p: 3 }}>

              {/* ── Tab 0: Text Analysis ──────────────────────────────── */}
              {activeTab === 0 && (
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                      Linguistic Feature Extraction
                    </Typography>
                    {Object.keys(lf).length > 0 ? (
                      <>
                        <FeatureBar
                          label="First-person pronoun rate"
                          value={lf.first_person_ratio || 0}
                          color="#6366f1"
                        />
                        <FeatureBar
                          label="Negative word rate"
                          value={lf.negative_word_ratio || 0}
                          color="#ef4444"
                        />
                        <FeatureBar
                          label="Positive word rate"
                          value={lf.positive_word_ratio || 0}
                          color="#10b981"
                        />
                        <Divider sx={{ my: 1.5 }} />
                        <Typography variant="body2">
                          Word count: <strong>{lf.word_count || 0}</strong>
                        </Typography>
                      </>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        Detailed linguistic features available in heuristic mode only.
                      </Typography>
                    )}
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                      Crisis Signal Detection
                    </Typography>
                    <List dense>
                      <ListItem>
                        <ListItemIcon>
                          {crisis.high_risk_detected
                            ? <ErrorOutline color="error" />
                            : <CheckCircle color="success" />}
                        </ListItemIcon>
                        <ListItemText
                          primary="High-risk language"
                          secondary={crisis.high_risk_detected ? 'Detected' : 'Not detected'}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon>
                          {crisis.medium_risk_detected
                            ? <Warning color="warning" />
                            : <CheckCircle color="success" />}
                        </ListItemIcon>
                        <ListItemText
                          primary="Medium-risk language"
                          secondary={crisis.medium_risk_detected ? 'Detected' : 'Not detected'}
                        />
                      </ListItem>
                    </List>

                    {results.note && (
                      <Alert severity="info" icon={<Info />} sx={{ mt: 2 }}>
                        <Typography variant="caption">{results.note}</Typography>
                      </Alert>
                    )}
                  </Grid>
                </Grid>
              )}

              {/* ── Tab 1: Modality Weights ───────────────────────────── */}
              {activeTab === 1 && (
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                      Attention Weights per Modality
                    </Typography>
                    {modalityData.map((m) => (
                      <FeatureBar
                        key={m.modality}
                        label={m.modality}
                        value={m.weight}
                        max={100}
                        color={
                          m.modality === 'Text'  ? '#6366f1' :
                          m.modality === 'Audio' ? '#10b981' : '#ec4899'
                        }
                      />
                    ))}
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Alert severity="info">
                      <Typography variant="body2">
                        <strong>How fusion works:</strong> The model assigns an attention weight to each
                        modality based on signal quality. When only text is provided, audio and video
                        weights are 0. A trained neural model produces per-sample weights; the heuristic
                        uses fixed text confidence (85%) and proportionally scales others.
                      </Typography>
                    </Alert>
                  </Grid>
                </Grid>
              )}

              {/* ── Tab 2: Audio / Video ──────────────────────────────── */}
              {activeTab === 2 && (
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                      Audio Modality
                    </Typography>
                    {audioFile ? (
                      <>
                        <Chip label={audioFile.name} color="primary" variant="outlined" sx={{ mb: 2 }} />
                        <audio controls style={{ width: '100%' }}>
                          <source src={URL.createObjectURL(audioFile)} />
                        </audio>
                        <Alert severity="success" sx={{ mt: 2 }}>
                          Audio was included in the analysis.
                          {modelUsed === 'neural'
                            ? ' The neural model extracted a mel-spectrogram and passed it through the AudioCNN encoder.'
                            : ' The heuristic raised audio confidence weight (0.55) accordingly.'}
                        </Alert>
                      </>
                    ) : (
                      <Alert severity="warning">
                        No audio file provided. Upload a .wav or .mp3 file to activate audio analysis.
                        The model will use zeros for the audio tensor until a file is provided.
                      </Alert>
                    )}
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                      Video Modality
                    </Typography>
                    {videoFile ? (
                      <>
                        <Chip label={videoFile.name} color="secondary" variant="outlined" sx={{ mb: 2 }} />
                        <video controls style={{ width: '100%', borderRadius: 8 }} height={160}>
                          <source src={URL.createObjectURL(videoFile)} />
                        </video>
                        <Alert severity="info" sx={{ mt: 2 }}>
                          Video included. Facial AU extraction (OpenFace) is performed server-side
                          when a trained model is active.
                        </Alert>
                      </>
                    ) : (
                      <Alert severity="warning">
                        No video file provided. Upload an .mp4 or .mov file to activate facial
                        expression analysis (requires OpenFace on the server).
                      </Alert>
                    )}
                  </Grid>
                </Grid>
              )}
            </Box>
          </Paper>

          {/* ── Action Plan ───────────────────────────────────────────── */}
          {results.action_plan && (
            <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <HealthAndSafety sx={{ color: risk.color }} />
                <Typography variant="h6" fontWeight={700}>Your Personalised Action Plan</Typography>
                <Chip
                  label={results.action_plan.summary}
                  size="small"
                  sx={{ ml: 'auto', backgroundColor: risk.bg, color: risk.color, fontWeight: 600, maxWidth: 340 }}
                />
              </Box>
              <Divider sx={{ mb: 3 }} />

              <Grid container spacing={2}>
                {results.action_plan.categories.map((cat, ci) => {
                  const priorityColor =
                    cat.priority === 'urgent' ? '#ef4444' :
                    cat.priority === 'high'   ? '#f59e0b' :
                    cat.priority === 'medium' ? '#6366f1' : '#10b981';
                  return (
                    <Grid item xs={12} md={6} key={ci}>
                      <Paper
                        variant="outlined"
                        sx={{
                          p: 2,
                          height: '100%',
                          borderLeft: `4px solid ${priorityColor}`,
                          borderColor: `${priorityColor} !important`,
                        }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                          <Typography variant="subtitle2" fontWeight={700} sx={{ flexGrow: 1 }}>
                            {cat.category}
                          </Typography>
                          <Chip
                            label={cat.priority.toUpperCase()}
                            size="small"
                            sx={{
                              backgroundColor: priorityColor,
                              color: '#fff',
                              fontSize: '0.65rem',
                              height: 20,
                            }}
                          />
                        </Box>
                        <List dense disablePadding>
                          {cat.steps.map((step, si) => (
                            <ListItem key={si} sx={{ alignItems: 'flex-start', px: 0, py: 0.4 }}>
                              <ListItemIcon sx={{ minWidth: 28, mt: 0.3 }}>
                                <CheckCircle sx={{ fontSize: 16, color: priorityColor }} />
                              </ListItemIcon>
                              <ListItemText
                                primary={step}
                                primaryTypographyProps={{ variant: 'body2', lineHeight: 1.5 }}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Paper>
                    </Grid>
                  );
                })}
              </Grid>
            </Paper>
          )}

          {/* ── Score Interpretation ──────────────────────────────────── */}
          <Paper elevation={1} sx={{ p: 2.5, mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Warning color="warning" />
              <Typography variant="subtitle1" fontWeight={600}>PHQ-8 Score Interpretation</Typography>
            </Box>
            <List dense>
              {[
                { range: '0–4',  label: 'Minimal depression',  color: '#10b981' },
                { range: '5–9',  label: 'Mild depression',     color: '#84cc16' },
                { range: '10–14',label: 'Moderate depression', color: '#f59e0b' },
                { range: '15–19',label: 'Moderately severe',   color: '#ef4444' },
                { range: '20–24',label: 'Severe depression',   color: '#7c3aed' },
              ].map((item) => (
                <ListItem key={item.range} dense>
                  <ListItemIcon>
                    <Box sx={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: item.color }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={`PHQ-8 ${item.range}: ${item.label}`}
                    primaryTypographyProps={{
                      variant: 'body2',
                      fontWeight: results.phq8_estimate >= parseInt(item.range) &&
                                  results.phq8_estimate <= parseInt(item.range.split('–')[1] || item.range) ? 700 : 400,
                    }}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>

          {/* ── Disclaimer ────────────────────────────────────────────── */}
          <Alert severity="info" icon={<Info />} sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>Disclaimer:</strong> This tool is for research and informational purposes only.
              It is <strong>not</strong> a substitute for professional mental health diagnosis or
              treatment. Always consult a qualified mental health professional for clinical assessment.
              In an emergency call <strong>KIRAN: 1800-599-0019</strong> (India) or your local emergency number.
            </Typography>
          </Alert>
        </>
      )}

      {/* ── Snackbar ─────────────────────────────────────────────────────── */}
      <Snackbar
        open={!!snack}
        autoHideDuration={3000}
        onClose={() => setSnack('')}
        message={snack}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
    </Container>
  );
}

export default MultimodalAnalysis;


