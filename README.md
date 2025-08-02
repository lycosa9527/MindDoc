# MindDoc - Document Analysis & AI Assistant

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.1.1-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-v0.1-orange.svg)](https://github.com/lycosa9527/MindDoc/releases)

> **MindDoc** is a powerful Flask-based document analysis application that provides real-time AI-powered analysis and editing capabilities for Word documents. Built with modern web technologies and enhanced with natural language processing.

## 🌟 Features

### 📄 Document Processing
- **Smart Upload**: Drag-and-drop or click-to-upload .docx files
- **Real-time Analysis**: Instant paragraph-by-paragraph analysis
- **AI-Powered Insights**: Advanced NLP using spaCy for text analysis
- **Readability Scoring**: Automated readability metrics and suggestions

### ✏️ Live Editing
- **In-place Editing**: Click any paragraph to edit directly
- **Auto-save**: Changes are saved automatically as you type
- **Real-time Updates**: See suggestions update as you edit
- **Version Control**: Track changes and revert if needed

### 🤖 AI Integration
- **Dify API**: Advanced AI analysis and suggestions
- **spaCy NLP**: Professional-grade natural language processing
- **Smart Suggestions**: Context-aware writing improvements
- **Performance Metrics**: Detailed analysis of document quality

### 🎨 Modern Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Bootstrap 5**: Professional, clean UI components
- **Progress Tracking**: Real-time upload and processing status
- **Toast Notifications**: User-friendly feedback system

### 📊 Analytics & Insights
- **Word Count**: Detailed paragraph and document statistics
- **Readability Scores**: Multiple readability metrics
- **Writing Suggestions**: AI-powered improvement recommendations
- **Export Options**: Download analyzed documents with suggestions

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Git**
- **pip** (Python package manager)

### 1. Clone the Repository

```bash
git clone https://github.com/lycosa9527/MindDoc.git
cd MindDoc
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

### 4. Configure Environment

Copy the example environment file and configure your settings:

```bash
cp env.example .env
```

Edit `.env` with your configuration:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here-change-in-production

# Dify API Configuration (Optional)
DIFY_API_KEY=your-dify-api-key-here
DIFY_API_URL=https://api.dify.ai/v1

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216

# Logging Configuration
LOG_LEVEL=INFO
```

### 5. Test the Setup

Run the comprehensive test suite:

```bash
python test_app.py
```

### 6. Launch the Application

```bash
python run.py
```

The application will be available at **http://localhost:5000**

## 📖 Usage Guide

### Uploading Documents

1. **Select File**: Click "Choose File" or drag-and-drop a .docx file
2. **Upload**: Click "Upload & Analyze" to start processing
3. **Monitor Progress**: Watch the progress bar for real-time status
4. **View Results**: See analysis results and suggestions

### Editing Documents

1. **Click to Edit**: Click on any paragraph to enter edit mode
2. **Make Changes**: Type your modifications directly
3. **Auto-save**: Changes are saved automatically
4. **View Suggestions**: See AI-powered improvement tips

### Downloading Results

1. **Process Complete**: Wait for analysis to finish
2. **Download**: Click "Download Updated Document"
3. **Get Enhanced File**: Receive document with all suggestions included

## 🏗️ Architecture

### Technology Stack

- **Backend**: Flask 3.1.1 (Python web framework)
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **NLP**: spaCy 3.8.7 (Natural Language Processing)
- **AI**: Dify API integration
- **Analysis**: textstat 0.7.8 (Text statistics)
- **Document Processing**: python-docx 1.2.0

### Project Structure

```
MindDoc/
├── app/                          # Flask application
│   ├── __init__.py              # App factory
│   ├── config.py                # Configuration
│   ├── routes/                  # API endpoints
│   │   ├── upload.py           # File upload
│   │   ├── analysis.py         # Main page
│   │   ├── status.py           # Status API
│   │   └── api.py              # Real-time API
│   ├── services/               # Business logic
│   │   ├── debug_logger.py     # Logging system
│   │   ├── document_processor.py # Document analysis
│   │   ├── dify_service.py     # AI integration
│   │   └── event_manager.py    # Background tasks
│   ├── static/                 # Frontend assets
│   │   ├── css/style.css      # Custom styles
│   │   └── js/                # JavaScript
│   │       ├── document-viewer.js
│   │       └── upload.js
│   └── templates/              # HTML templates
│       └── index.html         # Main page
├── logs/                       # Application logs
├── requirements.txt            # Python dependencies
├── run.py                     # Application entry point
├── test_app.py                # Test suite
└── README.md                  # This file
```

## 🔧 Development

### Running Tests

```bash
# Run application tests
python test_app.py

# Test routes (requires running app)
python test_routes.py

# View logs
python view_logs.py
```

### Logging

The application includes a comprehensive logging system:

```bash
# View recent logs
python view_logs.py

# View log statistics
python view_logs.py stats

# Clear logs
python view_logs.py clear
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `dev-secret-key` |
| `DIFY_API_KEY` | Dify API key | `None` |
| `DIFY_API_URL` | Dify API URL | `https://api.dify.ai/v1` |
| `MAX_CONTENT_LENGTH` | Max file size (bytes) | `16777216` (16MB) |
| `LOG_LEVEL` | Logging level | `INFO` |

## 📊 Features in Detail

### Document Analysis

- **Paragraph Analysis**: Individual paragraph statistics
- **Word Count**: Detailed word and character counts
- **Readability Metrics**: Multiple readability scores
- **Writing Quality**: AI-powered quality assessment

### Real-time Processing

- **Background Tasks**: Non-blocking document processing
- **Progress Tracking**: Real-time status updates
- **Error Handling**: Robust error management
- **Performance Monitoring**: Detailed performance metrics

### AI Integration

- **Dify API**: Advanced AI analysis capabilities
- **spaCy NLP**: Professional natural language processing
- **Smart Suggestions**: Context-aware writing improvements
- **Quality Metrics**: Comprehensive document quality assessment

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Author**: [lycosa9527](https://github.com/lycosa9527)
- **Team**: MindSpring Team
- **Version**: v0.1

## 🙏 Acknowledgments

- **Flask** - The web framework for Python
- **spaCy** - Industrial-strength Natural Language Processing
- **Bootstrap** - Frontend framework for responsive design
- **Dify** - AI platform for advanced analysis
- **python-docx** - Python library for Word document processing

## 📞 Support

If you encounter any issues or have questions:

1. **Check** the [Issues](https://github.com/lycosa9527/MindDoc/issues) page
2. **Create** a new issue with detailed information
3. **Include** error messages and system information

## 🔮 Roadmap

- [ ] **v0.2**: Enhanced AI analysis features
- [ ] **v0.3**: Multi-language support
- [ ] **v0.4**: Advanced export options
- [ ] **v1.0**: Production-ready release

---

**Made with ❤️ by the MindSpring Team**

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue.svg)](https://github.com/lycosa9527/MindDoc)
[![Issues](https://img.shields.io/badge/Issues-Welcome-green.svg)](https://github.com/lycosa9527/MindDoc/issues)
[![Stars](https://img.shields.io/badge/Stars-Welcome-yellow.svg)](https://github.com/lycosa9527/MindDoc/stargazers) 