# Mental Health AI Monitoring - Backend

FastAPI-based backend for AI-powered mental health monitoring and support system.

## Features

-  User authentication and profile management
-  Mood tracking and visualization
- Journal entries with AI sentiment analysis
- AI-powered risk assessment
- Chatbot for mental health support
- Personalized recommendations
-  Crisis detection and alerts

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite (development) / PostgreSQL (production)
- **AI/ML**: 
  - Transformers (Hugging Face)
  - VADER Sentiment Analysis
  - TextBlob
  - scikit-learn
- **Authentication**: JWT tokens

## Setup Instructions

### 1. Create Virtual Environment

```bash
# Navigate to backend directory
cd mental-health-ai/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env file with your configuration
# nano .env  # or use any text editor
```

### 4. Initialize Database

```bash
# Run Python to initialize database
python -c "from database import init_db; init_db()"
```

### 5. Run the Server

```bash
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

API Documentation (Swagger UI): `http://localhost:8000/docs`

## API Endpoints

### Health & Status
- `GET /` - Root endpoint
- `GET /health` - Health check

### User Management
- `POST /api/users/register` - Register new user
- `GET /api/users/{user_id}` - Get user profile

### Mood Tracking
- `POST /api/mood/log` - Log mood entry
- `GET /api/mood/history/{user_id}` - Get mood history

### Journal
- `POST /api/journal/entry` - Create journal entry
- `GET /api/journal/entries/{user_id}` - Get journal entries

### AI Analysis
- `POST /api/analyze/sentiment` - Analyze text sentiment
- `GET /api/analyze/risk/{user_id}` - Assess mental health risk

### Recommendations
- `GET /api/recommendations/{user_id}` - Get personalized recommendations

### Chatbot
- `POST /api/chat` - Chat with AI assistant

## Project Structure

```
backend/
├── main.py              # FastAPI application and routes
├── models.py            # SQLAlchemy database models
├── database.py          # Database configuration
├── ai_analyzer.py       # AI/ML sentiment analysis
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file
```

## AI Models

The system uses multiple AI approaches for comprehensive analysis:

1. **VADER Sentiment**: Rule-based sentiment analysis, excellent for social media text
2. **TextBlob**: Pattern-based sentiment analysis with polarity and subjectivity
3. **Transformers**: Deep learning models for advanced sentiment understanding
4. **Custom Risk Assessment**: Multi-factor algorithm combining sentiment, mood trends, and crisis keywords

## Crisis Detection

The system includes crisis keyword detection for:
- High-risk indicators (immediate intervention needed)
- Medium-risk indicators (professional help recommended)
- Low-risk indicators (monitoring and self-care)

**Important**: This is a support tool, not a replacement for professional mental health care.

## Development

### Adding New Endpoints

1. Define Pydantic models in `main.py`
2. Create route handler function
3. Implement business logic
4. Add database operations if needed

### Testing

```bash
# Install pytest
pip install pytest pytest-asyncio httpx

# Run tests (when test files are created)
pytest
```

## Security Considerations

- Always use HTTPS in production
- Keep SECRET_KEY secure and unique
- Implement rate limiting
- Validate and sanitize all user inputs
- Follow HIPAA/GDPR compliance for health data
- Regular security audits

## Next Steps

1. ✅ Set up virtual environment
2. ✅ Install dependencies
3. ✅ Configure environment variables
4. ✅ Initialize database
5. ✅ Run the server
6. 🔄 Test API endpoints
7. 🔄 Integrate with frontend
8. 🔄 Add authentication
9. 🔄 Implement remaining features
10. 🔄 Deploy to production

## Support & Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Transformers: https://huggingface.co/docs/transformers
- Mental Health Resources: https://www.nami.org/

## License

This project is for educational and support purposes. Always consult with qualified mental health professionals for serious concerns.
