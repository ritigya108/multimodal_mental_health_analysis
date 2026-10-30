import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Skeleton, Alert,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Grid, Divider, Chip,
} from '@mui/material';
import apiService from '../services/api';

const CARD_LABEL_SX = {
  textTransform: 'uppercase',
  letterSpacing: '0.06em',
  color: 'text.secondary',
  fontWeight: 600,
  fontSize: '0.72rem',
  display: 'block',
  mb: 1.5,
};

const METRIC_KEYS = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc'];
const METRIC_LABELS = {
  accuracy:  'Accuracy',
  precision: 'Precision',
  recall:    'Recall (Sensitivity)',
  f1:        'F1',
  roc_auc:   'ROC-AUC',
};

// ── MetricCell ────────────────────────────────────────────────────────────────
function MetricCell({ value }) {
  if (value == null) {
    return (
      <TableCell>
        <Typography variant="body2" color="text.secondary">—</Typography>
      </TableCell>
    );
  }
  const pct  = (value * 100).toFixed(1);
  const good = value >= 0.80;
  const ok   = value >= 0.70;
  return (
    <TableCell>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Typography variant="body2" sx={{ fontWeight: 600, minWidth: 40 }}>{pct}%</Typography>
        <Box sx={{ flex: 1, height: 4, backgroundColor: '#e5e7eb', borderRadius: 2, minWidth: 40 }}>
          <Box sx={{
            height: '100%',
            width: `${Math.min(pct, 100)}%`,
            borderRadius: 2,
            backgroundColor: good ? '#16a34a' : ok ? '#d97706' : '#dc2626',
          }} />
        </Box>
      </Box>
    </TableCell>
  );
}

// ── Confusion Matrix ──────────────────────────────────────────────────────────
function ConfusionMatrix({ matrix, labels }) {
  if (!matrix || !labels) return null;
  return (
    <Box role="table" aria-label="Confusion matrix" sx={{ display: 'inline-block' }}>
      {/* Column headers — "Predicted" */}
      <Box sx={{ display: 'flex', ml: '112px' }}>
        {labels.map((l) => (
          <Box key={l} sx={{ width: 100, textAlign: 'center' }}>
            <Typography variant="caption" sx={{ fontWeight: 600, color: 'text.secondary',
                          textTransform: 'uppercase', fontSize: '0.68rem' }}>
              {l}
            </Typography>
          </Box>
        ))}
      </Box>
      {matrix.map((row, ri) => (
        <Box key={ri} sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
          {/* Row header */}
          <Box sx={{ width: 110, pr: 1 }}>
            <Typography variant="caption" sx={{ fontWeight: 600, color: 'text.secondary',
                          textTransform: 'uppercase', fontSize: '0.68rem', wordBreak: 'break-word' }}>
              {labels[ri]}
            </Typography>
          </Box>
          {row.map((cell, ci) => {
            const isCorrect = ri === ci;
            return (
              <Box
                key={ci}
                sx={{
                  width: 100, height: 64,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  backgroundColor: isCorrect ? '#f0fdf4' : '#fef2f2',
                  border: '1px solid',
                  borderColor: isCorrect ? '#bbf7d0' : '#fecaca',
                  borderRadius: 1, mr: 0.5,
                }}
                role="cell"
                aria-label={`Predicted ${labels[ci]}, Actual ${labels[ri]}: ${cell ?? '—'}`}
              >
                <Typography variant="h6" sx={{ fontWeight: 700, color: isCorrect ? '#16a34a' : '#dc2626' }}>
                  {cell ?? '—'}
                </Typography>
              </Box>
            );
          })}
        </Box>
      ))}
    </Box>
  );
}

