import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Chip,
  TextField,
  InputAdornment,
  Tabs,
  Tab,
  Link,
  Alert,
} from '@mui/material';
import {
  Phone as PhoneIcon,
  Article as ArticleIcon,
  VideoLibrary as VideoIcon,
  FitnessCenter as ExerciseIcon,
  Search as SearchIcon,
  OpenInNew as OpenIcon,
  LocalHospital as HospitalIcon,
  SelfImprovement as MeditationIcon,
} from '@mui/icons-material';

function Resources() {
  const [selectedTab, setSelectedTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');

  const crisisResources = [
    {
      title: 'National Suicide Prevention Lifeline',
      description: '24/7 free and confidential support for people in distress',
      contact: '988',
      type: 'phone',
      urgent: true,
    },
    {
      title: 'Crisis Text Line',
      description: 'Text-based crisis support available 24/7',
      contact: 'Text HOME to 741741',
      type: 'text',
      urgent: true,
    },
    {
      title: 'SAMHSA National Helpline',
      description: 'Treatment referral and information service',
      contact: '1-800-662-4357',
      type: 'phone',
      urgent: false,
    },
    {
      title: 'Veterans Crisis Line',
      description: 'Support for veterans and their families',
      contact: '988 then Press 1',
      type: 'phone',
      urgent: false,
    },
    {
      title: 'NAMI Helpline',
      description: 'Information, referrals and support',
      contact: '1-800-950-6264',
      type: 'phone',
      urgent: false,
    },
  ];

  const articles = [
    {
      title: 'Understanding Depression: Signs and Symptoms',
      description: 'Learn about the common signs of depression and when to seek help',
      category: 'Mental Health',
      readTime: '8 min',
      url: 'https://www.nimh.nih.gov/health/topics/depression',
    },
    {
      title: 'Anxiety Management Techniques',
      description: 'Practical strategies to manage anxiety in daily life',
      category: 'Coping Skills',
      readTime: '10 min',
      url: 'https://www.nami.org/About-Mental-Illness/Mental-Health-Conditions/Anxiety-Disorders',
    },
    {
      title: 'The Importance of Sleep for Mental Health',
      description: 'How sleep affects your mental well-being and tips for better sleep',
      category: 'Wellness',
      readTime: '6 min',
      url: 'https://www.sleepfoundation.org/mental-health',
    },
    {
      title: 'Building Resilience in Difficult Times',
      description: 'Develop skills to bounce back from challenges',
      category: 'Personal Growth',
      readTime: '12 min',
      url: 'https://www.apa.org/topics/resilience',
    },
    {
      title: 'Mindfulness and Meditation for Beginners',
      description: 'Start your mindfulness journey with these simple practices',
      category: 'Mindfulness',
      readTime: '7 min',
      url: 'https://www.mindful.org/meditation/mindfulness-getting-started/',
    },
  ];

  const videos = [
    {
      title: 'Guided Meditation for Anxiety Relief',
      description: '10-minute guided meditation to calm your mind',
      duration: '10:00',
      category: 'Meditation',
      url: 'https://www.youtube.com/watch?v=O-6f5wQXSu8',
    },
    {
      title: 'Understanding Mental Health',
      description: 'TED Talk on breaking the stigma around mental health',
      duration: '15:30',
      category: 'Education',
      url: 'https://www.ted.com/topics/mental+health',
    },
    {
      title: 'Breathing Exercises for Stress',
      description: 'Simple breathing techniques you can do anywhere',
      duration: '5:45',
      category: 'Wellness',
      url: 'https://www.youtube.com/results?search_query=breathing+exercises+stress',
    },
    {
      title: 'Yoga for Mental Health',
      description: 'Gentle yoga practice for emotional well-being',
      duration: '20:00',
      category: 'Exercise',
      url: 'https://www.youtube.com/results?search_query=yoga+mental+health',
    },
  ];

  const exercises = [
    {
      title: 'Progressive Muscle Relaxation',
      description: 'Systematically tense and relax muscle groups to reduce stress',
      duration: '15 min',
      difficulty: 'Beginner',
    },
    {
      title: '5-4-3-2-1 Grounding Technique',
      description: 'Use your senses to ground yourself in the present moment',
      duration: '5 min',
      difficulty: 'Beginner',
    },
    {
      title: 'Box Breathing',
      description: 'Breathe in a pattern to calm your nervous system',
      duration: '5 min',
      difficulty: 'Beginner',
    },
    {
      title: 'Body Scan Meditation',
      description: 'Bring awareness to different parts of your body',
      duration: '20 min',
      difficulty: 'Intermediate',
    },
    {
      title: 'Gratitude Journaling',
      description: 'Write down things you\'re grateful for each day',
      duration: '10 min',
      difficulty: 'Beginner',
    },
    {
      title: 'Mindful Walking',
      description: 'Practice mindfulness while walking outdoors',
      duration: '15 min',
      difficulty: 'Beginner',
    },
  ];

  const filteredContent = (items) => {
    if (!searchQuery) return items;
    return items.filter(item =>
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.toLowerCase())
    );
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 1, fontWeight: 700 }}>
        Mental Health Resources ðŸ“š
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Curated resources to support your mental health journey
      </Typography>

      {/* Emergency Alert */}
      <Alert severity="error" sx={{ mb: 3 }}>
        <Typography variant="subtitle2" fontWeight={600}>
          ðŸš¨ In Crisis? Get Help Now
        </Typography>
        <Typography variant="body2">
          If you're in immediate danger, call 911. For crisis support, call 988 (Suicide & Crisis Lifeline) or text HOME to 741741.
        </Typography>
      </Alert>

      {/* Search Bar */}
      <TextField
        fullWidth
        placeholder="Search resources..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        sx={{ mb: 3 }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
        }}
      />

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={selectedTab} onChange={(e, newValue) => setSelectedTab(newValue)}>
          <Tab icon={<PhoneIcon />} label="Crisis Hotlines" />
          <Tab icon={<ArticleIcon />} label="Articles" />
          <Tab icon={<VideoIcon />} label="Videos" />
          <Tab icon={<ExerciseIcon />} label="Exercises" />
        </Tabs>
      </Box>

      {/* Crisis Hotlines Tab */}
      {selectedTab === 0 && (
        <Grid container spacing={3}>
          {filteredContent(crisisResources).map((resource, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card sx={{ height: '100%', border: resource.urgent ? 2 : 0, borderColor: 'error.main' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <PhoneIcon color={resource.urgent ? 'error' : 'primary'} />
                      <Typography variant="h6" fontWeight={600}>
                        {resource.title}
                      </Typography>
                    </Box>
                    {resource.urgent && (
                      <Chip label="URGENT" color="error" size="small" />
                    )}
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {resource.description}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, p: 2, backgroundColor: 'primary.light', borderRadius: 1 }}>
                    <Typography variant="h6" sx={{ color: 'white', fontWeight: 700 }}>
                      {resource.contact}
                    </Typography>
                  </Box>
                  <Chip label={resource.type} size="small" sx={{ mt: 2 }} />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Articles Tab */}
      {selectedTab === 1 && (
        <Grid container spacing={3}>
          {filteredContent(articles).map((article, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <ArticleIcon color="primary" />
                    <Typography variant="h6" fontWeight={600}>
                      {article.title}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {article.description}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <Chip label={article.category} size="small" color="primary" variant="outlined" />
                    <Chip label={article.readTime} size="small" />
                  </Box>
                  <Button
                    variant="outlined"
                    endIcon={<OpenIcon />}
                    component={Link}
                    href={article.url}
                    target="_blank"
                    fullWidth
                  >
                    Read Article
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Videos Tab */}
      {selectedTab === 2 && (
        <Grid container spacing={3}>
          {filteredContent(videos).map((video, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <VideoIcon color="secondary" />
                    <Typography variant="h6" fontWeight={600}>
                      {video.title}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {video.description}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <Chip label={video.category} size="small" color="secondary" variant="outlined" />
                    <Chip label={video.duration} size="small" />
                  </Box>
                  <Button
                    variant="contained"
                    color="secondary"
                    endIcon={<OpenIcon />}
                    component={Link}
                    href={video.url}
                    target="_blank"
                    fullWidth
                  >
                    Watch Video
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Exercises Tab */}
      {selectedTab === 3 && (
        <Grid container spacing={3}>
          {filteredContent(exercises).map((exercise, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <MeditationIcon color="success" />
                    <Typography variant="h6" fontWeight={600}>
                      {exercise.title}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {exercise.description}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <Chip label={exercise.duration} size="small" />
                    <Chip
                      label={exercise.difficulty}
                      size="small"
                      color={exercise.difficulty === 'Beginner' ? 'success' : 'warning'}
                    />
                  </Box>
                  <Button variant="outlined" color="success" fullWidth>
                    Try Exercise
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Additional Resources */}
      <Card sx={{ mt: 4, backgroundColor: 'info.light' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <HospitalIcon sx={{ color: 'white' }} />
            <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
              Find Professional Help
            </Typography>
          </Box>
          <Typography variant="body2" sx={{ color: 'white', mb: 2 }}>
            These resources can help you find mental health professionals in your area:
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              sx={{ backgroundColor: 'white', color: 'info.main' }}
              component={Link}
              href="https://www.psychologytoday.com/us/therapists"
              target="_blank"
            >
              Psychology Today
            </Button>
            <Button
              variant="contained"
              sx={{ backgroundColor: 'white', color: 'info.main' }}
              component={Link}
              href="https://www.nami.org/findsupport"
              target="_blank"
            >
              NAMI Support
            </Button>
            <Button
              variant="contained"
              sx={{ backgroundColor: 'white', color: 'info.main' }}
              component={Link}
              href="https://www.samhsa.gov/find-help/national-helpline"
              target="_blank"
            >
              SAMHSA
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}

export default Resources;
