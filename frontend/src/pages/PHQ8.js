import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Card, CardContent, Typography, Button, LinearProgress,
  Grid, Divider, Chip, Alert, RadioGroup, FormControlLabel, Radio,
} from '@mui/material';
import { CheckCircle as DoneIcon } from '@mui/icons-material';
import apiService from '../services/api';

const PHQ8_QUESTIONS = [
  'Little interest or pleasure in doing things',
  'Feeling down, depressed, or hopeless',
  'Trouble falling or staying asleep, or sleeping too much',
  'Feeling tired or having little energy',
  'Poor appetite or overeating',
  'Feeling bad about yourself â€” or that you are a failure, or have let yourself or your family down',
  'Trouble concentrating on things, such as reading the newspaper or watching television',
  'Moving or speaking so slowly that other people could have noticed â€” or the opposite, being so fidgety or restless',
];

const SCALE = [
  { value: 0, label: 'Not at all' },
  { value: 1, label: 'Several days' },
  { value: 2, label: 'More than half the days' },
  { value: 3, label: 'Nearly every day' },
];

const SEVERITY_CONFIG = {
  Minimal:             { color: '#16a34a', bg: '#f0fdf4', border: '#bbf7d0' },
  Mild:                { color: '#65a30d', bg: '#f7fee7', border: '#d9f99d' },
  Moderate:            { color: '#d97706', bg: '#fffbeb', border: '#fde68a' },
  'Moderately Severe': { color: '#ea580c', bg: '#fff7ed', border: '#fed7aa' },
  Severe:              { color: '#dc2626', bg: '#fef2f2', border: '#fecaca' },
};

const AGREEMENT_MAP = {
  'Low-Minimal':              'Agreement',
  'Low-Mild':                 'Partial agreement',
  'Low-Moderate':             'Disagreement',
  'Low-Moderately Severe':    'Disagreement',
  'Low-Severe':               'Disagreement',
  'Moderate-Minimal':         'Partial agreement',
  'Moderate-Mild':            'Agreement',
  'Moderate-Moderate':        'Agreement',
  'Moderate-Moderately Severe': 'Partial agreement',
  'Moderate-Severe':          'Partial agreement',
  'High-Minimal':             'Disagreement',
  'High-Mild':                'Partial agreement',
  'High-Moderate':            'Partial agreement',
  'High-Moderately Severe':   'Agreement',
  'High-Severe':              'Agreement',
  'Critical-Minimal':         'Disagreement',
  'Critical-Mild':            'Partial agreement',
  'Critical-Moderate':        'Agreement',
  'Critical-Moderately Severe': 'Agreement',
  'Critical-Severe':          'Agreement',
};

function getModelRiskBand(riskLevel) {
  if (riskLevel === 'low')                      return 'Low';
  if (riskLevel === 'moderate')                 return 'Moderate';
  if (riskLevel === 'high' || riskLevel === 'critical') return 'High';
  return null;
}

