# Blockchain Parental Control Dashboard Server
# Flask-based REST API for receiving and displaying parental control violations

from flask import Flask, request, jsonify, render_template, send_from_directory, send_file
from flask_cors import CORS
from datetime import datetime
import json
import hashlib
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import new intelligence modules
try:
    from gemini_analyzer import GeminiAnalyzer
    from report_generator import ReportGenerator
    from analytics import AnalyticsProcessor
    INTELLIGENCE_ENABLED = True
except ImportError as e:
    print(f"⚠️  Intelligence features not available: {e}")
    INTELLIGENCE_ENABLED = False

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Data storage (use database in production)
DATA_DIR = Path("blockchain_data")
DATA_DIR.mkdir(exist_ok=True)

# Initialize intelligence system directories
INTELLIGENCE_DIR = Path(os.getenv('INTELLIGENCE_DIR', 'intelligence_data'))
INTELLIGENCE_DIR.mkdir(exist_ok=True)

REPORTS_DIR = Path(os.getenv('REPORTS_DIR', 'generated_reports'))
REPORTS_DIR.mkdir(exist_ok=True)

# Initialize intelligence components
if INTELLIGENCE_ENABLED:
    try:
        gemini_analyzer = GeminiAnalyzer()
        report_generator = ReportGenerator(str(REPORTS_DIR))
        analytics_processor = AnalyticsProcessor(str(INTELLIGENCE_DIR))
        print("✅ Intelligence system initialized successfully")
    except Exception as e:
        print(f"⚠️  Could not initialize intelligence system: {e}")
        INTELLIGENCE_ENABLED = False

# Load bypass key for admin access
BYPASS_KEY = os.getenv('BYPASS_KEY', '1234')

def validate_device_key(device_key):
    """
    Validate device key format.
    Allows bypass key for admin/testing access.
    """
    # Check if it's the bypass key
    if device_key == BYPASS_KEY:
        return True
    
    # Validate 18-segment blockchain key format
    key_segments = device_key.split('-')
    if len(key_segments) != 18:
        return False
    
    # Optionally validate each segment is 8 hex characters
    for segment in key_segments:
        if len(segment) != 8 or not all(c in '0123456789abcdefABCDEF' for c in segment):
            return False
    
    return True

def verify_blockchain_integrity(blocks):
    """Verify the integrity of a blockchain."""
    if not blocks:
        return True
    
    # Verify genesis block
    if blocks[0].get('previousHash') != '0':
        return False
    
    # Verify each subsequent block
    for i in range(1, len(blocks)):
        current = blocks[i]
        previous = blocks[i - 1]
        
        # Check if previous hash matches
        if current['previousHash'] != previous['hash']:
            return False
        
        # Verify block hash
        data = f"{current['deviceId']}:{current['appName']}:{current['keyword']}:{current['timestamp']}"
        calculated_hash = hashlib.sha256(
            f"{current['index']}:{current['previousHash']}:{data}:{current['nonce']}".encode()
        ).hexdigest()
        
        if calculated_hash != current['hash']:
            return False
        
        # Verify proof of work (4 leading zeros)
        if not current['hash'].startswith('0000'):
            return False
    
    return True

@app.route('/')
def index():
    """Serve the parental dashboard homepage."""
    return render_template('index.html')

