"""
Analytics Module
Processes intelligence JSON data and generates visualization data for charts
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import Counter, defaultdict
from pathlib import Path
import os

class AnalyticsProcessor:
    """Processes behavioral data and generates chart-ready analytics."""
    
    def __init__(self, intelligence_dir: str = None):
        """Initialize analytics processor with intelligence data directory."""
        self.intelligence_dir = Path(intelligence_dir or os.getenv('INTELLIGENCE_DIR', 'intelligence_data'))
        self.intelligence_dir.mkdir(exist_ok=True, parents=True)
        
        # Create charts subdirectory
        self.charts_dir = self.intelligence_dir / 'charts'
        self.charts_dir.mkdir(exist_ok=True)
    
    def load_intelligence(self, device_key: str) -> Dict:
        """Load intelligence data for a specific device."""
        intel_file = self.intelligence_dir / f"{device_key}_intelligence.json"
        
        if not intel_file.exists():
            return None
        
        with open(intel_file, 'r') as f:
            return json.load(f)
    
    def save_intelligence(self, device_key: str, data: Dict):
        """Save intelligence data for a specific device."""
        intel_file = self.intelligence_dir / f"{device_key}_intelligence.json"
        
        with open(intel_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def generate_all_analytics(self, intelligence_data: Dict, device_key: str) -> Dict:
        """
        Generate all analytics charts from intelligence data.
        Returns paths to generated chart JSON files.
        """
        behavioral = intelligence_data.get('behavioralData', {})
        
        analytics = {
            'topAppsChart': self._generate_top_apps_chart(behavioral.get('mostUsedApps', []), device_key),
            'screenTimeTrend': self._generate_screen_time_trend(behavioral.get('screenTimeData', {}), device_key),
            'blockedAttemptsScatter': self._generate_blocked_attempts_scatter(behavioral.get('blockedNSFWAttempts', []), device_key),
            'keywordPieChart': self._generate_keyword_pie_chart(behavioral.get('searchedKeywords', []), device_key),
            'sleepTimeHeatmap': self._generate_sleep_time_heatmap(behavioral.get('screenTimeData', {}), device_key)
        }
        
        # Update analytics files paths in intelligence data
        intelligence_data['analyticsFiles'] = analytics
        self.save_intelligence(device_key, intelligence_data)
        
        return analytics
    
    def _generate_top_apps_chart(self, apps: List[Dict], device_key: str) -> str:
        """Generate bar chart data for top apps usage."""
        if not apps:
            chart_data = {
                'type': 'bar',
                'labels': ['No Data'],
                'datasets': [{
                    'label': 'Usage Count',
                    'data': [0],
                    'backgroundColor': ['rgba(99, 102, 241, 0.8)']
                }]
            }
        else:
            # Sort by usage count
            sorted_apps = sorted(apps, key=lambda x: x.get('usageCount', 0), reverse=True)[:10]
            
            labels = [app['appName'] for app in sorted_apps]
            data = [app.get('usageCount', 0) for app in sorted_apps]
            
            # Color code by category
            colors = []
            for app in sorted_apps:
                category = app.get('categoryType', 'unknown')
                if category == 'browser':
                    colors.append('rgba(99, 102, 241, 0.8)')  # Blue
                elif category == 'social':
                    colors.append('rgba(236, 72, 153, 0.8)')  # Pink
                elif category == 'education':
                    colors.append('rgba(34, 197, 94, 0.8)')  # Green
                else:
                    colors.append('rgba(148, 163, 184, 0.8)')  # Gray
            
            chart_data = {
                'type': 'bar',
                'labels': labels,
                'datasets': [{
                    'label': 'Usage Count',
                    'data': data,
                    'backgroundColor': colors,
                    'borderColor': colors,
                    'borderWidth': 1
                }],
                'options': {
                    'responsive': True,
                    'plugins': {
                        'legend': {'display': False},
                        'title': {
                            'display': True,
                            'text': 'Top Applications by Usage'
                        }
                    },
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'title': {'display': True, 'text': 'Number of Uses'}
                        }
                    }
                }
            }
        
        # Save chart data
        chart_file = self.charts_dir / f"{device_key}_top_apps.json"
        with open(chart_file, 'w') as f:
            json.dump(chart_data, f, indent=2)
        
        return f"charts/{device_key}_top_apps.json"
    
    def _generate_screen_time_trend(self, screen_time_data: Dict, device_key: str) -> str:
        """Generate line chart for daily screen time trends."""
        daily_data = screen_time_data.get('dailyScreenTime', [])
        
        if not daily_data:
            chart_data = {
                'type': 'line',
                'labels': ['No Data'],
                'datasets': [{
                    'label': 'Screen Time (minutes)',
                    'data': [0],
                    'borderColor': 'rgba(99, 102, 241, 1)',
                    'backgroundColor': 'rgba(99, 102, 241, 0.2)',
                    'fill': True
                }]
            }
        else:
            # Sort by date
            sorted_data = sorted(daily_data, key=lambda x: x.get('date', ''))[-30:]  # Last 30 days
            
            labels = [d.get('date', '') for d in sorted_data]
            data = [d.get('minutes', 0) for d in sorted_data]
            
            chart_data = {
                'type': 'line',
                'labels': labels,
                'datasets': [{
                    'label': 'Screen Time (minutes)',
                    'data': data,
                    'borderColor': 'rgba(99, 102, 241, 1)',
                    'backgroundColor': 'rgba(99, 102, 241, 0.2)',
                    'fill': True,
                    'tension': 0.4
                }],
                'options': {
                    'responsive': True,
                    'plugins': {
                        'legend': {'display': True},
                        'title': {
                            'display': True,
                            'text': 'Daily Screen Time Trend (Last 30 Days)'
                        }
                    },
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'title': {'display': True, 'text': 'Minutes'}
                        },
                        'x': {
                            'title': {'display': True, 'text': 'Date'}
                        }
                    }
                }
            }
        
        chart_file = self.charts_dir / f"{device_key}_screen_time.json"
        with open(chart_file, 'w') as f:
            json.dump(chart_data, f, indent=2)
        
        return f"charts/{device_key}_screen_time.json"
    
    def _generate_blocked_attempts_scatter(self, blocked_attempts: List[Dict], device_key: str) -> str:
        """Generate scatter plot for blocked NSFW attempts."""
        if not blocked_attempts:
            chart_data = {
                'type': 'scatter',
                'datasets': [{
                    'label': 'Blocked Attempts',
                    'data': [],
                    'backgroundColor': 'rgba(239, 68, 68, 0.6)'
                }]
            }
        else:
            # Convert to scatter plot format (x: time, y: attempt number)
            data_points = []
            for i, attempt in enumerate(blocked_attempts[:100]):  # Limit to 100
                timestamp = attempt.get('timestamp', '')
                if timestamp:
                    try:
                        dt = datetime.fromtimestamp(int(timestamp) / 1000)
                        data_points.append({
                            'x': dt.strftime('%Y-%m-%d %H:%M'),
                            'y': i + 1,
                            'keyword': attempt.get('keyword', 'unknown')
                        })
                    except:
                        pass
            
            chart_data = {
                'type': 'scatter',
                'datasets': [{
                    'label': 'Blocked Attempts',
                    'data': data_points,
                    'backgroundColor': 'rgba(239, 68, 68, 0.6)',
                    'pointRadius': 6,
                    'pointHoverRadius': 8
                }],
                'options': {
                    'responsive': True,
                    'plugins': {
                        'legend': {'display': True},
                        'title': {
                            'display': True,
                            'text': 'Blocked NSFW Attempts Over Time'
                        },
                        'tooltip': {
                            'callbacks': {
                                'label': 'function(context) { return "Keyword: " + context.raw.keyword; }'
                            }
                        }
                    },
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'title': {'display': True, 'text': 'Attempt Number'}
                        },
                        'x': {
                            'title': {'display': True, 'text': 'Date & Time'}
                        }
                    }
                }
            }
        
        chart_file = self.charts_dir / f"{device_key}_blocked_attempts.json"
        with open(chart_file, 'w') as f:
            json.dump(chart_data, f, indent=2)
        
        return f"charts/{device_key}_blocked_attempts.json"
    
    def _generate_keyword_pie_chart(self, keywords: List[Dict], device_key: str) -> str:
        """Generate pie chart for keyword sentiment distribution."""
        if not keywords:
            chart_data = {
                'type': 'pie',
                'labels': ['No Data'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['rgba(148, 163, 184, 0.8)']
                }]
            }
        else:
            # Count by category
            categories = Counter([kw.get('category', 'neutral') for kw in keywords])
            
            labels = list(categories.keys())
            data = list(categories.values())
            
            # Color map
            color_map = {
                'positive': 'rgba(34, 197, 94, 0.8)',   # Green
                'neutral': 'rgba(148, 163, 184, 0.8)',  # Gray
                'risky': 'rgba(239, 68, 68, 0.8)',      # Red
                'educational': 'rgba(59, 130, 246, 0.8)', # Blue
                'entertainment': 'rgba(168, 85, 247, 0.8)' # Purple
            }
            
            colors = [color_map.get(label, 'rgba(148, 163, 184, 0.8)') for label in labels]
            
            chart_data = {
                'type': 'pie',
                'labels': [label.capitalize() for label in labels],
                'datasets': [{
                    'data': data,
                    'backgroundColor': colors,
                    'borderColor': 'rgba(255, 255, 255, 1)',
                    'borderWidth': 2
                }],
                'options': {
                    'responsive': True,
                    'plugins': {
                        'legend': {'position': 'right'},
                        'title': {
                            'display': True,
                            'text': 'Search Keywords by Sentiment Category'
                        }
                    }
                }
            }
        
        chart_file = self.charts_dir / f"{device_key}_keyword_sentiment.json"
        with open(chart_file, 'w') as f:
            json.dump(chart_data, f, indent=2)
        
        return f"charts/{device_key}_keyword_sentiment.json"
    
    def _generate_sleep_time_heatmap(self, screen_time_data: Dict, device_key: str) -> str:
        """Generate heatmap data for bedtime activity."""
        daily_data = screen_time_data.get('dailyScreenTime', [])
        
        if not daily_data:
            heatmap_data = {
                'type': 'matrix',
                'data': [],
                'message': 'No sleep-time activity data available'
            }
        else:
            # Create heatmap matrix: days x hours (21:00 to 07:00)
            heatmap_matrix = []
            
            for day_data in daily_data[-14:]:  # Last 14 days
                date = day_data.get('date', '')
                peak_hours = day_data.get('peakHours', [])
                
                # Count activity in sleep hours (21:00 - 07:00)
                sleep_hour_activity = [0] * 10  # 10 hours from 21:00 to 07:00
                
                for hour in peak_hours:
                    if hour >= 21 or hour < 7:
                        if hour >= 21:
                            idx = hour - 21
                        else:
                            idx = hour + 3
                        if 0 <= idx < 10:
                            sleep_hour_activity[idx] += 1
                
                heatmap_matrix.append({
                    'date': date,
                    'activity': sleep_hour_activity
                })
            
            heatmap_data = {
                'type': 'matrix',
                'labels': {
                    'x': ['21:00', '22:00', '23:00', '00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00'],
                    'y': [d['date'] for d in heatmap_matrix]
                },
                'data': heatmap_matrix,
                'colorScale': {
                    'min': 0,
                    'max': 5,
                    'colors': ['rgba(99, 102, 241, 0.1)', 'rgba(239, 68, 68, 0.9)']
                },
                'options': {
                    'title': 'Late Night Screen Activity Heatmap',
                    'description': 'Activity detected during recommended sleep hours (9 PM - 7 AM)'
                }
            }
        
        chart_file = self.charts_dir / f"{device_key}_sleep_heatmap.json"
        with open(chart_file, 'w') as f:
            json.dump(heatmap_data, f, indent=2)
        
        return f"charts/{device_key}_sleep_heatmap.json"
    
    def update_behavioral_data_from_blockchain(self, device_key: str, blockchain_data: Dict) -> Dict:
        """
        Update intelligence data from blockchain violations.
        This integrates your existing blockchain data with the new intelligence system.
        """
        # Load or create intelligence data
        intelligence = self.load_intelligence(device_key)
        
        if not intelligence:
            # Load template
            template_path = Path(__file__).parent / 'intelligence_template.json'
            with open(template_path, 'r') as f:
                intelligence = json.load(f)
            
            # Set device key
            intelligence['childProfile']['deviceKey'] = device_key
            intelligence['childProfile']['profileCreated'] = datetime.now().isoformat()
        
        # Update from blockchain
        blocks = blockchain_data.get('blocks', [])
        
        # Update app usage
        app_counter = Counter()
        keyword_list = []
        blocked_attempts = []
        
        for block in blocks:
            app_name = block.get('appName', 'Unknown')
            keyword = block.get('keyword', '')
            timestamp = block.get('timestamp', 0)
            
            app_counter[app_name] += 1
            
            keyword_list.append({
                'keyword': keyword,
                'frequency': 1,
                'sentiment': 0,  # Will be calculated by Gemini
                'category': 'neutral',
                'timestamp': datetime.fromtimestamp(timestamp / 1000).isoformat()
            })
            
            blocked_attempts.append({
                'keyword': keyword,
                'appName': app_name,
                'timestamp': timestamp,
                'blockHash': block.get('hash', '')
            })
        
        # Update most used apps
        intelligence['behavioralData']['mostUsedApps'] = [
            {
                'appName': app,
                'usageCount': count,
                'categoryType': 'browser',  # Categorize based on app name
                'lastUsed': datetime.now().isoformat()
            }
            for app, count in app_counter.most_common(20)
        ]
        
        # Merge keywords (deduplicate and sum frequencies)
        keyword_freq = Counter()
        for kw in keyword_list:
            keyword_freq[kw['keyword']] += 1
        
        intelligence['behavioralData']['searchedKeywords'] = [
            {
                'keyword': kw,
                'frequency': freq,
                'sentiment': 0,
                'category': 'neutral',
                'timestamp': datetime.now().isoformat()
            }
            for kw, freq in keyword_freq.most_common(100)
        ]
        
        # Update blocked attempts
        intelligence['behavioralData']['blockedNSFWAttempts'] = blocked_attempts
        
        # Update metadata
        intelligence['metadata']['lastSync'] = datetime.now().isoformat()
        intelligence['metadata']['totalViolations'] = len(blocks)
        intelligence['metadata']['integrityVerified'] = blockchain_data.get('integrity_verified', True)
        intelligence['childProfile']['lastUpdated'] = datetime.now().isoformat()
        
        # Save updated intelligence
        self.save_intelligence(device_key, intelligence)
        
        return intelligence
    
    def generate_conversation_starters(self, intelligence_data: Dict) -> List[Dict]:
        """Generate conversation starter cards based on behavioral data."""
        starters = []
        behavioral = intelligence_data.get('behavioralData', {})
        
        # Top apps starter
        apps = behavioral.get('mostUsedApps', [])
        if apps:
            top_app = apps[0]['appName']
            starters.append({
                'id': len(starters) + 1,
                'type': 'positive',
                'title': 'Favorite Application',
                'message': f"Your child frequently uses {top_app}. This could be a great conversation starter!",
                'actionSuggestion': f"Ask them what they like most about {top_app} and if they've discovered anything interesting."
            })
        
        # Screen time starter
        screen_data = behavioral.get('screenTimeData', {})
        weekly_avg = screen_data.get('weeklyAverage', 0)
        if weekly_avg > 180:  # More than 3 hours/day
            starters.append({
                'id': len(starters) + 1,
                'type': 'concern',
                'title': 'Screen Time Discussion',
                'message': f"Average daily screen time is {weekly_avg} minutes. Consider discussing balance.",
                'actionSuggestion': "Talk about other activities they enjoy and create a balanced schedule together."
            })
        
        # Positive keywords starter
        emotional_tone = behavioral.get('emotionalTone', {})
        trending_positive = emotional_tone.get('trendingPositive', [])
        if trending_positive:
            starters.append({
                'id': len(starters) + 1,
                'type': 'positive',
                'title': 'Positive Interests',
                'message': f"Your child shows interest in: {', '.join(trending_positive[:3])}",
                'actionSuggestion': "Encourage their curiosity by providing related books, activities, or educational resources."
            })
        
        # Late night activity
        bedtime_activity = screen_data.get('bedtimeActivity', {})
        late_sessions = bedtime_activity.get('lateNightSessions', 0)
        if late_sessions > 5:
            starters.append({
                'id': len(starters) + 1,
                'type': 'concern',
                'title': 'Bedtime Routine',
                'message': f"Detected {late_sessions} late-night browsing sessions recently.",
                'actionSuggestion': "Discuss the importance of sleep and consider adjusting device access during bedtime hours."
            })
        
        return starters if starters else intelligence_data.get('conversationStarters', [])
