# LimitX Intelligence System - API Testing Guide

## 🔑 Prerequisites
- Server running: `python app.py`
- Device key: Your 18-segment blockchain key
- Gemini API configured in `.env`

---

## 📝 Example API Requests (PowerShell)

### 1. Sync Intelligence Data

```powershell
$deviceKey = "your-18-segment-device-key"
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/intelligence/sync/$deviceKey" -Method POST
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Intelligence data synced successfully",
  "sentimentScore": 0.45,
  "chartsGenerated": 5,
  "conversationStarters": 3,
  "timestamp": "2025-11-08T10:30:00"
}
```

---

### 2. Get Intelligence Data

```powershell
$deviceKey = "your-18-segment-device-key"
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/intelligence/$deviceKey" -Method GET
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

**Returns:** Complete intelligence JSON with behavioral data, sentiment scores, and analytics

---

### 3. Generate AI Report

```powershell
$deviceKey = "your-18-segment-device-key"
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/report/generate/$deviceKey" -Method POST
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Report generated successfully",
  "reportId": "RPT-20251108-103045",
  "pdfPath": "generated_reports/RPT-20251108-103045_full.pdf",
  "downloadUrl": "/api/report/download/...",
  "timestamp": "2025-11-08T10:30:45"
}
```

---

### 4. Download PDF Report

**Full Report:**
```powershell
$deviceKey = "your-18-segment-device-key"
Invoke-WebRequest -Uri "http://localhost:5000/api/report/download/$deviceKey?type=full" -OutFile "report_full.pdf"
```

**Redacted Report:**
```powershell
$deviceKey = "your-18-segment-device-key"
Invoke-WebRequest -Uri "http://localhost:5000/api/report/download/$deviceKey?type=redacted" -OutFile "report_redacted.pdf"
```

---

### 5. Get Chart Data

**Top Apps Chart:**
```powershell
$deviceKey = "your-18-segment-device-key"
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/analytics/$deviceKey/top_apps" -Method GET
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

**Available Chart Types:**
- `top_apps` - Bar chart of application usage
- `screen_time` - Line graph of daily trends
- `blocked_attempts` - Scatter plot of violations
- `keyword_sentiment` - Pie chart of categories
- `sleep_heatmap` - Heatmap of bedtime activity

---

### 6. Get Current Policy

```powershell
$deviceKey = "your-18-segment-device-key"
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/policy/$deviceKey" -Method GET
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

**Expected Response:**
```json
{
  "currentPolicy": {
    "dailyLimitMinutes": 120,
    "weekendLimitMinutes": 180,
    "bedtimeHour": "21:30",
    "autoApply": true
  },
  "recommendedPolicy": {
    "recommendedDailyLimit": 120,
    "weekendLimit": 180,
    "suggestedBedtime": "21:30",
    "reasoning": "Based on age-appropriate guidelines..."
  }
}
```

---

### 7. Update Policy

```powershell
$deviceKey = "your-18-segment-device-key"
$policy = @{
    dailyLimitMinutes = 90
    weekendLimitMinutes = 150
    bedtimeHour = "21:00"
    autoApply = $true
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:5000/api/policy/$deviceKey" `
    -Method POST `
    -ContentType "application/json" `
    -Body $policy

$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Policy updated successfully",
  "newPolicy": {
    "dailyLimitMinutes": 90,
    "weekendLimitMinutes": 150,
    "bedtimeHour": "21:00",
    "autoApply": true
  },
  "timestamp": "2025-11-08T10:35:00"
}
```

---

### 8. Get Conversation Starters

```powershell
$deviceKey = "your-18-segment-device-key"
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/conversation-starters/$deviceKey" -Method GET
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

**Expected Response:**
```json
{
  "conversationStarters": [
    {
      "id": 1,
      "type": "positive",
      "title": "Encourage Learning",
      "message": "Your child shows interest in educational content...",
      "actionSuggestion": "Consider educational apps..."
    }
  ],
  "count": 3
}
```

---

## 🔄 Complete Workflow Example

### Step-by-Step: From Blockchain to Report

```powershell
# Set your device key
$deviceKey = "12345678-87654321-abcdefgh-hgfedcba-..."

# Step 1: Verify blockchain data exists
$blockchain = Invoke-WebRequest -Uri "http://localhost:5000/api/dashboard/$deviceKey" -Method GET
Write-Host "✓ Blockchain data loaded"

# Step 2: Sync intelligence
$sync = Invoke-WebRequest -Uri "http://localhost:5000/api/intelligence/sync/$deviceKey" -Method POST
Write-Host "✓ Intelligence synced"

# Step 3: Get intelligence data
$intel = Invoke-WebRequest -Uri "http://localhost:5000/api/intelligence/$deviceKey" -Method GET
Write-Host "✓ Intelligence retrieved"

# Step 4: Generate report
$report = Invoke-WebRequest -Uri "http://localhost:5000/api/report/generate/$deviceKey" -Method POST
Write-Host "✓ Report generated"

# Step 5: Download report
Invoke-WebRequest -Uri "http://localhost:5000/api/report/download/$deviceKey?type=full" -OutFile "my_report.pdf"
Write-Host "✓ Report downloaded to my_report.pdf"

Write-Host "`n🎉 Complete! Open my_report.pdf to view your parental control report."
```

---

## 🧪 Testing Sentiment Analysis

### Test with Sample Keywords

```powershell
# Create test data
$testData = @{
    device_key = "test-device-key-12345678-87654321-..."
    blockchain_data = @{
        device_id = "TEST_DEVICE_001"
        blocks = @(
            @{
                index = 1
                deviceId = "TEST_DEVICE_001"
                appName = "Chrome Browser"
                keyword = "science homework"
                timestamp = [DateTimeOffset]::Now.ToUnixTimeMilliseconds()
                hash = "0000abcd1234"
                previousHash = "0"
                nonce = 12345
            },
            @{
                index = 2
                deviceId = "TEST_DEVICE_001"
                appName = "YouTube"
                keyword = "educational videos"
                timestamp = [DateTimeOffset]::Now.ToUnixTimeMilliseconds()
                hash = "0000efgh5678"
                previousHash = "0000abcd1234"
                nonce = 67890
            }
        )
    }
    app_version = "1.0.0"
    sync_timestamp = [DateTimeOffset]::Now.ToUnixTimeSeconds()
} | ConvertTo-Json -Depth 10

