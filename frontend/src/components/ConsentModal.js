import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Button,
  Box,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import { PrivacyTip as PrivacyIcon } from '@mui/icons-material';

/**
 * ConsentModal â€” shown on first visit.
 * Explains what data is recorded and processed.
 * Requires explicit Accept before the app is accessible.
 */
function ConsentModal({ onAccept, onDecline }) {
  return (
    <Dialog
      open
      maxWidth="sm"
      fullWidth
      disableEscapeKeyDown
      aria-labelledby="consent-dialog-title"
      aria-describedby="consent-dialog-description"
    >
      <DialogTitle id="consent-dialog-title">
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <PrivacyIcon sx={{ color: 'primary.main' }} />
          <Typography variant="h6" component="span" sx={{ fontWeight: 600 }}>
            Privacy and data notice
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent dividers id="consent-dialog-description">
        <Typography variant="body2" sx={{ mb: 2 }}>
          Before you continue, please read how MindCare handles your information.
          This tool provides <strong>screening support only</strong> and is not a
          medical diagnosis.
        </Typography>

        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
          What is collected and processed
        </Typography>
        <List dense disablePadding sx={{ mb: 2 }}>
          {[
            'Text transcripts you enter or speak (processed on the server for analysis).',
            'Audio recordings â€” uploaded to the server, features extracted, then the file is deleted immediately.',
            'Video recordings â€” uploaded to the server, facial features extracted, then the file is deleted immediately.',
            'PHQ-8 questionnaire answers and computed score.',
            'Assessment results (risk level, confidence, key findings) stored server-side.',
          ].map((item, i) => (
            <ListItem key={i} sx={{ py: 0.25, pl: 0 }}>
              <ListItemText
                primary={`${i + 1}. ${item}`}
                primaryTypographyProps={{ variant: 'body2' }}
              />
            </ListItem>
          ))}
        </List>

        <Divider sx={{ my: 1.5 }} />

        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
          Your rights
        </Typography>
        <List dense disablePadding sx={{ mb: 2 }}>
          {[
            'You can delete all your data at any time from Settings.',
            'No data is shared with third parties.',
            'Audio and video files are deleted immediately after feature extraction.',
          ].map((item, i) => (
            <ListItem key={i} sx={{ py: 0.25, pl: 0 }}>
              <ListItemText
                primary={`â€¢ ${item}`}
                primaryTypographyProps={{ variant: 'body2' }}
              />
            </ListItem>
          ))}
        </List>

        <Typography variant="caption" color="text.secondary">
          By clicking "Accept", you confirm you have read this notice and consent
          to your data being processed as described above.
        </Typography>
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2, gap: 1 }}>
        <Button
          variant="outlined"
          color="inherit"
          onClick={onDecline}
          aria-label="Decline and do not use the application"
        >
          Decline
        </Button>
        <Button
          variant="contained"
          onClick={onAccept}
          aria-label="Accept and continue to the application"
        >
          Accept and continue
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default ConsentModal;
