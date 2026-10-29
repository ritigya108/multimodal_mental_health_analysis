import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Avatar,
  Divider,
  Switch,
  FormControlLabel,
  Alert,
  Snackbar,
  IconButton,
  Chip,
} from '@mui/material';
import {
  Person as PersonIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Cake as BirthdayIcon,
  ContactEmergency as EmergencyIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';

function Profile() {
  const [editMode, setEditMode] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  
  const [profile, setProfile] = useState({
    name: 'John Doe',
    email: 'john.doe@example.com',
    phone: '+1 (555) 123-4567',
    age: 28,
    emergencyContact: 'Jane Doe - +1 (555) 987-6543',
    bio: 'Working on improving my mental health one day at a time.',
  });

  const [settings, setSettings] = useState({
    emailNotifications: true,
    dailyReminders: true,
    weeklyReports: false,
    crisisAlerts: true,
  });

  const [stats] = useState({
    joinDate: 'January 2024',
    totalMoodLogs: 45,
    totalJournalEntries: 23,
    currentStreak: 7,
    longestStreak: 14,
  });

  const handleSave = () => {
    // Save profile changes
    setEditMode(false);
    setSnackbar({
      open: true,
      message: 'Profile updated successfully!',
      severity: 'success',
    });
  };

  const handleCancel = () => {
    setEditMode(false);
    // Reset changes if needed
  };

  const handleSettingChange = (setting) => {
    setSettings({
      ...settings,
      [setting]: !settings[setting],
    });
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 700 }}>
        My Profile ðŸ‘¤
      </Typography>

      <Grid container spacing={3}>
        {/* Profile Card */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Avatar
                sx={{
                  width: 120,
                  height: 120,
                  margin: '0 auto',
                  mb: 2,
                  bgcolor: 'primary.main',
                  fontSize: '3rem',
                }}
              >
                {profile.name.charAt(0)}
              </Avatar>
              
              {editMode ? (
                <TextField
                  fullWidth
                  value={profile.name}
                  onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                  sx={{ mb: 1 }}
                />
              ) : (
                <Typography variant="h5" fontWeight={600} sx={{ mb: 1 }}>
                  {profile.name}
                </Typography>
              )}

              {editMode ? (
                <TextField
                  fullWidth
                  value={profile.email}
                  onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                  sx={{ mb: 2 }}
                />
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {profile.email}
                </Typography>
              )}

              {!editMode && (
                <Button
                  variant="outlined"
                  startIcon={<EditIcon />}
                  onClick={() => setEditMode(true)}
                  fullWidth
                >
                  Edit Profile
                </Button>
              )}

              {editMode && (
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="contained"
                    startIcon={<SaveIcon />}
                    onClick={handleSave}
                    fullWidth
                  >
                    Save
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<CancelIcon />}
                    onClick={handleCancel}
                    fullWidth
                  >
                    Cancel
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>

          {/* Stats Card */}
          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                ðŸ“Š Your Stats
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">
                    Member Since
                  </Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {stats.joinDate}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">
                    Mood Logs
                  </Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {stats.totalMoodLogs}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">
                    Journal Entries
                  </Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {stats.totalJournalEntries}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">
                    Current Streak
                  </Typography>
                  <Chip label={`${stats.currentStreak} days ðŸ”¥`} size="small" color="primary" />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="text.secondary">
                    Longest Streak
                  </Typography>
                  <Chip label={`${stats.longestStreak} days ðŸ†`} size="small" color="success" />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Details and Settings */}
        <Grid item xs={12} md={8}>
          {/* Personal Information */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" fontWeight={600} sx={{ mb: 3 }}>
                Personal Information
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <EmailIcon color="primary" fontSize="small" />
                    <Typography variant="subtitle2" fontWeight={600}>
                      Email
                    </Typography>
                  </Box>
                  {editMode ? (
                    <TextField
                      fullWidth
                      value={profile.email}
                      onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                      size="small"
                    />
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      {profile.email}
                    </Typography>
                  )}
                </Grid>

                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <PhoneIcon color="primary" fontSize="small" />
                    <Typography variant="subtitle2" fontWeight={600}>
                      Phone
                    </Typography>
                  </Box>
                  {editMode ? (
                    <TextField
                      fullWidth
                      value={profile.phone}
                      onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                      size="small"
                    />
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      {profile.phone}
                    </Typography>
                  )}
                </Grid>

                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <BirthdayIcon color="primary" fontSize="small" />
                    <Typography variant="subtitle2" fontWeight={600}>
                      Age
                    </Typography>
                  </Box>
                  {editMode ? (
                    <TextField
                      fullWidth
                      type="number"
                      value={profile.age}
                      onChange={(e) => setProfile({ ...profile, age: e.target.value })}
                      size="small"
                    />
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      {profile.age} years old
                    </Typography>
                  )}
                </Grid>

                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <EmergencyIcon color="error" fontSize="small" />
                    <Typography variant="subtitle2" fontWeight={600}>
                      Emergency Contact
                    </Typography>
                  </Box>
                  {editMode ? (
                    <TextField
                      fullWidth
                      value={profile.emergencyContact}
                      onChange={(e) => setProfile({ ...profile, emergencyContact: e.target.value })}
                      size="small"
                    />
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      {profile.emergencyContact}
                    </Typography>
                  )}
                </Grid>

                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <PersonIcon color="primary" fontSize="small" />
                    <Typography variant="subtitle2" fontWeight={600}>
                      Bio
                    </Typography>
                  </Box>
                  {editMode ? (
                    <TextField
                      fullWidth
                      multiline
                      rows={3}
                      value={profile.bio}
                      onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                    />
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      {profile.bio}
                    </Typography>
                  )}
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Notification Settings */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <NotificationsIcon color="primary" />
                <Typography variant="h6" fontWeight={600}>
                  Notification Settings
                </Typography>
              </Box>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.emailNotifications}
                      onChange={() => handleSettingChange('emailNotifications')}
                    />
                  }
                  label={
                    <Box>
                      <Typography variant="body2" fontWeight={600}>
                        Email Notifications
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Receive updates and insights via email
                      </Typography>
                    </Box>
                  }
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.dailyReminders}
                      onChange={() => handleSettingChange('dailyReminders')}
                    />
                  }
                  label={
                    <Box>
                      <Typography variant="body2" fontWeight={600}>
                        Daily Check-in Reminders
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Get reminded to log your mood daily
                      </Typography>
                    </Box>
                  }
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.weeklyReports}
                      onChange={() => handleSettingChange('weeklyReports')}
                    />
                  }
                  label={
                    <Box>
                      <Typography variant="body2" fontWeight={600}>
                        Weekly Progress Reports
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Receive weekly summaries of your mental health
                      </Typography>
                    </Box>
                  }
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.crisisAlerts}
                      onChange={() => handleSettingChange('crisisAlerts')}
                      color="error"
                    />
                  }
                  label={
                    <Box>
                      <Typography variant="body2" fontWeight={600}>
                        Crisis Alerts
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Receive immediate support when concerning patterns are detected
                      </Typography>
                    </Box>
                  }
                />
              </Box>
            </CardContent>
          </Card>

          {/* Security */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                <SecurityIcon color="primary" />
                <Typography variant="h6" fontWeight={600}>
                  Security
                </Typography>
              </Box>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button variant="outlined" fullWidth sx={{ justifyContent: 'flex-start' }}>
                  Change Password
                </Button>
                <Button variant="outlined" fullWidth sx={{ justifyContent: 'flex-start' }}>
                  Two-Factor Authentication
                </Button>
                <Button variant="outlined" fullWidth sx={{ justifyContent: 'flex-start' }}>
                  Download My Data
                </Button>
              </Box>
            </CardContent>
          </Card>

          {/* Danger Zone */}
          <Card sx={{ border: 2, borderColor: 'error.main' }}>
            <CardContent>
              <Typography variant="h6" fontWeight={600} color="error" sx={{ mb: 2 }}>
                Danger Zone
              </Typography>
              <Alert severity="warning" sx={{ mb: 2 }}>
                These actions are permanent and cannot be undone.
              </Alert>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<DeleteIcon />}
                  fullWidth
                  sx={{ justifyContent: 'flex-start' }}
                >
                  Delete All Journal Entries
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<DeleteIcon />}
                  fullWidth
                  sx={{ justifyContent: 'flex-start' }}
                >
                  Delete Account
                </Button>
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

export default Profile;
