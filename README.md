# 🤖 AI Mobile Testing Agent

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![React](https://img.shields.io/badge/React-18+-61DAFB.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Automated Android App Testing Powered by Generative AI**

[Features](#features) • [Architecture](#architecture) • [Installation](#installation) • [Usage](#usage) • [API Reference](#api-reference)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Testing Modes](#testing-modes)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

The **AI Mobile Testing Agent** is an intelligent automation framework that leverages Google Gemini AI to perform comprehensive testing of Android applications. It combines traditional mobile testing techniques with generative AI to explore apps, identify issues, and generate detailed test reports.

### What Makes It Different?

- 🧠 **AI-Driven Testing**: Uses Google Gemini to make intelligent decisions about what to test
- 🔄 **Adaptive Exploration**: Learns app structure and adapts testing strategy in real-time
- 📊 **Rich Reporting**: Generates detailed HTML reports with screenshots and AI insights
- 🎨 **Modern UI**: Beautiful React-based web interface for easy interaction
- 🚀 **Zero Configuration**: Works out of the box with Android emulators

---

## ✨ Features

### Core Capabilities

- ✅ **Automated APK Installation** - Upload and install APKs directly to emulator
- ✅ **AI-Powered UI Exploration** - Intelligent navigation through app screens
- ✅ **Smart Test Generation** - AI creates test scenarios based on app context
- ✅ **Visual Regression Testing** - Captures and analyzes screenshots
- ✅ **Login Flow Testing** - Handles authentication with provided credentials
- ✅ **Crash Detection** - Identifies and reports app crashes
- ✅ **Performance Monitoring** - Tracks app responsiveness and lag
- ✅ **Comprehensive Reports** - HTML reports with screenshots and insights

### Testing Modes

1. **Fully Automated** - AI handles all testing decisions
2. **Guided Testing** - Provide app context for targeted testing
3. **Custom Instructions** - Give specific AI prompts for custom test scenarios

---

## 🏗️ Architecture

```
┌─────────────────┐
│   React UI      │  ← User Interface
└────────┬────────┘
         │ HTTP/REST
┌────────▼────────┐
│  Flask API      │  ← Backend Server
└────────┬────────┘
         │
    ┌────┴────┬──────────┬─────────────┐
    │         │          │             │
┌───▼───┐ ┌──▼──┐ ┌─────▼─────┐ ┌────▼────┐
│Gemini │ │ ADB │ │  Appium   │ │ Report  │
│  AI   │ │     │ │           │ │Generator│
└───────┘ └─────┘ └───────────┘ └─────────┘
```

### Key Components

- **Frontend (React)**: Modern web UI for APK upload and test configuration
- **Backend (Flask)**: RESTful API server handling test orchestration
- **AI Agent (Gemini)**: Intelligent decision-making for test scenarios
- **Emulator Manager**: Controls Android Virtual Device
- **APK Installer**: Handles app installation via ADB
- **UI Explorer**: Interacts with app UI using Appium
- **Report Generator**: Creates detailed HTML test reports

---

## 🔧 Prerequisites

### System Requirements

- **OS**: Windows 10/11, macOS, or Linux
- **RAM**: 8GB minimum (16GB recommended)
- **Disk**: 10GB free space
- **Python**: 3.8 or higher
- **Node.js**: 16.x or higher (for frontend)

### Required Software

1. **Android Studio** with:
   - Android SDK
   - Android Emulator (AVD)
   - ADB (Android Debug Bridge)

2. **Java Development Kit (JDK)**
   - Version 11 or higher

3. **Appium** (installed globally)
   ```bash
   npm install -g appium
   ```

4. **Google Gemini API Key**
   - Get from: [Google AI Studio](https://makersuite.google.com/app/apikey)

---

## 📦 Installation

### 1. Clone Repository

```bash
git clone https://github.com/hasibnirjhar07/mobile-testing-agent-ai.git
cd mobile-testing-agent-ai
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### 4. Android Emulator Setup

```bash
# List available emulators
emulator -list-avds

# Start an emulator (replace with your AVD name)
emulator -avd Pixel_6_API_34 -no-snapshot-load &

# Verify connection
adb devices
```

---

## ⚙️ Configuration

### 1. Create Configuration File

Create `config/config.yaml`:

```yaml
adb:
  device_id: "emulator-5554"  # Your emulator ID

emulator:
  name: "Pixel_6_API_34"      # Your AVD name
  port: 5554
  wait_timeout: 120

testing:
  max_exploration_depth: 10
  max_clicks_per_screen: 5
  screenshot_delay: 2
  
appium:
  host: "localhost"
  port: 4723
  
report:
  output_dir: "reports"
  screenshot_dir: "screenshots"
  format: "html"

logging:
  level: "INFO"
  file: "testing_agent.log"
```

### 2. Set Environment Variables

Create `.env` file in root directory:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
FLASK_ENV=development
FLASK_DEBUG=1
```

### 3. Update Frontend Configuration

Edit `frontend/src/config.js` (if needed):

```javascript
export const API_BASE_URL = 'http://localhost:5000';
```

---

## 🚀 Usage

### Quick Start

1. **Start Backend API** (Terminal 2)
   ```bash
   python api_server.py
   ```

2. **Start Frontend** (Terminal 3)
   ```bash
   cd frontend
   npm start
   ```


### Step-by-Step Testing

#### Step 1: Upload APK
1. Click upload area or drag APK file
2. Wait for upload to complete
3. Session ID is automatically generated

#### Step 2: Configure Test
- **Select Testing Mode**:
  - Fully Automated: AI handles everything
  - Guided Testing: Provide app context
  - Custom Instructions: Specific AI prompts

- **Add Credentials** (if app requires login):
  - Username
  - Password
  - Email (optional)

- **Provide Context** (for guided/custom modes):
  - App description
  - Features to test
  - Expected behaviors

#### Step 3: Start Testing
1. Review configuration
2. Ensure emulator is running
3. Click "Start AI Testing"
4. Monitor progress in real-time

#### Step 4: View Results
- View test statistics
- Read AI insights
- Download HTML report
- View full report in browser

---

## 📡 API Reference

### Upload APK

```http
POST /api/upload
Content-Type: multipart/form-data

Body:
- file: APK file

Response:
{
  "success": true,
  "session_id": "uuid",
  "filename": "app.apk",
  "filepath": "uploads/uuid_app.apk"
}
```

### Start Test

```http
POST /api/test/start
Content-Type: application/json

Body:
{
  "session_id": "uuid",
  "test_mode": "auto|guided|custom",
  "credentials": {
    "hasLogin": true,
    "username": "user",
    "password": "pass",
    "email": "user@email.com"
  },
  "test_context": "Banking app testing",
  "ai_instructions": "Test login and transactions"
}

Response:
{
  "success": true,
  "session_id": "uuid",
  "message": "Test started successfully"
}
```

### Get Test Status

```http
GET /api/test/status/{session_id}

Response:
{
  "status": "running|completed|failed",
  "progress": 75,
  "message": "Testing in progress...",
  "results": { ... }
}
```

### Download Report

```http
GET /api/report/{session_id}

Response: HTML file download
```

### View Report

```http
GET /api/report/view/{session_id}

Response: HTML page
```

### List Sessions

```http
GET /api/sessions

Response:
{
  "sessions": [
    {
      "session_id": "uuid",
      "status": "completed",
      "progress": 100,
      "message": "Testing complete",
      "created_at": 1699123456
    }
  ]
}
```

---

## 📁 Project Structure

```
mobile-testing-agent-ai/
├── app/
│   ├── __init__.py
│   ├── ai_agent_core.py          # Gemini AI integration
│   ├── ai_test_executor.py       # AI-powered test execution
│   ├── apk_installer.py          # APK installation handler
│   ├── emulator_manager.py       # Emulator control
│   ├── report_generator.py       # HTML report generation
│   ├── test_executor.py          # Basic test executor
│   └── ui_explorer.py            # UI interaction via Appium
├── config/
│   └── config.yaml               # Main configuration
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── README.md
├── reports/                      # Generated test reports
├── screenshots/                  # Test screenshots
├── uploads/                      # Uploaded APK files
├── api_server.py                 # Flask backend server
├── main.py                       # CLI entry point
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables
├── .gitignore
└── README.md
```

---

## 🧪 Testing Modes

### 1. Fully Automated Mode

**Best for**: Quick exploratory testing

The AI agent:
- Automatically explores the entire app
- Identifies clickable elements
- Tests common user flows
- Detects crashes and errors
- No user input required

**Example Use Case**: Testing a new app before manual testing

### 2. Guided Testing Mode

**Best for**: Focused testing with context

Provide context like:
```
This is a social media app. Test user registration, 
profile creation, and posting functionality. 
Verify images load correctly.
```

The AI:
- Focuses on mentioned features
- Creates relevant test scenarios
- Validates expected behaviors

**Example Use Case**: Testing specific features after code changes

### 3. Custom Instructions Mode

**Best for**: Specific test scenarios

Provide detailed instructions:
```
1. Test login with invalid credentials - verify error message
2. Test password reset flow
3. Attempt SQL injection in login form
4. Test app behavior with airplane mode
5. Capture screenshots at each step
```

The AI:
- Follows specific instructions
- Documents each step
- Reports deviations from expected behavior

**Example Use Case**: Regression testing, security testing

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Emulator Not Detected

**Problem**: "No devices found" error

**Solution**:
```bash
# Check ADB connection
adb devices

# Restart ADB server
adb kill-server
adb start-server

# Check emulator is running
emulator -list-avds
```

#### 2. Appium Connection Failed

**Problem**: "Could not connect to Appium server"

**Solution**:
```bash
# Ensure Appium is running
appium

# Check Appium status
curl http://localhost:4723/status
```

#### 3. APK Installation Failed

**Problem**: "Failed to install APK"

**Solution**:
- Verify APK is not corrupted
- Check sufficient storage on emulator
- Try: `adb install -r your_app.apk`
- Enable "Install from unknown sources" in emulator

#### 4. Frontend Can't Connect to Backend

**Problem**: CORS errors or connection refused

**Solution**:
```python
# In api_server.py, verify CORS settings
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "DELETE", "OPTIONS"],
    }
})
```

#### 5. Gemini API Errors

**Problem**: "Invalid API key" or rate limit errors

**Solution**:
- Verify API key in `.env` file
- Check quota at Google AI Studio
- Wait if rate limited (free tier has limits)

#### 6. Port Already in Use

**Problem**: "Port 5000 already in use"

**Solution**:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

---

## 🔍 Advanced Features

### Custom AI Prompts

Enhance AI behavior by editing `app/ai_agent_core.py`:

```python
def _get_system_prompt(self):
    return """
    You are an expert mobile app tester.
    Focus on:
    - User experience issues
    - Performance problems
    - Security vulnerabilities
    - Accessibility concerns
    """
```

### Parallel Testing

Run multiple tests simultaneously:

```python
# In api_server.py
app.config['MAX_WORKERS'] = 4  # Adjust based on system
```

### Custom Report Templates

Modify `app/report_generator.py` to customize HTML output.

---

## 📊 Performance Tips

### For Faster Testing

1. **Reduce Screenshot Delay**
   ```yaml
   testing:
     screenshot_delay: 1  # Instead of 2
   ```

2. **Limit Exploration Depth**
   ```yaml
   testing:
     max_exploration_depth: 5  # Instead of 10
   ```

3. **Use Faster Emulator**
   - Enable hardware acceleration
   - Use x86 system images
   - Allocate more RAM to emulator

### For Better Results

1. **Increase Exploration**
   ```yaml
   testing:
     max_exploration_depth: 15
     max_clicks_per_screen: 8
   ```

2. **Provide Detailed Context**
   - Describe app purpose
   - List critical features
   - Mention known issues

---

## 🤝 Contributing

We welcome contributions! Here's how:

### Report Bugs

Open an issue with:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- System information

### Submit Features

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Code Style

- Python: Follow PEP 8
- JavaScript: Use ESLint configuration
- Add docstrings to functions
- Write unit tests for new features

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Gemini** - For powerful AI capabilities
- **Appium** - Mobile automation framework
- **Flask** - Lightweight web framework
- **React** - Modern UI library
- **Loguru** - Beautiful logging

---

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/mobile-testing-agent-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mobile-testing-agent-ai/discussions)
- **Email**: support@example.com

---

## 🗺️ Roadmap

### Version 2.0 (Planned)

- [ ] iOS app testing support
- [ ] Cloud-based testing (AWS Device Farm, Firebase Test Lab)
- [ ] Visual regression testing with AI comparison
- [ ] Integration with CI/CD pipelines
- [ ] Multi-language support
- [ ] Test case management
- [ ] Performance benchmarking
- [ ] Accessibility testing automation
- [ ] API testing integration
- [ ] Team collaboration features

---

## 📈 Stats

![GitHub stars](https://img.shields.io/github/stars/yourusername/mobile-testing-agent-ai)
![GitHub forks](https://img.shields.io/github/forks/yourusername/mobile-testing-agent-ai)
![GitHub issues](https://img.shields.io/github/issues/yourusername/mobile-testing-agent-ai)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/mobile-testing-agent-ai)

---

<div align="center">

**Made with ❤️ by the AI Testing Team**

[⬆ Back to Top](#-ai-mobile-testing-agent)

</div>
