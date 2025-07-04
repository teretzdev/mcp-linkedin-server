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

## 🎯 Enhanced Application Tracking

The LinkedIn Job Hunter now includes comprehensive application tracking features to help you manage your job search effectively.

### 📊 Application Tracker Features

#### **Status Management**
- **Multiple Status Types**: Applied, Under Review, Interview, Offer, Rejected, Withdrawn
- **Visual Status Indicators**: Color-coded badges with icons for quick identification
- **Status Updates**: Easily update application status with dropdown menus
- **Progress Tracking**: See your application pipeline at a glance

#### **Advanced Filtering & Search**
- **Smart Search**: Search by job title, company, or location
- **Status Filtering**: Filter applications by current status
- **Sorting Options**: Sort by date applied, job title, company, or status
- **Date Range Filtering**: Focus on recent or specific time periods

#### **Notes & Follow-ups**
- **Application Notes**: Add detailed notes to each application
- **Follow-up Reminders**: Set reminders for follow-up actions
- **Note History**: Track all notes with timestamps
- **Quick Actions**: Mark follow-ups as completed

#### **Analytics Dashboard**
- **Performance Metrics**: Success rate, response rate, daily averages
- **Status Breakdown**: Visual charts showing application distribution
- **Company Analysis**: Top companies you've applied to
- **Monthly Trends**: Track application volume over time
- **Insights & Recommendations**: AI-powered suggestions for improvement

#### **Export & Reporting**
- **CSV Export**: Export application data for external analysis
- **Custom Reports**: Generate reports based on filters and date ranges
- **Data Backup**: Secure local storage of all application data

### 🔄 Follow-up Tracker

#### **Smart Reminders**
- **Overdue Alerts**: Highlight follow-ups that are past due
- **Upcoming Reminders**: Show follow-ups due in the next week
- **Multiple Types**: Email, phone call, LinkedIn message tracking
- **Completion Tracking**: Mark follow-ups as completed

#### **Follow-up Management**
- **Add Follow-ups**: Create reminders for any application
- **Due Date Tracking**: Set specific dates for follow-up actions
- **Notes Integration**: Add context to each follow-up
- **Bulk Actions**: Manage multiple follow-ups efficiently

### 📈 Analytics & Insights

#### **Key Performance Indicators**
- **Application Success Rate**: Percentage of applications leading to interviews/offers
- **Response Rate**: Percentage of applications receiving any response
- **Daily Application Volume**: Average applications per day
- **Company Engagement**: Most responsive companies

#### **Visual Analytics**
- **Status Distribution Charts**: See your application pipeline
- **Monthly Trend Graphs**: Track application volume over time
- **Company Performance**: Identify most promising companies
- **Geographic Analysis**: Track applications by location

#### **Smart Recommendations**
- **Performance Insights**: AI-powered analysis of your job search
- **Improvement Suggestions**: Actionable advice based on your data
- **Success Patterns**: Identify what's working for you
- **Risk Alerts**: Warning signs for potential issues

### 🛠️ How to Use

#### **Getting Started**
1. **Navigate to Applications**: Click "Applications" in the sidebar
2. **View Your Pipeline**: See all applications with current status
3. **Update Status**: Use dropdown menus to update application progress
4. **Add Notes**: Click the edit icon to add notes to any application

#### **Using Follow-ups**
1. **Go to Follow-ups**: Click "Follow-ups" in the sidebar
2. **Add Reminder**: Click "Add Follow-up" to create a new reminder
3. **Set Due Date**: Choose when you need to follow up
4. **Track Progress**: Mark follow-ups as completed when done

#### **Analyzing Performance**
1. **Open Analytics**: Click "Analytics" in the sidebar
2. **Choose Time Range**: Select the period you want to analyze
3. **Review Metrics**: Check your success and response rates
4. **Export Data**: Download reports for external analysis

### 📱 Mobile-Friendly Design

All application tracking features are fully responsive and work seamlessly on:
- **Desktop Computers**: Full-featured experience with all tools
- **Tablets**: Touch-optimized interface for easy navigation
- **Mobile Phones**: Streamlined view for on-the-go tracking

### 🔒 Data Privacy & Security

- **Local Storage**: All application data is stored locally on your device
- **No Cloud Sync**: Your data never leaves your machine
- **Encrypted Sessions**: Secure handling of LinkedIn credentials
- **Export Control**: You control what data to export and when

### 🚀 Advanced Features

#### **Integration with Job Search**
- **Automatic Tracking**: Applications submitted through the tool are automatically tracked
- **Easy Apply Integration**: Seamless tracking of Easy Apply submissions
- **Manual Entry**: Add applications submitted outside the tool

#### **Customization Options**
- **Status Customization**: Add custom status types if needed
- **Note Templates**: Create reusable note templates
- **Filter Presets**: Save commonly used filter combinations

#### **Automation Features**
- **Auto-reminders**: Automatic follow-up suggestions based on application age
- **Status Suggestions**: AI-powered status update recommendations
- **Performance Alerts**: Notifications when metrics need attention

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