import React, { useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Card, CardContent, Typography, Button, TextField,
  Alert, Chip, LinearProgress, Divider, Grid, CircularProgress,
  Tooltip, IconButton, Stepper, Step, StepLabel, StepContent,
  Paper,
} from '@mui/material';
import {
  Mic as MicIcon,
  Stop as StopIcon,
  Replay as ReplayIcon,
  Send as SubmitIcon,
  CheckCircleOutline as DoneIcon,
  ArrowForward as NextIcon,
  ArrowBack as BackIcon,
  InfoOutlined as InfoIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import apiService from '../services/api';
import CrisisBanner from '../components/CrisisBanner';

// ── EATD question definitions ─────────────────────────────────────────────────
const EATD_QUESTIONS = [
  {
    key:         'positive',
    label:       'Positive question',
    prompt:      'Describe a positive memory or a time you felt happy.',
    placeholder: 'Write your response here. For example: "I felt happy when..." (Mandarin or English)',
    sampleText:  '我和家人一起去旅行，大家都很开心，感觉特别幸福。',
  },
  {
    key:         'neutral',
    label:       'Neutral question',
    prompt:      'Describe your daily routine.',
    placeholder: 'Describe a typical day: when you wake up, what you do, how you feel.',
    sampleText:  '我每天早上七点起床，吃早饭，然后去上学或者工作。',
  },
  {
    key:         'negative',
    label:       'Negative question',
    prompt:      'Describe a difficult or stressful experience.',
    placeholder: 'You can write about a challenging situation, how it affected you, or how you coped.',
    sampleText:  '最近我感到很疲惫，有时候觉得很难集中注意力，睡眠也不太好。',
  },
];

const CARD_LABEL_SX = {
  textTransform: 'uppercase',
  letterSpacing: '0.06em',
  color: 'text.secondary',
  fontWeight: 600,
  fontSize: '0.72rem',
  display: 'block',
  mb: 1,
};

// ── Audio recorder hook ────────────────────────────────────────────────────────
function useRecorder() {
  const [recording, setRecording] = useState(false);
  const [blob, setBlob]           = useState(null);
  const [seconds, setSeconds]     = useState(0);
  const [permError, setPermError] = useState(null);
  const mediaRef  = useRef(null);
  const timerRef  = useRef(null);
  const chunksRef = useRef([]);

  const start = useCallback(async () => {
    setPermError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      chunksRef.current = [];
      const mr = new MediaRecorder(stream);
      mr.ondataavailable = (e) => chunksRef.current.push(e.data);
      mr.onstop = () => {
        setBlob(new Blob(chunksRef.current, { type: 'audio/webm' }));
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
          ? 'Microphone access denied. Please allow microphone access in your browser settings, then try again.'
          : `Could not access microphone: ${e.message}`
      );
    }
  }, []);

  const stop = useCallback(() => {
    mediaRef.current?.stop();
    clearInterval(timerRef.current);
    setRecording(false);
  }, []);

  const reset = useCallback(() => {
    stop();
    setBlob(null);
    setSeconds(0);
    setPermError(null);
  }, [stop]);

  const fmt = (s) =>
    `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;

  return { recording, blob, seconds, permError, start, stop, reset, fmt };
}

// ── RecorderPanel ─────────────────────────────────────────────────────────────
function RecorderPanel({ recorder }) {
  const { recording, blob, seconds, permError, start, stop, reset, fmt } = recorder;

  return (
    <Box>
      {permError && (
        <Alert severity="error" sx={{ mb: 1.5 }}>{permError}</Alert>
      )}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexWrap: 'wrap' }}>
        {!recording && !blob && (
          <Button
            variant="outlined"
            size="small"
            startIcon={<MicIcon />}
            onClick={start}
            aria-label="Start audio recording"
          >
            Record audio (optional)
          </Button>
        )}
        {recording && (
          <>
            <Button
              variant="contained"
              color="error"
              size="small"
              startIcon={<StopIcon />}
              onClick={stop}
              aria-label="Stop recording"
            >
              Stop
            </Button>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
              <Box
                sx={{
                  width: 8, height: 8, borderRadius: '50%', backgroundColor: 'error.main',
                  animation: 'blink 1s step-start infinite',
                  '@keyframes blink': { '50%': { opacity: 0 } },
                }}
                aria-hidden="true"
              />
              <Typography variant="caption" sx={{ fontFamily: 'monospace', fontWeight: 600 }}>
                {fmt(seconds)}
              </Typography>
            </Box>
            <LinearProgress color="error" sx={{ flex: 1, minWidth: 80, borderRadius: 2 }} />
          </>
        )}
        {blob && !recording && (
          <>
            <Chip
              icon={<DoneIcon />}
              label={`Recorded (${fmt(seconds)})`}
              size="small"
              sx={{
                backgroundColor: '#f0fdf4', color: '#16a34a',
                border: '1px solid #bbf7d0', fontWeight: 600,
              }}
            />
            <Tooltip title="Record again">
              <IconButton size="small" onClick={reset} aria-label="Re-record audio">
                <ReplayIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </>
        )}
      </Box>
    </Box>
  );
}

// ── Risk badge (inline) ───────────────────────────────────────────────────────
function RiskBadge({ level }) {
  const cfg = {
    low:      { bg: '#f0fdf4', color: '#16a34a', border: '#bbf7d0', label: 'Low' },
    moderate: { bg: '#fffbeb', color: '#d97706', border: '#fde68a', label: 'Moderate' },
    elevated: { bg: '#fff7ed', color: '#ea580c', border: '#fed7aa', label: 'Elevated' },
    high:     { bg: '#fef2f2', color: '#dc2626', border: '#fecaca', label: 'High' },
    critical: { bg: '#fef2f2', color: '#dc2626', border: '#fecaca', label: 'Critical' },
  }[level] || { bg: '#f9fafb', color: '#6b7280', border: '#e5e7eb', label: level || 'N/A' };

  return (
    <Chip
      label={cfg.label}
      size="medium"
      sx={{
        backgroundColor: cfg.bg, color: cfg.color,
        border: `1px solid ${cfg.border}`, fontWeight: 700, fontSize: '0.8rem',
      }}
    />
  );
}

// ── Question step card ────────────────────────────────────────────────────────
function QuestionStep({ q, text, onTextChange, recorder, error }) {
  return (
    <Box>
      <Typography variant="body1" sx={{ fontWeight: 500, mb: 0.5 }}>
        {q.prompt}
      </Typography>
      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1.5 }}>
        EATD-Corpus emotional question — respond in Mandarin or English.
      </Typography>

      <TextField
        multiline
        rows={5}
        fullWidth
        placeholder={q.placeholder}
        value={text}
        onChange={(e) => onTextChange(e.target.value)}
        error={!!error}
        helperText={error || `${text.length}/2000 characters`}
        inputProps={{ 'aria-label': `${q.label} response`, maxLength: 2000 }}
        sx={{ mb: 2 }}
      />

      {/* Sample text */}
      <Box
        sx={{
          mb: 2, p: 1.5, border: '1px dashed', borderColor: 'divider',
          borderRadius: 1, cursor: 'pointer',
          '&:hover': { borderColor: 'primary.main', backgroundColor: '#f0fafa' },
        }}
        onClick={() => onTextChange(q.sampleText)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && onTextChange(q.sampleText)}
        aria-label={`Use sample response for ${q.label}`}
      >
        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, display: 'block', mb: 0.5 }}>
          Sample response (click to use)
        </Typography>
        <Typography variant="caption" color="text.secondary">{q.sampleText}</Typography>
      </Box>

      {/* Audio recorder */}
      <Typography variant="caption" sx={{ ...CARD_LABEL_SX, mb: 1 }}>
        Audio recording
      </Typography>
      <RecorderPanel recorder={recorder} />
    </Box>
  );
}

// ── Result view ───────────────────────────────────────────────────────────────
function ResultView({ result, onNew }) {
  const navigate = useNavigate();
  const pqs      = result.per_question_scores || [];

  return (
    <Box>
      {(result.risk_level === 'high' || result.risk_level === 'critical') && (
        <CrisisBanner riskLevel={result.risk_level} />
      )}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 700 }}>Assessment result</Typography>
        <Button variant="outlined" onClick={onNew} aria-label="Start a new assessment">
          New assessment
        </Button>
      </Box>

      {/* KPI row */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ p: 2.5 }}>
              <Typography variant="caption" sx={CARD_LABEL_SX}>Risk level</Typography>
              <Box sx={{ mt: 0.5 }}>
                <RiskBadge level={result.risk_level} />
              </Box>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                Based on all three questions
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ p: 2.5 }}>
              <Typography variant="caption" sx={CARD_LABEL_SX}>Confidence</Typography>
              <Typography variant="h4" sx={{ fontWeight: 700, fontSize: '2rem', lineHeight: 1.1 }}>
                {result.confidence != null ? `${(result.confidence * 100).toFixed(0)}%` : '—'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ p: 2.5 }}>
              <Typography variant="caption" sx={CARD_LABEL_SX}>SDS estimate</Typography>
              <Typography variant="h4" sx={{ fontWeight: 700, fontSize: '2rem', lineHeight: 1.1 }}>
                {result.sds_estimated ?? '—'}
                <Typography component="span" variant="caption" color="text.secondary" sx={{ ml: 0.5 }}>/ 80</Typography>
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ p: 2.5 }}>
              <Typography variant="caption" sx={CARD_LABEL_SX}>Model</Typography>
              <Chip
                label={result.demo_mode ? 'Heuristic (demo)' : 'Neural'}
                size="small"
                variant="outlined"
                sx={{ mt: 0.5 }}
              />
              {result.demo_mode && (
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.75 }}>
                  No trained checkpoint found
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Modality contributions */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ p: 2.5 }}>
              <Typography variant="caption" sx={CARD_LABEL_SX}>Modality contribution</Typography>
              {['text', 'audio'].map((m) => {
                const pct = result.modality_contributions?.[m] ?? 0;
                return (
                  <Box key={m} sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.75 }}>
                      <Typography variant="body2" sx={{ fontWeight: 500, textTransform: 'capitalize' }}>{m}</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 700 }}>{pct.toFixed(1)}%</Typography>
                    </Box>
                    <Box sx={{ height: 6, backgroundColor: '#e5e7eb', borderRadius: 3, overflow: 'hidden' }}>
                      <Box
                        sx={{ height: '100%', width: `${pct}%`, backgroundColor: 'primary.main', borderRadius: 3 }}
                        role="progressbar"
                        aria-valuenow={Math.round(pct)} aria-valuemin={0} aria-valuemax={100}
                        aria-label={`${m} contribution: ${pct.toFixed(1)}%`}
                      />
                    </Box>
                  </Box>
                );
              })}
            </CardContent>
          </Card>
        </Grid>

        {/* Per-question scores */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ p: 2.5 }}>
              <Typography variant="caption" sx={CARD_LABEL_SX}>Per-question scores</Typography>
              {pqs.map((q) => (
                <Box key={q.question} sx={{ mb: 1.5 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2" sx={{ fontWeight: 500, textTransform: 'capitalize' }}>
                      {q.question}
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 700 }}>
                      {(q.score * 100).toFixed(0)}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={q.score * 100}
                    sx={{
                      height: 4, borderRadius: 2,
                      backgroundColor: '#e5e7eb',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor:
                          q.score >= 0.6 ? '#dc2626' :
                          q.score >= 0.3 ? '#d97706' : '#16a34a',
                        borderRadius: 2,
                      },
                    }}
                    aria-label={`${q.question} question score: ${(q.score * 100).toFixed(0)}%`}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Key findings */}
      {result.key_findings?.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent sx={{ p: 2.5 }}>
            <Typography variant="caption" sx={CARD_LABEL_SX}>Key findings</Typography>
            <Box component="ul" sx={{ m: 0, pl: 2.5 }}>
              {result.key_findings.map((f, i) => (
                <Box component="li" key={i} sx={{ mb: 0.75 }}>
                  <Typography variant="body2">{f}</Typography>
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Action plan */}
      {result.action_plan?.categories?.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent sx={{ p: 2.5 }}>
            <Typography variant="caption" sx={CARD_LABEL_SX}>Recommended actions</Typography>
            {result.action_plan.categories.map((cat) => (
              <Box key={cat.category} sx={{ mb: 2 }}>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>{cat.category}</Typography>
                <Box component="ul" sx={{ m: 0, pl: 2.5 }}>
                  {cat.steps.map((step, i) => (
                    <Box component="li" key={i} sx={{ mb: 0.5 }}>
                      <Typography variant="body2" color="text.secondary">{step}</Typography>
                    </Box>
                  ))}
                </Box>
              </Box>
            ))}
          </CardContent>
        </Card>
      )}

      {/* CTA buttons */}
      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 2 }}>
        <Button
          variant="contained"
          onClick={() => navigate('/assess/report/0', { state: { result } })}
        >
          View full report
        </Button>
        <Button variant="outlined" onClick={() => navigate('/dashboard')}>
          Back to dashboard
        </Button>
      </Box>

      <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
        This tool provides screening support only and is not a medical diagnosis.
        Results must be interpreted by a qualified healthcare professional.
      </Typography>
    </Box>
  );
}

// ── Main Assessment page ──────────────────────────────────────────────────────
function Assessment() {
  const navigate = useNavigate();

  // Per-question state
  const [texts, setTexts]     = useState({ positive: '', neutral: '', negative: '' });
  const [errors, setErrors]   = useState({});
  const [step, setStep]       = useState(0);   // 0 = positive, 1 = neutral, 2 = negative
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult]   = useState(null);
  const [apiError, setApiError] = useState(null);

  // One recorder per question
  const recorders = [useRecorder(), useRecorder(), useRecorder()];

  const currentQ = EATD_QUESTIONS[step];

  const handleTextChange = (val) => {
    setTexts((prev) => ({ ...prev, [currentQ.key]: val }));
    if (errors[currentQ.key]) setErrors((prev) => ({ ...prev, [currentQ.key]: null }));
  };

  const handleNext = () => {
    if (!texts[currentQ.key].trim()) {
      setErrors((prev) => ({ ...prev, [currentQ.key]: 'Please enter a response before proceeding.' }));
      return;
    }
    setStep((s) => s + 1);
  };

  const handleBack = () => setStep((s) => s - 1);

  const handleSubmit = async () => {
    // Validate all three
    const newErrs = {};
    EATD_QUESTIONS.forEach((q) => {
      if (!texts[q.key].trim()) newErrs[q.key] = 'Response required.';
    });
    if (Object.keys(newErrs).length > 0) {
      setErrors(newErrs);
      return;
    }

    setSubmitting(true);
    setApiError(null);

    try {
      const blobs = recorders.map((r, i) =>
        r.blob
          ? new File([r.blob], `${EATD_QUESTIONS[i].key}.webm`, { type: r.blob.type })
          : null
      );

      const res = await apiService.assessEATD(texts, blobs);
      setResult(res);

      // Store in session storage for ReportDetail
      const existing = JSON.parse(sessionStorage.getItem('mindcare_assessments') || '[]');
      sessionStorage.setItem('mindcare_assessments', JSON.stringify([res, ...existing]));
    } catch (e) {
      setApiError(
        e?.response?.data?.detail ||
        'Analysis failed. Check that the backend is running (python backend/main.py).'
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    setTexts({ positive: '', neutral: '', negative: '' });
    setErrors({});
    setStep(0);
    setResult(null);
    setApiError(null);
    recorders.forEach((r) => r.reset());
  };

  if (result) {
    return <ResultView result={result} onNew={handleReset} />;
  }

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, fontSize: '1.5rem', mb: 0.25 }}>
          New assessment
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Answer each of the three EATD-Corpus emotional questions. Audio is optional.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Left: stepper + question */}
        <Grid item xs={12} md={8}>

          {/* Step progress */}
          <Stepper activeStep={step} sx={{ mb: 3 }}>
            {EATD_QUESTIONS.map((q, i) => (
              <Step key={q.key} completed={i < step}>
                <StepLabel
                  optional={i < step ? <Typography variant="caption" color="success.main">Done</Typography> : null}
                >
                  {q.label}
                </StepLabel>
              </Step>
            ))}
          </Stepper>

          <Card>
            <CardContent sx={{ p: 3 }}>
              <QuestionStep
                q={currentQ}
                text={texts[currentQ.key]}
                onTextChange={handleTextChange}
                recorder={recorders[step]}
                error={errors[currentQ.key]}
              />

              {apiError && (
                <Alert severity="error" sx={{ mt: 2 }}>{apiError}</Alert>
              )}

              <Divider sx={{ mt: 3, mb: 2 }} />

              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Button
                  variant="outlined"
                  startIcon={<BackIcon />}
                  onClick={handleBack}
                  disabled={step === 0}
                  aria-label="Previous question"
                >
                  Back
                </Button>

                <Typography variant="caption" color="text.secondary">
                  Question {step + 1} of {EATD_QUESTIONS.length}
                </Typography>

                {step < EATD_QUESTIONS.length - 1 ? (
                  <Button
                    variant="contained"
                    endIcon={<NextIcon />}
                    onClick={handleNext}
                    aria-label="Next question"
                  >
                    Next
                  </Button>
                ) : (
                  <Button
                    variant="contained"
                    startIcon={
                      submitting
                        ? <CircularProgress size={18} color="inherit" />
                        : <SubmitIcon />
                    }
                    onClick={handleSubmit}
                    disabled={submitting}
                    aria-label="Submit assessment"
                  >
                    {submitting ? 'Analysing…' : 'Submit assessment'}
                  </Button>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Right: info panel */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ p: 2.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                <InfoIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                <Typography variant="caption" sx={{ ...CARD_LABEL_SX, mb: 0 }}>
                  How this works
                </Typography>
              </Box>
              <Box component="ol" sx={{ m: 0, pl: 2 }}>
                {[
                  'Answer all three EATD emotional questions (positive, neutral, negative).',
                  'Optionally record audio for each question for bimodal analysis.',
                  'The model extracts text features (Chinese-aware) and audio features (MFCC, pitch, energy, speech rate, pauses).',
                  'A late-fusion layer combines both signals across all three questions.',
                  'You receive a risk level, SDS estimate, modality contributions and key findings.',
                ].map((s, i) => (
                  <Box component="li" key={i} sx={{ mb: 0.75 }}>
                    <Typography variant="caption" color="text.secondary">{s}</Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ mt: 2 }}>
            <CardContent sx={{ p: 2.5 }}>
              <Typography variant="caption" sx={CARD_LABEL_SX}>Progress</Typography>
              {EATD_QUESTIONS.map((q, i) => (
                <Box key={q.key} sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
                  <Chip
                    label={i + 1}
                    size="small"
                    sx={{
                      width: 28, height: 28,
                      backgroundColor: i < step
                        ? '#f0fdf4'
                        : i === step
                        ? 'primary.main'
                        : '#f3f4f6',
                      color: i < step
                        ? '#16a34a'
                        : i === step
                        ? 'white'
                        : 'text.secondary',
                      fontWeight: 700, fontSize: '0.7rem',
                      border: i < step ? '1px solid #bbf7d0' : 'none',
                    }}
                  />
                  <Box sx={{ flex: 1 }}>
                    <Typography
                      variant="caption"
                      sx={{ fontWeight: i === step ? 600 : 400, color: i === step ? 'text.primary' : 'text.secondary' }}
                    >
                      {q.label}
                    </Typography>
                    {texts[q.key] && (
                      <Typography variant="caption" color="success.main" sx={{ display: 'block' }}>
                        {texts[q.key].length} chars
                        {recorders[i].blob ? ' + audio' : ''}
                      </Typography>
                    )}
                  </Box>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Assessment;
