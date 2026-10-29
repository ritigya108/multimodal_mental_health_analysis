import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Slider,
  Grid,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  SentimentVeryDissatisfied,
  SentimentDissatisfied,
  SentimentNeutral,
  SentimentSatisfied,
  SentimentVerySatisfied,
} from '@mui/icons-material';
import apiService from '../services/api';

const moodEmojis = [
  { value: 1, icon: <SentimentVeryDissatisfied />, label: 'Very Bad', color: '#ef4444' },
  { value: 2, icon: <SentimentVeryDissatisfied />, label: 'Bad', color: '#f97316' },
  { value: 3, icon: <SentimentDissatisfied />, label: 'Poor', color: '#f59e0b' },
  { value: 4, icon: <SentimentDissatisfied />, label: 'Below Average', color: '#eab308' },
  { value: 5, icon: <SentimentNeutral />, label: 'Neutral', color: '#84cc16' },
  { value: 6, icon: <SentimentNeutral />, label: 'Okay', color: '#22c55e' },
  { value: 7, icon: <SentimentSatisfied />, label: 'Good', color: '#10b981' },
  { value: 8, icon: <SentimentSatisfied />, label: 'Great', color: '#14b8a6' },
  { value: 9, icon: <SentimentVerySatisfied />, label: 'Excellent', color: '#06b6d4' },
  { value: 10, icon: <SentimentVerySatisfied />, label: 'Amazing', color: '#0ea5e9' },
];

function MoodTracker() {
  const [moodScore, setMoodScore] = useState(5);
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const userId = 'user123'; // Replace with actual auth

  const handleSubmit = async () => {
    try {
      setLoading(true);
      await apiService.logMood({
        user_id: userId,
        mood_score: moodScore,
        notes: notes || null,
      });
      
      setSnackbar({
        open: true,
        message: 'Mood logged successfully! ðŸŽ‰',
        severity: 'success',
      });
      
      // Reset form
      setNotes('');
      setMoodScore(5);
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Failed to log mood. Please try again.',
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const currentMood = moodEmojis.find(m => m.value === moodScore);

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 700 }}>
        How are you feeling today?
      </Typography>

      <Grid container spacing={3}>
        {/* Mood Selection Card */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent sx={{ p: 4 }}>
              <Box sx={{ textAlign: 'center', mb: 4 }}>
                <Box
                  sx={{
                    fontSize: 80,
                    color: currentMood?.color,
                    mb: 2,
                  }}
                >
                  {currentMood?.icon}
                </Box>
                <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
                  {currentMood?.label}
                </Typography>
                <Typography variant="h3" sx={{ fontWeight: 700, color: currentMood?.color }}>
                  {moodScore}/10
                </Typography>
              </Box>

              <Box sx={{ px: 2, mb: 4 }}>
                <Slider
                  value={moodScore}
                  onChange={(e, value) => setMoodScore(value)}
                  min={1}
                  max={10}
                  marks
                  valueLabelDisplay="auto"
                  sx={{
                    '& .MuiSlider-thumb': {
                      width: 24,
                      height: 24,
                    },
                    '& .MuiSlider-track': {
                      height: 8,
                    },
                    '& .MuiSlider-rail': {
                      height: 8,
                    },
                  }}
                />
              </Box>

              <TextField
                fullWidth
                multiline
                rows={4}
                label="What's on your mind? (Optional)"
                placeholder="Share your thoughts, feelings, or what influenced your mood today..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                sx={{ mb: 3 }}
              />

              <Button
                variant="contained"
                size="large"
                fullWidth
                onClick={handleSubmit}
                disabled={loading}
              >
                {loading ? 'Logging...' : 'Log Mood'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Tips Card */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                ðŸ’¡ Mood Tracking Tips
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box>
                  <Typography variant="subtitle2" fontWeight={600}>
                    Be Honest
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    There's no right or wrong answer. Track how you truly feel.
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" fontWeight={600}>
                    Track Regularly
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Daily tracking helps identify patterns and triggers.
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" fontWeight={600}>
                    Add Context
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Notes help you understand what affects your mood.
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" fontWeight={600}>
                    Review Trends
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Check your dashboard to see mood patterns over time.
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ mt: 2, backgroundColor: 'primary.light' }}>
            <CardContent>
              <Typography variant="subtitle2" sx={{ color: 'white', fontWeight: 600, mb: 1 }}>
                Feeling Low?
              </Typography>
              <Typography variant="body2" sx={{ color: 'white', mb: 2 }}>
                It's okay to not be okay. Consider talking to someone.
              </Typography>
              <Button
                variant="contained"
                size="small"
                sx={{ backgroundColor: 'white', color: 'primary.main' }}
                href="/chat"
              >
                Chat with AI
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Mood Selection */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Quick Select
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {moodEmojis.map((mood) => (
                  <Button
                    key={mood.value}
                    variant={moodScore === mood.value ? 'contained' : 'outlined'}
                    onClick={() => setMoodScore(mood.value)}
                    sx={{
                      minWidth: 60,
                      flexDirection: 'column',
                      py: 1,
                      borderColor: mood.color,
                      color: moodScore === mood.value ? 'white' : mood.color,
                      backgroundColor: moodScore === mood.value ? mood.color : 'transparent',
                      '&:hover': {
                        backgroundColor: moodScore === mood.value ? mood.color : `${mood.color}20`,
                        borderColor: mood.color,
                      },
                    }}
                  >
                    <Box sx={{ fontSize: 24, mb: 0.5 }}>{mood.icon}</Box>
                    <Typography variant="caption">{mood.value}</Typography>
                  </Button>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default MoodTracker;
