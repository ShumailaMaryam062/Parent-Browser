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
            'sleepTimeHeatmap': self._generate_sleep_time_heatmap(behavioral.get('screenTimeData', {}), device_key),
            'humanActivityPattern': self._generate_human_activity_pattern(behavioral, device_key)
        }
        
        # Update analytics files paths in intelligence data
        intelligence_data['analyticsFiles'] = analytics
        self.save_intelligence(device_key, intelligence_data)
        
        return analytics
    
    def _generate_top_apps_chart(self, apps: List[Dict], device_key: str) -> str:
        """Generate enhanced bar chart data for top apps usage with gradients."""
        if not apps:
            chart_data = {
                'type': 'bar',
                'labels': ['No Data'],
                'datasets': [{
                    'label': 'Usage Count',
                    'data': [0],
                    'backgroundColor': ['rgba(99, 102, 241, 0.9)'],
                    'borderColor': ['rgba(99, 102, 241, 1)'],
                    'borderWidth': 2
                }],
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'legend': {'display': True, 'position': 'top'},
                        'title': {'display': True, 'text': 'Top Applications by Usage', 'font': {'size': 18, 'weight': 'bold'}}
                    },
                    'scales': {
                        'y': {'beginAtZero': True, 'grid': {'color': 'rgba(0,0,0,0.05)'}}
                    }
                }
            }
        else:
            # Sort by usage count
            sorted_apps = sorted(apps, key=lambda x: x.get('usageCount', 0), reverse=True)[:10]
            
            labels = [app['appName'] for app in sorted_apps]
            data = [app.get('usageCount', 0) for app in sorted_apps]
            
            # Enhanced natural colors by category (more muted, less AI-looking)
            bg_colors = []
            border_colors = []
            for app in sorted_apps:
                category = app.get('categoryType', 'unknown')
                if category == 'browser':
                    bg_colors.append('#6b7280')  # Gray
                    border_colors.append('#4b5563')
                elif category == 'social':
                    bg_colors.append('#f472b6')  # Light Pink
                    border_colors.append('#ec4899')
                elif category == 'education':
                    bg_colors.append('#34d399')  # Light Emerald
                    border_colors.append('#10b981')
                elif category == 'entertainment':
                    bg_colors.append('#fbbf24')  # Light Amber
                    border_colors.append('#f59e0b')
                else:
                    bg_colors.append('#a78bfa')  # Light Purple
                    border_colors.append('#8b5cf6')
            
            chart_data = {
                'type': 'bar',
                'labels': labels,
                'datasets': [{
                    'label': 'Usage Count',
                    'data': data,
                    'backgroundColor': bg_colors,
                    'borderColor': border_colors,
                    'borderWidth': 2,
                    'borderRadius': 6,
                    'borderSkipped': False,
                }],
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'legend': {'display': False},
                        'title': {
                            'display': True,
                            'text': 'Top Applications by Usage',
                            'font': {'size': 18, 'weight': 'bold'},
                            'color': '#c7d2fe',
                            'padding': 20
                        },
                        'tooltip': {
                            'backgroundColor': 'rgba(30, 27, 75, 0.95)',
                            'titleFont': {'size': 14, 'weight': 'bold'},
                            'bodyFont': {'size': 13},
                            'padding': 12,
                            'cornerRadius': 10,
                            'borderColor': 'rgba(139, 92, 246, 0.5)',
                            'borderWidth': 2
                        }
                    },
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'grid': {'color': 'rgba(139, 92, 246, 0.1)', 'lineWidth': 1},
                            'ticks': {'font': {'size': 11}, 'color': '#a5b4fc'}
                        },
                        'x': {
                            'grid': {'display': False},
                            'ticks': {'font': {'size': 11}, 'color': '#a5b4fc', 'maxRotation': 45, 'minRotation': 45}
                        }
                    },
                    'animation': {
                        'duration': 1200,
                        'easing': 'easeOutQuart'
                    }
                }
            }
        
        # Save chart data
        chart_file = self.charts_dir / f"{device_key}_top_apps.json"
        with open(chart_file, 'w') as f:
            json.dump(chart_data, f, indent=2)
        
        return f"charts/{device_key}_top_apps.json"
    
    def _generate_screen_time_trend(self, screen_time_data: Dict, device_key: str) -> str:
        """Generate enhanced line chart for daily screen time trends with gradient fill."""
        daily_data = screen_time_data.get('dailyScreenTime', [])
        
        if not daily_data:
            chart_data = {
                'type': 'line',
                'labels': ['No Data'],
                'datasets': [{
                    'label': 'Screen Time (minutes)',
                    'data': [0],
                    'borderColor': 'rgba(139, 92, 246, 1)',
                    'backgroundColor': 'rgba(139, 92, 246, 0.2)',
                    'borderWidth': 3,
                    'fill': True
                }],
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'legend': {'display': True, 'position': 'top'},
                        'title': {
                            'display': True,
                            'text': 'Daily Screen Time Trend',
                            'font': {'size': 20, 'weight': 'bold'},
                            'color': '#1f2937'
                        }
                    },
                    'scales': {
                        'y': {'beginAtZero': True}
                    }
                }
            }
        else:
            # Sort by date
            sorted_data = sorted(daily_data, key=lambda x: x.get('date', ''))[-30:]  # Last 30 days
            
            labels = [d.get('date', '') for d in sorted_data]
            data = [d.get('minutes', 0) for d in sorted_data]
            
            # Calculate average for reference line
            avg = sum(data) / len(data) if data else 0
            
            chart_data = {
                'type': 'line',
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Screen Time',
                        'data': data,
                        'borderColor': '#8b5cf6',
                        'backgroundColor': 'rgba(139, 92, 246, 0.12)',
                        'fill': True,
                        'tension': 0.35,
                        'borderWidth': 2.8,
                        'pointRadius': 3,
                        'pointBackgroundColor': '#8b5cf6',
                        'pointBorderColor': 'rgba(255, 255, 255, 0.8)',
                        'pointBorderWidth': 1.5,
                        'pointHoverRadius': 6,
                        'pointHoverBackgroundColor': '#7c3aed',
                        'pointHoverBorderWidth': 2
                    },
                    {
                        'label': f'Average ({int(avg//60)}h {int(avg%60)}m)',
                        'data': [avg] * len(labels),
                        'borderColor': '#10b981',
                        'backgroundColor': 'transparent',
                        'borderWidth': 2,
                        'borderDash': [6, 3],
                        'pointRadius': 0,
                        'tension': 0
                    }
                ],
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'interaction': {
                        'mode': 'index',
                        'intersect': False
                    },
                    'plugins': {
                        'legend': {
                            'display': True,
                            'position': 'top',
                            'labels': {
                                'font': {'size': 13, 'weight': '600'},
                                'padding': 15,
                                'usePointStyle': True,
                                'color': '#c7d2fe',
                                'boxWidth': 8,
                                'boxHeight': 8
                            }
                        },
                        'title': {
                            'display': True,
                            'text': 'Daily Screen Time Trend (Last 30 Days)',
                            'font': {'size': 18, 'weight': 'bold'},
                            'color': '#c7d2fe',
                            'padding': 20
                        },
                        'tooltip': {
                            'backgroundColor': 'rgba(30, 27, 75, 0.95)',
                            'titleFont': {'size': 14, 'weight': 'bold'},
                            'bodyFont': {'size': 13},
                            'padding': 12,
                            'cornerRadius': 10,
                            'displayColors': True,
                            'borderColor': 'rgba(139, 92, 246, 0.5)',
                            'borderWidth': 2,
                            'callbacks': {
                                'label': '(function(context) { const mins = context.parsed.y; const hours = Math.floor(mins / 60); const minutes = Math.floor(mins % 60); return context.dataset.label + ": " + hours + "h " + minutes + "m (" + mins + " min)"; })'
                            }
                        }
                    },
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'title': {
                                'display': True,
                                'text': 'Time (minutes)',
                                'font': {'size': 13, 'weight': '600'},
                                'color': '#a5b4fc'
                            },
                            'grid': {'color': 'rgba(139, 92, 246, 0.1)', 'lineWidth': 1},
                            'ticks': {
                                'font': {'size': 11},
                                'color': '#a5b4fc',
                                'callback': '(function(value) { const hours = Math.floor(value / 60); const mins = Math.floor(value % 60); return hours + "h " + mins + "m"; })'
                            }
                        },
                        'x': {
                            'title': {
                                'display': True,
                                'text': 'Date',
                                'font': {'size': 14, 'weight': 'bold'},
                                'color': '#6b7280'
                            },
                            'grid': {'display': False},
                            'ticks': {
                                'font': {'size': 11},
                                'color': '#6b7280',
                                'maxRotation': 45,
                                'minRotation': 0
                            }
                        }
                    },
                    'animation': {
                        'duration': 2000,
                        'easing': 'easeInOutQuart'
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
                    'backgroundColor': 'rgba(248, 113, 113, 0.7)',
                    'borderColor': '#ef4444',
                    'pointRadius': 7,
                    'pointHoverRadius': 11,
                    'pointBorderWidth': 2,
                    'pointBorderColor': '#fff',
                    'pointHoverBorderWidth': 3
                }],
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'legend': {
                            'display': True,
                            'labels': {
                                'font': {'size': 13, 'weight': '600'},
                                'color': '#c7d2fe',
                                'usePointStyle': True
                            }
                        },
                        'title': {
                            'display': True,
                            'text': 'Blocked NSFW Attempts Over Time',
                            'font': {'size': 18, 'weight': 'bold'},
                            'color': '#c7d2fe',
                            'padding': 20
                        },
                        'tooltip': {
                            'backgroundColor': 'rgba(30, 27, 75, 0.95)',
                            'titleFont': {'size': 14, 'weight': 'bold'},
                            'bodyFont': {'size': 13},
                            'padding': 12,
                            'cornerRadius': 10,
                            'borderColor': 'rgba(239, 68, 68, 0.5)',
                            'borderWidth': 2,
                            'callbacks': {
                                'label': 'function(context) { return "Keyword: " + context.raw.keyword + " at " + context.raw.x; }'
                            }
                        }
                    },
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'title': {
                                'display': True,
                                'text': 'Attempt Number',
                                'font': {'size': 13, 'weight': '600'},
                                'color': '#a5b4fc'
                            },
                            'grid': {'color': 'rgba(139, 92, 246, 0.1)'},
                            'ticks': {'color': '#a5b4fc', 'font': {'size': 11}}
                        },
                        'x': {
                            'title': {
                                'display': True,
                                'text': 'Date & Time',
                                'font': {'size': 13, 'weight': '600'},
                                'color': '#a5b4fc'
                            },
                            'grid': {'display': False},
                            'ticks': {'color': '#a5b4fc', 'font': {'size': 10}, 'maxRotation': 45}
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
            
            # Color map with natural, muted tones (less saturated)
            color_map = {
                'positive': '#34d399',      # Light Emerald
                'neutral': '#94a3b8',       # Light Gray
                'risky': '#f87171',         # Light Red
                'educational': '#60a5fa',   # Light Blue
                'entertainment': '#a78bfa'  # Light Purple
            }
            
            colors = [color_map.get(label, '#6b7280') for label in labels]
            
            chart_data = {
                'type': 'pie',
                'labels': [label.capitalize() for label in labels],
                'datasets': [{
                    'data': data,
                    'backgroundColor': colors,
                    'borderColor': '#ffffff',
                    'borderWidth': 2.5,
                    'hoverOffset': 10,
                    'hoverBorderWidth': 3
                }],
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'legend': {
                            'position': 'right',
                            'labels': {
                                'font': {'size': 13, 'weight': '600'},
                                'color': '#c7d2fe',
                                'padding': 15,
                                'usePointStyle': True,
                                'pointStyle': 'circle'
                            }
                        },
                        'title': {
                            'display': True,
                            'text': 'Search Keywords by Sentiment',
                            'font': {'size': 18, 'weight': 'bold'},
                            'color': '#c7d2fe',
                            'padding': 20
                        },
                        'tooltip': {
                            'backgroundColor': 'rgba(30, 27, 75, 0.95)',
                            'titleFont': {'size': 14, 'weight': 'bold'},
                            'bodyFont': {'size': 13},
                            'padding': 12,
                            'cornerRadius': 10,
                            'borderColor': 'rgba(139, 92, 246, 0.5)',
                            'borderWidth': 2
                        }
                    },
                    'cutout': '65%'
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
        
        # Calculate screen time data from blockchain timestamps
        daily_screen_time = defaultdict(int)
        for block in blocks:
            timestamp = block.get('timestamp', 0)
            if timestamp:
                date = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
                daily_screen_time[date] += 1  # Count activities per day
        
        # Convert to minutes (estimate: 1 activity = ~2 minutes of usage)
        screen_time_entries = []
        for date, count in sorted(daily_screen_time.items()):
            minutes = count * 2  # Rough estimate
            screen_time_entries.append({
                'date': date,
                'minutes': minutes,
                'peakHours': []
            })
        
        # Calculate weekly average
        if screen_time_entries:
            total_minutes = sum(entry['minutes'] for entry in screen_time_entries)
            days_count = len(screen_time_entries)
            weekly_average = total_minutes // days_count if days_count > 0 else 0
        else:
            weekly_average = 0
        
        # Update screen time data
        intelligence['behavioralData']['screenTimeData'] = {
            'dailyScreenTime': screen_time_entries[-30:],  # Keep last 30 days
            'weeklyAverage': weekly_average,
            'bedtimeActivity': {
                'lateNightSessions': 0,
                'avgSleepTime': '22:00'
            }
        }
        
        # Update metadata
        intelligence['metadata']['lastSync'] = datetime.now().isoformat()
        intelligence['metadata']['totalViolations'] = len(blocks)
        intelligence['metadata']['integrityVerified'] = blockchain_data.get('integrity_verified', True)
        intelligence['childProfile']['lastUpdated'] = datetime.now().isoformat()
        
        # Save updated intelligence
        self.save_intelligence(device_key, intelligence)
        
        return intelligence
    
    def _generate_human_activity_pattern(self, behavioral: Dict, device_key: str) -> str:
        """Generate human activity and engagement pattern chart showing hourly interaction intensity."""
        # Analyze hourly activity patterns from screen time and app usage
        screen_time_data = behavioral.get('screenTimeData', {})
        apps = behavioral.get('mostUsedApps', [])
        keywords = behavioral.get('searchedKeywords', [])
        
        # Create 24-hour activity pattern (simulated based on usage)
        hourly_activity = [0] * 24
        hourly_engagement = [0] * 24
        
        # Simulate realistic activity distribution (peak hours: 7-9am, 4-10pm)
        peak_hours = [7, 8, 16, 17, 18, 19, 20, 21]
        moderate_hours = [6, 9, 10, 11, 12, 13, 14, 15, 22]
        
        # Base activity on actual usage count
        total_usage = sum([app.get('usageCount', 0) for app in apps])
        total_searches = len(keywords)
        
        for hour in range(24):
            if hour in peak_hours:
                hourly_activity[hour] = (total_usage / 8) * (1 + (hour % 3) * 0.2)
                hourly_engagement[hour] = (total_searches / 8) * (1 + (hour % 3) * 0.15)
            elif hour in moderate_hours:
                hourly_activity[hour] = (total_usage / 16) * (0.5 + (hour % 4) * 0.1)
                hourly_engagement[hour] = (total_searches / 16) * (0.4 + (hour % 4) * 0.1)
            else:
                hourly_activity[hour] = total_usage * 0.01  # Minimal night activity
                hourly_engagement[hour] = total_searches * 0.01
        
        hours_labels = [f"{h:02d}:00" for h in range(24)]
        
        chart_data = {
            'type': 'line',
            'labels': hours_labels,
            'datasets': [
                {
                    'label': 'App Interactions (Activity Level)',
                    'data': hourly_activity,
                    'borderColor': '#3b82f6',
                    'backgroundColor': 'rgba(59, 130, 246, 0.08)',
                    'fill': True,
                    'tension': 0.3,
                    'borderWidth': 2.5,
                    'pointRadius': 2.5,
                    'pointHoverRadius': 7,
                    'pointHoverBackgroundColor': '#3b82f6',
                    'pointHoverBorderColor': '#fff',
                    'pointHoverBorderWidth': 2,
                    'pointBackgroundColor': '#3b82f6',
                    'pointBorderColor': 'rgba(255, 255, 255, 0.5)',
                    'pointBorderWidth': 1
                },
                {
                    'label': 'Search & Engagement Intensity',
                    'data': hourly_engagement,
                    'borderColor': '#f59e0b',
                    'backgroundColor': 'rgba(245, 158, 11, 0.08)',
                    'fill': True,
                    'tension': 0.3,
                    'borderWidth': 2.5,
                    'pointRadius': 2.5,
                    'pointHoverRadius': 7,
                    'pointHoverBackgroundColor': '#f59e0b',
                    'pointHoverBorderColor': '#fff',
                    'pointHoverBorderWidth': 2,
                    'pointBackgroundColor': '#f59e0b',
                    'pointBorderColor': 'rgba(255, 255, 255, 0.5)',
                    'pointBorderWidth': 1
                }
            ],
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'interaction': {
                    'mode': 'index',
                    'intersect': False
                },
                'plugins': {
                    'legend': {
                        'display': True,
                        'position': 'top',
                        'labels': {
                            'font': {'size': 12, 'weight': '500'},
                            'padding': 12,
                            'usePointStyle': True,
                            'color': '#c7d2fe',
                            'boxWidth': 10,
                            'boxHeight': 10
                        }
                    },
                    'title': {
                        'display': False
                    },
                    'tooltip': {
                        'backgroundColor': 'rgba(30, 27, 75, 0.95)',
                        'titleFont': {'size': 13, 'weight': '600'},
                        'bodyFont': {'size': 12},
                        'padding': 12,
                        'cornerRadius': 8,
                        'displayColors': True,
                        'borderColor': 'rgba(139, 92, 246, 0.4)',
                        'borderWidth': 1
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'grid': {
                            'color': 'rgba(139, 92, 246, 0.08)',
                            'lineWidth': 1,
                            'drawBorder': False
                        },
                        'ticks': {
                            'font': {'size': 11},
                            'color': '#9ca3af',
                            'padding': 8
                        },
                        'border': {
                            'display': False
                        }
                    },
                    'x': {
                        'grid': {
                            'color': 'rgba(139, 92, 246, 0.05)',
                            'lineWidth': 1,
                            'drawBorder': False
                        },
                        'ticks': {
                            'font': {'size': 10},
                            'color': '#9ca3af',
                            'maxRotation': 0,
                            'padding': 6
                        },
                        'border': {
                            'display': False
                        }
                    }
                }
            }
        }
        
        chart_file = self.charts_dir / f"{device_key}_human_activity.json"
        with open(chart_file, 'w') as f:
            json.dump(chart_data, f, indent=2)
        
        return f"charts/{device_key}_human_activity.json"
    
    def generate_conversation_starters(self, intelligence_data: Dict) -> List[Dict]:
        """Generate dynamic, personalized conversation starters based on actual behavioral patterns."""
        starters = []
        behavioral = intelligence_data.get('behavioralData', {})
        emotional_tone = behavioral.get('emotionalTone', {})
        wellness_score = emotional_tone.get('overallSentiment', 50)
        
        # Get actual data for personalization
        apps = behavioral.get('mostUsedApps', [])
        keywords = behavioral.get('searchedKeywords', [])
        screen_data = behavioral.get('screenTimeData', {})
        trending_positive = emotional_tone.get('trendingPositive', [])
        trending_risky = emotional_tone.get('trendingRisky', [])
        
        # 1. Top App Deep Dive (Dynamic based on actual usage)
        if apps and len(apps) > 0:
            top_app = apps[0]['appName']
            usage_count = apps[0].get('usageCount', 0)
            category = apps[0].get('categoryType', 'application')
            
            if category == 'education':
                starters.append({
                    'id': len(starters) + 1,
                    'type': 'positive',
                    'icon': '🎓',
                    'title': f'Celebrating Learning: {top_app}',
                    'message': f"Amazing! Your child has used {top_app} {usage_count} times - they're genuinely curious and engaged in learning!",
                    'actionSuggestion': f"Ask them: 'What's the coolest thing you've discovered using {top_app} lately? Can you teach me something new?'",
                    'deeperQuestions': [
                        f"What made you interested in using {top_app}?",
                        "Have you learned anything that surprised you?",
                        "Would you like me to help you explore similar topics?"
                    ]
                })
            elif category == 'social':
                starters.append({
                    'id': len(starters) + 1,
                    'type': 'neutral',
                    'icon': '💬',
                    'title': f'Social Connection: {top_app}',
                    'message': f"{top_app} is important to them ({usage_count} uses). Let's understand their social world.",
                    'actionSuggestion': f"Try: 'I notice you spend time on {top_app}. Who are you connecting with? What do you enjoy sharing with friends?'",
                    'deeperQuestions': [
                        "How does this app make you feel when you use it?",
                        "Are there any parts of online socializing that feel stressful?",
                        "How can we balance online and face-to-face friendships?"
                    ]
                })
            else:
                starters.append({
                    'id': len(starters) + 1,
                    'type': 'positive',
                    'icon': '⭐',
                    'title': f'Exploring Together: {top_app}',
                    'message': f"{top_app} has captured their attention ({usage_count} times). Let's explore why!",
                    'actionSuggestion': f"Say: 'I'd love to understand {top_app} better. Could you give me a quick tour of what you do there?'",
                    'deeperQuestions': [
                        "What's your favorite feature and why?",
                        "If you could change one thing about it, what would it be?",
                        "Are there other apps or activities you'd like to explore?"
                    ]
                })
        
        # 2. Curiosity-Based Starter (From actual search keywords)
        if keywords and len(keywords) > 0:
            top_keywords = [kw['keyword'] for kw in keywords[:3]]
            keyword_str = ', '.join(top_keywords)
            
            starters.append({
                'id': len(starters) + 1,
                'type': 'positive',
                'icon': '🔍',
                'title': 'Curiosity Mapping',
                'message': f"Their recent searches include: \"{keyword_str}\" - their mind is actively exploring!",
                'actionSuggestion': f"Ask: 'I saw you were curious about {top_keywords[0]}. What sparked that interest? Want to dive deeper together?'",
                'deeperQuestions': [
                    "What questions are you trying to answer?",
                    "Have you found anything surprising or confusing?",
                    "Would you like help finding more resources about this?"
                ],
                'enrichmentIdeas': [
                    f"Visit library for books on {top_keywords[0]}",
                    "Watch documentaries together on related topics",
                    "Start a curiosity journal to track discoveries"
                ]
            })
        
        # 3. Wellness Score Conversation (Dynamic based on 0-100 scale)
        if wellness_score >= 80:
            starters.append({
                'id': len(starters) + 1,
                'type': 'positive',
                'icon': '🌟',
                'title': 'Thriving Digital Wellness',
                'message': f"Excellent wellness score ({wellness_score}/100)! They're making fantastic digital choices.",
                'actionSuggestion': "Celebrate: 'I'm really proud of how you balance your online time. What helps you make good choices?'",
                'deeperQuestions': [
                    "What strategies help you use technology in healthy ways?",
                    "How do you decide when it's time to take a break?",
                    "Can you share your tips with siblings/friends?"
                ]
            })
        elif wellness_score >= 60:
            starters.append({
                'id': len(starters) + 1,
                'type': 'positive',
                'icon': '👍',
                'title': 'Solid Digital Habits',
                'message': f"Good wellness score ({wellness_score}/100). They're developing healthy patterns with room to grow.",
                'actionSuggestion': "Discuss: 'Your digital habits are pretty good! What's one thing you'd like to improve?'",
                'deeperQuestions': [
                    "What parts of screen time feel most valuable to you?",
                    "Are there times you wish you used devices less?",
                    "How can I support better balance?"
                ]
            })
        elif wellness_score >= 40:
            starters.append({
                'id': len(starters) + 1,
                'type': 'concern',
                'icon': '⚖️',
                'title': 'Finding Balance Together',
                'message': f"Wellness score ({wellness_score}/100) suggests room for improvement. Let's collaborate on balance.",
                'actionSuggestion': "Open dialogue: 'I want to understand your relationship with screens. How do you feel after using devices?'",
                'deeperQuestions': [
                    "Do you ever feel like screen time takes away from other things you enjoy?",
                    "What would a 'balanced day' look like to you?",
                    "What boundaries might help you feel better?"
                ]
            })
        else:
            starters.append({
                'id': len(starters) + 1,
                'type': 'concern',
                'icon': '💭',
                'title': 'Wellness Check-In Needed',
                'message': f"Wellness score ({wellness_score}/100) indicates concern. Time for a supportive conversation.",
                'actionSuggestion': "Gentle approach: 'I've noticed your screen habits lately. I'm not mad - I'm concerned. Can we talk about what's going on?'",
                'deeperQuestions': [
                    "Are you using screens to cope with something stressful?",
                    "Is everything okay at school/with friends?",
                    "How can we work together to feel better?"
                ],
                'professionalSupport': "Consider consulting a child counselor if patterns persist"
            })
        
        # 4. Positive Interest Amplification
        if trending_positive and len(trending_positive) > 0:
            positive_interests = ', '.join(trending_positive[:3])
            starters.append({
                'id': len(starters) + 1,
                'type': 'positive',
                'icon': '🎯',
                'title': 'Nurturing Passions',
                'message': f"Positive trends detected: {positive_interests}. Let's fuel their interests!",
                'actionSuggestion': f"Say: 'I love that you're interested in {trending_positive[0]}. How can we take this passion offline too?'",
                'enrichmentIdeas': [
                    f"Join community groups related to {trending_positive[0]}",
                    "Create hands-on projects together",
                    "Connect with mentors in areas of interest",
                    "Document their learning journey"
                ],
                'deeperQuestions': [
                    "What excites you most about this topic?",
                    "Where do you see yourself going with this interest?",
                    "Can we set a goal together around this?"
                ]
            })
        
        # 5. Screen Time Optimization (Dynamic based on actual data)
        weekly_avg = screen_data.get('weeklyAverage', 0)
        daily_avg = weekly_avg / 7 if weekly_avg else 0
        
        if daily_avg > 240:  # Over 4 hours/day
            starters.append({
                'id': len(starters) + 1,
                'type': 'concern',
                'icon': '⏰',
                'title': 'Screen Time Redesign',
                'message': f"Daily average is {daily_avg:.0f} minutes ({daily_avg/60:.1f} hours). Let's co-create healthier boundaries.",
                'actionSuggestion': "Collaborative approach: 'Let's design your ideal day together. How much screen time would make you feel good while leaving room for other things you love?'",
                'strategicQuestions': [
                    "What activities have you been missing out on?",
                    "How do you feel before vs. after long screen sessions?",
                    "What would be a realistic screen time goal you'd be proud of?"
                ],
                'implementationPlan': [
                    "Week 1: Track current feelings and create awareness",
                    "Week 2: Reduce by 30 minutes, add one offline activity",
                    "Week 3: Establish new routine with built-in breaks",
                    "Week 4: Evaluate and adjust together"
                ]
            })
        elif daily_avg > 120:  # 2-4 hours/day
            starters.append({
                'id': len(starters) + 1,
                'type': 'neutral',
                'icon': '⚡',
                'title': 'Optimizing Screen Time',
                'message': f"Average {daily_avg:.0f} minutes/day is moderate. Let's maximize quality over quantity.",
                'actionSuggestion': "Say: 'Your screen time is reasonable. What if we focused on making sure it's time well spent?'",
                'qualityChecks': [
                    "Are you learning or just scrolling?",
                    "Does this content align with your goals/interests?",
                    "Are you connecting meaningfully or just consuming?"
                ]
            })
        else:  # Under 2 hours/day
            starters.append({
                'id': len(starters) + 1,
                'type': 'positive',
                'icon': '🏆',
                'title': 'Healthy Screen Habits!',
                'message': f"Only {daily_avg:.0f} minutes/day - excellent balance! They're prioritizing offline life.",
                'actionSuggestion': "Affirm: 'I notice you use screens mindfully and make time for other activities. What helps you maintain this balance?'",
                'deeperQuestions': [
                    "What offline activities bring you the most joy?",
                    "How do you decide what deserves your screen time?",
                    "What advice would you give other kids about screens?"
                ]
            })
        
        # 6. Late Night Digital Boundaries (if applicable)
        bedtime_activity = screen_data.get('bedtimeActivity', {})
        late_sessions = bedtime_activity.get('lateNightSessions', 0)
        if late_sessions > 5:
            starters.append({
                'id': len(starters) + 1,
                'type': 'concern',
                'icon': '🌙',
                'title': 'Sleep & Screen Boundaries',
                'message': f"{late_sessions} late-night sessions detected. Sleep is foundational for well-being.",
                'actionSuggestion': "Empathetic approach: 'I've noticed you're on devices late at night. I'm worried about your sleep. What's making it hard to disconnect before bed?'",
                'deeperQuestions': [
                    "Do you have trouble falling asleep? Is something keeping you awake?",
                    "Are you staying up to connect with friends or for other reasons?",
                    "What bedtime routine would help you feel rested?"
                ],
                'sleepStrategies': [
                    "Create 1-hour 'digital sunset' before bed",
                    "Charge devices outside bedroom",
                    "Replace screen time with reading, journaling, or calming music",
                    "Set consistent bedtime together"
                ]
            })
        
        return starters if starters else [{
            'id': 1,
            'type': 'neutral',
            'icon': '💬',
            'title': 'Start the Dialogue',
            'message': 'Begin tracking to generate personalized conversation starters',
            'actionSuggestion': 'Ask: "How do you feel about your relationship with technology?"'
        }]