function PHQ8() {
  const navigate = useNavigate();
  const [answers, setAnswers] = useState(Array(8).fill(null));
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const answeredCount = answers.filter((a) => a !== null).length;
  const progress = (answeredCount / 8) * 100;
  const allAnswered = answeredCount === 8;

  const handleAnswer = (index, value) => {
    const updated = [...answers];
    updated[index] = value;
    setAnswers(updated);
  };

  const handleSubmit = async () => {
    if (!allAnswered) return;
    setSubmitting(true);
    setError(null);
    try {
      const res = await apiService.scorePHQ8(answers.map(Number));
      setResult(res);
    } catch (e) {
      setError(e?.response?.data?.detail || 'Scoring failed. Please check the backend is running.');
    } finally {
      setSubmitting(false);
    }
  };

  // Get last model assessment from sessionStorage for comparison
  const lastAssessment = (() => {
    try {
      const stored = JSON.parse(sessionStorage.getItem('mindcare_assessments') || '[]');
      return stored[0] || null;
    } catch { return null; }
  })();

  const agreementKey = result && lastAssessment
    ? `${lastAssessment.risk_level?.charAt(0).toUpperCase()}${lastAssessment.risk_level?.slice(1)}-${result.severity}`
    : null;
  const agreementLabel = agreementKey ? (AGREEMENT_MAP[agreementKey] || 'Partial agreement') : null;

  const sevCfg = result ? (SEVERITY_CONFIG[result.severity] || SEVERITY_CONFIG.Minimal) : null;

  if (result) {
    return (
      <Box>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>PHQ-8 results</Typography>
          <Typography variant="body2" color="text.secondary">
            Patient Health Questionnaire â€” 8 item version
          </Typography>
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12} md={7}>
            <Card sx={{ mb: 3 }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
                  <Box>
                    <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                                  color: 'text.secondary', fontWeight: 600, display: 'block', mb: 1 }}>
                      Total score
                    </Typography>
                    <Typography variant="h2" sx={{ fontWeight: 700, fontSize: '2.5rem' }}>
                      {result.score}
                      <Typography component="span" variant="body1" color="text.secondary"> / 24</Typography>
                    </Typography>
                  </Box>
                  <Box
                    sx={{ px: 2, py: 1, borderRadius: 2,
                          backgroundColor: sevCfg?.bg,
                          color: sevCfg?.color,
                          border: `1px solid ${sevCfg?.border}`,
                          fontWeight: 700, fontSize: '0.9rem' }}
                  >
                    {result.severity}
                  </Box>
                </Box>

                <Typography variant="body2" sx={{ mb: 3, color: 'text.secondary' }}>
                  {result.severity_description}
                </Typography>

                {/* Score bar */}
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ height: 8, backgroundColor: '#e5e7eb', borderRadius: 4, overflow: 'hidden' }}>
                    <Box sx={{ height: '100%', width: `${(result.score / 24) * 100}%`,
                               backgroundColor: sevCfg?.color, borderRadius: 4, transition: 'width 0.5s' }} />
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5 }}>
                    {['Minimal\n(0â€“4)', 'Mild\n(5â€“9)', 'Moderate\n(10â€“14)', 'Severe\n(20â€“24)'].map((l) => (
                      <Typography key={l} variant="caption" color="text.secondary" sx={{ whiteSpace: 'pre-line', textAlign: 'center', fontSize: '0.65rem' }}>
                        {l}
                      </Typography>
                    ))}
                  </Box>
                </Box>

                {/* Agreement with model */}
                {agreementLabel && lastAssessment && (
                  <Box sx={{ p: 2, borderRadius: 2, border: '1px solid', borderColor: 'divider',
                             backgroundColor: 'background.default' }}>
                    <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                                  color: 'text.secondary', fontWeight: 600, display: 'block', mb: 1 }}>
                      Comparison with model prediction
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                      <Box>
                        <Typography variant="caption" color="text.secondary">Model risk</Typography>
                        <Chip
                          label={(lastAssessment.risk_level || '').charAt(0).toUpperCase() + (lastAssessment.risk_level || '').slice(1)}
                          size="small"
                          sx={{ ml: 1 }}
                        />
                      </Box>
                      <Box>
                        <Typography variant="caption" color="text.secondary">PHQ-8 severity</Typography>
                        <Chip label={result.severity} size="small" sx={{ ml: 1 }} />
                      </Box>
                      <Chip
                        label={agreementLabel}
                        size="small"
                        sx={{
                          fontWeight: 700,
                          backgroundColor:
                            agreementLabel === 'Agreement' ? '#f0fdf4' :
                            agreementLabel === 'Partial agreement' ? '#fffbeb' : '#fef2f2',
                          color:
                            agreementLabel === 'Agreement' ? '#16a34a' :
                            agreementLabel === 'Partial agreement' ? '#d97706' : '#dc2626',
                        }}
                      />
                    </Box>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                      {agreementLabel === 'Agreement'
                        ? 'The PHQ-8 severity band and model risk level are consistent.'
                        : agreementLabel === 'Partial agreement'
                        ? 'The PHQ-8 and model results are in partial alignment. Consider clinical review.'
                        : 'The PHQ-8 and model results diverge. A clinician should review both assessments.'}
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>

            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button
                variant="outlined"
                onClick={() => { setResult(null); setAnswers(Array(8).fill(null)); }}
              >
                Retake questionnaire
              </Button>
              <Button variant="contained" onClick={() => navigate('/dashboard')}>
                Back to overview
              </Button>
            </Box>
          </Grid>

          <Grid item xs={12} md={5}>
            <Card>
              <CardContent sx={{ p: 2.5 }}>
                <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                              color: 'text.secondary', fontWeight: 600, display: 'block', mb: 2 }}>
                  Your answers
                </Typography>
                {PHQ8_QUESTIONS.map((q, i) => (
                  <Box key={i} sx={{ mb: 1.5 }}>
                    <Typography variant="body2" sx={{ mb: 0.25 }}>
                      {i + 1}. {q}
                    </Typography>
                    <Chip
                      label={SCALE.find((s) => s.value === answers[i])?.label || 'â€”'}
                      size="small"
                      variant="outlined"
                    />
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center', mt: 3 }}>
          The PHQ-8 is a validated screening tool. This is not a clinical diagnosis.
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>PHQ-8 questionnaire</Typography>
        <Typography variant="body2" color="text.secondary">
          Over the last 2 weeks, how often have you been bothered by the following problems?
        </Typography>
      </Box>

      {/* Progress */}
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
          <Typography variant="caption" color="text.secondary">
            {answeredCount} of 8 answered
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {Math.round(progress)}%
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={progress}
          sx={{ height: 6, borderRadius: 3 }}
          aria-label={`${answeredCount} of 8 questions answered`}
        />
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {PHQ8_QUESTIONS.map((question, qi) => (
        <Card key={qi} sx={{ mb: 2 }}>
          <CardContent sx={{ p: 2.5 }}>
            <Typography variant="body1" sx={{ fontWeight: 500, mb: 2 }}>
              {qi + 1}. {question}
            </Typography>
            <RadioGroup
              value={answers[qi] !== null ? String(answers[qi]) : ''}
              onChange={(e) => handleAnswer(qi, parseInt(e.target.value, 10))}
              row
              aria-label={`Question ${qi + 1}: ${question}`}
            >
              {SCALE.map((s) => (
                <FormControlLabel
                  key={s.value}
                  value={String(s.value)}
                  control={<Radio size="small" />}
                  label={
                    <Typography variant="body2">{s.label}</Typography>
                  }
                  sx={{ mr: 3 }}
                />
              ))}
            </RadioGroup>
          </CardContent>
        </Card>
      ))}

      <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
        <Button
          variant="contained"
          size="large"
          startIcon={<DoneIcon />}
          onClick={handleSubmit}
          disabled={!allAnswered || submitting}
          aria-label="Submit PHQ-8 questionnaire"
        >
          {submitting ? 'Scoringâ€¦' : 'Submit questionnaire'}
        </Button>
        <Button
          variant="outlined"
          onClick={() => setAnswers(Array(8).fill(null))}
          aria-label="Clear all answers"
        >
          Clear
        </Button>
      </Box>

      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
        The PHQ-8 is a validated depression screening tool (Kroenke et al., 2009).
        This is not a clinical diagnosis.
      </Typography>
    </Box>
  );
}

export default PHQ8;
