import React, { useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import {
  Box, Card, CardContent, Typography, Button, Chip, Grid,
  Divider, Switch, FormControlLabel, Tooltip, IconButton,
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Download as DownloadIcon,
  InfoOutlined as InfoIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import CrisisBanner from '../components/CrisisBanner';

// â”€â”€ Risk badge â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
const RISK_CFG = {
  low:      { label: 'Low',      color: '#16a34a', bg: '#f0fdf4', border: '#bbf7d0' },
  moderate: { label: 'Moderate', color: '#d97706', bg: '#fffbeb', border: '#fde68a' },
  high:     { label: 'High',     color: '#dc2626', bg: '#fef2f2', border: '#fecaca' },
  critical: { label: 'Critical', color: '#dc2626', bg: '#fef2f2', border: '#fecaca' },
};
function RiskBadge({ level }) {
  const cfg = RISK_CFG[level] || { label: level || 'N/A', color: '#6b7280', bg: '#f9fafb', border: '#e5e7eb' };
  return (
    <Chip
      label={cfg.label}
      size="small"
      sx={{ backgroundColor: cfg.bg, color: cfg.color, border: `1px solid ${cfg.border}`,
            fontWeight: 700, fontSize: '0.72rem' }}
    />
  );
}

// â”€â”€ Highlighted transcript â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function HighlightedTranscript({ text, wordWeights, enabled }) {
  if (!text) return <Typography variant="body2" color="text.secondary">No transcript available.</Typography>;

  const words = text.split(/(\s+)/);
  return (
    <Box
      component="p"
      sx={{ m: 0, lineHeight: 2, fontFamily: 'inherit', fontSize: '0.9375rem' }}
      aria-label="Highlighted transcript"
    >
      {words.map((chunk, i) => {
        const word = chunk.trim().toLowerCase().replace(/[^a-z]/g, '');
        const w = wordWeights?.[word];
        if (!enabled || w === undefined) {
          return <span key={i}>{chunk}</span>;
        }
        const isNeg = w < 0;
        const isPos = w > 0;
        return (
          <Tooltip
            key={i}
            title={isNeg ? 'Negative indicator' : isPos ? 'Positive indicator' : ''}
            arrow
          >
            <mark
              style={{
                backgroundColor: isNeg ? '#fef2f2' : '#f0fdf4',
                color:           isNeg ? '#dc2626' : '#16a34a',
                borderRadius: 3,
                padding: '0 2px',
                fontWeight: 600,
                textDecoration: 'none',
              }}
            >
              {chunk}
            </mark>
          </Tooltip>
        );
      })}
    </Box>
  );
}

// â”€â”€ Audio stat tile â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function AudioStat({ label, value, unit, reference, loading }) {
  return (
    <Box
      sx={{ p: 1.5, border: '1px solid', borderColor: 'divider', borderRadius: 2,
            backgroundColor: 'background.paper' }}
    >
      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5,
                    textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
        {label}
      </Typography>
      <Typography variant="h6" sx={{ fontWeight: 700, fontSize: '1.1rem' }}>
        {value ?? 'â€”'}{unit && <Typography component="span" variant="caption" color="text.secondary"> {unit}</Typography>}
      </Typography>
      {reference && (
        <Typography variant="caption" color="text.secondary">
          Ref: {reference}
        </Typography>
      )}
    </Box>
  );
}

// â”€â”€ PDF export helper â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function downloadReport(result) {
  const lines = [
    'MINDCARE â€” ASSESSMENT REPORT',
    '='.repeat(50),
    `Date:       ${result.timestamp ? format(new Date(result.timestamp), 'dd MMM yyyy, HH:mm') : 'N/A'}`,
    `Risk level: ${(result.risk_level || '').toUpperCase()}`,
    `Score:      ${result.score ?? 'â€”'}`,
    `Confidence: ${result.confidence != null ? (result.confidence * 100).toFixed(0) + '%' : 'â€”'}`,
    `Model:      ${result.demo_mode ? 'Heuristic (demo)' : 'Neural'}`,
    '',
    'MODALITY CONTRIBUTIONS',
    '-'.repeat(30),
    `  Text:  ${result.modality_contributions?.text ?? 0}%`,
    `  Audio: ${result.modality_contributions?.audio ?? 0}%`,
    `  Video: ${result.modality_contributions?.video ?? 0}%`,
    '',
    'KEY FINDINGS',
    '-'.repeat(30),
    ...(result.key_findings || []).map((f, i) => `  ${i + 1}. ${f}`),
    '',
    'DISCLAIMER',
    '-'.repeat(30),
    'This tool provides screening support and is not a medical diagnosis.',
    'Results should be interpreted by a qualified healthcare professional.',
    '',
    `Generated by MindCare on ${format(new Date(), 'dd MMM yyyy')}`,
  ];

  const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `mindcare-report-${format(new Date(), 'yyyyMMdd-HHmm')}.txt`;
  a.click();
  URL.revokeObjectURL(url);
}

