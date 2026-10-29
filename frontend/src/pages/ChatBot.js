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
  Divider,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  RefreshOutlined as RefreshIcon,
} from '@mui/icons-material';
import apiService from '../services/api';

const HELPLINE_NUMBER = '14416';
const HELPLINE_NAME   = 'Tele-MANAS';

// â”€â”€ Local fallback â€” response pools with round-robin rotation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
const LOCAL_POOLS = {
  crisis: [
    `I'm very concerned about what you're sharing. Please reach out for help right now. ${HELPLINE_NAME}: ${HELPLINE_NUMBER} (free, 24/7). You are not alone.`,
    `What you're sharing worries me deeply. Please call ${HELPLINE_NAME} ${HELPLINE_NUMBER} right now â€” it's free and available 24/7. Is there someone physically near you right now?`,
    `Your safety matters most. Please reach out: ${HELPLINE_NAME} ${HELPLINE_NUMBER} (free, 24/7). If you feel unsafe, go to the nearest hospital emergency department.`,
  ],
  hopeless: [
    "It sounds like you're carrying a very heavy weight right now. Those feelings are real, but they can change with the right support. Have you been able to talk to anyone â€” a friend, family member, or counsellor?",
    "Feeling hopeless is one of the most exhausting experiences. You reached out here, and that matters. What has felt most unbearable recently?",
    "When everything feels pointless, it's a signal you need more support â€” not a reflection of who you are. Have you spoken to a doctor or mental health professional about how you've been feeling?",
  ],
  anxiety: [
    "Anxiety can feel overwhelming, but your body is safe even when your mind says otherwise. Try box breathing: inhale 4 counts, hold 4, exhale 4. Repeat 3 times. What's been triggering it?",
    "When anxiety spikes, your nervous system is in overdrive. A quick reset: plant both feet flat on the floor, name 5 things you can see, then take one slow breath. How long have you been feeling this way?",
    "Anxiety often comes with a specific trigger, even when it feels general. What's the one thought or situation that keeps coming back to your mind?",
    "It's exhausting to feel anxious all the time. Have you tried the 5-4-3-2-1 grounding method? (5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste.) It can interrupt the spiral quickly.",
  ],
  stress: [
    "Stress is your mind's signal that something needs attention â€” you're not weak for feeling it. Try writing down the one thing bothering you most. What's weighing on you the most?",
    "When everything piles up, pick the single smallest task you can finish in 10 minutes and do just that one thing. Sometimes one small win shifts the whole feeling. What's on your plate right now?",
    "Chronic stress takes a real physical toll. Have you had any moments to rest or step away lately, even briefly?",
    "Stress often comes from feeling out of control. What's one thing in your current situation that you actually have some control over?",
  ],
  depression: [
    "I'm sorry you're feeling this way. Depression is a real condition, not a weakness. If this has lasted more than two weeks, please consider speaking to a doctor. What has been hardest for you day to day?",
    "Depression can make even small things feel impossible. Is there one tiny thing â€” even just drinking a glass of water â€” that you might be able to do today?",
    "You don't have to carry this alone. Have you spoken to anyone about how you've been feeling â€” a friend, a family member, or a professional?",
    "Sometimes depression tells us nothing will change. But that's the illness talking, not the truth. What did life feel like before this started?",
  ],
  loneliness: [
    "Feeling lonely is painful â€” and more common than people admit. Is there one person you could send a simple message to today? Connection doesn't have to be deep to be meaningful.",
    "Loneliness can feel invisible because people around you might not know you're struggling. Have you been able to tell anyone how isolated you've been feeling?",
    "Sometimes loneliness is about the quality of connection, not just the quantity. Is there someone you used to feel close to that you've drifted from?",
  ],
  sleep: [
    "Poor sleep and low mood are closely linked. Try this tonight: no screens 30 minutes before bed, keep the room dark, and do 4-7-8 breathing (inhale 4, hold 7, exhale 8). How long has sleep been difficult?",
    "Sleep problems are one of the earliest signs that something needs attention mentally. Are you struggling to fall asleep, staying asleep, or waking too early?",
    "A consistent wind-down routine makes a real difference â€” even just 15 minutes of the same calm activity each night. What does your evening usually look like?",
  ],
  positive: [
    "That's genuinely great to hear. Positive moments are worth pausing on. What's been going well for you?",
    "It's really good to hear you're doing well. What do you think has made the biggest difference lately?",
    "Hold onto that feeling â€” and consider writing it down. Noting what went well each day builds resilience for harder times. What's made today good?",
  ],
  mindfulness: [
    "Mindfulness is one of the most evidence-backed tools for mental wellbeing. Here's a 1-minute grounding exercise: name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste. Would you like more?",
    "A simple start: set a timer for 5 minutes, sit comfortably, and just notice your breath. When your mind wanders â€” gently bring it back without judging yourself. Have you tried this before?",
    "Body scan meditation is great for releasing physical tension. Starting from the top of your head, slowly move your attention downward, just noticing any tightness. Would you like a step-by-step guide?",
  ],
  coping: [
    "Here are 5 evidence-based coping strategies:\n1. Box breathing (inhale 4s â†’ hold 4s â†’ exhale 4s)\n2. A 10-minute walk â€” it shifts brain chemistry\n3. Journaling â€” write 3 sentences about how you feel\n4. Grounding â€” name 5 things you can see\n5. Reach out â€” send one message to someone you trust\n\nWhich would you like to explore more?",
    "When overwhelmed, the most effective tools are physical: cold water on your face, a brisk walk, or slow deep breathing. These directly calm the nervous system. What have you tried before that helped, even a little?",
    "Long-term coping is about small consistent habits, not big dramatic changes. What does your current daily routine look like?",
  ],
  default: [
    "Thank you for sharing that with me. I'm here to listen without judgment. Can you tell me more about how you've been feeling?",
    "I hear you. Can you say more about what's been going on?",
    "That sounds like it's been weighing on you. What's been the hardest part of what you're going through?",
    "I want to make sure I understand what you're experiencing. How long have you been feeling this way?",
    "Thank you for trusting me with this. Is this something that came on recently, or has it been building for a while?",
  ],
};