@app.route('/api/sync', methods=['POST'])
def sync_blockchain():
    """
    Receive blockchain data from mobile devices.
    
    Expected payload:
    {
        "device_key": "18-segment blockchain key",
        "blockchain_data": {...},
        "app_version": "1.0.0",
        "sync_timestamp": 1234567890
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'device_key' not in data or 'blockchain_data' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        device_key = data['device_key']
        blockchain_data = data['blockchain_data']
        
        # Validate blockchain key format (with bypass support)
        if not validate_device_key(device_key):
            return jsonify({'error': 'Invalid blockchain key format. Key must have 18 segments separated by hyphens.'}), 400
        
        # Verify blockchain integrity
        blocks = blockchain_data.get('blocks', [])
        if not verify_blockchain_integrity(blocks):
            return jsonify({'error': 'Blockchain integrity verification failed'}), 400
        
        # Store the blockchain data
        device_file = DATA_DIR / f"{device_key}.json"
        
        storage_data = {
            'device_key': device_key,
            'device_id': blockchain_data.get('device_id'),
            'blocks': blocks,
            'last_sync': datetime.now().isoformat(),
            'app_version': data.get('app_version', 'unknown'),
            'integrity_verified': True
        }
        
        with open(device_file, 'w') as f:
            json.dump(storage_data, f, indent=2)
        
        print(f"✅ Blockchain synced successfully for device: {device_key[:20]}...")
        print(f"   Total violations: {len(blocks)}")
        
        return jsonify({
            'status': 'success',
            'message': 'Blockchain data synced successfully',
            'violations_count': len(blocks),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Error syncing blockchain: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/<device_key>', methods=['GET'])
def get_dashboard_data(device_key):
    """
    Retrieve dashboard data for a specific device key.
    Parents use this endpoint to view violations.
    """
    try:
        # Validate key format (with bypass support)
        if not validate_device_key(device_key):
            return jsonify({'error': 'Invalid blockchain key format. Key must have 18 segments separated by hyphens.'}), 400
        
        # Check if device data exists
        device_file = DATA_DIR / f"{device_key}.json"
        
        if not device_file.exists():
            return jsonify({
                'error': 'Device not found',
                'message': 'No data found for this blockchain key. Make sure the device has synced at least once.'
            }), 404
        
        # Load device data
        with open(device_file, 'r') as f:
            device_data = json.load(f)
        
        # Verify blockchain integrity again
        blocks = device_data.get('blocks', [])
        integrity_ok = verify_blockchain_integrity(blocks)
        
        # Process violations for display
        violations = []
        for block in blocks:
            violations.append({
                'id': block['index'],
                'device_id': block['deviceId'],
                'app_name': block['appName'],
                'keyword': block['keyword'],
                'timestamp': block['timestamp'],
                'date': datetime.fromtimestamp(block['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                'hash': block['hash']
            })
        
        # Sort by timestamp (newest first)
        violations.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'device_key': device_key,
            'device_id': device_data.get('device_id'),
            'violations': violations,
            'total_violations': len(violations),
            'last_sync': device_data.get('last_sync'),
            'app_version': device_data.get('app_version'),
            'blockchain_integrity': integrity_ok,
            'message': 'Data retrieved successfully'
        }), 200
        
    except Exception as e:
        print(f"❌ Error retrieving dashboard data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/<device_key>', methods=['GET'])
def get_device_stats(device_key):
    """Get statistics for a device."""
    try:
        device_file = DATA_DIR / f"{device_key}.json"
        
        if not device_file.exists():
            return jsonify({'error': 'Device not found'}), 404
        
        with open(device_file, 'r') as f:
            device_data = json.load(f)
        
        blocks = device_data.get('blocks', [])
        
        # Calculate statistics
        app_counts = {}
        keyword_counts = {}
        hourly_distribution = [0] * 24
        
        for block in blocks:
            # Count by app
            app_name = block['appName']
            app_counts[app_name] = app_counts.get(app_name, 0) + 1
            
            # Count by keyword
            keyword = block['keyword']
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            # Hourly distribution
            hour = datetime.fromtimestamp(block['timestamp'] / 1000).hour
            hourly_distribution[hour] += 1
        
        return jsonify({
            'total_violations': len(blocks),
            'app_breakdown': app_counts,
            'keyword_breakdown': keyword_counts,
            'hourly_distribution': hourly_distribution,
            'last_sync': device_data.get('last_sync')
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify/<device_key>', methods=['GET'])
def verify_blockchain(device_key):
    """Verify blockchain integrity for a device."""
    try:
        device_file = DATA_DIR / f"{device_key}.json"
        
        if not device_file.exists():
            return jsonify({'error': 'Device not found'}), 404
        
        with open(device_file, 'r') as f:
            device_data = json.load(f)
        
        blocks = device_data.get('blocks', [])
        is_valid = verify_blockchain_integrity(blocks)
        
        return jsonify({
            'blockchain_valid': is_valid,
            'total_blocks': len(blocks),
            'message': 'Blockchain integrity verified' if is_valid else 'Blockchain integrity check failed'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Blockchain Parental Control Dashboard',
        'timestamp': datetime.now().isoformat()
    }), 200

# ============================================================================
# NEW INTELLIGENCE SYSTEM ENDPOINTS
# These endpoints extend the blockchain system with AI-powered insights
# ============================================================================

@app.route('/api/intelligence/<device_key>', methods=['GET'])
def get_intelligence_data(device_key):
    """
    Get intelligence data (behavioral analytics) for a device.
    This includes sentiment scores, app usage patterns, and conversation starters.
    """
    if not INTELLIGENCE_ENABLED:
        return jsonify({'error': 'Intelligence system not available'}), 503
    
    try:
        intelligence = analytics_processor.load_intelligence(device_key)
        
        if not intelligence:
            return jsonify({
                'error': 'Intelligence data not found',
                'message': 'Run /api/intelligence/sync first to generate intelligence data'
            }), 404
        
        return jsonify(intelligence), 200
        
    except Exception as e:
        print(f"❌ Error retrieving intelligence: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/intelligence/sync/<device_key>', methods=['POST'])
def sync_intelligence(device_key):
    """
    Sync blockchain data to intelligence system.
    Processes blockchain violations and creates behavioral intelligence data.
    """
    if not INTELLIGENCE_ENABLED:
        return jsonify({'error': 'Intelligence system not available'}), 503
    
    try:
        # Load blockchain data
        device_file = DATA_DIR / f"{device_key}.json"
        
        if not device_file.exists():
            return jsonify({
                'error': 'Device not found',
                'message': 'Blockchain data must be synced first using /api/sync'
            }), 404
        
        with open(device_file, 'r') as f:
            blockchain_data = json.load(f)
        
        # Update intelligence from blockchain
        intelligence = analytics_processor.update_behavioral_data_from_blockchain(
            device_key, 
            blockchain_data
        )
        
        # Try to calculate sentiment scores using Gemini (with fallback)
        try:
            keywords = intelligence.get('behavioralData', {}).get('searchedKeywords', [])
            sentiment_score = gemini_analyzer.calculate_sentiment_score(keywords)
            
            # Categorize keywords
            categorized = gemini_analyzer.categorize_keywords(keywords)
            
            # Update emotional tone
            intelligence['behavioralData']['emotionalTone'] = {
                'overallSentiment': sentiment_score,
                'trendingPositive': categorized.get('positive', [])[:10],
                'trendingRisky': categorized.get('risky', [])[:10],
                'neutralPatterns': categorized.get('neutral', [])[:10]
            }
        except Exception as gemini_error:
            print(f"⚠️  Gemini API error (using fallback): {gemini_error}")
            # Use fallback sentiment calculation
            intelligence['behavioralData']['emotionalTone'] = {
                'overallSentiment': 0.0,
                'trendingPositive': [],
                'trendingRisky': [],
                'neutralPatterns': [kw['keyword'] for kw in intelligence.get('behavioralData', {}).get('searchedKeywords', [])[:10]]
            }
            sentiment_score = 0.0
        
        # Generate conversation starters
        intelligence['conversationStarters'] = analytics_processor.generate_conversation_starters(intelligence)
        
        # Generate analytics charts
        chart_paths = analytics_processor.generate_all_analytics(intelligence, device_key)
        
        # Save updated intelligence
        analytics_processor.save_intelligence(device_key, intelligence)
        
        print(f"✅ Intelligence synced for device: {device_key[:20]}...")
        
        return jsonify({
            'status': 'success',
            'message': 'Intelligence data synced successfully',
            'sentimentScore': sentiment_score,
            'chartsGenerated': len(chart_paths),
            'conversationStarters': len(intelligence['conversationStarters']),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Error syncing intelligence: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/report/generate/<device_key>', methods=['POST'])
def generate_report(device_key):
    """
    Generate comprehensive parental control report using Gemini AI.
    Creates a professional PDF report with insights and recommendations.
    
    Query params:
    - type: 'full' or 'redacted' (default: full)
    """
    if not INTELLIGENCE_ENABLED:
        return jsonify({'error': 'Intelligence system not available'}), 503
    
    try:
        report_type = request.args.get('type', 'full')
        
        # Load intelligence data
        intelligence = analytics_processor.load_intelligence(device_key)
        
        if not intelligence:
            return jsonify({
                'error': 'Intelligence data not found',
                'message': 'Sync intelligence first using /api/intelligence/sync'
            }), 404
        
        # Generate behavioral report using Gemini
        print(f"🤖 Generating AI report for {device_key[:20]}...")
        synthetic_report = gemini_analyzer.generate_behavioral_report(intelligence)
        
        # Update intelligence with report
        intelligence['syntheticReport'] = synthetic_report
        analytics_processor.save_intelligence(device_key, intelligence)
        
        # Generate PDF
        print(f"📄 Creating PDF report...")
        pdf_path = report_generator.generate_report(intelligence, report_type)
        
        return jsonify({
            'status': 'success',
            'message': 'Report generated successfully',
            'reportId': synthetic_report.get('reportId'),
            'pdfPath': pdf_path,
            'downloadUrl': f"/api/report/download/{device_key}?type={report_type}",
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/report/download/<device_key>', methods=['GET'])
def download_report(device_key):
    """
    Download generated PDF report.
    
    Query params:
    - type: 'full' or 'redacted' (default: full)
    """
    try:
        report_type = request.args.get('type', 'full')
        
        # Load intelligence to get report ID
        intelligence = analytics_processor.load_intelligence(device_key)
        
        if not intelligence or not intelligence.get('syntheticReport'):
            return jsonify({'error': 'Report not generated yet'}), 404
        
        report_id = intelligence['syntheticReport'].get('reportId', 'unknown')
        filename = f"{report_id}_{report_type}.pdf"
        filepath = REPORTS_DIR / filename
        
        if not filepath.exists():
            return jsonify({'error': 'Report file not found'}), 404
        
        return send_file(
            str(filepath),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"❌ Error downloading report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/<device_key>/<chart_type>', methods=['GET'])
def get_chart_data(device_key, chart_type):
    """
    Get chart data for visualizations.
    
    Chart types: top_apps, screen_time, blocked_attempts, keyword_sentiment, sleep_heatmap
    """
    try:
        chart_file = INTELLIGENCE_DIR / 'charts' / f"{device_key}_{chart_type}.json"
        
        if not chart_file.exists():
            return jsonify({
                'error': 'Chart data not found',
                'message': 'Sync intelligence first to generate chart data'
            }), 404
        
        with open(chart_file, 'r') as f:
            chart_data = json.load(f)
        
        return jsonify(chart_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/policy/<device_key>', methods=['GET', 'POST'])
def manage_policy(device_key):
    """
    Get or update screen time policy for a device.
    
    GET: Returns current policy
    POST: Updates policy with JSON body
    """
    if not INTELLIGENCE_ENABLED:
        return jsonify({'error': 'Intelligence system not available'}), 503
    
    try:
        intelligence = analytics_processor.load_intelligence(device_key)
        
        if not intelligence:
            return jsonify({'error': 'Intelligence data not found'}), 404
        
        if request.method == 'GET':
            policy = intelligence.get('policySettings', {}).get('currentPolicy', {})
            recommended = intelligence.get('syntheticReport', {}).get('screenTimePolicy', {})
            
            return jsonify({
                'currentPolicy': policy,
                'recommendedPolicy': recommended
            }), 200
        
        elif request.method == 'POST':
            new_policy = request.get_json()
            
            if not new_policy:
                return jsonify({'error': 'No policy data provided'}), 400
            
            # Save old policy to history
            current_policy = intelligence.get('policySettings', {}).get('currentPolicy', {})
            
            if not intelligence.get('policySettings'):
                intelligence['policySettings'] = {'policyHistory': []}
            
            intelligence['policySettings']['policyHistory'].append({
                'policy': current_policy,
                'changedAt': datetime.now().isoformat()
            })
            
            # Update current policy
            intelligence['policySettings']['currentPolicy'] = new_policy
            intelligence['policySettings']['lastUpdated'] = datetime.now().isoformat()
            
            # Save intelligence
            analytics_processor.save_intelligence(device_key, intelligence)
            
            return jsonify({
                'status': 'success',
                'message': 'Policy updated successfully',
                'newPolicy': new_policy,
                'timestamp': datetime.now().isoformat()
            }), 200
        
    except Exception as e:
        print(f"❌ Error managing policy: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversation-starters/<device_key>', methods=['GET'])
def get_conversation_starters(device_key):
    """Get conversation starter cards for parents."""
    if not INTELLIGENCE_ENABLED:
        return jsonify({'error': 'Intelligence system not available'}), 503
    
    try:
        intelligence = analytics_processor.load_intelligence(device_key)
        
        if not intelligence:
            return jsonify({'error': 'Intelligence data not found'}), 404
        
        starters = intelligence.get('conversationStarters', [])
        
        return jsonify({
            'conversationStarters': starters,
            'count': len(starters)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard/v2')
def enhanced_dashboard():
    """Serve the enhanced intelligence dashboard."""
    return render_template('dashboard_v2.html')

if __name__ == '__main__':
    print("🚀 Starting Blockchain Parental Control Dashboard Server...")
    print("📡 Server will listen on http://0.0.0.0:5000")
    print("🔗 API Endpoints:")
    print("   POST /api/sync - Receive blockchain data from devices")
    print("   GET  /api/dashboard/<key> - Get violation data")
    print("   GET  /api/stats/<key> - Get device statistics")
    print("   GET  /api/verify/<key> - Verify blockchain integrity")
    print("   GET  /health - Health check")
    print("\n🤖 Intelligence System Endpoints:")
    if INTELLIGENCE_ENABLED:
        print("   POST /api/intelligence/sync/<key> - Sync intelligence data")
        print("   GET  /api/intelligence/<key> - Get intelligence data")
        print("   POST /api/report/generate/<key> - Generate AI report")
        print("   GET  /api/report/download/<key> - Download PDF report")
        print("   GET  /api/analytics/<key>/<chart> - Get chart data")
        print("   GET  /api/policy/<key> - Get policy settings")
        print("   POST /api/policy/<key> - Update policy settings")
        print("   GET  /api/conversation-starters/<key> - Get conversation starters")
    else:
        print("   ⚠️  Intelligence features disabled (missing dependencies)")
    print("\n🌐 Web Dashboards:")
    print("   http://localhost:5000 - Classic Dashboard")
    print("   http://localhost:5000/dashboard/v2 - Enhanced Intelligence Dashboard")
    print("\n✅ Server is ready!")
    
    # Run the server
    app.run(host='0.0.0.0', port=5000, debug=True)
