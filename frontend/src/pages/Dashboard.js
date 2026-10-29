import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Divider,
  Alert,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon,
  OpenInNew as ViewIcon,
  ErrorOutline as ErrorIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import apiService from '../services/api';
import CrisisBanner from '../components/CrisisBanner';

// â”€â”€ Design tokens â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
const RISK_CONFIG = {
  low:      { label: 'Low',      color: '#16a34a', bg: '#f0fdf4', border: '#bbf7d0', index: 0 },
  moderate: { label: 'Moderate', color: '#d97706', bg: '#fffbeb', border: '#fde68a', index: 1 },
  elevated: { label: 'Elevated', color: '#ea580c', bg: '#fff7ed', border: '#fed7aa', index: 2 },
  high:     { label: 'High',     color: '#dc2626', bg: '#fef2f2', border: '#fecaca', index: 3 },
  critical: { label: 'Critical', color: '#dc2626', bg: '#fef2f2', border: '#fecaca', index: 3 },
  unknown:  { label: 'N/A',      color: '#6b7280', bg: '#f9fafb', border: '#e5e7eb', index: -1 },
};

function RiskBadge({ level, size = 'small' }) {
  const cfg = RISK_CONFIG[level] || RISK_CONFIG.unknown;
  return (
    <Chip
      label={cfg.label}
      size={size}
      sx={{
        backgroundColor: cfg.bg,
        color: cfg.color,
        border: `1px solid ${cfg.border}`,
        fontWeight: 700,
        fontSize: size === 'small' ? '0.72rem' : '0.8rem',
      }}
    />
  );
}

// â”€â”€ KPI Card â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function KpiCard({ label, value, subtext, loading, badge, trend }) {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 2.5 }}>
        <Typography
          variant="caption"
          sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                color: 'text.secondary', fontWeight: 600, display: 'block', mb: 1 }}
        >
          {label}
        </Typography>
        {loading ? (
          <>
            <Skeleton variant="text" width={80} height={44} />
            <Skeleton variant="text" width={120} height={20} />
          </>
        ) : (
          <>
            {badge || (
              <Typography
                variant="h4"
                sx={{ fontWeight: 700, fontSize: '2rem', color: 'text.primary', lineHeight: 1.1, mb: 0.5 }}
              >
                {value}
              </Typography>
            )}
            {subtext && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: badge ? 1 : 0 }}>
                {trend === 'up'    && <TrendingUpIcon   sx={{ fontSize: 16, color: 'error.main' }} />}
                {trend === 'down'  && <TrendingDownIcon  sx={{ fontSize: 16, color: 'success.main' }} />}
                {trend === 'stable'&& <TrendingFlatIcon  sx={{ fontSize: 16, color: 'text.secondary' }} />}
                <Typography variant="caption" color="text.secondary">{subtext}</Typography>
              </Box>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}

// â”€â”€ Risk Meter â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
const RISK_SEGMENTS = [
  { key: 'low',      label: 'Low',      color: '#16a34a' },
  { key: 'moderate', label: 'Moderate', color: '#d97706' },
  { key: 'elevated', label: 'Elevated', color: '#ea580c' },
  { key: 'high',     label: 'High',     color: '#dc2626' },
];

