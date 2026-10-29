import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Card, CardContent, Typography, Button, TextField,
  Tab, Tabs, Alert, Chip, LinearProgress, Divider,
  Grid, CircularProgress, Tooltip, IconButton,
} from '@mui/material';
import {
  TextFields as TextIcon,
  Mic as MicIcon,
  Videocam as VideoIcon,
  Layers as CombinedIcon,
  Stop as StopIcon,
  Replay as ReplayIcon,
  Send as SubmitIcon,
  CheckCircleOutline as DoneIcon,
  InfoOutlined as InfoIcon,
} from '@mui/icons-material';
import apiService from '../services/api';
import CrisisBanner from '../components/CrisisBanner';

const SAMPLE_TEXTS = [
  "I have been feeling very low and unmotivated for several weeks. I struggle to get out of bed and find no enjoyment in things I used to love.",
  "Things have been okay. I've had some stressful days but mostly I feel fine. Sleeping well and eating regularly.",
  "I feel completely hopeless. Nothing seems worth doing. I am exhausted all the time and can't concentrate.",
];

// â”€â”€ Recording hook â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function useRecorder(mediaType) {
  const [recording, setRecording]   = useState(false);
  const [blob, setBlob]             = useState(null);
  const [seconds, setSeconds]       = useState(0);
  const [permError, setPermError]   = useState(null);
  const mediaRef   = useRef(null);
  const timerRef   = useRef(null);
  const chunksRef  = useRef([]);

  const start = async () => {
    setPermError(null);
    try {
      const constraints = mediaType === 'video'
        ? { video: true, audio: true }
        : { audio: true };
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      chunksRef.current = [];
      const mr = new MediaRecorder(stream);
      mr.ondataavailable = (e) => chunksRef.current.push(e.data);
      mr.onstop = () => {
        const mimeType = mediaType === 'video' ? 'video/webm' : 'audio/webm';
        setBlob(new Blob(chunksRef.current, { type: mimeType }));
        stream.getTracks().forEach((t) => t.stop());
      };
      mr.start();
      mediaRef.current = mr;
      setRecording(true);
      setSeconds(0);
      timerRef.current = setInterval(() => setSeconds((s) => s + 1), 1000);
    } catch (e) {
      setPermError(
        e.name === 'NotAllowedError'
          ? 'Permission denied. Please allow microphone/camera access in browser settings.'
          : `Could not access ${mediaType}: ${e.message}`
      );
    }
  };

  const stop = () => {
    mediaRef.current?.stop();
    clearInterval(timerRef.current);
    setRecording(false);
  };

  const reset = () => {
    stop();
    setBlob(null);
    setSeconds(0);
    setPermError(null);
  };

  const formatTime = (s) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;

  return { recording, blob, seconds, permError, start, stop, reset, formatTime };
}

// â”€â”€ RecorderPanel â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function RecorderPanel({ type, label, icon }) {
  const { recording, blob, seconds, permError, start, stop, reset, formatTime } = useRecorder(type);

  return (
    <Box>
      {permError && (
        <Alert severity="error" sx={{ mb: 2 }}>{permError}</Alert>
      )}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
        {!recording && !blob && (
          <Button
            variant="contained"
            startIcon={icon}
            onClick={start}
            aria-label={`Start ${label} recording`}
          >
            Start recording
          </Button>
        )}
        {recording && (
          <>
            <Button
              variant="contained"
              color="error"
              startIcon={<StopIcon />}
              onClick={stop}
              aria-label="Stop recording"
            >
              Stop
            </Button>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: 'error.main',
                         animation: 'pulse 1s infinite', '@keyframes pulse': {
                           '0%, 100%': { opacity: 1 }, '50%': { opacity: 0.3 } } }} />
              <Typography variant="body2" sx={{ fontFamily: 'monospace', fontWeight: 600 }}>
                {formatTime(seconds)}
              </Typography>
            </Box>
          </>
        )}
        {blob && !recording && (
          <>
            <Chip
              icon={<DoneIcon />}
              label={`Recorded (${formatTime(seconds)})`}
              color="success"
              variant="outlined"
            />
            <Tooltip title="Record again">
              <IconButton size="small" onClick={reset} aria-label="Re-record">
                <ReplayIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </>
        )}
      </Box>
      {recording && (
        <LinearProgress color="error" sx={{ borderRadius: 2 }} />
      )}
    </Box>
  );
}

// â”€â”€ Tab panel wrapper â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function TabPanel({ children, value, index }) {
  return (
    <Box
      role="tabpanel"
      hidden={value !== index}
      id={`assess-tab-${index}`}
      aria-labelledby={`assess-tab-btn-${index}`}
    >
      {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
    </Box>
  );
}

