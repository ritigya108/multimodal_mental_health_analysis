import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';

// Pages
import Dashboard from './pages/Dashboard';
import Assessment from './pages/Assessment';
import PHQ8 from './pages/PHQ8';
import Settings from './pages/Settings';
import ReportDetail from './pages/ReportDetail';

// Components
import Navigation from './components/Navigation';
import CrisisFooter from './components/CrisisFooter';
import ConsentModal from './components/ConsentModal';

// Clinical-grade theme: neutral palette, one teal accent, Inter font
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#0d6e6e',    // deep teal accent
      light: '#1a9090',
      dark: '#0a5252',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#64748b',
      light: '#94a3b8',
      dark: '#475569',
    },
    success: { main: '#16a34a' },
    warning: { main: '#d97706' },
    error:   { main: '#dc2626' },
    info:    { main: '#0891b2' },
    background: {
      default: '#f3f4f6',
      paper: '#ffffff',
    },
    text: {
      primary: '#1f2328',
      secondary: '#57606a',
    },
    divider: '#e5e7eb',
  },
  typography: {
    fontFamily: '"Inter", "Segoe UI", system-ui, -apple-system, sans-serif',
    fontSize: 14,
    h1: { fontWeight: 700, fontSize: '2rem' },
    h2: { fontWeight: 600, fontSize: '1.5rem' },
    h3: { fontWeight: 600, fontSize: '1.25rem' },
    h4: { fontWeight: 600, fontSize: '1.5rem' },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
    body1: { fontSize: '0.9375rem', lineHeight: 1.6 },
    body2: { fontSize: '0.875rem', lineHeight: 1.5 },
    caption: { fontSize: '0.75rem' },
  },
  shape: { borderRadius: 12 },
  shadows: [
    'none',
    '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    '0 1px 3px 0 rgb(0 0 0 / 0.08), 0 1px 2px -1px rgb(0 0 0 / 0.06)',
    '0 2px 4px 0 rgb(0 0 0 / 0.06)',
    '0 4px 6px -1px rgb(0 0 0 / 0.08)',
    ...Array(20).fill('0 4px 6px -1px rgb(0 0 0 / 0.08)'),
  ],
  components: {
    MuiButton: {
      styleOverrides: {
        root: { textTransform: 'none', fontWeight: 600, borderRadius: 8 },
        containedPrimary: { boxShadow: 'none', '&:hover': { boxShadow: 'none' } },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          border: '1px solid #e5e7eb',
          boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.06)',
          borderRadius: 12,
        },
      },
    },
    MuiChip: {
      styleOverrides: { root: { fontWeight: 600, fontSize: '0.75rem' } },
    },
    MuiTableCell: {
      styleOverrides: {
        head: { fontWeight: 600, color: '#57606a', textTransform: 'uppercase',
                fontSize: '0.75rem', letterSpacing: '0.05em' },
      },
    },
  },
});

function App() {
  const [consentGiven, setConsentGiven] = useState(
    () => localStorage.getItem('mindcare_consent') === 'true'
  );

  const handleConsent = () => {
    localStorage.setItem('mindcare_consent', 'true');
    setConsentGiven(true);
  };

  const handleDecline = () => {
    // Redirect to a neutral page or show limited view
    setConsentGiven(false);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        {!consentGiven && (
          <ConsentModal onAccept={handleConsent} onDecline={handleDecline} />
        )}
        <Box sx={{ display: 'flex', minHeight: '100vh', flexDirection: 'column' }}>
          <Box sx={{ display: 'flex', flex: 1 }}>
            <Navigation />
            <Box
              component="main"
              sx={{
                flexGrow: 1,
                backgroundColor: 'background.default',
                minHeight: '100vh',
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              <Box sx={{ flex: 1, p: { xs: 2, sm: 3 } }}>
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/assess" element={<Assessment />} />
                  <Route path="/assess/report/:id" element={<ReportDetail />} />
                  <Route path="/phq8" element={<PHQ8 />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </Box>
              <CrisisFooter />
            </Box>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
