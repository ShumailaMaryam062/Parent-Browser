# LimitX Parental Control - Intelligence System Setup Guide

## 🚀 New Features Added

Your LimitX Parental Control system now includes:

### ✨ Core Features
- **JSON-Driven Intelligence System**: All child activity stored in structured JSON format
- **Gemini 2.0 AI Integration**: Advanced sentiment analysis and behavioral insights
- **Sentiment Scoring**: Emotional health scores from -1 (risky) to +1 (healthy)
- **Professional PDF Reports**: Legal-style, privacy-safe parental reports
- **Interactive Visualizations**: Charts for apps, screen time, keywords, and more
- **Conversation Starters**: AI-generated topics to discuss with your child
- **Dynamic Policy Management**: AI-recommended screen time policies with simulation
- **Privacy-First Design**: No raw conversations or identifiable data in reports

---

## 📦 Installation Steps

### 1. Install Required Python Packages

```powershell
cd "c:\Users\Hp\Desktop\parental contorl browser\requirements"
pip install -r requirements.txt
```

This installs:
- Flask & Flask-CORS (existing)
- python-dotenv (environment variables)
- google-generativeai (Gemini AI)
- reportlab (PDF generation)
- matplotlib, pandas (analytics)
- Pillow (image processing)

### 2. Configure Environment Variables

**Copy the example file:**
```powershell
copy .env.example .env
```

**Edit `.env` file** with your actual values:
```ini
# Get your Gemini API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=YOUR_ACTUAL_GEMINI_API_KEY_HERE

# Gemini Configuration
GEMINI_API_ENDPOINT=https://generativelanguage.googleapis.com/v1beta/models
GEMINI_MODEL=gemini-2.0-flash-exp

# Application Settings
APP_HOST=0.0.0.0
APP_PORT=5000
APP_DEBUG=True

# Data Storage Paths (these will be auto-created)
DATA_DIR=blockchain_data
INTELLIGENCE_DIR=intelligence_data
REPORTS_DIR=generated_reports

# Security
SECRET_KEY=change_this_to_a_random_string_in_production

# Report Branding
REPORT_COMPANY_NAME=LimitX Parental Control
```

### 3. Get Your Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and paste it into your `.env` file

---

## 🎯 How to Use the Intelligence System

### Step 1: Start the Server

```powershell
cd "c:\Users\Hp\Desktop\parental contorl browser\requirements"
python app.py
```

You should see:
```
✅ Intelligence system initialized successfully
🚀 Starting Blockchain Parental Control Dashboard Server...
📡 Server will listen on http://0.0.0.0:5000
```

### Step 2: Sync Blockchain Data (Existing Functionality)

Your existing blockchain sync still works:

```python
# Mobile device sends blockchain data
POST http://localhost:5000/api/sync
{
  "device_key": "your-18-segment-key",
  "blockchain_data": {...}
}
```

### Step 3: Access the Intelligence Dashboard

**Option A: Enhanced Dashboard (NEW)**
1. Open browser: http://localhost:5000/dashboard/v2
2. Enter your 18-segment blockchain key
3. Click "Access Dashboard"

**Option B: Classic Dashboard (Original)**
- Still available at: http://localhost:5000

### Step 4: Sync Intelligence Data

The system automatically syncs intelligence when you load the dashboard. Or use the API:

```bash
POST http://localhost:5000/api/intelligence/sync/<device_key>
```

This will:
- Process blockchain violations
- Calculate sentiment scores using Gemini AI
- Categorize keywords (positive/risky/neutral)
- Generate conversation starters
- Create analytics charts

### Step 5: Generate AI Report

Click **"Generate Report"** in the dashboard, or use API:

```bash
POST http://localhost:5000/api/report/generate/<device_key>
```

This creates a professional PDF report with:
- Executive Summary
- Key Findings
- Emotional Trends
- Positive Habits
- Possible Concerns
- Guidance for Parents
- Recommended Screen Time Policy
- Conversation Starters

### Step 6: Download Reports

- **Full Report**: Includes all details
- **Redacted Report**: Privacy-safe for sharing with counselors

---

## 📊 API Endpoints Reference

### Intelligence Endpoints (NEW)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/intelligence/sync/<key>` | POST | Sync intelligence from blockchain |
| `/api/intelligence/<key>` | GET | Get intelligence data |
| `/api/report/generate/<key>` | POST | Generate AI report |
| `/api/report/download/<key>?type=full` | GET | Download PDF report |
| `/api/analytics/<key>/<chart_type>` | GET | Get chart data |
| `/api/policy/<key>` | GET/POST | Get or update policy |
| `/api/conversation-starters/<key>` | GET | Get conversation starters |

### Blockchain Endpoints (EXISTING - Unchanged)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sync` | POST | Receive blockchain data |
| `/api/dashboard/<key>` | GET | Get violation data |
| `/api/stats/<key>` | GET | Get device statistics |
| `/api/verify/<key>` | GET | Verify blockchain integrity |

---

## 📈 Chart Types Available

Access with: `/api/analytics/<device_key>/<chart_type>`

1. **top_apps** - Bar chart of most-used applications
2. **screen_time** - Line graph of daily screen time trends
3. **blocked_attempts** - Scatter plot of blocked NSFW attempts
4. **keyword_sentiment** - Pie chart of keyword categories
5. **sleep_heatmap** - Heatmap of late-night activity

---

## 🎨 Dashboard Features

### Overview Tab
- Sentiment health score (-1 to +1)
- Top app usage
- Weekly screen time average
- Blocked attempts count
- Positive behavior patterns

### Analytics Tab
- Interactive charts (powered by Chart.js)
- Top applications bar chart
- Screen time trend line graph
- Keyword sentiment pie chart
- Blocked attempts timeline

