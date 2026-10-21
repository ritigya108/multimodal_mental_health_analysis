import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Grid,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  SentimentSatisfied,
  SentimentNeutral,
  SentimentDissatisfied,
} from '@mui/icons-material';
import { format } from 'date-fns';
import apiService from '../services/api';

function Journal() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [currentEntry, setCurrentEntry] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);

  const userId = 'user123'; // Replace with actual auth

  useEffect(() => {
    loadEntries();
  }, []);

  const loadEntries = async () => {
    try {
      setLoading(true);
      const response = await apiService.getJournalEntries(userId, 20);
      // Mock data for demonstration
      setEntries([
        {
          id: 1,
          content: "Today was a good day. I felt productive and accomplished my goals. The weather was nice and I went for a walk.",
          timestamp: new Date().toISOString(),
          sentiment: 'positive',
          score: 0.75,
        },
        {
          id: 2,
          content: "Feeling a bit overwhelmed with work. Too many deadlines approaching. Need to take a break and relax.",
          timestamp: new Date(Date.now() - 86400000).toISOString(),
          sentiment: 'negative',
          score: -0.45,
        },
        {
          id: 3,
          content: "Had a great conversation with a friend today. It really helped me feel better about things.",
          timestamp: new Date(Date.now() - 172800000).toISOString(),
          sentiment: 'positive',
          score: 0.65,
        },
      ]);
    } catch (error) {
      console.error('Error loading entries:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateEntry = async () => {
    if (!currentEntry.trim()) return;

    try {
      setAnalyzing(true);
      
      // Analyze sentiment
      const sentimentResult = await apiService.analyzeSentiment(currentEntry);
      
      // Create entry
      await apiService.createJournalEntry({
        user_id: userId,
        content: currentEntry,
      });

      setAnalysis(sentimentResult);
      
      // Reload entries
      await loadEntries();
      
      // Reset form
      setTimeout(() => {
        setCurrentEntry('');
        setOpenDialog(false);
        setAnalysis(null);
      }, 3000);
      
    } catch (error) {
      console.error('Error creating entry:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  const getSentimentIcon = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return <SentimentSatisfied sx={{ color: 'success.main' }} />;
      case 'negative':
        return <SentimentDissatisfied sx={{ color: 'error.main' }} />;
      default:
        return <SentimentNeutral sx={{ color: 'warning.main' }} />;
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return 'success';
      case 'negative':
        return 'error';
      default:
        return 'warning';
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>
          My Journal 📝
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
          size="large"
        >
          New Entry
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Writing Tips */}
        <Grid item xs={12} md={4}>
          <Card sx={{ position: 'sticky', top: 20 }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                ✍️ Journaling Tips
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box>
                  <Typography variant="subtitle2" fontWeight={600}>
                    Be Honest
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Write freely without judgment. This is your safe space.
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" fontWeight={600}>
                    Express Emotions
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Don't hold back. Let your feelings flow onto the page.
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" fontWeight={600}>
                    Reflect on Patterns
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Review past entries to identify triggers and growth.
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" fontWeight={600}>
                    Practice Gratitude
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Include things you're grateful for each day.
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ mt: 2, backgroundColor: 'primary.light' }}>
            <CardContent>
              <Typography variant="subtitle2" sx={{ color: 'white', fontWeight: 600, mb: 1 }}>
                🤖 AI Analysis
              </Typography>
              <Typography variant="body2" sx={{ color: 'white', mb: 2 }}>
                Our AI analyzes your entries to provide insights and support.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Journal Entries */}
        <Grid item xs={12} md={8}>
          {entries.length === 0 ? (
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 8 }}>
                <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                  No journal entries yet
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Start writing to track your thoughts and feelings
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setOpenDialog(true)}
                >
                  Write Your First Entry
                </Button>
              </CardContent>
            </Card>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {entries.map((entry) => (
                <Card key={entry.id}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getSentimentIcon(entry.sentiment)}
                        <Typography variant="caption" color="text.secondary">
                          {format(new Date(entry.timestamp), 'MMMM dd, yyyy • h:mm a')}
                        </Typography>
                      </Box>
                      <Chip
                        label={entry.sentiment}
                        size="small"
                        color={getSentimentColor(entry.sentiment)}
                        sx={{ textTransform: 'capitalize' }}
                      />
                    </Box>
                    
                    <Typography variant="body1" sx={{ mb: 2, lineHeight: 1.7 }}>
                      {entry.content}
                    </Typography>

                    <Divider sx={{ my: 2 }} />

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Chip
                          label={`Sentiment Score: ${(entry.score * 100).toFixed(0)}%`}
                          size="small"
                          variant="outlined"
                        />
                      </Box>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button size="small" startIcon={<EditIcon />}>
                          Edit
                        </Button>
                        <Button size="small" color="error" startIcon={<DeleteIcon />}>
                          Delete
                        </Button>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </Box>
          )}
        </Grid>
      </Grid>

      {/* New Entry Dialog */}
      <Dialog
        open={openDialog}
        onClose={() => !analyzing && setOpenDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Typography variant="h6" fontWeight={600}>
            New Journal Entry
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              multiline
              rows={12}
              placeholder="Write your thoughts, feelings, and experiences here... Be honest and open with yourself."
              value={currentEntry}
              onChange={(e) => setCurrentEntry(e.target.value)}
              disabled={analyzing}
              sx={{
                '& .MuiOutlinedInput-root': {
                  fontSize: '1rem',
                  lineHeight: 1.7,
                },
              }}
            />
            
            {analysis && (
              <Alert severity="success" sx={{ mt: 2 }}>
                <Typography variant="subtitle2" fontWeight={600}>
                  Entry Analyzed Successfully!
                </Typography>
                <Typography variant="body2">
                  Sentiment: {analysis.sentiment} • Confidence: {(analysis.confidence * 100).toFixed(0)}%
                </Typography>
              </Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setOpenDialog(false)} disabled={analyzing}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleCreateEntry}
            disabled={!currentEntry.trim() || analyzing}
          >
            {analyzing ? <CircularProgress size={24} /> : 'Save Entry'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Journal;


