import React, { useState, useEffect } from 'react';
import { Box, Typography, Link } from '@mui/material';
import { Phone as PhoneIcon } from '@mui/icons-material';

/**
 * CrisisFooter â€” persistent one-line footer on every page.
 * Helpline number is loaded from the backend config endpoint so it's
 * editable in backend/app_config.py without touching the frontend.
 */
function CrisisFooter() {
  const [helpline, setHelpline] = useState({ name: 'Tele-MANAS', number: '14416' });

  useEffect(() => {
    fetch('/api/config/helpline')
      .then((r) => r.ok ? r.json() : null)
      .then((d) => { if (d) setHelpline({ name: d.name, number: d.number }); })
      .catch(() => {}); // silently use default
  }, []);

  return (
    <Box
      component="footer"
      role="contentinfo"
      aria-label="Crisis helpline information"
      sx={{
        borderTop: '1px solid',
        borderColor: 'divider',
        backgroundColor: 'background.paper',
        px: 3,
        py: 1,
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        flexShrink: 0,
      }}
    >
      <PhoneIcon sx={{ fontSize: 14, color: 'text.secondary' }} aria-hidden="true" />
      <Typography variant="caption" color="text.secondary">
        Crisis support?{' '}
        <strong>{helpline.name}</strong>{' â€” '}
        <Link
          href={`tel:${helpline.number}`}
          underline="hover"
          sx={{ color: 'primary.main', fontWeight: 600 }}
          aria-label={`Call ${helpline.name} at ${helpline.number}`}
        >
          {helpline.number}
        </Link>
        {' '}(free, 24/7)
      </Typography>
    </Box>
  );
}

export default CrisisFooter;
