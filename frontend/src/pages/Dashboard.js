import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material';
import {
  TrendingUp,
  Warning,
  CheckCircle,
  Info,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import apiService from '../services/api';

function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [riskAssessment, setRiskAssessment] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [moodData, setMoodData] = useState([]);

  // Mock user ID - replace with actual auth
  const userId = 'user123';

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load risk assessment
      const risk = await apiService.assessRisk(userId);
      setRiskAssessment(risk);

      // Load recommendations
      const recs = await apiService.getRecommendations(userId);
      setRecommendations(recs.recommendations || []);

      // Load mood history
      const mood = await apiService.getMoodHistory(userId, 7);
      setMoodData(mood.entries || []);

    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'low':
        return 'success';
      case 'medium':
        return 'warning';
      case 'high':
        return 'error';
      case 'critical':
        return 'error';
      default:
        return 'info';
    }
  };

  const getRiskIcon = (level) => {
    switch (level?.toLowerCase()) {
      case 'low':
        return <CheckCircle />;
      case 'medium':
        return <Info />;
      case 'high':
      case 'critical':
        return <Warning />;
      default:
        return <Info />;
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
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 700 }}>
        Welcome Back! 👋
      </Typography>

      <Grid container spacing={3}>
        {/* Risk Assessment Card */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                {getRiskIcon(riskAssessment?.risk_level)}
                <Typography variant="h6" sx={{ ml: 1 }}>
                  Mental Health Status
                </Typography>
              </Box>
              <Chip
                label={riskAssessment?.risk_level || 'Unknown'}
                color={getRiskColor(riskAssessment?.risk_level)}
                sx={{ mb: 2, fontWeight: 600 }}
              />
              <Typography variant="body2" color="text.secondary">
                Based on your recent activity and mood patterns
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Stats */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                This Week
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">
                    Journal Entries
                  </Typography>
                  <Typography variant="body2" fontWeight={600}>
                    5
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">
                    Mood Logs
                  </Typography>
                  <Typography variant="body2" fontWeight={600}>
                    7
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">
                    Average Mood
                  </Typography>
                  <Typography variant="body2" fontWeight={600}>
                    7.2/10
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Streak Card */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <CardContent>
              <Typography variant="h6" sx={{ color: 'white', mb: 1 }}>
                Current Streak 🔥
              </Typography>
              <Typography variant="h3" sx={{ color: 'white', fontWeight: 700 }}>
                7 Days
              </Typography>
              <Typography variant="body2" sx={{ color: 'white', opacity: 0.9, mt: 1 }}>
                Keep up the great work!
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Mood Trend Chart */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUp sx={{ mr: 1 }} />
                <Typography variant="h6">
                  Mood Trend (Last 7 Days)
                </Typography>
              </Box>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={moodData.length > 0 ? moodData : [
                  { day: 'Mon', mood: 6 },
                  { day: 'Tue', mood: 7 },
                  { day: 'Wed', mood: 6.5 },
                  { day: 'Thu', mood: 8 },
                  { day: 'Fri', mood: 7.5 },
                  { day: 'Sat', mood: 8 },
                  { day: 'Sun', mood: 7 },
                ]}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis domain={[0, 10]} />
                  <Tooltip />
                  <Line type="monotone" dataKey="mood" stroke="#6366f1" strokeWidth={3} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Recommendations */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Today's Recommendations
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {recommendations.slice(0, 3).map((rec, index) => (
                  <Box key={index}>
                    <Typography variant="subtitle2" fontWeight={600}>
                      {rec.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {rec.description}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button variant="contained" href="/mood">
                  Log Mood
                </Button>
                <Button variant="contained" href="/journal">
                  Write Journal
                </Button>
                <Button variant="outlined" href="/chat">
                  Chat with AI
                </Button>
                <Button variant="outlined" href="/resources">
                  View Resources
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Emergency Alert */}
        {riskAssessment?.risk_level === 'critical' && (
          <Grid item xs={12}>
            <Alert severity="error" sx={{ fontWeight: 600 }}>
              ⚠️ We're concerned about your well-being. Please reach out to a mental health professional or call the crisis hotline: 988
            </Alert>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}

export default Dashboard;


