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
  Alert,
  Tooltip,
  AppBar,
  Toolbar,
  Avatar,
  IconButton,
  Menu,
  MenuItem,
  Divider,
  LinearProgress,
} from '@mui/material';
import {
  Add as AddIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon,
  OpenInNew as ViewIcon,
  ErrorOutline as ErrorIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  KeyboardArrowDown as ArrowDownIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import CrisisBanner from '../components/CrisisBanner';

// ── Mock data (swap this import for a real apiService call when backend ready) ──
import { MOCK_DASHBOARD } from '../mock/dashboardData';

// ── Design tokens ─────────────────────────────────────────────────────────────
const RISK_CONFIG = {
  low:      { label: 'Low',      color: '#16a34a', bg: '#f0fdf4', border: '#bbf7d0', index: 0 },
  moderate: { label: 'Moderate', color: '#d97706', bg: '#fffbeb', border: '#fde68a', index: 1 },
  elevated: { label: 'Elevated', color: '#ea580c', bg: '#fff7ed', border: '#fed7aa', index: 2 },
  high:     { label: 'High',     color: '#dc2626', bg: '#fef2f2', border: '#fecaca', index: 3 },
  critical: { label: 'Critical', color: '#dc2626', bg: '#fef2f2', border: '#fecaca', index: 3 },
  unknown:  { label: 'N/A',      color: '#6b7280', bg: '#f9fafb', border: '#e5e7eb', index: -1 },
};

const CARD_LABEL_SX = {
  textTransform: 'uppercase',
  letterSpacing: '0.06em',
  color: 'text.secondary',
  fontWeight: 600,
  fontSize: '0.72rem',
  display: 'block',
  mb: 1.5,
};

// ── RiskBadge ─────────────────────────────────────────────────────────────────
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

// ── KPI Card ──────────────────────────────────────────────────────────────────
function KpiCard({ label, value, subtext, loading, badge, trend }) {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 2.5 }}>
        <Typography variant="caption" sx={CARD_LABEL_SX}>{label}</Typography>
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
                {trend === 'up'     && <TrendingUpIcon   sx={{ fontSize: 16, color: 'error.main' }} />}
                {trend === 'down'   && <TrendingDownIcon  sx={{ fontSize: 16, color: 'success.main' }} />}
                {trend === 'stable' && <TrendingFlatIcon  sx={{ fontSize: 16, color: 'text.secondary' }} />}
                <Typography variant="caption" color="text.secondary">{subtext}</Typography>
              </Box>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}

// ── Risk Meter ────────────────────────────────────────────────────────────────
const RISK_SEGMENTS = [
  { key: 'low',      label: 'Low',      color: '#16a34a' },
  { key: 'moderate', label: 'Moderate', color: '#d97706' },
  { key: 'elevated', label: 'Elevated', color: '#ea580c' },
  { key: 'high',     label: 'High',     color: '#dc2626' },
];

const RISK_EXPLANATION = {
  low:      'No significant indicators of depression detected. Continue regular self-monitoring.',
  moderate: 'Moderate depressive indicators present. Consider a check-in with a qualified professional.',
  elevated: 'Elevated indicators detected. A professional consultation is strongly recommended.',
  high:     'High-level indicators identified. Please seek professional support as soon as possible.',
  critical: 'Significant distress indicators present. Please seek professional support promptly.',
  unknown:  'No assessment data available yet. Start an assessment to see your risk profile.',
};

