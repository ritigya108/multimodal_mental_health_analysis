import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Skeleton, Alert,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Grid, Divider, Chip,
} from '@mui/material';
import apiService from '../services/api';

const METRIC_LABELS = {
  accuracy:  'Accuracy',
  precision: 'Precision',
  recall:    'Recall',
  f1:        'F1',
  roc_auc:   'ROC-AUC',
};

function MetricCell({ value }) {
  if (value == null) return <TableCell>â€”</TableCell>;
  const pct = (value * 100).toFixed(1);
  const good = value >= 0.80;
  const ok   = value >= 0.70;
  return (
    <TableCell>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Typography variant="body2" sx={{ fontWeight: 600 }}>{pct}%</Typography>
        <Box sx={{ flex: 1, height: 4, backgroundColor: '#e5e7eb', borderRadius: 2, minWidth: 40 }}>
          <Box sx={{
            height: '100%', width: `${pct}%`, borderRadius: 2,
            backgroundColor: good ? '#16a34a' : ok ? '#d97706' : '#dc2626',
          }} />
        </Box>
      </Box>
    </TableCell>
  );
}

// Confusion matrix as a styled grid (no chart library)
function ConfusionMatrix({ matrix, labels }) {
  if (!matrix || !labels) return null;
  return (
    <Box
      role="table"
      aria-label="Confusion matrix"
      sx={{ display: 'inline-block' }}
    >
      {/* Column headers */}
      <Box sx={{ display: 'flex', ml: 12 }}>
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
                  width: 100,
                  height: 64,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: isCorrect ? '#f0fdf4' : '#fef2f2',
                  border: '1px solid',
                  borderColor: isCorrect ? '#bbf7d0' : '#fecaca',
                  borderRadius: 1,
                  mr: 0.5,
                }}
                role="cell"
                aria-label={`Predicted ${labels[ci]}, Actual ${labels[ri]}: ${cell}`}
              >
                <Typography variant="h6" sx={{ fontWeight: 700,
                              color: isCorrect ? '#16a34a' : '#dc2626' }}>
                  {cell}
                </Typography>
              </Box>
            );
          })}
        </Box>
      ))}
    </Box>
  );
}

function ModelPerformance() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    apiService.getModelMetrics()
      .then((d) => { setData(d); setLoading(false); })
      .catch((e) => {
        const msg = e?.response?.data?.detail
          || (e?.code === 'ERR_NETWORK' ? 'Cannot reach backend at localhost:8000. Start it with: python main.py' : null)
          || 'Failed to load metrics. Make sure the backend is running.';
        setError(msg);
        setLoading(false);
      });
  }, []);

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>Model performance</Typography>
        <Typography variant="body2" color="text.secondary">
          Evaluation metrics for each model branch and the late-fusion ensemble.
        </Typography>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {/* Dataset info */}
      {!loading && data && (
        <Card sx={{ mb: 3 }}>
          <CardContent sx={{ p: 2.5 }}>
            <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                          color: 'text.secondary', fontWeight: 600, display: 'block', mb: 2 }}>
              Dataset and training setup
            </Typography>
            <Grid container spacing={2}>
              {[
                { label: 'Dataset',  value: data._dataset },
                { label: 'Split',    value: data._split },
                { label: 'Training', value: data._training },
              ].map(({ label, value }) => (
                <Grid item xs={12} md={4} key={label}>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', fontWeight: 600 }}>
                    {label}
                  </Typography>
                  <Typography variant="body2">{value}</Typography>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Metrics table */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 0 }}>
          <Box sx={{ px: 2.5, pt: 2.5, pb: 1.5 }}>
            <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                          color: 'text.secondary', fontWeight: 600 }}>
              Per-model metrics
            </Typography>
          </Box>
          {loading ? (
            <Box sx={{ px: 2.5, pb: 2 }}>
              {[1, 2, 3, 4].map(i => <Skeleton key={i} variant="text" height={40} sx={{ mb: 0.5 }} />)}
            </Box>
          ) : (
            <TableContainer>
              <Table size="small" aria-label="Model performance metrics">
                <TableHead>
                  <TableRow sx={{ '& th': { borderColor: 'divider', py: 1.25 } }}>
                    <TableCell>Model</TableCell>
                    <TableCell>Description</TableCell>
                    {Object.values(METRIC_LABELS).map((l) => (
                      <TableCell key={l}>{l}</TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(data?.models || []).map((m) => (
                    <TableRow
                      key={m.name}
                      sx={{
                        '& td': { borderColor: 'divider', py: 1 },
                        backgroundColor: m.name === 'Fusion' ? '#f0fafa' : 'inherit',
                      }}
                    >
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>{m.name}</Typography>
                          {m.name === 'Fusion' && (
                            <Chip label="Best" size="small" color="primary" sx={{ height: 18, fontSize: '0.65rem' }} />
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption" color="text.secondary">{m.description}</Typography>
                      </TableCell>
                      {Object.keys(METRIC_LABELS).map((key) => (
                        <MetricCell key={key} value={m[key]} />
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Confusion matrix */}
      {!loading && data?.confusion_matrix && (
        <Card>
          <CardContent sx={{ p: 2.5 }}>
            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                            color: 'text.secondary', fontWeight: 600, display: 'block', mb: 0.5 }}>
                Confusion matrix â€” Fusion model
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Rows = actual label, columns = predicted label
              </Typography>
            </Box>
            <Box sx={{ overflowX: 'auto' }}>
              <ConfusionMatrix
                matrix={data.confusion_matrix.Fusion}
                labels={data.confusion_matrix.labels}
              />
            </Box>
            <Divider sx={{ my: 2 }} />
            <Box sx={{ display: 'flex', gap: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ width: 14, height: 14, borderRadius: 1, backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0' }} />
                <Typography variant="caption" color="text.secondary">Correct predictions</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ width: 14, height: 14, borderRadius: 1, backgroundColor: '#fef2f2', border: '1px solid #fecaca' }} />
                <Typography variant="caption" color="text.secondary">Incorrect predictions</Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      <Typography variant="caption" color="text.secondary"
                  sx={{ display: 'block', textAlign: 'center', mt: 3 }}>
        Metrics are loaded from <code>backend/model_metrics.json</code>. Update with your real results after training.
      </Typography>
    </Box>
  );
}

export default ModelPerformance;
