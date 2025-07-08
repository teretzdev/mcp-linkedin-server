# 🤖 AI Job Automation System - Setup Guide

## 🚀 Quick Start

### 1. Set Up Gemini API Key
```bash
# Add to your .env file
GEMINI_API_KEY=your_gemini_api_key_here

# Or set as environment variable
set GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Start All Services
```bash
# Start API bridge, MCP server, and other services
start_all_optimized.bat
```

### 3. Start React Frontend
```bash
# In a new terminal
cd src
npm start
```

### 4. Access the Dashboard
- Open http://localhost:3000
- Navigate to "AI Automation" in the sidebar
- Configure your preferences and upload resumes
- Start the automation!

## 📋 System Features

### 🎯 AI-Powered Job Matching
- **Gemini AI Analysis**: Intelligent job fit assessment
- **Smart Scoring**: Multi-factor job matching algorithm
- **Configurable Thresholds**: Set apply/save thresholds
- **Real-time Processing**: Continuous job search and application

### 📄 Resume Management
- **Upload Up to 3 Resumes**: Store multiple resume versions
- **Smart Selection**: Choose which resume to use for each job
- **Easy Apply Integration**: Automatic resume attachment
- **File Management**: Upload, delete, and organize resumes

### ⚙️ Preferences Configuration
- **Job Keywords**: Define your target job titles
- **Location Preferences**: Remote, specific cities, or regions
- **Experience Level**: Entry, mid-level, senior, lead, principal
- **Job Type**: Full-time, part-time, contract, internship
- **Skills Matching**: Required and preferred skills
- **Company Targeting**: Target specific companies or avoid others

### 📊 Real-time Monitoring
- **Live Statistics**: Jobs searched, applied, saved
- **Activity Logs**: Detailed automation activity
- **Performance Metrics**: Success rates and error tracking
- **System Status**: API connectivity and service health

## 🔧 Configuration

### Job Preferences
```json
{
  "keywords": ["python developer", "software engineer", "backend developer"],
  "location": "Remote",
  "experience_level": "mid-level",
  "job_type": "full-time",
  "remote_preference": true,
  "skills_required": ["Python", "Django", "PostgreSQL"],
  "skills_preferred": ["React", "AWS", "Docker"],
  "companies_to_target": ["Google", "Microsoft", "Amazon"],
  "companies_to_avoid": ["StartupXYZ"]
}
```

### Automation Settings
- **Search Interval**: How often to search for new jobs (default: 30 minutes)
- **Apply Threshold**: Minimum score to automatically apply (default: 0.6)
- **Save Threshold**: Minimum score to save for later (default: 0.4)
- **Max Runs**: Limit automation cycles (optional)

## 🎮 Usage Instructions

### 1. Initial Setup
1. **Set Gemini API Key**: Add your key to environment variables
2. **Configure Preferences**: Set your job search criteria
3. **Upload Resumes**: Add up to 3 resume files
4. **Test System**: Run a single automation cycle

### 2. Start Automation
1. **Manual Start**: Use the dashboard "Start Automation" button
2. **Background Execution**: Run `start_ai_automation.ps1`
3. **Continuous Operation**: Set up scheduled tasks

### 3. Monitor Progress
1. **Dashboard Stats**: Real-time automation statistics
2. **Activity Logs**: Detailed operation logs
3. **Applied Jobs**: Track successful applications
4. **Saved Jobs**: Review jobs saved for later

### 4. Manage Results
1. **Review Applications**: Check applied jobs in LinkedIn
2. **Follow Up**: Use the follow-up system for responses
3. **Adjust Preferences**: Refine based on results
4. **Update Resumes**: Optimize based on job requirements

## 🔍 Troubleshooting

### Common Issues

#### Gemini API Not Working
```bash
# Check if key is set
echo $GEMINI_API_KEY

# Install Gemini package
pip install google-generativeai

# Test connection
python -c "import google.generativeai as genai; genai.configure(api_key='your_key'); print('Working!')"
```

#### API Bridge Not Starting
```bash
# Check if port is available
netstat -an | findstr :8001

# Kill conflicting processes
taskkill /F /IM python.exe

# Restart services
start_all_optimized.bat
```

#### React Frontend Issues
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Start fresh
npm start
```

### Log Files
- **Automation Logs**: `logs/automation.log`
- **API Bridge Logs**: Console output
- **React Logs**: Browser console and terminal

## 📈 Performance Optimization

### Best Practices
1. **Set Realistic Thresholds**: Start with 0.6-0.7 for apply threshold
2. **Use Specific Keywords**: Avoid generic terms like "developer"
3. **Target Specific Skills**: List exact technologies you know
4. **Monitor Logs**: Check for errors and adjust settings
5. **Regular Updates**: Keep preferences current with market trends

### Recommended Settings
- **Search Interval**: 30-60 minutes (avoid rate limiting)
- **Apply Threshold**: 0.7+ (high-quality matches only)
- **Save Threshold**: 0.5+ (worth reviewing)
- **Max Daily Applications**: 10-20 (maintain quality)

## 🛡️ Safety & Ethics

### LinkedIn Terms of Service
- **Respect Rate Limits**: Don't overwhelm LinkedIn servers
- **Manual Review**: Always review applications before sending
- **Authentic Applications**: Ensure resume matches job requirements
- **Follow Up Responsibly**: Don't spam recruiters

### Data Privacy
- **Secure Storage**: Resumes stored locally only
- **No Data Sharing**: All data stays on your system
- **Regular Cleanup**: Remove old logs and data
- **API Key Security**: Keep Gemini key private

## 🎯 Success Metrics

### Track These KPIs
- **Application Success Rate**: % of applications that get responses
- **Interview Rate**: % of applications leading to interviews
- **Job Match Quality**: Average match scores of applied jobs
- **Time to Response**: How quickly companies respond
- **Conversion Rate**: Applications → Interviews → Offers

### Optimization Tips
1. **A/B Test Resumes**: Try different resume versions
2. **Refine Keywords**: Update based on job descriptions
3. **Adjust Thresholds**: Lower if getting few matches, raise if too many
4. **Monitor Trends**: Adapt to changing job market
5. **Network Integration**: Combine with networking efforts

## 🚀 Advanced Features

### Custom Integrations
- **Email Notifications**: Get alerts for new matches
- **Slack Integration**: Send updates to Slack
- **Calendar Integration**: Schedule follow-ups
- **CRM Integration**: Track applications in your CRM

### Automation Extensions
- **Cover Letter Generation**: AI-powered cover letters
- **Interview Preparation**: Generate Q&A based on job description
- **Salary Negotiation**: Market rate analysis
- **Company Research**: Automated company background checks

---

## 🎉 You're Ready to Automate Your Job Search!

The AI Job Automation System will work tirelessly to find and apply to the best job opportunities for you. Monitor the dashboard, adjust preferences based on results, and watch your job search efficiency soar!

**Happy job hunting! 🚀**

# AI Automation Setup

## Unified Setup & Management

All automation and setup actions are now handled through a single menu:

```
python manage.py
```

Use the arrow keys to select actions. All previous .bat files have been removed.

---

(Replace all .bat references below with python manage.py) 