function RiskMeter({ level, loading }) {
  const idx = RISK_CONFIG[level]?.index ?? -1;

  if (loading) {
    return (
      <>
        <Skeleton variant="rectangular" height={10} sx={{ borderRadius: 5, mb: 1.5 }} />
        <Skeleton variant="text" width="60%" sx={{ mb: 0.5 }} />
        <Skeleton variant="text" width="75%" />
      </>
    );
  }

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

      {/* Segment labels */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        {RISK_SEGMENTS.map((seg, i) => (
          <Typography
            key={seg.key}
            variant="caption"
            aria-hidden="true"
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

      {/* Plain-language explanation — 2 lines max */}
      <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.55 }}>
        {RISK_EXPLANATION[level] || RISK_EXPLANATION.unknown}
      </Typography>
    </Box>
  );
}

// ── Modality Bar ──────────────────────────────────────────────────────────────
function ModalityBar({ label, value, confidence, loading }) {
  const pct = value ?? 0;

  if (loading) {
    return (
      <Box sx={{ mb: 2.5 }}>
        <Skeleton variant="text" width="50%" height={20} sx={{ mb: 0.75 }} />
        <Skeleton variant="rectangular" height={6} sx={{ borderRadius: 3 }} />
      </Box>
    );
  }

  return (
    <Box sx={{ mb: 2.5 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.75, alignItems: 'center' }}>
        <Typography variant="body2" sx={{ fontWeight: 500 }}>{label}</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Typography variant="body2" sx={{ fontWeight: 700, color: 'text.primary' }}>
            {pct.toFixed(1)}%
          </Typography>
          {confidence != null && (
            <Typography variant="caption" color="text.secondary">
              conf.&nbsp;{(confidence * 100).toFixed(0)}%
            </Typography>
          )}
        </Box>
      </Box>
      <Box sx={{ height: 6, backgroundColor: '#e5e7eb', borderRadius: 3, overflow: 'hidden' }}>
        <Box
          sx={{ height: '100%', width: `${pct}%`, backgroundColor: 'primary.main', borderRadius: 3 }}
          role="progressbar"
          aria-valuenow={Math.round(pct)}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`${label} contribution: ${pct.toFixed(1)}%`}
        />
      </Box>
    </Box>
  );
}

