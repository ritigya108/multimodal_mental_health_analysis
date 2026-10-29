import React, { useState, useEffect } from 'react';
import { Box, Typography, Link, Alert, IconButton } from '@mui/material';
import { Phone as PhoneIcon, Close as CloseIcon } from '@mui/icons-material';

/**
 * CrisisBanner â€” shown when risk level is "critical" or crisis language detected.
 * Calm, non-alarming tone. Dismissible. Not a modal â€” stays in-page.
 */
function CrisisBanner({ riskLevel, onDismiss }) {
  const [helpline, setHelpline] = useState({ name: 'Tele-MANAS', number: '14416' });
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    fetch('/api/config/helpline')
      .then((r) => r.ok ? r.json() : null)
      .then((d) => { if (d) setHelpline({ name: d.name, number: d.number }); })
      .catch(() => {});
  }, []);

  const show = !dismissed && (riskLevel === 'critical' || riskLevel === 'high');
  if (!show) return null;

  const handleDismiss = () => {
    setDismissed(true);
    onDismiss && onDismiss();
  };

  return (
    <Alert
      severity={riskLevel === 'critical' ? 'error' : 'warning'}
      role="alert"
      aria-live="polite"
      sx={{
        mb: 2,
        borderRadius: 2,
        '& .MuiAlert-message': { flex: 1 },
      }}
      action={
        <IconButton
          size="small"
          onClick={handleDismiss}
          aria-label="Dismiss alert"
        >
          <CloseIcon fontSize="small" />
        </IconButton>
      }
      icon={<PhoneIcon aria-hidden="true" />}
    >
      <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.25 }}>
        {riskLevel === 'critical'
          ? 'The screening suggests significant distress.'
          : 'The screening indicates elevated distress.'}
      </Typography>
      <Typography variant="body2">
        If you're finding things difficult, speaking with someone can help.{' '}
        <strong>{helpline.name}</strong>:{' '}
        <Link
          href={`tel:${helpline.number}`}
          underline="hover"
          sx={{ fontWeight: 600 }}
          aria-label={`Call ${helpline.name} at ${helpline.number}`}
        >
          {helpline.number}
        </Link>{' '}
        (free, 24/7) â€” or talk to a trusted friend or mental health professional.
      </Typography>
    </Alert>
  );
}

export default CrisisBanner;
