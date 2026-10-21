import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  IconButton,
  Avatar,
  Paper,
  Chip,
  Button,
  Alert,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import apiService from '../services/api';

function ChatBot() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your AI mental health companion. I'm here to listen and support you. How are you feeling today?",
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const userId = 'user123';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const quickResponses = [
    "I'm feeling anxious",
    "I need someone to talk to",
    "I'm feeling stressed",
    "I'm having a good day",
    "I need coping strategies",
    "Tell me about mindfulness",
  ];

  const handleSendMessage = async (messageText = inputMessage) => {
    if (!messageText.trim()) return;

    // Add user message — use functional updater so ID is always correct
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        text: messageText,
        sender: 'user',
        timestamp: new Date(),
      },
    ]);
    setInputMessage('');
    setIsTyping(true);

    let botText = getBotResponse(messageText); // local fallback ready

    try {
      const response = await apiService.sendChatMessage(messageText, userId);
      if (response?.bot_response) botText = response.bot_response;
    } catch (error) {
      // backend offline — botText stays as local getBotResponse result
      console.warn('Chat API unreachable, using local response:', error.message);
    }

    // Small delay to simulate typing, then append bot reply
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          text: botText,
          sender: 'bot',
          timestamp: new Date(),
        },
      ]);
      setIsTyping(false);
    }, 900);
  };

  const getBotResponse = (userMessage) => {
    const lowerMessage = userMessage.toLowerCase();
    
    // Crisis keywords
    if (lowerMessage.includes('suicide') || lowerMessage.includes('kill myself') || lowerMessage.includes('end my life')) {
      return "I'm very concerned about what you're sharing. Please reach out to a crisis counselor immediately. You can call the National Suicide Prevention Lifeline at 988 (US) or text HOME to 741741. Your life matters, and help is available 24/7.";
    }
    
    // Anxiety
    if (lowerMessage.includes('anxious') || lowerMessage.includes('anxiety') || lowerMessage.includes('worried')) {
      return "I hear that you're feeling anxious. That's a very common feeling, and it's okay to feel this way. Try this: Take a deep breath in for 4 counts, hold for 4, and exhale for 4. Repeat this a few times. Would you like to talk about what's making you feel anxious?";
    }
    
    // Stress
    if (lowerMessage.includes('stress') || lowerMessage.includes('overwhelmed')) {
      return "Stress can feel overwhelming, but you're taking a positive step by acknowledging it. Here are some quick tips: 1) Take short breaks throughout your day, 2) Practice deep breathing, 3) Break tasks into smaller steps, 4) Talk to someone you trust. What's been causing you the most stress lately?";
    }
    
    // Depression
    if (lowerMessage.includes('depressed') || lowerMessage.includes('sad') || lowerMessage.includes('hopeless')) {
      return "I'm sorry you're feeling this way. Depression is a real condition, and you don't have to face it alone. It's important to talk to a mental health professional who can provide proper support. In the meantime, try to maintain a routine, get some sunlight, and reach out to loved ones. Would you like some resources for professional help?";
    }
    
    // Good day
    if (lowerMessage.includes('good') || lowerMessage.includes('great') || lowerMessage.includes('happy')) {
      return "That's wonderful to hear! I'm so glad you're having a good day. What's been going well for you? Celebrating positive moments is important for mental health.";
    }
    
    // Mindfulness
    if (lowerMessage.includes('mindfulness') || lowerMessage.includes('meditation')) {
      return "Mindfulness is a powerful tool for mental health! Here's a simple exercise: Find a quiet spot, close your eyes, and focus on your breathing. Notice the sensation of air entering and leaving your body. When your mind wanders (and it will!), gently bring your attention back to your breath. Start with just 5 minutes a day. Would you like more mindfulness techniques?";
    }
    
    // Coping strategies
    if (lowerMessage.includes('coping') || lowerMessage.includes('strategies') || lowerMessage.includes('help')) {
      return "Here are some effective coping strategies: 1) Deep breathing exercises, 2) Physical activity or stretching, 3) Journaling your thoughts, 4) Talking to someone you trust, 5) Engaging in a hobby you enjoy, 6) Progressive muscle relaxation. Which of these would you like to learn more about?";
    }
    
    // Default response
    return "Thank you for sharing that with me. I'm here to listen and support you. Can you tell me more about how you're feeling? Remember, if you're in crisis, please reach out to a professional counselor at 988 (US) or your local emergency services.";
  };

  const handleQuickResponse = (response) => {
    handleSendMessage(response);
  };

  const handleReset = () => {
    setMessages([
      {
        id: 1,
        text: "Hello! I'm your AI mental health companion. I'm here to listen and support you. How are you feeling today?",
        sender: 'bot',
        timestamp: new Date(),
      },
    ]);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>
          AI Mental Health Chat 💬
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={handleReset}
        >
          New Conversation
        </Button>
      </Box>

      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>Important:</strong> This AI chatbot is for support and information only. It's not a replacement for professional mental health care. 
          In case of emergency, call 988 (US) or your local crisis hotline.
        </Typography>
      </Alert>

      <Card sx={{ height: 'calc(100vh - 280px)', display: 'flex', flexDirection: 'column' }}>
        {/* Chat Messages */}
        <Box
          sx={{
            flexGrow: 1,
            overflowY: 'auto',
            p: 3,
            backgroundColor: 'background.default',
          }}
        >
          {messages.map((message) => (
            <Box
              key={message.id}
              sx={{
                display: 'flex',
                justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                mb: 2,
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: message.sender === 'user' ? 'row-reverse' : 'row',
                  alignItems: 'flex-start',
                  maxWidth: '70%',
                  gap: 1,
                }}
              >
                <Avatar
                  sx={{
                    bgcolor: message.sender === 'user' ? 'primary.main' : 'secondary.main',
                    width: 36,
                    height: 36,
                  }}
                >
                  {message.sender === 'user' ? <PersonIcon /> : <BotIcon />}
                </Avatar>
                <Paper
                  elevation={1}
                  sx={{
                    p: 2,
                    backgroundColor: message.sender === 'user' ? 'primary.main' : 'white',
                    color: message.sender === 'user' ? 'white' : 'text.primary',
                    borderRadius: 2,
                  }}
                >
                  <Typography variant="body1" sx={{ lineHeight: 1.6 }}>
                    {message.text}
                  </Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      display: 'block',
                      mt: 0.5,
                      opacity: 0.7,
                    }}
                  >
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </Typography>
                </Paper>
              </Box>
            </Box>
          ))}

          {isTyping && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Avatar sx={{ bgcolor: 'secondary.main', width: 36, height: 36 }}>
                <BotIcon />
              </Avatar>
              <Paper elevation={1} sx={{ p: 2, borderRadius: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  AI is typing...
                </Typography>
              </Paper>
            </Box>
          )}

          <div ref={messagesEndRef} />
        </Box>

        {/* Quick Responses */}
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider', backgroundColor: 'background.paper' }}>
          <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
            Quick responses:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {quickResponses.map((response, index) => (
              <Chip
                key={index}
                label={response}
                onClick={() => handleQuickResponse(response)}
                size="small"
                sx={{ cursor: 'pointer' }}
              />
            ))}
          </Box>
        </Box>

        {/* Message Input */}
        <CardContent sx={{ borderTop: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              placeholder="Type your message here..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              multiline
              maxRows={3}
              disabled={isTyping}
            />
            <IconButton
              color="primary"
              onClick={() => handleSendMessage()}
              disabled={!inputMessage.trim() || isTyping}
              sx={{
                backgroundColor: 'primary.main',
                color: 'white',
                '&:hover': {
                  backgroundColor: 'primary.dark',
                },
                '&:disabled': {
                  backgroundColor: 'action.disabledBackground',
                },
              }}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}

export default ChatBot;