function RiskMeter({ level, loading }) {
  const idx = RISK_CONFIG[level]?.index ?? -1;

  return (
    <Box>
      {/* Segmented bar */}
      <Box
        sx={{ display: 'flex', height: 10, borderRadius: 5, overflow: 'hidden', mb: 1.5 }}
        role="img"
        aria-label={`Risk level: ${RISK_CONFIG[level]?.label || 'Unknown'}`}
      >
        {RISK_SEGMENTS.map((seg, i) => (
          <Box
            key={seg.key}
            sx={{
              flex: 1,
              backgroundColor: i <= idx ? seg.color : '#e5e7eb',
              mr: i < 3 ? '2px' : 0,
              borderRadius: i === 0 ? '5px 0 0 5px' : i === 3 ? '0 5px 5px 0' : 0,
              transition: 'background-color 0.3s',
            }}
          />
        ))}
      </Box>

      {/* Labels */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        {RISK_SEGMENTS.map((seg, i) => (
          <Typography
            key={seg.key}
            variant="caption"
            sx={{
              color: i === idx ? seg.color : 'text.secondary',
              fontWeight: i === idx ? 700 : 400,
              fontSize: '0.7rem',
            }}
          >
            {seg.label}
          </Typography>
        ))}
      </Box>

      {/* Explanation */}
      {loading ? (
        <Skeleton variant="text" width="80%" />
      ) : (
        <Typography variant="body2" color="text.secondary">
          {level === 'low'
            ? 'No significant indicators of depression detected. Continue regular self-monitoring.'
            : level === 'moderate'
            ? 'Moderate depressive indicators present. Consider a check-in with a professional.'
            : level === 'elevated' || level === 'high'
            ? 'Elevated indicators detected. A professional consultation is recommended soon.'
            : level === 'critical'
            ? 'Significant distress indicators. Please seek professional support promptly.'
            : 'No assessment data available. Start an assessment to see your result.'}
        </Typography>
      )}
    </Box>
  );
}

// â”€â”€ Modality Bar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function ModalityBar({ label, value, confidence, loading }) {
  const pct = value ?? 0;
  return (
    <Box sx={{ mb: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
        <Typography variant="body2" sx={{ fontWeight: 500 }}>{label}</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Typography variant="body2" sx={{ fontWeight: 600 }}>{pct.toFixed(1)}%</Typography>
          {confidence != null && (
            <Typography variant="caption" color="text.secondary">
              conf. {(confidence * 100).toFixed(0)}%
            </Typography>
          )}
        </Box>
      </Box>
      {loading ? (
        <Skeleton variant="rectangular" height={6} sx={{ borderRadius: 3 }} />
      ) : (
        <Box sx={{ height: 6, backgroundColor: '#e5e7eb', borderRadius: 3, overflow: 'hidden' }}>
          <Box
            sx={{ height: '100%', width: `${pct}%`, backgroundColor: 'primary.main', borderRadius: 3 }}
            role="progressbar"
            aria-valuenow={pct}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`${label} contribution: ${pct.toFixed(1)}%`}
          />
        </Box>
      )}
    </Box>
  );
}

// â”€â”€ Empty state â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function EmptyState({ onStart }) {
  return (
    <Box
      sx={{ textAlign: 'center', py: 6, px: 3,
            border: '1px dashed #e5e7eb', borderRadius: 2, backgroundColor: '#fafafa' }}
    >
      <Typography variant="h6" color="text.secondary" sx={{ mb: 1 }}>
        No assessments yet
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Start your first assessment to see your risk profile and insights here.
      </Typography>
      <Button variant="contained" startIcon={<AddIcon />} onClick={onStart}>
        Start first assessment
      </Button>
    </Box>
  );
}

// â”€â”€ Error state â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function ErrorState({ onRetry }) {
  return (
    <Alert
      severity="warning"
      icon={<ErrorIcon />}
      action={<Button size="small" onClick={onRetry}>Retry</Button>}
    >
      Could not reach the backend at <strong>localhost:8000</strong>. Make sure you ran{' '}
      <code>python main.py</code> inside the <code>backend/</code> folder, then click Retry.
    </Alert>
  );
}

