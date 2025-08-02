# MindDoc - Document Analysis PoC

A Flask-based proof of concept for analyzing Word documents with real-time editing capabilities.

## Features

- **Document Upload**: Upload .docx files for analysis
- **Real-time Analysis**: Analyze paragraphs for readability, word count, and writing suggestions
- **Live Editing**: Edit document content with auto-save functionality
- **AI Integration**: Uses spaCy for NLP and Dify API for advanced analysis
- **Professional UI**: Clean Bootstrap-based interface with progress tracking
- **Download Support**: Export analyzed documents with suggestions

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

### 3. Set Environment Variables

Copy `env.example` to `.env` and configure:

```bash
cp env.example .env
```

Edit `.env`:
```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here-change-in-production

# Dify API Configuration
DIFY_API_KEY=your-dify-api-key-here
DIFY_API_URL=https://api.dify.ai/v1

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216

# Logging Configuration
LOG_LEVEL=INFO
```

### 4. Test the Application

Run the test script to verify everything is set up correctly:

```bash
python test_app.py
```

### 5. Run the Application

```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Usage

1. **Upload Document**: Select a .docx file and click "Upload & Analyze"
2. **Monitor Progress**: Watch the progress bar as the document is analyzed
3. **Edit Content**: Click on any paragraph to edit it in real-time
4. **View Suggestions**: See AI-generated suggestions for each paragraph
5. **Download Results**: Export the analyzed document with all suggestions

## Project Structure

```
MindDoc/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration settings
│   ├── routes/              # Flask routes
│   │   ├── upload.py        # File upload handling
│   │   ├── analysis.py      # Main page route
│   │   ├── status.py        # Status checking
│   │   └── api.py           # Real-time API endpoints
│   ├── services/            # Business logic
│   │   ├── debug_logger.py  # Logging system
│   │   ├── document_processor.py  # Document analysis
│   │   ├── dify_service.py  # Dify API integration
│   │   └── event_manager.py # Background processing
│   ├── static/              # Frontend assets
│   │   ├── css/style.css    # Custom styles
│   │   └── js/              # JavaScript files
│   │       ├── document-viewer.js  # Real-time editing
│   │       └── upload.js    # Upload handling
│   └── templates/           # HTML templates
│       └── index.html       # Main page
├── logs/                    # Application logs
├── requirements.txt          # Python dependencies
├── run.py                   # Application entry point
├── test_app.py              # Test script
└── README.md               # This file
```

## Key Components

### Document Processing
- Uses `python-docx` for Word document parsing
- `spaCy` for natural language processing
- `textstat` for readability analysis
- Background processing with threading

### Real-time Features
- Auto-save functionality (2-second delay)
- Live paragraph editing
- Progress tracking
- Toast notifications

### UI/UX
- Bootstrap 5 for responsive design
- Font Awesome icons
- Professional styling
- Mobile-friendly layout

## Development

### Logging
Logs are stored in `logs/app.log` with console output for development.

### Debug Mode
The application runs in debug mode by default. Check `run.py` for configuration.

### Error Handling
Comprehensive error handling with user-friendly messages and logging.

### Testing
Run `python test_app.py` to verify:
- All imports work correctly
- Configuration is loaded properly
- Flask app can be created
- spaCy model is available

## Code Review Fixes Applied

### ✅ **Fixed Issues:**
1. **Environment Variables**: Added `python-dotenv` import and proper loading
2. **Configuration**: Updated app to use Config class instead of hardcoded values
3. **Error Handling**: Added comprehensive try-catch blocks throughout
4. **Type Safety**: Fixed paragraph_id type conversion in API routes
5. **Directory Creation**: Ensured upload directory exists before saving files
6. **API Key Validation**: Added proper validation for Dify API key
7. **spaCy Model**: Added error handling for missing spaCy model
8. **Network Errors**: Added specific handling for API timeouts and network issues

### ✅ **Security Improvements:**
- Proper environment variable validation
- Secure file upload handling
- Input validation and sanitization
- Error message sanitization

### ✅ **Reliability Improvements:**
- Graceful degradation when spaCy model is missing
- Fallback analysis when NLP features fail
- Better error messages and logging
- Configuration validation on startup

## Future Enhancements

- Database integration (PostgreSQL)
- Redis caching
- Docker containerization
- Advanced AI features
- User authentication
- Multi-language support

## Troubleshooting

### Common Issues

1. **spaCy model not found**: Run `python -m spacy download en_core_web_sm`
2. **Upload directory error**: The app will create the directory automatically
3. **Dify API errors**: Check your API key and URL in `.env`
4. **Import errors**: Run `python test_app.py` to diagnose issues

### Logs
Check `logs/app.log` for detailed error information.

## License

This is a proof of concept application for educational purposes. 