// ── Question Stat Tile ────────────────────────────────────────────────────────
function QuestionTile({ label, score, max, note, loading }) {
  const pct = max > 0 ? (score / max) * 100 : 0;

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 2.5 }}>
        <Typography variant="caption" sx={CARD_LABEL_SX}>{label} question</Typography>
        {loading ? (
          <>
            <Skeleton variant="text" width={60} height={44} />
            <Skeleton variant="rectangular" height={4} sx={{ borderRadius: 2, mt: 1 }} />
          </>
        ) : score == null ? (
          <Typography variant="body2" color="text.secondary">No data</Typography>
        ) : (
          <>
            <Typography
              variant="h4"
              sx={{ fontWeight: 700, fontSize: '2rem', color: 'text.primary', lineHeight: 1.1, mb: 1 }}
            >
              {score.toFixed(1)}
              <Typography component="span" variant="caption" color="text.secondary" sx={{ ml: 0.5 }}>
                / {max}
              </Typography>
            </Typography>
            {/* Thin progress bar */}
            <LinearProgress
              variant="determinate"
              value={pct}
              sx={{
                height: 4,
                borderRadius: 2,
                backgroundColor: '#e5e7eb',
                mb: 1,
                '& .MuiLinearProgress-bar': { backgroundColor: 'primary.main', borderRadius: 2 },
              }}
              aria-label={`${label} score: ${score} out of ${max}`}
            />
            {note && (
              <Typography variant="caption" color="text.secondary">
                {note}
              </Typography>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}

// ── Empty State ───────────────────────────────────────────────────────────────
function EmptyState({ onStart }) {
  return (
    <Box
      sx={{
        textAlign: 'center', py: 6, px: 3,
        border: '1px dashed #e5e7eb', borderRadius: 2, backgroundColor: '#fafafa',
      }}
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

// ── Error State ───────────────────────────────────────────────────────────────
function ErrorState({ onRetry }) {
  return (
    <Alert
      severity="warning"
      icon={<ErrorIcon />}
      action={<Button size="small" onClick={onRetry}>Retry</Button>}
      sx={{ mb: 3 }}
    >
      Could not reach the backend at <strong>localhost:8000</strong>. Make sure
      you ran <code>python main.py</code> inside the <code>backend/</code> folder,
      then click Retry.
    </Alert>
  );
}

// ── Top App Bar (user menu) ───────────────────────────────────────────────────
function DashboardTopBar({ today }) {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const userName = localStorage.getItem('mindcare_user_name') || 'Clinician';

  const handleOpen  = (e) => setAnchorEl(e.currentTarget);
  const handleClose = () => setAnchorEl(null);
  const handleSignOut = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('mindcare_consent');
    window.location.href = '/';
  };

  return (
    <AppBar
      position="static"
      color="transparent"
      elevation={0}
      sx={{
        borderBottom: '1px solid',
        borderColor: 'divider',
        backgroundColor: 'background.paper',
        mb: 3,
        mx: -3,
        mt: -3,
        width: 'calc(100% + 48px)',
        px: 3,
      }}
    >
      <Toolbar
        disableGutters
        sx={{ minHeight: '56px !important', justifyContent: 'space-between' }}
      >
        {/* Left: page title + date */}
        <Box>
          <Typography
            variant="h5"
            sx={{ fontWeight: 700, fontSize: '1.5rem', color: 'text.primary', lineHeight: 1.2 }}
          >
            Overview
          </Typography>
          <Typography variant="caption" color="text.secondary">{today}</Typography>
        </Box>

        {/* Right: user avatar + menu */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <IconButton
            onClick={handleOpen}
            aria-label="User menu"
            aria-haspopup="true"
            aria-expanded={Boolean(anchorEl)}
            size="small"
            sx={{ borderRadius: 2, px: 1, gap: 0.75 }}
          >
            <Avatar sx={{ width: 28, height: 28, fontSize: '0.8rem', bgcolor: 'primary.main' }}>
              {userName.charAt(0).toUpperCase()}
            </Avatar>
            <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.primary' }}>
              {userName}
            </Typography>
            <ArrowDownIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleClose}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          >
            <MenuItem onClick={() => { handleClose(); navigate('/settings'); }}>
              <SettingsIcon fontSize="small" sx={{ mr: 1 }} /> Settings
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleSignOut} sx={{ color: 'error.main' }}>
              <LogoutIcon fontSize="small" sx={{ mr: 1 }} /> Sign out
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

// ── Dashboard ─────────────────────────────────────────────────────────────────
function Dashboard() {
  const navigate = useNavigate();
  const [loading, setLoading]           = useState(true);
  const [error, setError]               = useState(false);
  const [latestResult, setLatestResult] = useState(null);
  const [assessments, setAssessments]   = useState([]);
  const [page, setPage]                 = useState(0);
  const [backendOnline, setBackendOnline] = useState(null); // null=checking, true, false

  // ── Data loading ────────────────────────────────────────────────────────────
  // SWAP POINT: replace the body of loadDashboard() with a real apiService call.
  // The state variables (latestResult, assessments) have the same shape as
  // MOCK_DASHBOARD.latestResult and MOCK_DASHBOARD.assessments.
  const loadDashboard = useCallback(async () => {
    try {
      setLoading(true);
      setError(false);

      // ── Using mock data ──────────────────────────────────────────────────
      // Simulate a brief network delay so loading skeletons are visible.
      await new Promise((res) => setTimeout(res, 600));
      const { latestResult: lr, assessments: list } = MOCK_DASHBOARD;
      setLatestResult(lr);
      setAssessments(list);

      // ── Real API (replace the block above with this when ready) ─────────
      // const res  = await apiService.getAssessmentHistory('user123', 1, 20);
      // const list = res.assessments || [];
      // setAssessments(list);
      // if (list.length > 0) setLatestResult(list[0]);
    } catch (e) {
      setAssessments([]);
      setLatestResult(null);
      if (e?.code === 'ERR_NETWORK' || e?.message?.includes('Network')) {
        setError(true);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  // ── Backend health check ─────────────────────────────────────────────────────
  useEffect(() => {
    fetch('/health')
      .then((r) => setBackendOnline(r.ok))
      .catch(() => setBackendOnline(false));
  }, []);

  useEffect(() => { loadDashboard(); }, [loadDashboard]);

  // ── Derived values ──────────────────────────────────────────────────────────
  const riskLevel        = latestResult?.risk_level || 'unknown';
  const confidence       = latestResult?.confidence ?? null;
  const totalAssessments = assessments.length;

  let changeTrend = 'stable';
  let changeLabel = 'No previous data';
  let changeSubtext = '';
  if (assessments.length >= 2) {
    const prevIdx = RISK_CONFIG[assessments[1]?.risk_level]?.index ?? 0;
    const curIdx  = RISK_CONFIG[riskLevel]?.index ?? 0;
    if (curIdx < prevIdx) {
      changeTrend = 'down';
      changeLabel = 'Improved';
      changeSubtext = 'vs. previous assessment';
    } else if (curIdx > prevIdx) {
      changeTrend = 'up';
      changeLabel = 'Worsened';
      changeSubtext = 'vs. previous assessment';
    } else {
      changeTrend = 'stable';
      changeLabel = 'Unchanged';
      changeSubtext = 'vs. previous assessment';
    }
  } else if (assessments.length === 1) {
    changeLabel   = 'First assessment';
    changeSubtext = 'No comparison available';
  }

  const modality       = latestResult?.modality_contributions || {};
  const perConf        = latestResult?.per_modality_confidence || {};
  const qResponses     = latestResult?.question_responses || {};
  const keyFindings    = latestResult?.key_findings || [];

  const rowsPerPage = 5;
  const pagedRows   = assessments.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);
  const today       = format(new Date(), 'EEEE, d MMMM yyyy');

  return (
    <Box sx={{ position: 'relative' }}>

      {/* ── Top bar ─────────────────────────────────────────────────────── */}
      <DashboardTopBar today={today} />

      {/* ── Crisis banner ───────────────────────────────────────────────── */}
      {(riskLevel === 'critical' || riskLevel === 'high') && (
        <CrisisBanner riskLevel={riskLevel} />
      )}

      {/* ── Page header ─────────────────────────────────────────────────── */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography
            variant="h4"
            sx={{ fontWeight: 700, fontSize: '1.5rem', color: 'text.primary', lineHeight: 1.2 }}
          >
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

      {/* ── Backend offline banner ──────────────────────────────────────── */}
      {backendOnline === false && (
        <Alert
          severity="error"
          sx={{ mb: 2, borderRadius: 2 }}
          action={
            <Button
              size="small"
              color="inherit"
              onClick={() => {
                setBackendOnline(null);
                fetch('/health').then((r) => setBackendOnline(r.ok)).catch(() => setBackendOnline(false));
              }}
            >
              Retry
            </Button>
          }
        >
          <strong>Backend server is not running.</strong> Start it with:{' '}
          <code style={{ backgroundColor: '#fee2e2', padding: '1px 6px', borderRadius: 4 }}>
            cd backend &amp;&amp; python main.py
          </code>{' '}
          — then click Retry. Assessments will not work until it is online.
        </Alert>
      )}

      {/* ── Error banner ────────────────────────────────────────────────── */}
      {error && <ErrorState onRetry={loadDashboard} />}

      {/* ── 1. KPI cards ────────────────────────────────────────────────── */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {/* Current risk level */}
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            label="Current risk level"
            loading={loading}
            badge={<RiskBadge level={riskLevel} size="medium" />}
            subtext={riskLevel !== 'unknown' ? 'Based on latest assessment' : undefined}
          />
        </Grid>

        {/* Model confidence */}
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            label="Model confidence"
            value={confidence != null ? `${(confidence * 100).toFixed(0)}%` : '—'}
            subtext={confidence != null ? 'Latest assessment' : 'No data'}
            loading={loading}
          />
        </Grid>

        {/* Assessments completed */}
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            label="Assessments completed"
            value={totalAssessments}
            subtext="Total sessions recorded"
            loading={loading}
          />
        </Grid>

        {/* Change since last */}
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            label="Change since last"
            value={changeLabel}
            subtext={changeSubtext || undefined}
            trend={changeTrend}
            loading={loading}
          />
        </Grid>
      </Grid>

      {/* ── 2. Risk assessment + Modality contribution ──────────────────── */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {/* Risk assessment */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ p: 2.5 }}>
              <Typography variant="caption" sx={CARD_LABEL_SX}>
                Risk assessment
              </Typography>
              {!loading && assessments.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  Complete an assessment to see your risk profile.
                </Typography>
              ) : (
                <RiskMeter level={riskLevel} loading={loading} />
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Modality contribution */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ p: 2.5 }}>
              <Typography variant="caption" sx={CARD_LABEL_SX}>
                Modality contribution
              </Typography>
              {!loading && assessments.length === 0 ? (
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
                    value={modality.audio}
                    confidence={perConf.audio}
                    loading={loading}
                  />
                  {!loading && latestResult?.demo_mode && (
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                      Demo mode — values are model estimates. Upload audio for real modality data.
                    </Typography>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* ── 3. Responses by question ────────────────────────────────────── */}
      <Typography variant="caption" sx={{ ...CARD_LABEL_SX, mb: 1 }}>
        Responses by question
      </Typography>
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {['positive', 'neutral', 'negative'].map((key) => {
          const q = qResponses[key];
          return (
            <Grid item xs={12} sm={4} key={key}>
              <QuestionTile
                label={key.charAt(0).toUpperCase() + key.slice(1)}
                score={loading ? null : (q?.score ?? null)}
                max={q?.max ?? 10}
                note={q?.note}
                loading={loading}
              />
            </Grid>
          );
        })}
      </Grid>

      {/* ── 4. Key insights ─────────────────────────────────────────────── */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 2.5 }}>
          <Typography variant="caption" sx={CARD_LABEL_SX}>Key insights</Typography>
          {loading ? (
            [1, 2, 3].map((i) => <Skeleton key={i} variant="text" width="80%" height={24} sx={{ mb: 0.5 }} />)
          ) : keyFindings.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              Complete an assessment to see findings here.
            </Typography>
          ) : (
            <Box component="ul" sx={{ m: 0, pl: 2.5 }}>
              {keyFindings.slice(0, 3).map((finding, i) => (
                <Box component="li" key={i} sx={{ mb: 0.75 }}>
                  <Typography variant="body2">{finding}</Typography>
                </Box>
              ))}
            </Box>
          )}
        </CardContent>
      </Card>

      {/* ── 5. Recent assessments table ─────────────────────────────────── */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 0 }}>
          <Box sx={{ px: 2.5, pt: 2.5, pb: 1.5 }}>
            <Typography variant="caption" sx={{ ...CARD_LABEL_SX, mb: 0 }}>
              Recent assessments
            </Typography>
          </Box>

          {loading ? (
            <Box sx={{ px: 2.5, pb: 2 }}>
              {[1, 2, 3, 4, 5].map((i) => (
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
                    <TableRow sx={{ '& th': { borderColor: 'divider', py: 1.25 } }}>
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
                        key={row.id || i}
                        hover
                        sx={{ '& td': { borderColor: 'divider', py: 1.25 } }}
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
                            {row.confidence != null
                              ? `${(row.confidence * 100).toFixed(0)}%`
                              : '—'}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Tooltip title="View full report">
                            <Button
                              size="small"
                              endIcon={<ViewIcon sx={{ fontSize: 14 }} />}
                              onClick={() => navigate(`/assess/report/${row.id || page * rowsPerPage + i}`)}
                              aria-label={`View report from ${row.timestamp || 'this assessment'}`}
                            >
                              View report
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

      {/* ── Disclaimer footer ────────────────────────────────────────────── */}
      <Typography
        variant="caption"
        color="text.secondary"
        sx={{ display: 'block', textAlign: 'center', py: 1.5, borderTop: '1px solid', borderColor: 'divider' }}
      >
        This tool provides screening support only and is not a medical diagnosis.
        Results must be interpreted by a qualified healthcare professional.
      </Typography>
    </Box>
  );
}

export default Dashboard;
