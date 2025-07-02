# LinkedIn Job Hunter

A powerful LinkedIn job search automation tool built with FastMCP, Playwright, and React. Automate your job search process by finding, applying to, and tracking jobs on LinkedIn.

## 🚀 Features

### Job Search & Application
- **Real-time Job Search**: Search LinkedIn jobs by keywords, location, and filters
- **One-Click Apply**: Automatically apply to Easy Apply jobs
- **Job Saving**: Save interesting jobs for later review
- **Application Tracking**: Keep track of all jobs you've applied to
- **Job Recommendations**: Get personalized job suggestions from LinkedIn

### Automation & Efficiency
- **Browser Automation**: Uses Playwright for reliable LinkedIn interaction
- **Session Management**: Persistent login sessions with cookie encryption
- **Rate Limiting**: Intelligent automation to avoid detection
- **Error Handling**: Robust error handling and recovery

### User Interface
- **Modern Dashboard**: Clean, responsive React interface
- **Real-time Stats**: Track your job search progress
- **Job Cards**: Easy-to-read job listings with apply/save buttons
- **Mobile Responsive**: Works on desktop and mobile devices

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │   FastAPI Bridge│    │  FastMCP Server │
│   (Port 3000)   │◄──►│   (Port 8001)   │◄──►│  (Playwright)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

- **Frontend**: React with Tailwind CSS and Lucide icons
- **API Bridge**: FastAPI server connecting frontend to MCP
- **Backend**: FastMCP server with Playwright browser automation

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- LinkedIn account
- Windows 10/11 (tested on Windows)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mcp-linkedin-server
   ```

2. **Set up Python environment**
   ```bash
   # Create virtual environment
   python -m venv env
   
   # Activate (Windows)
   env\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set up React frontend**
   ```bash
   # Install dependencies
   npm install
   ```

4. **Configure environment**
   ```bash
   # Create .env file with your LinkedIn credentials
   echo "LINKEDIN_USERNAME=your_email@example.com" > .env
   echo "LINKEDIN_PASSWORD=your_password" >> .env
   ```

## 🚀 Quick Start

### One-Command Startup
```bash
# Windows PowerShell
.\start_all.bat
```

This will:
- Start the MCP server
- Start the API bridge
- Start the React frontend
- Open the dashboard in your browser

### Manual Startup
```bash
# Terminal 1: Start MCP Server
python linkedin_browser_mcp.py

# Terminal 2: Start API Bridge
python api_bridge.py

# Terminal 3: Start React Frontend
npm start
```

## 📖 Usage

### 1. Login to LinkedIn
- The system will automatically log in using your credentials from `.env`
- Sessions are encrypted and persisted between runs

### 2. Search for Jobs
- Go to "Job Search" in the dashboard
- Enter job keywords and location
- Click "Search Jobs" to find matching positions

### 3. Apply to Jobs
- Click "Apply" on any job card
- The system will attempt Easy Apply for you
- Track your applications in the "Applications" section

### 4. Save Jobs
- Click "Save" on interesting jobs
- View saved jobs in the "Saved Jobs" section
- Get personalized recommendations

### 5. Track Progress
- Monitor your job search stats on the dashboard
- View applied jobs and their status
- Check system status and connection

## 🔧 API Endpoints

### Job Search
- `POST /api/search_jobs` - Search for LinkedIn jobs
- `POST /api/apply_job` - Apply to a job
- `POST /api/save_job` - Save a job

### Job Tracking
- `GET /api/list_applied_jobs` - List applied jobs
- `GET /api/list_saved_jobs` - List saved jobs
- `GET /api/job_recommendations` - Get job recommendations

### System
- `GET /api/health` - Health check

## 📁 Project Structure

```
mcp-linkedin-server/
├── linkedin_browser_mcp.py    # FastMCP server with Playwright
├── api_bridge.py              # FastAPI bridge
├── src/                       # React frontend
│   ├── components/
│   │   ├── Dashboard.js       # Main dashboard
│   │   ├── JobSearch.js       # Job search interface
│   │   ├── Applications.js    # Applied jobs tracking
│   │   ├── SavedJobs.js       # Saved jobs & recommendations
│   │   └── SettingsPage.js    # Settings
│   └── App.js                 # Main app component
├── start_all.bat              # One-command startup
├── requirements.txt           # Python dependencies
├── package.json              # Node.js dependencies
└── README.md                 # This file
```

## 🔒 Security & Privacy

- **Encrypted Sessions**: LinkedIn cookies are encrypted before storage
- **Local Storage**: All data is stored locally on your machine
- **No Data Sharing**: Your LinkedIn data never leaves your system
- **Rate Limiting**: Built-in delays to respect LinkedIn's terms

## 🚨 Important Notes

1. **LinkedIn Terms**: This tool respects LinkedIn's terms of service
2. **Easy Apply Only**: Automatic applications work only with Easy Apply jobs
3. **Session Management**: Keep your `.env` file secure
4. **Rate Limiting**: Don't overload LinkedIn with too many requests

## 🐛 Troubleshooting

### Common Issues

1. **Login Failed**
   - Check your `.env` credentials
   - Ensure 2FA is disabled or use app passwords
   - Clear browser cache and try again

2. **Jobs Not Loading**
   - Check internet connection
   - Verify LinkedIn is accessible
   - Check browser console for errors

3. **Apply Button Not Working**
   - Only works with Easy Apply jobs
   - Some jobs require manual application
   - Check if you're logged in

### Debug Mode
```bash
# Enable debug logging
export DEBUG=1
python linkedin_browser_mcp.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational purposes. Please respect LinkedIn's terms of service.

## 🆘 Support

- Check the troubleshooting section above
- Review the code comments for implementation details
- Open an issue for bugs or feature requests

---

**Happy Job Hunting! 🎯** 