// ── ModelPerformance page ─────────────────────────────────────────────────────
function ModelPerformance() {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    apiService.getModelMetrics()
      .then((d) => { setData(d); setLoading(false); })
      .catch((e) => {
        const msg =
          e?.response?.data?.detail ||
          (e?.code === 'ERR_NETWORK'
            ? 'Cannot reach backend at localhost:8000. Start it with: python backend/main.py'
            : null) ||
          'Failed to load metrics. Make sure the backend is running.';
        setError(msg);
        setLoading(false);
      });
  }, []);

  const models       = data?.models || [];
  const cm           = data?.confusion_matrix;
  const dsNotes      = data?.dataset_notes;
  const limitations  = data?.limitations || [];
  const cvNote       = data?._cross_validation;

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, fontSize: '1.5rem', mb: 0.25 }}>
          Model performance
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Evaluation metrics for each model branch and the late-fusion bimodal ensemble.
        </Typography>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {/* ── Dataset and training setup ────────────────────────────────── */}
      {!loading && data && (
        <Card sx={{ mb: 3 }}>
          <CardContent sx={{ p: 2.5 }}>
            <Typography variant="caption" sx={CARD_LABEL_SX}>
              Dataset and training setup
            </Typography>
            <Grid container spacing={2}>
              {[
                { label: 'Dataset',          value: data._dataset   },
                { label: 'Train/Val split',  value: data._split     },
                { label: 'Architecture',     value: data._training  },
              ].map(({ label, value }) => value ? (
                <Grid item xs={12} md={4} key={label}>
                  <Typography variant="caption" color="text.secondary"
                              sx={{ display: 'block', fontWeight: 600, mb: 0.25 }}>
                    {label}
                  </Typography>
                  <Typography variant="body2">{value}</Typography>
                </Grid>
              ) : null)}
            </Grid>

            {/* Cross-validation note */}
            {cvNote && (
              <>
                <Divider sx={{ my: 2 }} />
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                  <Chip
                    label="CV"
                    size="small"
                    sx={{ backgroundColor: '#eff6ff', color: '#2563eb',
                          border: '1px solid #bfdbfe', fontWeight: 700, fontSize: '0.65rem' }}
                  />
                  <Typography variant="body2" color="text.secondary">{cvNote}</Typography>
                </Box>
              </>
            )}

            {/* Dataset notes (citation, language, tokeniser) */}
            {dsNotes && (
              <>
                <Divider sx={{ my: 2 }} />
                <Grid container spacing={2}>
                  {[
                    { label: 'Language',        value: dsNotes.language        },
                    { label: 'Text tokeniser',  value: dsNotes.text_tokeniser  },
                    { label: 'Audio features',  value: dsNotes.audio_features  },
                    { label: 'Class balance',   value: dsNotes.class_balance   },
                    { label: 'Citation',        value: dsNotes.citation        },
                  ].map(({ label, value }) => value ? (
                    <Grid item xs={12} md={6} key={label}>
                      <Typography variant="caption" color="text.secondary"
                                  sx={{ display: 'block', fontWeight: 600, mb: 0.25 }}>
                        {label}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">{value}</Typography>
                    </Grid>
                  ) : null)}
                </Grid>
              </>
            )}
          </CardContent>
        </Card>
      )}

      {/* ── Per-model metrics table ───────────────────────────────────── */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 0 }}>
          <Box sx={{ px: 2.5, pt: 2.5, pb: 1.5 }}>
            <Typography variant="caption" sx={{ ...CARD_LABEL_SX, mb: 0 }}>
              Per-model metrics
            </Typography>
          </Box>
          {loading ? (
            <Box sx={{ px: 2.5, pb: 2 }}>
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} variant="text" height={40} sx={{ mb: 0.5 }} />
              ))}
            </Box>
          ) : models.length === 0 ? (
            <Box sx={{ px: 2.5, pb: 2.5 }}>
              <Typography variant="body2" color="text.secondary">
                No metrics available. Fill in{' '}
                <code>ml/results/metrics.json</code> after training.
              </Typography>
            </Box>
          ) : (
            <TableContainer>
              <Table size="small" aria-label="Model performance metrics">
                <TableHead>
                  <TableRow sx={{ '& th': { borderColor: 'divider', py: 1.25 } }}>
                    <TableCell>Model</TableCell>
                    <TableCell>Branch</TableCell>
                    <TableCell>Description</TableCell>
                    {METRIC_KEYS.map((k) => (
                      <TableCell key={k}>{METRIC_LABELS[k]}</TableCell>
                    ))}
                    <TableCell>CV F1</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {models.map((m) => {
                    const isFusion = m.branch === 'fusion';
                    return (
                      <TableRow
                        key={m.name}
                        hover
                        sx={{
                          '& td': { borderColor: 'divider', py: 1.1 },
                          backgroundColor: isFusion ? '#f0fafa' : 'inherit',
                        }}
                      >
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2" sx={{ fontWeight: 600 }}>{m.name}</Typography>
                            {isFusion && (
                              <Chip
                                label="Fusion"
                                size="small"
                                color="primary"
                                sx={{ height: 18, fontSize: '0.62rem' }}
                              />
                            )}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={m.branch || 'n/a'}
                            size="small"
                            variant="outlined"
                            sx={{ fontSize: '0.65rem', textTransform: 'capitalize' }}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="caption" color="text.secondary">
                            {m.description}
                          </Typography>
                        </TableCell>
                        {METRIC_KEYS.map((key) => (
                          <MetricCell key={key} value={m[key]} />
                        ))}
                        {/* CV F1 */}
                        <TableCell>
                          {m.cv_f1_mean != null ? (
                            <Typography variant="body2" sx={{ fontWeight: 600 }}>
                              {(m.cv_f1_mean * 100).toFixed(1)}%
                              {m.cv_f1_std != null && (
                                <Typography component="span" variant="caption" color="text.secondary">
                                  {' '}±{(m.cv_f1_std * 100).toFixed(1)}
                                </Typography>
                              )}
                            </Typography>
                          ) : (
                            <Typography variant="body2" color="text.secondary">—</Typography>
                          )}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* ── Confusion matrix ──────────────────────────────────────────── */}
      {!loading && cm && (
        <Card sx={{ mb: 3 }}>
          <CardContent sx={{ p: 2.5 }}>
            <Typography variant="caption" sx={CARD_LABEL_SX}>
              Confusion matrix — Fusion model
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
              Rows = actual label; Columns = predicted label.
              {cm._note && ` ${cm._note}`}
            </Typography>
            <Box sx={{ overflowX: 'auto', mb: 2 }}>
              <ConfusionMatrix matrix={cm.Fusion} labels={cm.labels} />
            </Box>
            <Box sx={{ display: 'flex', gap: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ width: 14, height: 14, borderRadius: 1,
                           backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0' }} />
                <Typography variant="caption" color="text.secondary">Correct (diagonal)</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ width: 14, height: 14, borderRadius: 1,
                           backgroundColor: '#fef2f2', border: '1px solid #fecaca' }} />
                <Typography variant="caption" color="text.secondary">Incorrect (off-diagonal)</Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* ── Limitations box ───────────────────────────────────────────── */}
      {!loading && limitations.length > 0 && (
        <Card sx={{ mb: 3, border: '1px solid #fde68a', backgroundColor: '#fffbeb' }}>
          <CardContent sx={{ p: 2.5 }}>
            <Typography variant="caption" sx={{ ...CARD_LABEL_SX, color: '#92400e' }}>
              Known limitations
            </Typography>
            <Box component="ul" sx={{ m: 0, pl: 2.5 }}>
              {limitations.map((l, i) => (
                <Box component="li" key={i} sx={{ mb: 0.75 }}>
                  <Typography variant="body2" color="text.secondary">{l}</Typography>
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* ── Footer note ───────────────────────────────────────────────── */}
      <Typography
        variant="caption"
        color="text.secondary"
        sx={{ display: 'block', textAlign: 'center', mt: 1 }}
      >
        Metrics are loaded from <code>ml/results/metrics.json</code>.
        Update with your real training results before submission.
        All null values are placeholders.
      </Typography>
    </Box>
  );
}

export default ModelPerformance;