// â”€â”€ ReportDetail â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function ReportDetail() {
  const navigate = useNavigate();
  const location = useLocation();
  const { id }   = useParams();
  const [highlightOn, setHighlightOn] = useState(true);

  // Prefer state passed via navigate, fall back to sessionStorage
  let result = location.state?.result;
  if (!result) {
    const stored = JSON.parse(sessionStorage.getItem('mindcare_assessments') || '[]');
    result = stored[parseInt(id, 10)] || null;
  }

  if (!result) {
    return (
      <Box>
        <Button startIcon={<BackIcon />} onClick={() => navigate(-1)} sx={{ mb: 2 }}>
          Back
        </Button>
        <Card>
          <CardContent>
            <Typography color="text.secondary">
              Report not found. Run a new assessment to generate a report.
            </Typography>
          </CardContent>
        </Card>
      </Box>
    );
  }

  const riskLevel = result.risk_level;

  return (
    <Box>
      {(riskLevel === 'critical' || riskLevel === 'high') && (
        <CrisisBanner riskLevel={riskLevel} />
      )}

      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <IconButton onClick={() => navigate(-1)} aria-label="Go back" size="small">
            <BackIcon />
          </IconButton>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>Assessment report</Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<DownloadIcon />}
          onClick={() => downloadReport(result)}
          aria-label="Download report as text file"
        >
          Download report
        </Button>
      </Box>

      {/* Summary KPIs */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {[
          { label: 'Risk level', content: <RiskBadge level={riskLevel} /> },
          { label: 'Score',      content: result.score != null ? (result.score * 100).toFixed(1) + '%' : 'â€”' },
          { label: 'Confidence', content: result.confidence != null ? (result.confidence * 100).toFixed(0) + '%' : 'â€”' },
          { label: 'PHQ-8 est.', content: `${result.phq8_estimate ?? 'â€”'} / 24` },
          { label: 'Model',      content: result.demo_mode ? 'Heuristic' : 'Neural' },
          { label: 'Date',       content: result.timestamp ? format(new Date(result.timestamp), 'dd MMM yyyy') : 'N/A' },
        ].map(({ label, content }) => (
          <Grid item xs={6} sm={4} md={2} key={label}>
            <Card>
              <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                              color: 'text.secondary', fontWeight: 600, display: 'block', mb: 0.75 }}>
                  {label}
                </Typography>
                {typeof content === 'string'
                  ? <Typography variant="h6" sx={{ fontWeight: 700 }}>{content}</Typography>
                  : content}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Modality contributions */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 2.5 }}>
          <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                        color: 'text.secondary', fontWeight: 600, display: 'block', mb: 2 }}>
            Modality contributions
          </Typography>
          <Grid container spacing={2}>
            {[
              { label: 'Text',  pct: result.modality_contributions?.text ?? 0,  conf: result.per_modality_confidence?.text },
              { label: 'Audio', pct: result.modality_contributions?.audio ?? 0, conf: result.per_modality_confidence?.audio },
              { label: 'Video', pct: result.modality_contributions?.video ?? 0, conf: result.per_modality_confidence?.video },
            ].map(({ label, pct, conf }) => (
              <Grid item xs={12} sm={4} key={label}>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>{label}</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>{pct.toFixed(1)}%</Typography>
                  </Box>
                  <Box sx={{ height: 8, backgroundColor: '#e5e7eb', borderRadius: 4, overflow: 'hidden' }}>
                    <Box sx={{ height: '100%', width: `${pct}%`, backgroundColor: 'primary.main', borderRadius: 4 }} />
                  </Box>
                  {conf != null && (
                    <Typography variant="caption" color="text.secondary">
                      Confidence: {(conf * 100).toFixed(0)}%
                    </Typography>
                  )}
                </Box>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Key findings */}
      {result.key_findings?.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent sx={{ p: 2.5 }}>
            <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                          color: 'text.secondary', fontWeight: 600, display: 'block', mb: 2 }}>
              Key findings
            </Typography>
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

      {/* Explainability â€” highlighted transcript */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 2.5 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                            color: 'text.secondary', fontWeight: 600 }}>
                Transcript â€” word-level influence
              </Typography>
              <Tooltip title="Words highlighted red are negative indicators; green are positive. Based on lexical heuristic.">
                <InfoIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
              </Tooltip>
            </Box>
            <FormControlLabel
              control={
                <Switch
                  checked={highlightOn}
                  onChange={(e) => setHighlightOn(e.target.checked)}
                  size="small"
                  aria-label="Toggle word highlighting"
                />
              }
              label={<Typography variant="caption">Highlighting</Typography>}
              labelPlacement="start"
              sx={{ m: 0 }}
            />
          </Box>

          {/* Legend */}
          {highlightOn && (
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
                <Box sx={{ width: 12, height: 12, borderRadius: 1, backgroundColor: '#fef2f2', border: '1px solid #fecaca' }} />
                <Typography variant="caption" color="text.secondary">Negative indicator</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
                <Box sx={{ width: 12, height: 12, borderRadius: 1, backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0' }} />
                <Typography variant="caption" color="text.secondary">Positive indicator</Typography>
              </Box>
            </Box>
          )}

          <Box sx={{ p: 2, backgroundColor: '#fafafa', borderRadius: 2,
                     border: '1px solid', borderColor: 'divider', maxHeight: 320, overflowY: 'auto' }}>
            <HighlightedTranscript
              text={result.transcript || result.text || '(No transcript stored â€” submit new assessment with text input to see highlighting)'}
              wordWeights={result.word_weights}
              enabled={highlightOn}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Audio cue summary */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 2.5 }}>
          <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                        color: 'text.secondary', fontWeight: 600, display: 'block', mb: 2 }}>
            Audio cue summary
          </Typography>
          {result.input_type === 'text' ? (
            <Typography variant="body2" color="text.secondary">
              No audio was included in this assessment. Add a voice recording for audio cue analysis.
            </Typography>
          ) : (
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <AudioStat label="Speech rate" value={result.audio_features?.speech_rate ?? 'â€”'}
                           unit="words/min" reference="120â€“180" />
              </Grid>
              <Grid item xs={6} sm={3}>
                <AudioStat label="Pause ratio" value={result.audio_features?.pause_ratio ?? 'â€”'}
                           unit="" reference="< 0.25" />
              </Grid>
              <Grid item xs={6} sm={3}>
                <AudioStat label="Pitch variability" value={result.audio_features?.pitch_variability ?? 'â€”'}
                           unit="Hz" reference="20â€“80 Hz" />
              </Grid>
              <Grid item xs={6} sm={3}>
                <AudioStat label="Energy (RMS)" value={result.audio_features?.energy_rms ?? 'â€”'}
                           unit="" reference="> 0.05" />
              </Grid>
            </Grid>
          )}
        </CardContent>
      </Card>

      {/* Recommendations */}
      {result.recommendations?.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent sx={{ p: 2.5 }}>
            <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                          color: 'text.secondary', fontWeight: 600, display: 'block', mb: 2 }}>
              Recommendations
            </Typography>
            <Box component="ul" sx={{ m: 0, pl: 2.5 }}>
              {result.recommendations.slice(0, 6).map((r, i) => (
                <Box component="li" key={i} sx={{ mb: 0.75 }}>
                  <Typography variant="body2">{r}</Typography>
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Disclaimer */}
      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center', py: 1 }}>
        This tool provides screening support and is not a medical diagnosis.
        Results should be interpreted by a qualified healthcare professional.
      </Typography>
    </Box>
  );
}

export default ReportDetail;