# Sync test blockchain data
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/sync" `
    -Method POST `
    -ContentType "application/json" `
    -Body $testData

Write-Host "✓ Test data synced"

# Now sync intelligence to see sentiment analysis
$deviceKey = "test-device-key-12345678-87654321-..."
$intel = Invoke-WebRequest -Uri "http://localhost:5000/api/intelligence/sync/$deviceKey" -Method POST
$result = $intel.Content | ConvertFrom-Json

Write-Host "📊 Sentiment Score: $($result.sentimentScore)"
Write-Host "💬 Conversation Starters: $($result.conversationStarters)"
```

---

## 📊 Understanding Sentiment Scores

| Score Range | Interpretation | Badge Color |
|-------------|----------------|-------------|
| +0.7 to +1.0 | Very Healthy | 🟢 Green |
| +0.3 to +0.7 | Positive | 🟢 Green |
| -0.3 to +0.3 | Neutral | 🟡 Gray |
| -0.7 to -0.3 | Concerning | 🔴 Red |
| -1.0 to -0.7 | Very Concerning | 🔴 Red |

**Factors Influencing Score:**
- ✅ Educational keywords → Positive
- ✅ Age-appropriate content → Positive
- ⚠️ Excessive usage → Neutral to Negative
- ❌ NSFW attempts → Negative
- ❌ Violent content → Negative

---

## 🎯 Quick Health Check

```powershell
# Test if server is running
Invoke-WebRequest -Uri "http://localhost:5000/health" -Method GET

# Expected response:
# {
#   "status": "healthy",
#   "service": "Blockchain Parental Control Dashboard",
#   "timestamp": "2025-11-08T10:00:00"
# }
```

---

## 📱 Mobile Integration Example

When your mobile app syncs data, it should follow this pattern:

```javascript
// Mobile app sync code (JavaScript/React Native example)
const syncData = async () => {
  const blockchainData = {
    device_key: DEVICE_KEY,
    blockchain_data: {
      device_id: DEVICE_ID,
      blocks: violationBlocks // Your blockchain array
    },
    app_version: "1.0.0",
    sync_timestamp: Date.now()
  };
  
  // Step 1: Sync blockchain
  await fetch('http://your-server:5000/api/sync', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(blockchainData)
  });
  
  // Step 2: Auto-sync intelligence (optional, can be done from dashboard)
  await fetch(`http://your-server:5000/api/intelligence/sync/${DEVICE_KEY}`, {
    method: 'POST'
  });
  
  console.log('✅ Data synced with intelligence system');
};
```

---

## 🐛 Common Errors and Solutions

### Error: "Intelligence system not available"
**Solution:** 
```powershell
pip install python-dotenv google-generativeai reportlab matplotlib pandas Pillow
```

### Error: "Gemini API key not found"
**Solution:** 
Check `.env` file exists and contains:
```ini
GEMINI_API_KEY=your_actual_key_here
```

### Error: "Device not found"
**Solution:** 
Sync blockchain data first:
```powershell
POST http://localhost:5000/api/sync
```

### Error: "Report not generated yet"
**Solution:** 
Generate report before downloading:
```powershell
POST http://localhost:5000/api/report/generate/<device_key>
```

---

## 📚 Additional Resources

- **Gemini API Docs**: https://ai.google.dev/docs
- **Chart.js Docs**: https://www.chartjs.org/docs/
- **ReportLab Guide**: https://www.reportlab.com/docs/

---

## ✅ Testing Checklist

- [ ] Server starts without errors
- [ ] Health endpoint responds: `/health`
- [ ] Blockchain sync works: `/api/sync`
- [ ] Intelligence sync works: `/api/intelligence/sync/<key>`
- [ ] Sentiment score calculated correctly
- [ ] Charts data generated: `/api/analytics/<key>/<type>`
- [ ] Report generation succeeds: `/api/report/generate/<key>`
- [ ] PDF downloads successfully: `/api/report/download/<key>`
- [ ] Policy updates save: `/api/policy/<key>`
- [ ] Dashboard loads: `http://localhost:5000/dashboard/v2`
- [ ] Conversation starters display
- [ ] All visualizations render

---

**🎉 Happy Testing!**

Your LimitX Intelligence System is ready to provide AI-powered insights for healthier digital habits.