// â”€â”€ Dashboard â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function Dashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [latestResult, setLatestResult] = useState(null);
  const [assessments, setAssessments] = useState([]);
  const [page, setPage] = useState(0);

  const userId = 'user123'; // TODO: replace with real JWT user id

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError(false);
      const res = await apiService.getAssessmentHistory(userId, 1, 20);
      const list = res.assessments || [];
      setAssessments(list);
      if (list.length > 0) setLatestResult(list[0]);
    } catch (e) {
      // Backend unreachable â€” show empty state, not a hard error
      // (assessment history is optional; the page still renders usefully)
      setAssessments([]);
      setLatestResult(null);
      if (e?.code === 'ERR_NETWORK' || e?.message?.includes('Network')) {
        setError(true); // only show error banner for true network failures
      }
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => { load(); }, [load]);

  const riskLevel = latestResult?.risk_level || 'unknown';
  const confidence = latestResult?.confidence ?? null;
  const totalAssessments = assessments.length;

  // Change since last
  let changeTrend = 'stable';
  let changeText  = 'No previous data';
  if (assessments.length >= 2) {
    const prevRisk = RISK_CONFIG[assessments[1]?.risk_level]?.index ?? 0;
    const curRisk  = RISK_CONFIG[riskLevel]?.index ?? 0;
    if (curRisk < prevRisk) { changeTrend = 'down'; changeText = 'Improved vs. last assessment'; }
    else if (curRisk > prevRisk) { changeTrend = 'up'; changeText = 'Worsened vs. last assessment'; }
    else { changeTrend = 'stable'; changeText = 'Unchanged vs. last assessment'; }
  } else if (assessments.length === 1) {
    changeText = 'First assessment';
  }

  const modality = latestResult?.modality_contributions || {};
  const perConf  = latestResult?.per_modality_confidence || {};
  const keyFindings = latestResult?.key_findings || [];

  // Paginated table rows
  const rowsPerPage = 5;
  const pagedRows = assessments.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

  const today = format(new Date(), 'EEEE, d MMMM yyyy');

  return (
    <Box>
      {/* Crisis banner */}
      {(riskLevel === 'critical' || riskLevel === 'high') && (
        <CrisisBanner riskLevel={riskLevel} />
      )}

      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, color: 'text.primary', mb: 0.25 }}>
            Overview
          </Typography>
          <Typography variant="body2" color="text.secondary">{today}</Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/assess')}
          aria-label="Start a new assessment"
          sx={{ flexShrink: 0 }}
        >
          Start new assessment
        </Button>
      </Box>

      {error && <ErrorState onRetry={load} />}

      {/* KPI row */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            label="Current risk level"
            loading={loading}
            badge={<RiskBadge level={riskLevel} size="medium" />}
            subtext={riskLevel !== 'unknown' ? 'Based on latest assessment' : undefined}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            label="Model confidence"
            value={confidence != null ? `${(confidence * 100).toFixed(0)}%` : 'â€”'}
            subtext={confidence != null ? 'Latest assessment' : 'No data'}
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            label="Assessments completed"
            value={totalAssessments}
            subtext="Total sessions"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            label="Change since last"
            value={changeText}
            trend={changeTrend}
            loading={loading}
          />
        </Grid>
      </Grid>

      {/* Two-column section */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {/* Risk assessment card */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ p: 2.5 }}>
              <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                            color: 'text.secondary', fontWeight: 600, display: 'block', mb: 2 }}>
                Risk assessment
              </Typography>
              {loading ? (
                <>
                  <Skeleton variant="rectangular" height={10} sx={{ borderRadius: 3, mb: 1.5 }} />
                  <Skeleton variant="text" width="70%" />
                  <Skeleton variant="text" width="50%" />
                </>
              ) : assessments.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  Complete an assessment to see your risk profile.
                </Typography>
              ) : (
                <RiskMeter level={riskLevel} loading={loading} />
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Modality contribution card */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ p: 2.5 }}>
              <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                            color: 'text.secondary', fontWeight: 600, display: 'block', mb: 2 }}>
                Modality contribution
              </Typography>
              {loading ? (
                <>
                  {[1, 2, 3].map(i => (
                    <Box key={i} sx={{ mb: 2 }}>
                      <Skeleton variant="text" width="60%" height={20} />
                      <Skeleton variant="rectangular" height={6} sx={{ borderRadius: 3 }} />
                    </Box>
                  ))}
                </>
              ) : assessments.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  Run an assessment to see modality contributions.
                </Typography>
              ) : (
                <>
                  <ModalityBar
                    label="Text"
                    value={modality.text}
                    confidence={perConf.text}
                    loading={loading}
                  />
                  <ModalityBar
                    label="Audio"
                    value={modality.audio ?? 0}
                    confidence={perConf.audio}
                    loading={loading}
                  />
                  <ModalityBar
                    label="Video"
                    value={modality.video ?? 0}
                    confidence={perConf.video}
                    loading={loading}
                  />
                  {latestResult?.demo_mode && (
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                      Demo mode â€” values are estimates. Upload audio/video for real modality data.
                    </Typography>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Key insights */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 2.5 }}>
          <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                        color: 'text.secondary', fontWeight: 600, display: 'block', mb: 2 }}>
            Key insights
          </Typography>
          {loading ? (
            [1, 2, 3].map(i => <Skeleton key={i} variant="text" width="80%" height={24} />)
          ) : keyFindings.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              Complete an assessment to see findings here.
            </Typography>
          ) : (
            <Box component="ul" sx={{ m: 0, pl: 2.5 }}>
              {keyFindings.map((finding, i) => (
                <Box component="li" key={i} sx={{ mb: 0.75 }}>
                  <Typography variant="body2">{finding}</Typography>
                </Box>
              ))}
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Recent assessments table */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 0 }}>
          <Box sx={{ px: 2.5, pt: 2.5, pb: 1.5 }}>
            <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                          color: 'text.secondary', fontWeight: 600 }}>
              Recent assessments
            </Typography>
          </Box>
          {loading ? (
            <Box sx={{ px: 2.5, pb: 2 }}>
              {[1, 2, 3].map(i => (
                <Skeleton key={i} variant="text" height={40} sx={{ mb: 0.5 }} />
              ))}
            </Box>
          ) : assessments.length === 0 ? (
            <Box sx={{ px: 2.5, pb: 2.5 }}>
              <EmptyState onStart={() => navigate('/assess')} />
            </Box>
          ) : (
            <>
              <TableContainer>
                <Table size="small" aria-label="Recent assessments">
                  <TableHead>
                    <TableRow sx={{ '& th': { borderColor: 'divider', py: 1 } }}>
                      <TableCell>Date</TableCell>
                      <TableCell>Input type</TableCell>
                      <TableCell>Risk level</TableCell>
                      <TableCell>Confidence</TableCell>
                      <TableCell align="right">Report</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {pagedRows.map((row, i) => (
                      <TableRow
                        key={i}
                        hover
                        sx={{ '& td': { borderColor: 'divider', py: 1 } }}
                      >
                        <TableCell>
                          <Typography variant="body2">
                            {row.timestamp
                              ? format(new Date(row.timestamp), 'dd MMM yyyy, HH:mm')
                              : 'N/A'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={row.input_type || 'text'}
                            size="small"
                            variant="outlined"
                            sx={{ textTransform: 'capitalize', fontSize: '0.7rem' }}
                          />
                        </TableCell>
                        <TableCell>
                          <RiskBadge level={row.risk_level} />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {row.confidence != null ? `${(row.confidence * 100).toFixed(0)}%` : 'â€”'}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Tooltip title="View full report">
                            <Button
                              size="small"
                              endIcon={<ViewIcon sx={{ fontSize: 14 }} />}
                              onClick={() => navigate(`/assess/report/${page * rowsPerPage + i}`)}
                              aria-label={`View report from ${row.timestamp || 'this assessment'}`}
                            >
                              View
                            </Button>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              <TablePagination
                component="div"
                count={assessments.length}
                page={page}
                onPageChange={(_, p) => setPage(p)}
                rowsPerPage={rowsPerPage}
                rowsPerPageOptions={[5]}
                sx={{ borderTop: '1px solid', borderColor: 'divider' }}
              />
            </>
          )}
        </CardContent>
      </Card>

      {/* Persistent disclaimer */}
      <Typography
        variant="caption"
        color="text.secondary"
        sx={{ display: 'block', textAlign: 'center', py: 1 }}
      >
        This tool provides screening support and is not a medical diagnosis.
        Results should be interpreted by a qualified healthcare professional.
      </Typography>
    </Box>
  );
}

export default Dashboard;