### AI Report Tab
- Generate comprehensive reports
- Executive summary
- Key findings and emotional trends
- Positive habits and concerns
- Parental guidance
- Download as PDF (full or redacted)

### Policy Tab
- View AI-recommended policies
- Set daily/weekend screen time limits
- Configure bedtime hours
- Simulate policy impact
- Auto-apply settings

### Conversation Starters Tab
- AI-generated discussion topics
- Positive reinforcement suggestions
- Concern-based conversation starters
- Actionable guidance for parents

---

## 🔒 Privacy & Security

### What's Tracked
- App usage patterns (names & frequency)
- Search keywords (for sentiment analysis)
- Blocked NSFW attempts (timestamps & hashes)
- Screen time data (daily/weekly averages)

### What's NOT Stored
- ❌ Raw conversations or messages
- ❌ Personal identifiable information
- ❌ Individual browsing URLs
- ❌ Location data
- ❌ Contact information

### Report Privacy
- **Full Report**: Complete analysis for parents
- **Redacted Report**: Sensitive details removed, safe for sharing with school counselors

---

## 📁 File Structure

```
requirements/
├── app.py                      # Main Flask server (ENHANCED)
├── gemini_analyzer.py          # Gemini AI integration (NEW)
├── report_generator.py         # PDF report generator (NEW)
├── analytics.py                # Analytics processor (NEW)
├── intelligence_template.json  # Intelligence data template (NEW)
├── requirements.txt            # Updated dependencies
├── .env.example               # Environment config example (NEW)
├── .env                       # Your actual config (CREATE THIS)
│
├── templates/
│   ├── index.html             # Classic dashboard (UNCHANGED)
│   └── dashboard_v2.html      # Intelligence dashboard (NEW)
│
├── blockchain_data/           # Your existing blockchain storage
├── intelligence_data/         # Intelligence JSON files (AUTO-CREATED)
│   └── charts/               # Generated chart data
└── generated_reports/         # PDF reports (AUTO-CREATED)
```

---

## 🐛 Troubleshooting

### Issue: Intelligence features not available

**Error**: `⚠️ Intelligence features not available`

**Solution**:
1. Install all dependencies: `pip install -r requirements.txt`
2. Check `.env` file exists with GEMINI_API_KEY
3. Verify Gemini API key is valid

### Issue: Report generation fails

**Error**: `Failed to generate report`

**Solution**:
1. Ensure intelligence is synced first: `POST /api/intelligence/sync/<key>`
2. Check Gemini API quota: https://console.cloud.google.com/
3. Verify device has blockchain data synced

### Issue: Charts not loading

**Solution**:
1. Sync intelligence data first
2. Check browser console for JavaScript errors
3. Ensure Chart.js CDN is accessible

### Issue: PDF download fails

**Solution**:
1. Generate report first using "Generate Report" button
2. Check `generated_reports/` directory exists
3. Verify reportlab is installed: `pip install reportlab`

---

## 🔄 Workflow Example

1. **Mobile Device** → Syncs blockchain data → `/api/sync`
2. **Parent** → Opens dashboard → `http://localhost:5000/dashboard/v2`
3. **System** → Auto-syncs intelligence → `/api/intelligence/sync/<key>`
4. **Gemini AI** → Analyzes keywords → Sentiment score calculated
5. **Dashboard** → Shows charts, stats, conversation starters
6. **Parent** → Clicks "Generate Report" → `/api/report/generate/<key>`
7. **Gemini AI** → Creates comprehensive analysis
8. **System** → Generates professional PDF
9. **Parent** → Downloads report → `/api/report/download/<key>`
10. **Parent** → Reviews AI-recommended policy → Adjusts settings
11. **System** → Saves policy → `/api/policy/<key>`

---

## 🎓 Using Conversation Starters

Example generated conversation starters:

**Positive Type:**
> 💬 "Your child shows interest in science content. Great opportunity to support their curiosity!"
> 💡 Consider educational apps or supervised research time.

**Concern Type:**
> 💬 "Increased browsing detected after bedtime hours."
> 💡 Review bedtime limits and discuss healthy sleep habits.

These are designed to:
- Start positive, collaborative conversations
- Avoid confrontational language
- Provide actionable suggestions
- Support understanding over surveillance

---

## 📞 Support

If you encounter issues:

1. **Check Logs**: Server console shows detailed error messages
2. **Verify Config**: Ensure `.env` file is properly configured
3. **Test API**: Use tools like Postman to test endpoints
4. **Check Gemini**: Visit https://console.cloud.google.com/ for API status

---

## ⚡ Quick Start Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create `.env` file from `.env.example`
- [ ] Add Gemini API key to `.env`
- [ ] Run server: `python app.py`
- [ ] Open dashboard: http://localhost:5000/dashboard/v2
- [ ] Enter blockchain key
- [ ] View intelligence insights
- [ ] Generate AI report
- [ ] Download PDF report
- [ ] Configure screen time policy

---

## 🎉 You're All Set!

Your LimitX Parental Control system now has advanced AI-powered intelligence features while maintaining all your existing blockchain functionality. The system emphasizes:

- 🔒 **Privacy First**: No raw data in reports
- 🤖 **AI-Powered**: Gemini 2.0 for smart insights
- 📊 **Visual Analytics**: Interactive charts and graphs
- 💬 **Communication**: Conversation starters for parents
- 📄 **Professional Reports**: Legal-style PDF documents
- ⚙️ **Dynamic Policies**: AI-recommended screen time limits

**Remember**: This is a tool to support understanding and healthy digital habits, not surveillance. Use insights to have positive conversations with your child!