// â”€â”€ Main Assessment Page â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function Assessment() {
  const navigate = useNavigate();
  const [tab, setTab] = useState(0);
  const [text, setText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [apiError, setApiError] = useState(null);

  const audioRecorder = useRecorder('audio');
  const videoRecorder = useRecorder('video');

  const handleSubmit = async () => {
    if (!text.trim()) {
      setApiError('Please enter or record a text transcript.');
      return;
    }
    setSubmitting(true);
    setApiError(null);
    try {
      const audioBlob = tab === 1 ? audioRecorder.blob : (tab === 3 ? audioRecorder.blob : null);
      const videoBlob = tab === 2 ? videoRecorder.blob : (tab === 3 ? videoRecorder.blob : null);

      const audioFile = audioBlob ? new File([audioBlob], 'recording.webm', { type: audioBlob.type }) : null;
      const videoFile = videoBlob ? new File([videoBlob], 'recording.webm', { type: videoBlob.type }) : null;

      const res = await apiService.assess(text, audioFile, videoFile);
      setResult(res);

      // Store result in session storage so ReportDetail can access it
      const existing = JSON.parse(sessionStorage.getItem('mindcare_assessments') || '[]');
      sessionStorage.setItem('mindcare_assessments', JSON.stringify([res, ...existing]));
    } catch (e) {
      setApiError(e?.response?.data?.detail || 'Analysis failed. Please check the backend is running.');
    } finally {
      setSubmitting(false);
    }
  };

  const TABS = [
    { label: 'Text', icon: <TextIcon /> },
    { label: 'Voice', icon: <MicIcon /> },
    { label: 'Video', icon: <VideoIcon /> },
    { label: 'Combined', icon: <CombinedIcon /> },
  ];

  return (
    <Box>
      {result?.risk_level && (result.risk_level === 'critical' || result.risk_level === 'high') && (
        <CrisisBanner riskLevel={result.risk_level} />
      )}

      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>
          New assessment
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Provide your text transcript and optionally record audio or video for a fuller analysis.
        </Typography>
      </Box>

      {!result ? (
        <Grid container spacing={3}>
          {/* Input card */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent sx={{ p: 3 }}>
                <Tabs
                  value={tab}
                  onChange={(_, v) => setTab(v)}
                  aria-label="Assessment input type"
                  sx={{ mb: 2, borderBottom: '1px solid', borderColor: 'divider' }}
                >
                  {TABS.map((t, i) => (
                    <Tab
                      key={t.label}
                      icon={t.icon}
                      iconPosition="start"
                      label={t.label}
                      id={`assess-tab-btn-${i}`}
                      aria-controls={`assess-tab-${i}`}
                      sx={{ minHeight: 44, textTransform: 'none', fontWeight: 500 }}
                    />
                  ))}
                </Tabs>

                {/* Text input â€” shown on all tabs */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
                    Transcript <Typography component="span" color="error">*</Typography>
                  </Typography>
                  <TextField
                    multiline
                    rows={6}
                    fullWidth
                    placeholder="Describe how you have been feeling recently, or paste an interview transcript..."
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    inputProps={{ 'aria-label': 'Assessment transcript text', maxLength: 5000 }}
                  />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5 }}>
                    <Typography variant="caption" color="text.secondary">
                      Required. Minimum 10 words recommended.
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {text.length}/5000
                    </Typography>
                  </Box>
                </Box>

                <TabPanel value={tab} index={1}>
                  <Divider sx={{ mb: 2 }} />
                  <Typography variant="body2" sx={{ mb: 2, fontWeight: 500 }}>
                    Voice recording (optional)
                  </Typography>
                  <RecorderPanel type="audio" label="audio" icon={<MicIcon />} />
                </TabPanel>

                <TabPanel value={tab} index={2}>
                  <Divider sx={{ mb: 2 }} />
                  <Typography variant="body2" sx={{ mb: 2, fontWeight: 500 }}>
                    Video recording (optional)
                  </Typography>
                  <RecorderPanel type="video" label="video" icon={<VideoIcon />} />
                </TabPanel>

                <TabPanel value={tab} index={3}>
                  <Divider sx={{ mb: 2 }} />
                  <Typography variant="body2" sx={{ mb: 2, fontWeight: 500 }}>
                    Audio recording
                  </Typography>
                  <RecorderPanel type="audio" label="audio" icon={<MicIcon />} />
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" sx={{ mb: 2, fontWeight: 500 }}>
                      Video recording
                    </Typography>
                    <RecorderPanel type="video" label="video" icon={<VideoIcon />} />
                  </Box>
                </TabPanel>

                {apiError && (
                  <Alert severity="error" sx={{ mt: 2 }}>{apiError}</Alert>
                )}

                <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                  <Button
                    variant="contained"
                    size="large"
                    startIcon={submitting ? <CircularProgress size={18} color="inherit" /> : <SubmitIcon />}
                    onClick={handleSubmit}
                    disabled={submitting || !text.trim()}
                    aria-label="Submit assessment"
                  >
                    {submitting ? 'Analysingâ€¦' : 'Run assessment'}
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={() => { setText(''); setApiError(null); }}
                    aria-label="Clear form"
                  >
                    Clear
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Sample texts + tips */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent sx={{ p: 2.5 }}>
                <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                              color: 'text.secondary', fontWeight: 600, display: 'block', mb: 2 }}>
                  Sample inputs
                </Typography>
                {SAMPLE_TEXTS.map((s, i) => (
                  <Box
                    key={i}
                    sx={{ mb: 1.5, p: 1.5, border: '1px solid', borderColor: 'divider',
                          borderRadius: 2, cursor: 'pointer', '&:hover': { borderColor: 'primary.main', backgroundColor: '#f0fafa' } }}
                    onClick={() => setText(s)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => e.key === 'Enter' && setText(s)}
                    aria-label={`Use sample text ${i + 1}`}
                  >
                    <Typography variant="caption" color="text.secondary" sx={{ display: '-webkit-box',
                      WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                      {s}
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>

            <Card sx={{ mt: 2 }}>
              <CardContent sx={{ p: 2.5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                  <InfoIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                  <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                                color: 'text.secondary', fontWeight: 600 }}>
                    How it works
                  </Typography>
                </Box>
                <Box component="ol" sx={{ m: 0, pl: 2 }}>
                  {[
                    'Enter or record your text transcript.',
                    'Optionally add audio or video for richer analysis.',
                    'The model extracts features from each modality.',
                    'A late-fusion layer combines all signals.',
                    'You receive a risk level, confidence, and key findings.',
                  ].map((step, i) => (
                    <Box component="li" key={i} sx={{ mb: 0.75 }}>
                      <Typography variant="caption" color="text.secondary">{step}</Typography>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      ) : (
        /* â”€â”€ Inline result summary â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
        <Card>
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h5" sx={{ fontWeight: 600 }}>Assessment result</Typography>
              <Button
                variant="outlined"
                onClick={() => { setResult(null); setText(''); }}
                aria-label="Start a new assessment"
              >
                New assessment
              </Button>
            </Box>

            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Box>
                  <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                                color: 'text.secondary', fontWeight: 600, display: 'block', mb: 1 }}>
                    Risk level
                  </Typography>
                  <RiskBadgeInline level={result.risk_level} />
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                              color: 'text.secondary', fontWeight: 600, display: 'block', mb: 1 }}>
                  Confidence
                </Typography>
                <Typography variant="h5" sx={{ fontWeight: 700 }}>
                  {result.confidence != null ? `${(result.confidence * 100).toFixed(0)}%` : 'â€”'}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                              color: 'text.secondary', fontWeight: 600, display: 'block', mb: 1 }}>
                  Model
                </Typography>
                <Chip
                  label={result.demo_mode ? 'Heuristic (demo)' : 'Neural'}
                  size="small"
                  variant="outlined"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                              color: 'text.secondary', fontWeight: 600, display: 'block', mb: 1 }}>
                  PHQ-8 estimate
                </Typography>
                <Typography variant="h5" sx={{ fontWeight: 700 }}>
                  {result.phq8_estimate ?? 'â€”'} / 24
                </Typography>
              </Grid>
            </Grid>

            <Divider sx={{ my: 3 }} />

            {result.key_findings?.length > 0 && (
              <>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1.5 }}>
                  Key findings
                </Typography>
                <Box component="ul" sx={{ m: 0, pl: 2.5, mb: 3 }}>
                  {result.key_findings.map((f, i) => (
                    <Box component="li" key={i} sx={{ mb: 0.75 }}>
                      <Typography variant="body2">{f}</Typography>
                    </Box>
                  ))}
                </Box>
              </>
            )}

            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                onClick={() => navigate('/assess/report/0', { state: { result } })}
              >
                View full report
              </Button>
              <Button
                variant="outlined"
                onClick={() => navigate('/phq8')}
              >
                Complete PHQ-8
              </Button>
            </Box>

            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
              This tool provides screening support and is not a medical diagnosis.
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}

// small inline risk badge (used in result summary)
function RiskBadgeInline({ level }) {
  const COLORS = {
    low:      { bg: '#f0fdf4', color: '#16a34a', border: '#bbf7d0', label: 'Low' },
    moderate: { bg: '#fffbeb', color: '#d97706', border: '#fde68a', label: 'Moderate' },
    high:     { bg: '#fef2f2', color: '#dc2626', border: '#fecaca', label: 'High' },
    critical: { bg: '#fef2f2', color: '#dc2626', border: '#fecaca', label: 'Critical' },
  };
  const cfg = COLORS[level] || { bg: '#f9fafb', color: '#6b7280', border: '#e5e7eb', label: level || 'N/A' };
  return (
    <Box sx={{ display: 'inline-block', px: 1.5, py: 0.5, borderRadius: 2,
               backgroundColor: cfg.bg, color: cfg.color, border: `1px solid ${cfg.border}`,
               fontWeight: 700, fontSize: '1rem' }}>
      {cfg.label}
    </Box>
  );
}

export default Assessment;