// Per-category call counters (resets on page refresh â€” fine for a session)
const _localCounters = {};
function _localPick(category) {
  const pool = LOCAL_POOLS[category];
  const idx = _localCounters[category] || 0;
  _localCounters[category] = idx + 1;
  return pool[idx % pool.length];
}

function localResponse(message) {
  const m = message.toLowerCase();
  if (['suicide', 'kill myself', 'end my life', 'want to die', 'harm myself'].some(kw => m.includes(kw)))
    return _localPick('crisis');
  if (['hopeless', 'worthless', "can't go on", 'give up', 'unbearable', 'no point'].some(kw => m.includes(kw)))
    return _localPick('hopeless');
  if (['anxious', 'anxiety', 'panic', 'worried', 'fear', 'nervous'].some(kw => m.includes(kw)))
    return _localPick('anxiety');
  if (['stress', 'stressed', 'overwhelmed', 'pressure', 'burnout'].some(kw => m.includes(kw)))
    return _localPick('stress');
  if (['depressed', 'depression', 'sad', 'unhappy', 'miserable', 'empty', 'numb'].some(kw => m.includes(kw)))
    return _localPick('depression');
  if (['lonely', 'alone', 'isolated', 'no one cares', 'nobody'].some(kw => m.includes(kw)))
    return _localPick('loneliness');
  if (["can't sleep", 'insomnia', 'tired', 'exhausted', 'no energy', 'fatigue', 'sleep'].some(kw => m.includes(kw)))
    return _localPick('sleep');
  if (['happy', 'great', 'wonderful', 'grateful', 'better', 'good day', 'excited'].some(kw => m.includes(kw)))
    return _localPick('positive');
  if (['mindful', 'meditation', 'calm', 'breathe', 'breathing', 'relax'].some(kw => m.includes(kw)))
    return _localPick('mindfulness');
  if (['coping', 'strategies', 'help me', 'tips', 'advice', 'what should i do'].some(kw => m.includes(kw)))
    return _localPick('coping');
  return _localPick('default');
}

