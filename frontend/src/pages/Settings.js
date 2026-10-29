import React, { useState } from 'react';
import {
  Box, Card, CardContent, Typography, Button, Alert,
  Dialog, DialogTitle, DialogContent, DialogActions, Divider,
} from '@mui/material';
import {
  DeleteForever as DeleteIcon,
  PrivacyTip as PrivacyIcon,
  Warning as WarnIcon,
} from '@mui/icons-material';
import apiService from '../services/api';

const DATA_RETENTION_NOTE =
  'Uploaded audio and video files are deleted immediately after feature extraction. ' +
  'Text transcripts and derived features (risk scores, modality contributions, key findings) ' +
  'are retained on the server until you request deletion below. ' +
  'No data is shared with third parties.';

function Settings() {
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteSuccess, setDeleteSuccess] = useState(false);
  const [deleteError, setDeleteError] = useState(null);

  const userId = 'user123'; // TODO: replace with real JWT user id

  const handleDeleteData = async () => {
    setDeleting(true);
    setDeleteError(null);
    try {
      await apiService.deleteUserData(userId);
      // Also clear session storage
      sessionStorage.removeItem('mindcare_assessments');
      setDeleteSuccess(true);
    } catch (e) {
      setDeleteError(e?.response?.data?.detail || 'Deletion failed. Please try again.');
    } finally {
      setDeleting(false);
      setConfirmOpen(false);
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>Settings</Typography>
        <Typography variant="body2" color="text.secondary">
          Privacy preferences and account settings.
        </Typography>
      </Box>

      {/* Data and Privacy */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 2.5 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <PrivacyIcon sx={{ color: 'primary.main', fontSize: 20 }} />
            <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                          color: 'text.secondary', fontWeight: 600 }}>
              Data and privacy
            </Typography>
          </Box>

          <Typography variant="body2" sx={{ mb: 2 }}>
            {DATA_RETENTION_NOTE}
          </Typography>

          <Box sx={{ p: 2, borderRadius: 2, backgroundColor: '#f8fafc',
                     border: '1px solid', borderColor: 'divider', mb: 3 }}>
            <Typography variant="caption" sx={{ fontWeight: 600, display: 'block', mb: 1 }}>
              What is stored on the server
            </Typography>
            {[
              'Assessment results (risk level, score, confidence, key findings)',
              'PHQ-8 questionnaire scores',
              'Text transcripts (only while retained)',
            ].map((item, i) => (
              <Box key={i} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 0.5 }}>
                <Typography variant="caption" color="text.secondary">â€¢</Typography>
                <Typography variant="caption" color="text.secondary">{item}</Typography>
              </Box>
            ))}
            <Divider sx={{ my: 1.5 }} />
            <Typography variant="caption" sx={{ fontWeight: 600, display: 'block', mb: 1 }}>
              What is NOT stored
            </Typography>
            {[
              'Audio files â€” deleted immediately after feature extraction',
              'Video files â€” deleted immediately after feature extraction',
            ].map((item, i) => (
              <Box key={i} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 0.5 }}>
                <Typography variant="caption" color="text.secondary">â€¢</Typography>
                <Typography variant="caption" color="text.secondary">{item}</Typography>
              </Box>
            ))}
          </Box>

          {deleteSuccess && (
            <Alert severity="success" sx={{ mb: 2 }}>
              All your data has been permanently deleted.
            </Alert>
          )}
          {deleteError && (
            <Alert severity="error" sx={{ mb: 2 }}>{deleteError}</Alert>
          )}

          <Button
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={() => setConfirmOpen(true)}
            disabled={deleteSuccess}
            aria-label="Delete all my data"
          >
            Delete all my data
          </Button>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
            This permanently deletes all assessments, PHQ-8 results, and transcripts.
            This action cannot be undone.
          </Typography>
        </CardContent>
      </Card>

      {/* Consent */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 2.5 }}>
          <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.06em',
                        color: 'text.secondary', fontWeight: 600, display: 'block', mb: 2 }}>
            Consent
          </Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            You accepted the privacy notice when you first used MindCare. To withdraw consent,
            click below â€” this will sign you out and clear your local session.
          </Typography>
          <Button
            variant="outlined"
            onClick={() => {
              localStorage.removeItem('mindcare_consent');
              window.location.href = '/';
            }}
            aria-label="Withdraw consent and sign out"
          >
            Withdraw consent and sign out
          </Button>
        </CardContent>
      </Card>

      {/* Confirmation dialog */}
      <Dialog
        open={confirmOpen}
        onClose={() => setConfirmOpen(false)}
        maxWidth="xs"
        fullWidth
        aria-labelledby="delete-confirm-title"
      >
        <DialogTitle id="delete-confirm-title">
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <WarnIcon color="error" />
            Confirm permanent deletion
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2">
            This will permanently delete <strong>all</strong> your assessments, PHQ-8 scores,
            and stored transcripts. This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setConfirmOpen(false)} disabled={deleting}>
            Cancel
          </Button>
          <Button
            variant="contained"
            color="error"
            onClick={handleDeleteData}
            disabled={deleting}
            aria-label="Confirm delete all my data"
          >
            {deleting ? 'Deletingâ€¦' : 'Delete permanently'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Settings;