const QUICK_PROMPTS = [
  "I'm feeling anxious",
  "I need someone to talk to",
  "I'm feeling stressed",
  "I'm having a good day",
  "I need coping strategies",
  "Tell me about mindfulness",
];

const INITIAL_MESSAGE = {
  id: 0,
  text: "Hello. I'm here to listen and support you. How are you feeling today?",
  sender: 'bot',
  timestamp: new Date(),
};

function MessageBubble({ message }) {
  const isUser = message.sender === 'user';
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
        gap: 1,
        alignItems: 'flex-end',
      }}
    >
      {!isUser && (
        <Avatar
          sx={{ width: 32, height: 32, bgcolor: 'primary.main', flexShrink: 0, mb: 0.5 }}
          aria-hidden="true"
        >
          <BotIcon sx={{ fontSize: 18 }} />
        </Avatar>
      )}
      <Box sx={{ maxWidth: '72%' }}>
        <Paper
          elevation={0}
          sx={{
            px: 2,
            py: 1.25,
            backgroundColor: isUser ? 'primary.main' : 'background.paper',
            color: isUser ? 'white' : 'text.primary',
            border: isUser ? 'none' : '1px solid',
            borderColor: 'divider',
            borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
          }}
        >
          <Typography
            variant="body2"
            sx={{ lineHeight: 1.65, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}
          >
            {message.text}
          </Typography>
        </Paper>
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ display: 'block', mt: 0.25, px: 0.5,
                textAlign: isUser ? 'right' : 'left' }}
        >
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Typography>
      </Box>
      {isUser && (
        <Avatar
          sx={{ width: 32, height: 32, bgcolor: 'secondary.main', flexShrink: 0, mb: 0.5 }}
          aria-hidden="true"
        >
          <PersonIcon sx={{ fontSize: 18 }} />
        </Avatar>
      )}
    </Box>
  );
}

function TypingIndicator() {
  return (
    <Box sx={{ display: 'flex', alignItems: 'flex-end', gap: 1, mb: 2 }}>
      <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main', flexShrink: 0 }}>
        <BotIcon sx={{ fontSize: 18 }} />
      </Avatar>
      <Paper
        elevation={0}
        sx={{ px: 2, py: 1.25, border: '1px solid', borderColor: 'divider',
              borderRadius: '18px 18px 18px 4px' }}
        aria-live="polite"
        aria-label="Assistant is typing"
      >
        <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center', height: 18 }}>
          {[0, 1, 2].map(i => (
            <Box
              key={i}
              sx={{
                width: 7, height: 7, borderRadius: '50%',
                backgroundColor: 'text.secondary',
                animation: 'bounce 1.2s infinite',
                animationDelay: `${i * 0.2}s`,
                '@keyframes bounce': {
                  '0%, 80%, 100%': { transform: 'translateY(0)' },
                  '40%': { transform: 'translateY(-5px)' },
                },
              }}
            />
          ))}
        </Box>
      </Paper>
    </Box>
  );
}

function ChatBot() {
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const userId = 'user123';

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const sendMessage = async (text) => {
    const trimmed = text.trim();
    if (!trimmed || isTyping) return;

    // Append user message immediately
    setMessages(prev => [...prev, {
      id: Date.now(),
      text: trimmed,
      sender: 'user',
      timestamp: new Date(),
    }]);
    setInputMessage('');
    setIsTyping(true);

    // Compute local fallback while waiting for API
    let botText = localResponse(trimmed);

    try {
      // POST /api/chat?message=...&user_id=...
      const res = await apiService.sendChatMessage(trimmed, userId);
      if (res?.bot_response) botText = res.bot_response;
    } catch {
      // Backend offline â€” fall through to local response
    }

    setTimeout(() => {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        text: botText,
        sender: 'bot',
        timestamp: new Date(),
      }]);
      setIsTyping(false);
      // Re-focus input after reply
      setTimeout(() => inputRef.current?.focus(), 50);
    }, 700);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputMessage);
    }
  };

  const handleReset = () => {
    setMessages([{ ...INITIAL_MESSAGE, timestamp: new Date() }]);
    setInputMessage('');
    setIsTyping(false);
    inputRef.current?.focus();
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 80px)', maxHeight: 820 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>AI Chat</Typography>
          <Typography variant="body2" color="text.secondary">
            Supportive conversation â€” not a substitute for professional care
          </Typography>
        </Box>
        <Button
          variant="outlined"
          size="small"
          startIcon={<RefreshIcon />}
          onClick={handleReset}
          aria-label="Start new conversation"
        >
          New conversation
        </Button>
      </Box>

      {/* Disclaimer */}
      <Alert severity="info" sx={{ mb: 2, py: 0.75 }}>
        <Typography variant="caption">
          This chat is for emotional support only â€” not clinical advice.
          If you are in crisis, call <strong>{HELPLINE_NAME} {HELPLINE_NUMBER}</strong> (free, 24/7).
        </Typography>
      </Alert>

      {/* Chat window */}
      <Card
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          minHeight: 0,
        }}
      >
        {/* Message list */}
        <Box
          role="log"
          aria-label="Conversation"
          aria-live="polite"
          sx={{
            flex: 1,
            overflowY: 'auto',
            p: 2.5,
            backgroundColor: 'background.default',
          }}
        >
          {messages.map(msg => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
          {isTyping && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </Box>

        {/* Quick prompts */}
        <Box
          sx={{
            px: 2.5, py: 1.25,
            borderTop: '1px solid',
            borderColor: 'divider',
            backgroundColor: 'background.paper',
          }}
        >
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.75 }}>
            Quick prompts
          </Typography>
          <Box sx={{ display: 'flex', gap: 0.75, flexWrap: 'wrap' }}>
            {QUICK_PROMPTS.map(prompt => (
              <Chip
                key={prompt}
                label={prompt}
                size="small"
                variant="outlined"
                onClick={() => sendMessage(prompt)}
                disabled={isTyping}
                sx={{ cursor: 'pointer', fontSize: '0.72rem' }}
                aria-label={`Send: ${prompt}`}
              />
            ))}
          </Box>
        </Box>

        {/* Input bar */}
        <CardContent
          sx={{
            borderTop: '1px solid',
            borderColor: 'divider',
            py: '12px !important',
            px: 2.5,
          }}
        >
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
            <TextField
              inputRef={inputRef}
              fullWidth
              placeholder="Type a messageâ€¦"
              value={inputMessage}
              onChange={e => setInputMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              multiline
              maxRows={4}
              disabled={isTyping}
              size="small"
              aria-label="Message input"
              inputProps={{ 'aria-label': 'Type your message' }}
              sx={{
                '& .MuiOutlinedInput-root': { borderRadius: '12px' },
              }}
            />
            <IconButton
              onClick={() => sendMessage(inputMessage)}
              disabled={!inputMessage.trim() || isTyping}
              aria-label="Send message"
              sx={{
                bgcolor: 'primary.main',
                color: 'white',
                width: 40,
                height: 40,
                flexShrink: 0,
                '&:hover': { bgcolor: 'primary.dark' },
                '&.Mui-disabled': { bgcolor: 'action.disabledBackground' },
              }}
            >
              <SendIcon sx={{ fontSize: 18 }} />
            </IconButton>
          </Box>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.75 }}>
            Press Enter to send Â· Shift+Enter for new line
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}

export default ChatBot;
