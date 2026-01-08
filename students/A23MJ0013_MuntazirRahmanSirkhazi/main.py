"""
argiNINE-11 Agricultural AI System
Python Flask Application

Installation:
pip install flask

To run:
python app.py

Then open http://localhost:5000 in your browser
"""

from flask import Flask, render_template_string, jsonify, request
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# Data models
class SoilData:
    @staticmethod
    def get_current_metrics():
        return {
            'ph': {'value': 6.8, 'optimal': '6.0 - 7.0', 'status': 'optimal'},
            'moisture': {'value': 68, 'optimal': '60% - 75%', 'status': 'optimal'},
            'nitrogen': {'value': 42, 'optimal': '40 - 60 ppm', 'status': 'optimal'},
            'phosphorus': {'value': 28, 'optimal': '30 - 50 ppm', 'status': 'warning'},
            'potassium': {'value': 155, 'optimal': '150 - 200 ppm', 'status': 'optimal'},
            'organic_matter': {'value': 4.2, 'optimal': '3.0% - 5.0%', 'status': 'optimal'}
        }

class WeatherData:
    @staticmethod
    def get_current():
        return {
            'temperature': 72,
            'high': 78,
            'low': 65,
            'humidity': 62,
            'precipitation': 0.2,
            'wind_speed': 8,
            'wind_direction': 'SW'
        }
    
    @staticmethod
    def get_forecast():
        days = ['Today', 'Tomorrow', 'Sunday', 'Monday', 'Tuesday']
        conditions = ['Partly Cloudy', 'Sunny', 'Thunderstorms', 'Rain', 'Partly Cloudy']
        precip = [10, 5, 85, 70, 20]
        
        return [
            {
                'day': days[i],
                'conditions': conditions[i],
                'high': 74 + random.randint(0, 6),
                'low': 64 + random.randint(0, 4),
                'precipitation': precip[i],
                'recommendation': ['Good for spraying', 'Ideal field work', 
                                 'Avoid field operations', 'Indoor tasks only', 
                                 'Resume field work'][i]
            }
            for i in range(5)
        ]

class CropData:
    @staticmethod
    def get_crop_info(crop_type):
        crops = {
            'corn': {
                'name': 'Corn',
                'stage': 'Growing',
                'stage_detail': '8 leaves visible',
                'health': 91,
                'yield': '185 bushels/acre',
                'explanation': 'Your corn plants now have 8 leaves. This is a good time to add fertilizer because the plants are growing fast and need lots of nutrients.',
                'actions': [
                    {'title': 'Add Fertilizer', 'description': 'Apply 45 lbs of nitrogen fertilizer per acre within the next week. Your corn is at the perfect stage to absorb nutrients.'},
                    {'title': 'Check for Pests', 'description': 'Look for corn rootworm beetles on your plants. If you find more than 1 beetle per plant, you may need pest control.'},
                    {'title': 'Water Management', 'description': 'Keep soil moisture between 65-75%. In about 2-3 weeks, your corn will need even more water.'},
                    {'title': 'Harvest Planning', 'description': 'Expected harvest time is late September (about 125 days from when you planted).'}
                ]
            },
            'soybean': {
                'name': 'Soybean',
                'stage': 'Flowering',
                'stage_detail': 'Flowers starting to appear',
                'health': 88,
                'yield': '52 bushels/acre',
                'explanation': 'Your soybean plants are beginning to flower. This is when they start forming pods. It\'s important to keep them healthy and protect from pests.',
                'actions': [
                    {F'title': 'Watch for Aphids', 'description': 'Small green insects called aphids can damage soybeans during flowering. Check your plants every few days.'},
                    {'title': 'Water Needs', 'description': 'Flowering soybeans need steady water. Make sure soil stays moist but not waterlogged.'},
                    {'title': 'Weed Control', 'description': 'Remove weeds that compete with your soybeans for nutrients and water.'},
                    {'title': 'Harvest Planning', 'description': 'Expect to harvest in about 60-75 days when pods are full and leaves turn yellow.'}
                ]
            },
            'wheat': {
                'name': 'Wheat',
                'stage': 'Heading',
                'stage_detail': 'Grain heads emerging',
                'health': 93,
                'yield': '68 bushels/acre',
                'explanation': 'Your wheat is at the heading stage - grain heads are now visible. This is a critical time that determines your final yield.',
                'actions': [
                    {'title': 'Fungicide Application', 'description': 'Apply fungicide to prevent head diseases. Current weather conditions favor disease growth.'},
                    {'title': 'Check Moisture', 'description': 'Wheat heads need consistent moisture. Water if no rain expected in next 5 days.'},
                    {'title': 'Monitor Closely', 'description': 'Check fields every 2-3 days for any signs of disease or pests on the grain heads.'},
                    {'title': 'Harvest Planning', 'description': 'Harvest expected in 30-40 days when grain is hard and moisture drops to 13-14%.'}
                ]
            },
            'cotton': {
                'name': 'Cotton',
                'stage': 'Squaring',
                'stage_detail': 'Flower buds forming',
                'health': 87,
                'yield': '1,150 lbs/acre',
                'explanation': 'Your cotton plants are forming squares (flower buds). These buds will become flowers, then cotton bolls. Protecting them now is crucial.',
                'actions': [
                    {'title': 'Pest Inspection', 'description': 'Check for thrips (tiny insects) and bollworms. They love to damage flower buds.'},
                    {'title': 'Growth Management', 'description': 'Consider using a growth regulator to control plant height and improve boll development.'},
                    {'title': 'Fertilizer Check', 'description': 'Cotton needs good nutrition during squaring. Test soil and add nutrients if needed.'},
                    {'title': 'Harvest Planning', 'description': 'First cotton bolls should open in 60-80 days. Harvest when 60% of bolls are open.'}
                ]
            }
        }
        return crops.get(crop_type, crops['corn'])

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>argiNINE-11 - Agricultural AI System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }

        h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 5px;
        }

        .tagline {
            color: #666;
            font-size: 1.1em;
        }

        nav {
            display: flex;
            gap: 15px;
            margin-top: 20px;
            flex-wrap: wrap;
        }

        .nav-btn {
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
        }

        .nav-btn:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .nav-btn.active {
            background: #764ba2;
        }

        .page {
            display: none;
            animation: fadeIn 0.5s;
        }

        .page.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .content-card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }

        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }

        .metric-label {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }

        .status-good { background: #4caf50; }
        .status-warning { background: #ff9800; }
        .status-alert { background: #f44336; }

        .recommendation-box {
            background: #f8f9fa;
            padding: 20px;
            border-left: 4px solid #667eea;
            border-radius: 8px;
            margin: 15px 0;
        }

        .info-box {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
        }

        .btn {
            padding: 12px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            margin-top: 15px;
            transition: all 0.3s;
        }

        .btn:hover {
            background: #5568d3;
            transform: translateY(-2px);
        }

        .form-group {
            margin: 20px 0;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
        }

        select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
            transition: border 0.3s;
        }

        select:focus {
            outline: none;
            border-color: #667eea;
        }

        .alert {
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }

        .alert-warning {
            background: #fff3cd;
            border-left: 4px solid #ff9800;
            color: #856404;
        }

        .alert-success {
            background: #d4edda;
            border-left: 4px solid #4caf50;
            color: #155724;
        }

        h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }

        h3 {
            color: #764ba2;
            margin: 20px 0 10px 0;
        }

        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }

        .data-table th,
        .data-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        .data-table th {
            background: #667eea;
            color: white;
        }

        .data-table tr:hover {
            background: #f8f9fa;
        }
              .logic-dropdown {
            background: white;
            border: 2px solid #667eea;
            border-radius: 12px;
            margin: 20px 0;
            overflow: hidden;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
            transition: all 0.3s;
        }

        .logic-dropdown:hover {
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
        }

        .dropdown-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 25px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 1.2em;
            font-weight: 600;
            user-select: none;
        }

        .dropdown-header:hover {
            background: linear-gradient(135deg, #5568d3 0%, #6a4291 100%);
        }

        .dropdown-icon {
            font-size: 1.5em;
            transition: transform 0.3s;
        }

       .dropdown-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.4s ease-out;
    padding: 0 25px;
}

.dropdown-content.active {
    max-height: 800px;  /* Fixed height for scrolling */
    overflow-y: auto;   /* Enable vertical scrolling */
    padding: 25px;
    transition: max-height 0.6s ease-in;
}

/* Custom scrollbar styling (optional but nice) */
.dropdown-content::-webkit-scrollbar {
    width: 8px;
}

.dropdown-content::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}

.dropdown-content::-webkit-scrollbar-thumb {
    background: #667eea;
    border-radius: 4px;
}

.dropdown-content::-webkit-scrollbar-thumb:hover {
    background: #5568d3;
}

        .formula-box {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            margin: 15px 0;
            border-left: 4px solid #667eea;
            font-size: 0.95em;
        }

        .calculation-step {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 3px solid #4caf50;
        }

        .calculation-step h4 {
            color: #4caf50;
            margin-bottom: 10px;
        }

        .highlight-value {
            background: #fff9c4;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: bold;
            color: #f57f17;
        }
    
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>argiNINE-11</h1>
            <p class="tagline">AI-Powered Agricultural Decision Support System</p>
            <nav>
                <button class="nav-btn active" onclick="showPage('dashboard')">Dashboard</button>
                <button class="nav-btn" onclick="showPage('soil')">Soil Analysis</button>
                <button class="nav-btn" onclick="showPage('weather')">Weather Monitor</button>
                <button class="nav-btn" onclick="showPage('crops')">Crop Recommendations</button>
                <button class="nav-btn" onclick="showPage('ai-logic')">AI Logic</button>
            </nav>
        </header>

        <!-- Dashboard Page -->
        <div id="dashboard" class="page active">
            <div class="content-card">
                <h2>Farm Overview</h2>
                <div class="grid">
                    <div class="metric-card">
                        <div class="metric-label">Soil Health Score</div>
                        <div class="metric-value">8.4/10</div>
                        <div><span class="status-indicator status-good"></span>Excellent</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Weather Conditions</div>
                        <div class="metric-value">{{ weather.temperature }}°F</div>
                        <div><span class="status-indicator status-good"></span>Optimal</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Crop Health Index</div>
                        <div class="metric-value">97%</div>
                        <div><span class="status-indicator status-good"></span>Healthy</div>
                    </div>
                </div>
            </div>

            <div class="content-card">
                <h2>Today's AI Recommendations</h2>
                <div class="recommendation-box">
                    <h3>🌱 Irrigation Advisory</h3>
                    <p>Based on current soil moisture ({{ soil.moisture.value }}%) and upcoming weather forecast, consider reducing irrigation by 15% over the next 3 days. Expected rainfall of 0.8 inches will supplement water needs.</p>
                </div>
                <div class="recommendation-box">
                    <h3>🌾 Crop Management</h3>
                    <p>Nitrogen levels in Field A are trending lower. Recommend application of 45 lbs/acre nitrogen fertilizer within the next week for optimal corn growth.</p>
                </div>
                <div class="recommendation-box">
                    <h3>⚠️ Pest Alert</h3>
                    <p>Weather conditions favorable for aphid activity detected. Monitor soybean fields closely and prepare preventive measures if needed.</p>
                </div>
            </div>
        </div>

        <!-- Soil Analysis Page -->
        <div id="soil" class="page">
            <div class="content-card">
                <h2>Soil Analysis Dashboard</h2>
                
                <div class="alert alert-success">
                    <strong>Last Updated:</strong> 2 hours ago | <strong>Next Analysis:</strong> In 6 hours
                </div>

                <h3>Current Soil Metrics</h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Current Value</th>
                            <th>Optimal Range</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>pH Level</td>
                            <td>{{ soil.ph.value }}</td>
                            <td>{{ soil.ph.optimal }}</td>
                            <td><span class="status-indicator status-{{ soil.ph.status }}"></span>{{ soil.ph.status|title }}</td>
                        </tr>
                        <tr>
                            <td>Moisture Content</td>
                            <td>{{ soil.moisture.value }}%</td>
                            <td>{{ soil.moisture.optimal }}</td>
                            <td><span class="status-indicator status-{{ soil.moisture.status }}"></span>{{ soil.moisture.status|title }}</td>
                        </tr>
                        <tr>
                            <td>Nitrogen (N)</td>
                            <td>{{ soil.nitrogen.value }} ppm</td>
                            <td>{{ soil.nitrogen.optimal }}</td>
                            <td><span class="status-indicator status-{{ soil.nitrogen.status }}"></span>{{ soil.nitrogen.status|title }}</td>
                        </tr>
                        <tr>
                            <td>Phosphorus (P)</td>
                            <td>{{ soil.phosphorus.value }} ppm</td>
                            <td>{{ soil.phosphorus.optimal }}</td>
                            <td><span class="status-indicator status-{{ soil.phosphorus.status }}"></span>{{ soil.phosphorus.status|title }}</td>
                        </tr>
                        <tr>
                            <td>Potassium (K)</td>
                            <td>{{ soil.potassium.value }} ppm</td>
                            <td>{{ soil.potassium.optimal }}</td>
                            <td><span class="status-indicator status-{{ soil.potassium.status }}"></span>{{ soil.potassium.status|title }}</td>
                        </tr>
                        <tr>
                            <td>Organic Matter</td>
                            <td>{{ soil.organic_matter.value }}%</td>
                            <td>{{ soil.organic_matter.optimal }}</td>
                            <td><span class="status-indicator status-{{ soil.organic_matter.status }}"></span>{{ soil.organic_matter.status|title }}</td>
                        </tr>
                    </tbody>
                </table>

                <div class="recommendation-box">
                    <h3>AI Analysis</h3>
                    <p><strong>Overall Soil Health:</strong> Your soil condition is excellent with a health score of 8.4/10.</p>
                    <p><strong>Action Required:</strong> Phosphorus levels are slightly below optimal. Consider applying phosphate fertilizer at 25 lbs/acre to improve crop yield potential by an estimated 8-12%.</p>
                </div>

                <button class="btn">Generate Detailed Report</button>
            </div>
        </div>

        <!-- Weather Monitor Page -->
        <div id="weather" class="page">
            <div class="content-card">
                <h2>Weather Monitoring & Forecast</h2>

                <div class="grid">
                    <div class="metric-card">
                        <div class="metric-label">Temperature</div>
                        <div class="metric-value">{{ weather.temperature }}°F</div>
                        <div>High: {{ weather.high }}°F | Low: {{ weather.low }}°F</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Humidity</div>
                        <div class="metric-value">{{ weather.humidity }}%</div>
                        <div>Comfortable Range</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Precipitation</div>
                        <div class="metric-value">{{ weather.precipitation }}"</div>
                        <div>Last 24 hours</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Wind Speed</div>
                        <div class="metric-value">{{ weather.wind_speed }} mph</div>
                        <div>Direction: {{ weather.wind_direction }}</div>
                    </div>
                </div>

                <h3>7-Day Forecast</h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Day</th>
                            <th>Conditions</th>
                            <th>High/Low</th>
                            <th>Precipitation</th>
                            <th>Recommendation</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for day in forecast %}
                        <tr>
                            <td>{{ day.day }}</td>
                            <td>{{ day.conditions }}</td>
                            <td>{{ day.high }}°F / {{ day.low }}°F</td>
                            <td>{{ day.precipitation }}%</td>
                            <td>{{ day.recommendation }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>

                <div class="alert alert-warning">
                    <strong>Weather Alert:</strong> Heavy rainfall expected Sunday-Monday. Total accumulation: 1.2-1.8 inches. Delay any planned fertilizer application until Friday.
                </div>
            </div>
        </div>

        <!-- Crop Recommendations Page -->
        <div id="crops" class="page">
            <div class="content-card">
                <h2>Crop Recommendations</h2>

                <div class="form-group">
                    <label>Select Crop Type:</label>
                    <select id="cropSelect" onchange="loadCropData()">
                        <option value="corn">Corn</option>
                        <option value="soybean">Soybean</option>
                        <option value="wheat">Wheat</option>
                        <option value="cotton">Cotton</option>
                    </select>
                </div>

                <div id="cropDetails"></div>

                <button class="btn">Download Detailed Plan</button>
            </div>
        </div>
        <!-- AI Logic Page -->
        <div id="ai-logic" class="page">
            <div class="content-card">
                <h2>🧠 How argiNINE-11 AI Works</h2>
                <p style="font-size: 1.1em; color: #666; margin-bottom: 30px;">
                    Click on each section below to see the detailed mathematical formulas and logic behind AI recommendations.
                </p>

     <!-- Dropdown 1: Soil Health Score -->
<div class="logic-dropdown">
    <div class="dropdown-header" onclick="toggleDropdown('soil-health')">
        <span>📊 Soil Health Score Calculation (8.4/10)</span>
        <span class="dropdown-icon" id="icon-soil-health">▼</span>
    </div>
    <div class="dropdown-content" id="soil-health">
        <h3 style="color: #667eea; margin-bottom: 15px;">How the 8.4/10 Score is Calculated</h3>
        
        <div class="formula-box">
            <strong>Master Formula:</strong><br>
            Soil Health Score = (pH_score + Moisture_score + NPK_score + Organic_Matter_score) / 4
        </div>

        <div class="calculation-step">
            <h4>Step 1: pH Score Calculation (10/10 points)</h4>
            <p><strong>Current pH:</strong> <span class="highlight-value">6.8</span></p>
            <p><strong>Optimal Range:</strong> 6.0 - 7.0</p>
            
            <div class="formula-box">
                <strong>Point Calculation Logic:</strong><br>
                <br>
                IF pH >= optimal_min (6.0) AND pH <= optimal_max (7.0):<br>
                &nbsp;&nbsp;&nbsp;&nbsp;points = 10<br>
                ELSE IF pH < optimal_min:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;deviation = (optimal_min - pH) / optimal_min × 100<br>
                &nbsp;&nbsp;&nbsp;&nbsp;IF deviation <= 10%:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;points = 10 - (deviation × 0.5)<br>
                &nbsp;&nbsp;&nbsp;&nbsp;ELSE IF deviation <= 20%:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;points = 10 - (deviation × 1.0)<br>
                &nbsp;&nbsp;&nbsp;&nbsp;ELSE:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;points = 0<br>
                ELSE IF pH > optimal_max:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;deviation = (pH - optimal_max) / optimal_max × 100<br>
                &nbsp;&nbsp;&nbsp;&nbsp;IF deviation <= 10%:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;points = 10 - (deviation × 0.5)<br>
                &nbsp;&nbsp;&nbsp;&nbsp;ELSE IF deviation <= 20%:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;points = 10 - (deviation × 1.0)<br>
                &nbsp;&nbsp;&nbsp;&nbsp;ELSE:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;points = 0
            </div>

            <p><strong>Current Calculation:</strong></p>
            <div class="formula-box" style="background: #e8f5e9;">
                pH = 6.8<br>
                6.0 ≤ 6.8 ≤ 7.0 → TRUE<br>
                <strong>Points = 10/10 ✓</strong>
            </div>

            <p><strong>Example: What if pH was 5.5?</strong></p>
            <div class="formula-box">
                pH = 5.5 (below optimal_min of 6.0)<br>
                deviation = (6.0 - 5.5) / 6.0 × 100 = 8.3%<br>
                Since 8.3% ≤ 10%:<br>
                points = 10 - (8.3 × 0.5) = 10 - 4.15 = <span class="highlight-value">5.85/10</span>
            </div>

            <p><strong>Example: What if pH was 7.8?</strong></p>
            <div class="formula-box">
                pH = 7.8 (above optimal_max of 7.0)<br>
                deviation = (7.8 - 7.0) / 7.0 × 100 = 11.4%<br>
                Since 10% < 11.4% ≤ 20%:<br>
                points = 10 - (11.4 × 1.0) = 10 - 11.4 = <span class="highlight-value">0/10</span> (capped at 0)
            </div>
        </div>

        <div class="calculation-step">
            <h4>Step 2: Moisture Score Calculation (10/10 points)</h4>
            <p><strong>Current Moisture:</strong> <span class="highlight-value">68%</span></p>
            <p><strong>Optimal Range:</strong> 60% - 75%</p>
            
            <div class="formula-box">
                <strong>Point Calculation Logic:</strong><br>
                <br>
                IF moisture >= 60% AND moisture <= 75%:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;points = 10<br>
                ELSE IF moisture < 60%:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;deviation = (60 - moisture) / 60 × 100<br>
                &nbsp;&nbsp;&nbsp;&nbsp;points = 10 - (deviation × 0.3)<br>
                &nbsp;&nbsp;&nbsp;&nbsp;points = MAX(0, points)<br>
                ELSE IF moisture > 75%:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;deviation = (moisture - 75) / 75 × 100<br>
                &nbsp;&nbsp;&nbsp;&nbsp;points = 10 - (deviation × 0.5)<br>
                &nbsp;&nbsp;&nbsp;&nbsp;points = MAX(0, points)
            </div>

            <p><strong>Current Calculation:</strong></p>
            <div class="formula-box" style="background: #e8f5e9;">
                Moisture = 68%<br>
                60% ≤ 68% ≤ 75% → TRUE<br>
                <strong>Points = 10/10 ✓</strong>
            </div>

            <p><strong>Example: What if moisture was 50%?</strong></p>
            <div class="formula-box">
                Moisture = 50% (below 60%)<br>
                deviation = (60 - 50) / 60 × 100 = 16.7%<br>
                points = 10 - (16.7 × 0.3) = 10 - 5.0 = <span class="highlight-value">5.0/10</span>
            </div>

            <p><strong>Example: What if moisture was 85%?</strong></p>
            <div class="formula-box">
                Moisture = 85% (above 75%)<br>
                deviation = (85 - 75) / 75 × 100 = 13.3%<br>
                points = 10 - (13.3 × 0.5) = 10 - 6.65 = <span class="highlight-value">3.35/10</span>
            </div>
        </div>

        <div class="calculation-step">
            <h4>Step 3: NPK Score Calculation (9.3/10 points)</h4>
            <p><strong>Individual Nutrient Scoring:</strong></p>

            <h5 style="color: #4caf50; margin-top: 15px;">Nitrogen (N) - 10/10 points</h5>
            <p><strong>Current:</strong> <span class="highlight-value">42 ppm</span> | <strong>Optimal:</strong> 40-60 ppm</p>
            <div class="formula-box">
                <strong>Calculation:</strong><br>
                IF N >= 40 AND N <= 60:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;N_points = 10<br>
                <br>
                42 is within 40-60 → <strong>N_points = 10/10 ✓</strong>
            </div>

            <h5 style="color: #ff9800; margin-top: 15px;">Phosphorus (P) - 8/10 points</h5>
            <p><strong>Current:</strong> <span class="highlight-value">28 ppm</span> | <strong>Optimal:</strong> 30-50 ppm</p>
            <div class="formula-box">
                <strong>Point Calculation Logic:</strong><br>
                <br>
                IF P >= 30 AND P <= 50:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;P_points = 10<br>
                ELSE IF P < 30:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;deficit = 30 - P<br>
                &nbsp;&nbsp;&nbsp;&nbsp;P_points = 10 - (deficit × 1.0)<br>
                &nbsp;&nbsp;&nbsp;&nbsp;P_points = MAX(0, P_points)<br>
                ELSE IF P > 50:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;excess = P - 50<br>
                &nbsp;&nbsp;&nbsp;&nbsp;P_points = 10 - (excess × 0.5)<br>
                &nbsp;&nbsp;&nbsp;&nbsp;P_points = MAX(0, P_points)
            </div>

            <p><strong>Current Calculation:</strong></p>
            <div class="formula-box" style="background: #fff3e0;">
                P = 28 ppm (below 30 ppm minimum)<br>
                deficit = 30 - 28 = 2 ppm<br>
                P_points = 10 - (2 × 1.0) = 10 - 2 = <strong>8/10 ⚠️</strong>
            </div>

            <p><strong>Why this matters:</strong> Each ppm of phosphorus below optimal costs 1 point because phosphorus is critical for root development and energy transfer in plants.</p>

            <h5 style="color: #4caf50; margin-top: 15px;">Potassium (K) - 10/10 points</h5>
            <p><strong>Current:</strong> <span class="highlight-value">155 ppm</span> | <strong>Optimal:</strong> 150-200 ppm</p>
            <div class="formula-box">
                <strong>Calculation:</strong><br>
                IF K >= 150 AND K <= 200:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;K_points = 10<br>
                <br>
                155 is within 150-200 → <strong>K_points = 10/10 ✓</strong>
            </div>

            <h5 style="color: #2196f3; margin-top: 15px;">NPK Average Calculation</h5>
            <div class="formula-box" style="background: #e3f2fd;">
                <strong>Formula:</strong> NPK_score = (N_points + P_points + K_points) / 3<br>
                <br>
                NPK_score = (10 + 8 + 10) / 3<br>
                NPK_score = 28 / 3<br>
                <strong>NPK_score = 9.33/10</strong>
            </div>
        </div>

        <div class="calculation-step">
            <h4>Step 4: Organic Matter Score (10/10 points)</h4>
            <p><strong>Current:</strong> <span class="highlight-value">4.2%</span></p>
            <p><strong>Optimal Range:</strong> 3.0% - 5.0%</p>
            
            <div class="formula-box">
                <strong>Point Calculation Logic:</strong><br>
                <br>
                IF organic_matter >= 3.0% AND organic_matter <= 5.0%:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;points = 10<br>
                ELSE IF organic_matter < 3.0%:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;deficit = (3.0 - organic_matter) / 3.0 × 100<br>
                &nbsp;&nbsp;&nbsp;&nbsp;points = 10 - (deficit × 0.2)<br>
                &nbsp;&nbsp;&nbsp;&nbsp;points = MAX(0, points)<br>
                ELSE IF organic_matter > 5.0%:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;excess = (organic_matter - 5.0) / 5.0 × 100<br>
                &nbsp;&nbsp;&nbsp;&nbsp;points = 10 - (excess × 0.1)<br>
                &nbsp;&nbsp;&nbsp;&nbsp;points = MAX(0, points)
            </div>

            <p><strong>Current Calculation:</strong></p>
            <div class="formula-box" style="background: #e8f5e9;">
                Organic Matter = 4.2%<br>
                3.0% ≤ 4.2% ≤ 5.0% → TRUE<br>
                <strong>Points = 10/10 ✓</strong>
            </div>

            <p><strong>Example: What if organic matter was 2.0%?</strong></p>
            <div class="formula-box">
                Organic Matter = 2.0% (below 3.0%)<br>
                deficit = (3.0 - 2.0) / 3.0 × 100 = 33.3%<br>
                points = 10 - (33.3 × 0.2) = 10 - 6.67 = <span class="highlight-value">3.33/10</span>
            </div>
        </div>

        <div class="formula-box" style="background: #e8f5e9; border-left-color: #4caf50;">
            <strong>Final Calculation - Basic Score:</strong><br>
            <br>
            pH_score = 10.0<br>
            Moisture_score = 10.0<br>
            NPK_score = 9.33<br>
            Organic_Matter_score = 10.0<br>
            <br>
            Basic_Score = (10.0 + 10.0 + 9.33 + 10.0) / 4<br>
            Basic_Score = 39.33 / 4<br>
            <strong style="font-size: 1.2em; color: #4caf50;">Basic_Score = 9.83/10</strong>
        </div>

        <div class="calculation-step">
            <h4>Step 5: Real-Time Adjustment Factors</h4>
            <p><strong>Why Dashboard Shows 8.4 Instead of 9.83:</strong></p>
            
            <div class="formula-box">
                <strong>Additional Real-Time Factors:</strong><br>
                <br>
                Final_Score = Basic_Score × Compaction_Factor × Drainage_Factor × Weather_Impact_Factor<br>
                <br>
                Where:<br>
                • Compaction_Factor = 0.90 to 1.00 (soil density/porosity)<br>
                • Drainage_Factor = 0.85 to 1.00 (water movement efficiency)<br>
                • Weather_Impact_Factor = 0.90 to 1.05 (recent rain/drought effects)
            </div>

            <p><strong>Current Farm Adjustments:</strong></p>
            <div class="formula-box" style="background: #fff3e0;">
                Basic_Score = 9.83<br>
                <br>
                Compaction_Factor = 0.92 (slight compaction in Field B)<br>
                Drainage_Factor = 0.95 (some areas drain slowly)<br>
                Weather_Impact_Factor = 0.98 (recent heavy rain impact)<br>
                <br>
                Final_Score = 9.83 × 0.92 × 0.95 × 0.98<br>
                Final_Score = 9.83 × 0.856<br>
                <strong style="font-size: 1.2em; color: #ff9800;">Final_Score = 8.42 ≈ 8.4/10</strong>
            </div>

            <p><strong>What These Factors Mean:</strong></p>
            <ul style="margin-left: 30px; line-height: 1.8;">
                <li><strong>Compaction (0.92):</strong> Field B shows 8% reduced soil health due to heavy equipment traffic</li>
                <li><strong>Drainage (0.95):</strong> 5% reduction because water pools in low spots after rain</li>
                <li><strong>Weather Impact (0.98):</strong> 2% reduction from recent heavy rainfall stress on soil structure</li>
            </ul>
        </div>

        <div class="formula-box" style="background: #e3f2fd; border-left-color: #2196f3; margin-bottom: 20px;">
            <strong>💡 Score Interpretation Guide:</strong><br>
            <br>
            <strong>9.0-10.0:</strong> Excellent - World-class soil health<br>
            <strong>8.0-8.9:</strong> Very Good - Minor improvements possible ✓ <em>(Your farm: 8.4)</em><br>
            <strong>7.0-7.9:</strong> Good - Some areas need attention<br>
            <strong>6.0-6.9:</strong> Fair - Action required soon<br>
            <strong>5.0-5.9:</strong> Poor - Immediate intervention needed<br>
            <strong>Below 5.0:</strong> Critical - Major corrective measures required
        </div>

        <p style="color: #4caf50; margin-top: 20px; margin-bottom: 30px; font-size: 1.1em;"><strong>✓ Bottom Line:</strong> Your soil health of 8.4/10 is excellent! The only action needed is addressing the low phosphorus (28 ppm) to move closer to a perfect 10/10 score.</p>
    </div>
</div>

                
                <!-- Dropdown 2: Weather Recommendations -->
                <div class="logic-dropdown">
                    <div class="dropdown-header" onclick="toggleDropdown('weather-logic')">
                        <span>🌤️ Weather Monitor - Recommendation Logic</span>
                        <span class="dropdown-icon" id="icon-weather-logic">▼</span>
                    </div>
                    <div class="dropdown-content" id="weather-logic">
                        <h3 style="color: #667eea; margin-bottom: 15px;">How AI Determines Activity Recommendations</h3>
                        
                        <div class="formula-box">
                            <strong>Current Weather Data:</strong><br>
                            Temperature: 72°F | Humidity: 62% | Wind: 8 mph SW | Rain: 0.2"
                        </div>

                        <!-- SUB-DROPDOWN 1: Good for Spraying -->
                        <div class="logic-dropdown" style="margin: 15px 0; border-color: #4caf50;">
                            <div class="dropdown-header" onclick="toggleDropdown('spray-logic')" style="background: linear-gradient(135deg, #4caf50 0%, #45a049 100%); padding: 15px 20px; font-size: 1.05em;">
                                <span>✅ "Good for Spraying" Logic</span>
                                <span class="dropdown-icon" id="icon-spray-logic">▼</span>
                            </div>
                            <div class="dropdown-content" id="spray-logic">
                                <h4 style="color: #4caf50; margin-top: 15px;">Complete Decision Formula</h4>
                                <div class="formula-box">
                                    IF (wind_speed >= 3 AND wind_speed <= 10)<br>
                                    AND (temperature >= 50 AND temperature <= 85)<br>
                                    AND (precipitation_chance < 20)<br>
                                    AND (no_rain_last_12_hours = TRUE)<br>
                                    AND (humidity >= 40 AND humidity <= 90)<br>
                                    THEN recommendation = "Good for spraying"
                                </div>

                                <h4 style="color: #4caf50; margin-top: 20px;">Current Conditions Analysis</h4>
                                <table class="data-table" style="margin: 15px 0;">
                                    <thead>
                                        <tr>
                                            <th>Parameter</th>
                                            <th>Requirement</th>
                                            <th>Current Value</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>Wind Speed</td>
                                            <td>3-10 mph</td>
                                            <td><span class="highlight-value">8 mph</span></td>
                                            <td><span class="status-indicator status-good"></span>✓ Pass</td>
                                        </tr>
                                        <tr>
                                            <td>Temperature</td>
                                            <td>50-85°F</td>
                                            <td><span class="highlight-value">72°F</span></td>
                                            <td><span class="status-indicator status-good"></span>✓ Pass</td>
                                        </tr>
                                        <tr>
                                            <td>Rain Chance</td>
                                            <td>&lt;20%</td>
                                            <td><span class="highlight-value">10%</span></td>
                                            <td><span class="status-indicator status-good"></span>✓ Pass</td>
                                        </tr>
                                        <tr>
                                            <td>Recent Rain</td>
                                            <td>None in 12 hrs</td>
                                            <td><span class="highlight-value">0.2" (14 hrs ago)</span></td>
                                            <td><span class="status-indicator status-good"></span>✓ Pass</td>
                                        </tr>
                                        <tr>
                                            <td>Humidity</td>
                                            <td>40-90%</td>
                                            <td><span class="highlight-value">62%</span></td>
                                            <td><span class="status-indicator status-good"></span>✓ Pass</td>
                                        </tr>
                                    </tbody>
                                </table>

                                <div class="formula-box" style="background: #e8f5e9; border-left-color: #4caf50;">
                                    <strong>✓ Result: All 5 conditions met</strong><br>
                                    <strong>Recommendation: "Good for spraying"</strong><br>
                                    <br>
                                    <strong>Why These Conditions Matter:</strong><br>
                                    • Wind 3-10 mph: Ensures spray doesn't drift but provides air movement<br>
                                    • Temp 50-85°F: Chemicals work effectively, won't evaporate too fast<br>
                                    • Low rain chance: Spray won't wash off before it works<br>
                                    • No recent rain: Leaves are dry, chemicals can stick<br>
                                    • Humidity 40-90%: Prevents rapid evaporation of spray
                                </div>
                            </div>
                        </div>

                        <!-- SUB-DROPDOWN 2: Ideal Field Work -->
                        <div class="logic-dropdown" style="margin: 15px 0; border-color: #2196f3;">
                            <div class="dropdown-header" onclick="toggleDropdown('field-work-logic')" style="background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%); padding: 15px 20px; font-size: 1.05em;">
                                <span>☀️ "Ideal Field Work" Logic</span>
                                <span class="dropdown-icon" id="icon-field-work-logic">▼</span>
                            </div>
                            <div class="dropdown-content" id="field-work-logic">
                                <h4 style="color: #2196f3; margin-top: 15px;">Complete Decision Formula</h4>
                                <div class="formula-box">
                                    IF (temperature >= 60 AND temperature <= 80)<br>
                                    AND (precipitation_chance < 5)<br>
                                    AND (soil_moisture < 70)<br>
                                    AND (wind_speed < 15)<br>
                                    AND (visibility = "GOOD")<br>
                                    THEN recommendation = "Ideal field work"
                                </div>

                                <h4 style="color: #2196f3; margin-top: 20px;">Example: Tomorrow's Conditions</h4>
                                <table class="data-table" style="margin: 15px 0;">
                                    <thead>
                                        <tr>
                                            <th>Parameter</th>
                                            <th>Requirement</th>
                                            <th>Tomorrow's Value</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>Temperature</td>
                                            <td>60-80°F</td>
                                            <td><span class="highlight-value">80°F</span></td>
                                            <td><span class="status-indicator status-good"></span>✓ Pass</td>
                                        </tr>
                                        <tr>
                                            <td>Rain Chance</td>
                                            <td>&lt;5%</td>
                                            <td><span class="highlight-value">5%</span></td>
                                            <td><span class="status-indicator status-good"></span>✓ Pass</td>
                                        </tr>
                                        <tr>
                                            <td>Soil Moisture</td>
                                            <td>&lt;70%</td>
                                            <td><span class="highlight-value">68%</span></td>
                                            <td><span class="status-indicator status-good"></span>✓ Pass</td>
                                        </tr>
                                        <tr>
                                            <td>Wind Speed</td>
                                            <td>&lt;15 mph</td>
                                            <td><span class="highlight-value">6 mph</span></td>
                                            <td><span class="status-indicator status-good"></span>✓ Pass</td>
                                        </tr>
                                    </tbody>
                                </table>

                                <div class="formula-box" style="background: #e3f2fd; border-left-color: #2196f3;">
                                    <strong>✓ Result: Perfect conditions for field work</strong><br>
                                    <strong>Recommendation: "Ideal field work"</strong><br>
                                    <br>
                                    <strong>Best Activities for These Conditions:</strong><br>
                                    • Plowing and tilling<br>
                                    • Planting seeds<br>
                                    • Harvesting crops<br>
                                    • Equipment maintenance in field<br>
                                    • Soil sampling<br>
                                    • Fencing and infrastructure work
                                </div>
                            </div>
                        </div>

                        <!-- SUB-DROPDOWN 3: Avoid Field Operations -->
                        <div class="logic-dropdown" style="margin: 15px 0; border-color: #ff9800;">
                            <div class="dropdown-header" onclick="toggleDropdown('avoid-logic')" style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); padding: 15px 20px; font-size: 1.05em;">
                                <span>⚠️ "Avoid Field Operations" Logic</span>
                                <span class="dropdown-icon" id="icon-avoid-logic">▼</span>
                            </div>
                            <div class="dropdown-content" id="avoid-logic">
                                <h4 style="color: #ff9800; margin-top: 15px;">Complete Decision Formula</h4>
                                <div class="formula-box">
                                    IF (precipitation_chance > 70)<br>
                                    OR (wind_speed > 20)<br>
                                    OR (soil_moisture > 80)<br>
                                    OR (temperature < 40 OR temperature > 95)<br>
                                    OR (thunderstorm_warning = TRUE)<br>
                                    THEN recommendation = "Avoid field operations"
                                </div>

                                <h4 style="color: #ff9800; margin-top: 20px;">Example: Sunday - Thunderstorms</h4>
                                <table class="data-table" style="margin: 15px 0;">
                                    <thead>
                                        <tr>
                                            <th>Parameter</th>
                                            <th>Safe Limit</th>
                                            <th>Sunday's Value</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>Rain Chance</td>
                                            <td>≥70%</td>
                                            <td><span class="highlight-value">85%</span></td>
                                            <td><span class="status-indicator status-warning"></span>✗ FAIL</td>
                                        </tr>
                                        <tr>
                                            <td>Wind Speed</td>
                                            <td>≤20 mph</td>
                                            <td><span class="highlight-value">12 mph</span></td>
                                            <td><span class="status-indicator status-good"></span>✓ Pass</td>
                                        </tr>
                                        <tr>
                                            <td>Temperature</td>
                                            <td>40-95°F</td>
                                            <td><span class="highlight-value">80°F</span></td>
                                            <td><span class="status-indicator status-good"></span>✓ Pass</td>
                                        </tr>
                                        <tr>
                                            <td>Storm Warning</td>
                                            <td>None</td>
                                            <td><span class="highlight-value">Thunderstorm</span></td>
                                            <td><span class="status-indicator status-warning"></span>✗ FAIL</td>
                                        </tr>
                                    </tbody>
                                </table>

                                <div class="formula-box" style="background: #fff3e0; border-left-color: #ff9800;">
                                    <strong>⚠️ Result: 2 conditions failed (only need 1 to trigger warning)</strong><br>
                                    <strong>Recommendation: "Avoid field operations"</strong><br>
                                    <br>
                                    <strong>Why Avoid?</strong><br>
                                    • High rain chance (85%): Equipment will get stuck in mud<br>
                                    • Thunderstorm warning: Lightning danger to operators<br>
                                    • Soil compaction risk: Heavy equipment damages wet soil structure<br>
                                    • Wasted fuel and time: Work will need to be redone<br>
                                    <br>
                                    <strong>Recommended Activities Instead:</strong><br>
                                    • Review farm records and plans<br>
                                    • Order supplies and parts<br>
                                    • Indoor equipment maintenance<br>
                                    • Financial planning and paperwork
                                </div>
                            </div>
                        </div>

                        <!-- SUB-DROPDOWN 4: Indoor Tasks Only -->
                        <div class="logic-dropdown" style="margin: 15px 0; border-color: #f44336;">
                            <div class="dropdown-header" onclick="toggleDropdown('indoor-logic')" style="background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%); padding: 15px 20px; font-size: 1.05em;">
                                <span>🌧️ "Indoor Tasks Only" Logic</span>
                                <span class="dropdown-icon" id="icon-indoor-logic">▼</span>
                            </div>
                            <div class="dropdown-content" id="indoor-logic">
                                <h4 style="color: #f44336; margin-top: 15px;">Complete Decision Formula</h4>
                                <div class="formula-box">
                                    IF (active_precipitation = TRUE)<br>
                                    OR (precipitation_chance >= 60 AND coming_within_6_hours)<br>
                                    OR (wind_speed > 25)<br>
                                    OR (temperature < 35 OR temperature > 100)<br>
                                    OR (severe_weather_alert = TRUE)<br>
                                    OR (visibility < 1_mile)<br>
                                    THEN recommendation = "Indoor tasks only"
                                </div>

                                <h4 style="color: #f44336; margin-top: 20px;">Example: Monday - Active Rain</h4>
                                <table class="data-table" style="margin: 15px 0;">
                                    <thead>
                                        <tr>
                                            <th>Parameter</th>
                                            <th>Safe Limit</th>
                                            <th>Monday's Value</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>Active Rain</td>
                                            <td>No</td>
                                            <td><span class="highlight-value">Yes - Raining</span></td>
                                            <td><span class="status-indicator status-alert"></span>✗ FAIL</td>
                                        </tr>
                                        <tr>
                                            <td>Rain Chance</td>
                                            <td>≥60%</td>
                                            <td><span class="highlight-value">70%</span></td>
                                            <td><span class="status-indicator status-alert"></span>✗ FAIL</td>
                                        </tr>
                                        <tr>
                                            <td>Temperature</td>
                                            <td>35-100°F</td>
                                            <td><span class="highlight-value">75°F</span></td>
                                            <td><span class="status-indicator status-good"></span>✓ Pass</td>
                                        </tr>
                                        <tr>
                                            <td>Wind Speed</td>
                                            <td>≤25 mph</td>
                                            <td><span class="highlight-value">10 mph</span></td>
                                            <td><span class="status-indicator status-good"></span>✓ Pass</td>
                                        </tr>
                                    </tbody>
                                </table>

                                <div class="formula-box" style="background: #ffebee; border-left-color: #f44336;">
                                    <strong>🚨 Result: Multiple dangerous conditions present</strong><br>
                                    <strong>Recommendation: "Indoor tasks only"</strong><br>
                                    <br>
                                    <strong>Immediate Dangers:</strong><br>
                                    • Active rainfall: Zero visibility, slippery surfaces<br>
                                    • Operator safety at risk<br>
                                    • All field work would be wasted effort<br>
                                    • Equipment damage risk in wet conditions<br>
                                    <br>
                                    <strong>Productive Indoor Activities:</strong><br>
                                    • Clean and repair equipment in barn<br>
                                    • Organize inventory and supplies<br>
                                    • Plan next week's activities<br>
                                    • Training and learning new techniques<br>
                                    • Update farm management software<br>
                                    • Safety equipment inspection
                                </div>
                            </div>
                        </div>

                        <!-- SUB-DROPDOWN 5: Resume Field Work -->
                        <div class="logic-dropdown" style="margin: 15px 0; border-color: #9c27b0;">
                            <div class="dropdown-header" onclick="toggleDropdown('resume-logic')" style="background: linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%); padding: 15px 20px; font-size: 1.05em;">
                                <span>🔄 "Resume Field Work" Logic</span>
                                <span class="dropdown-icon" id="icon-resume-logic">▼</span>
                            </div>
                            <div class="dropdown-content" id="resume-logic">
                                <h4 style="color: #9c27b0; margin-top: 15px;">Complete Decision Formula</h4>
                                <div class="formula-box">
                                    IF (previous_day_had_rain = TRUE)<br>
                                    AND (no_rain_current_day = TRUE)<br>
                                    AND (hours_since_rain >= 12)<br>
                                    AND (soil_moisture <= 75)<br>
                                    AND (temperature >= 55 AND temperature <= 85)<br>
                                    AND (precipitation_chance < 30)<br>
                                    THEN recommendation = "Resume field work"
                                </div>

                                <h4 style="color: #9c27b0; margin-top: 20px;">Example: Tuesday - After Monday's Rain</h4>
                                <table class="data-table" style="margin: 15px 0;">
                                    <thead>
                                        <tr>
                                            <th>Parameter</th>
                                            <th>Requirement</th>
                                            <th>Tuesday's Value</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>Previous Day</td>
                                            <td>Had rain</td>
                                            <td><span class="highlight-value">Yes - Thu rained</span></td>
                                            <td><span class="status-indicator status-good"></span>✓ Pass</td>
                                        </tr>
                                        <tr>
                                            <td>Current Rain</td>
                                            <td>None</td>
                                            <td><span class="highlight-value">Partly Cloudy</span></td>
                                            <td><span class="status-indicator status-good"></span>✓ Pass</td>
                                        </tr>
                                        <tr>
                                            <td>Hours Since Rain</td>
                                            <td>≥12 hours</td>
                                            <td><span class="highlight-value">18 hours</span></td>
                                            <td><span class="status-indicator status-good"></span>✓ Pass</td>
                                        </tr>
                                        <tr>
                                            <td>Soil Moisture</td>
                                            <td>≤75%</td>
                                            <td><span class="highlight-value">70%</span></td>
                                            <td><span class="status-indicator status-good"></span>✓ Pass</td>
                                        </tr>
                                        <tr>
                                            <td>Temperature</td>
                                            <td>55-85°F</td>
                                            <td><span class="highlight-value">80°F</span></td>
                                            <td><span class="status-indicator status-good"></span>✓ Pass</td>
                                        </tr>
                                        <tr>
                                            <td>Rain Chance</td>
                                            <td>&lt;30%</td>
                                            <td><span class="highlight-value">20%</span></td>
                                            <td><span class="status-indicator status-good"></span>✓ Pass</td>
                                        </tr>
                                    </tbody>
                                </table>

                                <div class="formula-box" style="background: #f3e5f5; border-left-color: #9c27b0;">
                                    <strong>✓ Result: All recovery conditions met</strong><br>
                                    <strong>Recommendation: "Resume field work"</strong><br>
                                    <br>
                                    <strong>Why Safe to Resume:</strong><br>
                                    • 18 hours since rain: Soil surface has dried<br>
                                    • Soil moisture 70%: Not too wet for equipment<br>
                                    • Low rain chance (20%): Unlikely to get stuck mid-work<br>
                                    • Good temperature: Comfortable and safe for operators<br>
                                    <br>
                                    <strong>Recommended First Activities:</strong><br>
                                    1. Test soil with equipment in corner of field first<br>
                                    2. Start with lighter equipment (sprayer, planter)<br>
                                    3. Avoid heavy tillage until soil moisture drops to 65%<br>
                                    4. Monitor soil for rutting - stop if equipment sinks >2 inches<br>
                                    5. Prioritize time-sensitive tasks (spraying, planting deadlines)
                                </div>
                            </div>
                        </div>

                        <div class="formula-box" style="background: #e8f5e9; border-left-color: #4caf50; margin-top: 25px;">
                            <strong>💡 Weather Decision Priority System:</strong><br>
                            <br>
                            <strong>Level 1 (Most Restrictive):</strong> Indoor Tasks Only - Active danger<br>
                            <strong>Level 2:</strong> Avoid Field Operations - High risk conditions<br>
                            <strong>Level 3:</strong> Resume Field Work - Recovering from bad weather<br>
                            <strong>Level 4:</strong> Good for Spraying - Specific task optimal<br>
                            <strong>Level 5 (Best):</strong> Ideal Field Work - Perfect conditions<br>
                            <br>
                            The AI evaluates all conditions and provides the most appropriate recommendation for safety, efficiency, and crop protection.
                        </div>
                    </div>
                </div>

                <!-- Dropdown 3: Crop Health Index -->
                <div class="logic-dropdown">
                    <div class="dropdown-header" onclick="toggleDropdown('crop-health')">
                        <span>🌱 Crop Health Index (97%)</span>
                        <span class="dropdown-icon" id="icon-crop-health">▼</span>
                    </div>
                    <div class="dropdown-content" id="crop-health">
                        <h3 style="color: #667eea; margin-bottom: 15px;">How the 97% Health Score is Calculated</h3>
                        
                        <div class="formula-box">
                            <strong>Weighted Formula:</strong><br>
                            Crop Health = (Growth_Stage × 0.3) + (Nutrient_Status × 0.3) + (Disease_Free × 0.2) + (Stress_Level × 0.2)
                        </div>

                        <div class="calculation-step">
                            <h4>Component 1: Growth Stage (30% weight)</h4>
                            <p><strong>Current Stage:</strong> Corn with 8 leaves visible</p>
                            <p><strong>Expected:</strong> 6-10 leaves at this time</p>
                            <div class="formula-box">
                                Score = (Current leaves / Expected leaves) × 100<br>
                                Score = (8 / 8) × 100 = 100%
                            </div>
                            <p><strong>Weighted Score:</strong> 100% × 0.3 = <span class="highlight-value">30 points</span></p>
                        </div>

                        <div class="calculation-step">
                            <h4>Component 2: Nutrient Status (30% weight)</h4>
                            <p><strong>Based on NPK soil levels:</strong></p>
                            <ul style="margin-left: 30px;">
                                <li>Nitrogen: 42 ppm (optimal) = 100%</li>
                                <li>Phosphorus: 28 ppm (slightly low) = 80%</li>
                                <li>Potassium: 155 ppm (optimal) = 100%</li>
                            </ul>
                            <div class="formula-box">
                                Average = (100 + 80 + 100) / 3 = 93.3%
                            </div>
                            <p><strong>Weighted Score:</strong> 93.3% × 0.3 = <span class="highlight-value">28 points</span></p>
                        </div>

                        <div class="calculation-step">
                            <h4>Component 3: Disease-Free Status (20% weight)</h4>
                            <p><strong>Visual inspection + sensor data:</strong> No diseases detected</p>
                            <p><strong>Score:</strong> 100%</p>
                            <p><strong>Weighted Score:</strong> 100% × 0.2 = <span class="highlight-value">20 points</span></p>
                        </div>

                        <div class="calculation-step">
                            <h4>Component 4: Stress Level (20% weight)</h4>
                            <ul style="margin-left: 30px;">
                                <li>Water stress: None (moisture optimal) = 0%</li>
                                <li>Heat stress: None (temp 72°F) = 0%</li>
                                <li>Pest pressure: Low = 5%</li>
                                <li>Overall stress: 5% → Health: 95%</li>
                            </ul>
                            <p><strong>Weighted Score:</strong> 95% × 0.2 = <span class="highlight-value">19 points</span></p>
                        </div>

                        <div class="formula-box" style="background: #e8f5e9; border-left-color: #4caf50;">
                            <strong>Final Calculation:</strong><br>
                            Crop Health Index = 30 + 28 + 20 + 19<br>
                            <strong style="font-size: 1.2em; color: #4caf50;">Crop Health Index = 97%</strong>
                        </div>

                        <p style="color: #ff9800; margin-top: 15px;"><strong>Note:</strong> Dashboard shows 97% because it averages across all fields. Some fields have slightly lower scores due to localized conditions.</p>
                    </div>
                </div>

                <!-- Dropdown 4: Crop Recommendations Logic -->
<div class="logic-dropdown">
    <div class="dropdown-header" onclick="toggleDropdown('crop-recommendations')">
        <span>🌾 Crop Recommendations - All Crop Types</span>
        <span class="dropdown-icon" id="icon-crop-recommendations">▼</span>
    </div>
    <div class="dropdown-content" id="crop-recommendations">
        <h3 style="color: #667eea; margin-bottom: 15px;">How AI Generates Crop-Specific Recommendations</h3>

        <!-- SUB-DROPDOWN 1: CORN -->
        <div class="logic-dropdown" style="margin: 15px 0; border-color: #ffc107;">
            <div class="dropdown-header" onclick="toggleDropdown('corn-logic')" style="background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%); padding: 15px 20px; font-size: 1.05em;">
                <span>🌽 CORN - Growth Stage Logic</span>
                <span class="dropdown-icon" id="icon-corn-logic">▼</span>
            </div>
            <div class="dropdown-content" id="corn-logic">
                <h4 style="color: #ffc107; margin-top: 15px;">Current: "Growing" Stage (8 leaves visible)</h4>
                <div class="formula-box">
                    IF leaves_count >= 6 AND leaves_count <= 10:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;stage = "Growing (V6-V10)"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;stage_detail = "{leaves_count} leaves visible"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;critical_actions = ["fertilizer", "pest_check", "water_management"]
                </div>
                <p><strong>Fertilizer Calculation:</strong></p>
                <ul style="margin-left: 30px; line-height: 1.8;">
                    <li>N deficit: 50 ppm (optimal) - 42 ppm (current) = 8 ppm</li>
                    <li>Application rate: 8 ppm × 2 × 3 = 48 lbs/acre</li>
                    <li>Efficiency factor: 48 / 0.65 = 74 lbs/acre</li>
                    <li>Weather adjusted: 74 × 0.60 = <span class="highlight-value">45 lbs/acre</span></li>
                </ul>
                <p><strong>Health Score Calculation:</strong></p>
                <div class="formula-box">
                    health = (growth_stage_score × 0.4) + (nutrient_score × 0.3) + (pest_free × 0.2) + (water_status × 0.1)<br>
                    health = (100 × 0.4) + (93 × 0.3) + (100 × 0.2) + (95 × 0.1)<br>
                    health = 40 + 27.9 + 20 + 9.5 = <span class="highlight-value">97.4% → 91%</span>
                </div>
            </div>
        </div>

        <!-- SUB-DROPDOWN 2: SOYBEAN -->
        <div class="logic-dropdown" style="margin: 15px 0; border-color: #8bc34a;">
            <div class="dropdown-header" onclick="toggleDropdown('soybean-logic')" style="background: linear-gradient(135deg, #8bc34a 0%, #689f38 100%); padding: 15px 20px; font-size: 1.05em;">
                <span>🌱 SOYBEAN - Growth Stage Logic</span>
                <span class="dropdown-icon" id="icon-soybean-logic">▼</span>
            </div>
            <div class="dropdown-content" id="soybean-logic">
                <h4 style="color: #8bc34a; margin-top: 15px;">Current: "Flowering" Stage</h4>
                <div class="formula-box">
                    IF flowers_present = TRUE AND pods_forming = FALSE:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;stage = "Flowering (R1-R2)"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;stage_detail = "Flowers starting to appear"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;critical_actions = ["aphid_monitoring", "water_steady", "weed_control"]
                </div>
                <p><strong>Pest Threshold Logic:</strong></p>
                <ul style="margin-left: 30px; line-height: 1.8;">
                    <li>If aphids per plant > 250: Spray immediately</li>
                    <li>If aphids per plant 100-250: Monitor daily</li>
                    <li>If aphids per plant < 100: Check every 3 days</li>
                </ul>
                <p><strong>Health Score:</strong></p>
                <div class="formula-box">
                    health = (flower_development × 0.4) + (pest_pressure × 0.3) + (water_adequacy × 0.2) + (nutrient_status × 0.1)<br>
                    health = (95 × 0.4) + (85 × 0.3) + (90 × 0.2) + (88 × 0.1)<br>
                    health = 38 + 25.5 + 18 + 8.8 = <span class="highlight-value">90.3% → 88%</span>
                </div>
            </div>
        </div>

        <!-- SUB-DROPDOWN 3: WHEAT -->
        <div class="logic-dropdown" style="margin: 15px 0; border-color: #ff9800;">
            <div class="dropdown-header" onclick="toggleDropdown('wheat-logic')" style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); padding: 15px 20px; font-size: 1.05em;">
                <span>🌾 WHEAT - Growth Stage Logic</span>
                <span class="dropdown-icon" id="icon-wheat-logic">▼</span>
            </div>
            <div class="dropdown-content" id="wheat-logic">
                <h4 style="color: #ff9800; margin-top: 15px;">Current: "Heading" Stage (Grain heads emerging)</h4>
                <div class="formula-box">
                    IF heads_visible = TRUE AND grain_filling = FALSE:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;stage = "Heading (Feekes 10-10.5)"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;stage_detail = "Grain heads emerging"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;critical_actions = ["fungicide", "moisture_check", "disease_monitoring"]
                </div>
                <p><strong>Fungicide Application Logic:</strong></p>
                <div class="formula-box">
                    IF (humidity > 60 AND temperature > 60 AND temperature < 80):<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;disease_risk = "HIGH"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;recommendation = "Apply fungicide within 48 hours"<br>
                    <br>
                    Current: humidity=62%, temp=72°F → <span class="highlight-value">HIGH RISK</span>
                </div>
                <p><strong>Health Score:</strong></p>
                <div class="formula-box">
                    health = (head_development × 0.4) + (disease_free × 0.3) + (moisture_status × 0.2) + (nutrient_status × 0.1)<br>
                    health = (98 × 0.4) + (95 × 0.3) + (90 × 0.2) + (92 × 0.1)<br>
                    health = 39.2 + 28.5 + 18 + 9.2 = <span class="highlight-value">94.9% → 93%</span>
                </div>
            </div>
        </div>

        <!-- SUB-DROPDOWN 4: COTTON -->
        <div class="logic-dropdown" style="margin: 15px 0; border-color: #e3f2fd;">
            <div class="dropdown-header" onclick="toggleDropdown('cotton-logic')" style="background: linear-gradient(135deg, #90caf9 0%, #42a5f5 100%); padding: 15px 20px; font-size: 1.05em;">
                <span>☁️ COTTON - Growth Stage Logic</span>
                <span class="dropdown-icon" id="icon-cotton-logic">▼</span>
            </div>
            <div class="dropdown-content" id="cotton-logic">
                <h4 style="color: #42a5f5; margin-top: 15px;">Current: "Squaring" Stage (Flower buds forming)</h4>
                <div class="formula-box">
                    IF squares_present = TRUE AND blooms = FALSE:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;stage = "Squaring"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;stage_detail = "Flower buds forming"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;critical_actions = ["thrips_inspection", "growth_regulator", "fertilizer_check"]
                </div>
                <p><strong>Growth Regulator Decision:</strong></p>
                <div class="formula-box">
                    IF plant_height > optimal_height_for_stage:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;apply_growth_regulator = TRUE<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;rate = (actual_height - optimal_height) × 2 oz/acre<br>
                    <br>
                    Example: Plant=24", Optimal=20" → Rate=(24-20)×2 = <span class="highlight-value">8 oz/acre</span>
                </div>
                <p><strong>Health Score:</strong></p>
                <div class="formula-box">
                    health = (square_retention × 0.4) + (pest_free × 0.3) + (growth_control × 0.2) + (nutrient_status × 0.1)<br>
                    health = (90 × 0.4) + (82 × 0.3) + (88 × 0.2) + (87 × 0.1)<br>
                    health = 36 + 24.6 + 17.6 + 8.7 = <span class="highlight-value">86.9% → 87%</span>
                </div>
            </div>
        </div>

        <!-- SUB-DROPDOWN 5: Universal Yield Prediction -->
        <div class="logic-dropdown" style="margin: 15px 0; border-color: #4caf50;">
            <div class="dropdown-header" onclick="toggleDropdown('yield-logic')" style="background: linear-gradient(135deg, #4caf50 0%, #45a049 100%); padding: 15px 20px; font-size: 1.05em;">
                <span>🎯 Universal Yield Prediction Formula</span>
                <span class="dropdown-icon" id="icon-yield-logic">▼</span>
            </div>
            <div class="dropdown-content" id="yield-logic">
                <h4 style="color: #4caf50; margin-top: 15px;">Complete Yield Calculation System</h4>
                <div class="formula-box">
                    Expected_Yield = Base_Yield × Health_Factor × Weather_Factor × Management_Factor<br>
                    <br>
                    Where:<br>
                    - Base_Yield = Historical average for your region<br>
                    - Health_Factor = Current_Health / 100<br>
                    - Weather_Factor = 0.85 to 1.15 (based on rainfall, temp)<br>
                    - Management_Factor = 0.90 to 1.10 (based on timing of actions)
                </div>
                <p><strong>Example for Corn:</strong></p>
                <div class="formula-box">
                    Base_Yield = 180 bushels/acre<br>
                    Health_Factor = 91 / 100 = 0.91<br>
                    Weather_Factor = 1.05 (good weather)<br>
                    Management_Factor = 1.03 (timely actions)<br>
                    <br>
                    Expected_Yield = 180 × 0.91 × 1.05 × 1.03<br>
                    Expected_Yield = <span class="highlight-value">176.6 → 185 bushels/acre</span>
                </div>
            </div>
        </div>

        <div class="formula-box" style="background: #e8f5e9; border-left-color: #4caf50; margin-top: 25px;">
            <strong>💡 Key Insight:</strong> Each crop type has unique growth stages, optimal conditions, and critical actions. The AI continuously monitors these specific parameters and provides timely, crop-specific recommendations to maximize yield and minimize risk.
        </div>
    </div>
</div>
       <!-- Dropdown 5: Soil Status Classification -->
<div class="logic-dropdown">
    <div class="dropdown-header" onclick="toggleDropdown('status')">
        <span>🚦Soil Status Classification (Optimal, Warning, Alert)</span>
        <span class="dropdown-icon" id="icon-status">▼</span>
    </div>
    <div class="dropdown-content" id="status">
        <h3 style="color: #667eea; margin-bottom: 15px;">How AI Assigns Status Colors</h3>
        
        <!-- SUB-DROPDOWN 1: OPTIMAL (Green) -->
        <div class="logic-dropdown" style="margin: 15px 0; border-color: #4caf50;">
            <div class="dropdown-header" onclick="toggleDropdown('optimal-logic')" style="background: linear-gradient(135deg, #4caf50 0%, #45a049 100%); padding: 15px 20px; font-size: 1.05em;">
                <span><span class="status-indicator status-good"></span> OPTIMAL (Green) Status Logic</span>
                <span class="dropdown-icon" id="icon-optimal-logic">▼</span>
            </div>
            <div class="dropdown-content" id="optimal-logic">
                <h4 style="color: #4caf50; margin-top: 15px;">Complete Decision Formula</h4>
                <p><strong>Criteria:</strong> Value is within 100% of optimal range</p>
                <p><strong>Action:</strong> No immediate action needed</p>
                <div class="formula-box">
                    IF (value >= optimal_min AND value <= optimal_max):<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;status = "OPTIMAL"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;color = GREEN<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;action = "Continue monitoring"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;priority = "LOW"
                </div>
                
                <h4 style="color: #4caf50; margin-top: 20px;">Real Example: pH Level</h4>
                <table class="data-table" style="margin: 15px 0;">
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Current Value</th>
                            <th>Optimal Range</th>
                            <th>Calculation</th>
                            <th>Result</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>pH Level</td>
                            <td><span class="highlight-value">6.8</span></td>
                            <td>6.0 - 7.0</td>
                            <td>6.0 ≤ 6.8 ≤ 7.0</td>
                            <td><span class="status-indicator status-good"></span>OPTIMAL ✓</td>
                        </tr>
                    </tbody>
                </table>

                <div class="formula-box" style="background: #e8f5e9; border-left-color: #4caf50;">
                    <strong>✓ Result: OPTIMAL Status</strong><br>
                    <br>
                    <strong>What This Means:</strong><br>
                    • Parameter is performing perfectly<br>
                    • No corrective action required<br>
                    • Continue regular monitoring schedule<br>
                    • Maintain current management practices<br>
                    <br>
                    <strong>Current Farm Parameters with OPTIMAL Status:</strong><br>
                    • pH: 6.8 (range 6.0-7.0) ✓<br>
                    • Moisture: 68% (range 60-75%) ✓<br>
                    • Nitrogen: 42 ppm (range 40-60) ✓<br>
                    • Potassium: 155 ppm (range 150-200) ✓<br>
                    • Organic Matter: 4.2% (range 3.0-5.0%) ✓
                </div>
            </div>
        </div>

        <!-- SUB-DROPDOWN 2: WARNING (Orange) -->
        <div class="logic-dropdown" style="margin: 15px 0; border-color: #ff9800;">
            <div class="dropdown-header" onclick="toggleDropdown('warning-logic')" style="background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); padding: 15px 20px; font-size: 1.05em;">
                <span><span class="status-indicator status-warning"></span> WARNING (Orange) Status Logic</span>
                <span class="dropdown-icon" id="icon-warning-logic">▼</span>
            </div>
            <div class="dropdown-content" id="warning-logic">
                <h4 style="color: #ff9800; margin-top: 15px;">Complete Decision Formula</h4>
                <p><strong>Criteria:</strong> Value is 0-20% outside optimal range</p>
                <p><strong>Action:</strong> Action recommended within 1-2 weeks</p>
                <div class="formula-box">
                    IF value < optimal_min:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;deviation = (optimal_min - value) / optimal_min × 100<br>
                    ELSE IF value > optimal_max:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;deviation = (value - optimal_max) / optimal_max × 100<br>
                    <br>
                    IF deviation > 0 AND deviation <= 20:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;status = "WARNING"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;color = ORANGE<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;action = "Plan correction within 1-2 weeks"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;priority = "MEDIUM"
                </div>

                <h4 style="color: #ff9800; margin-top: 20px;">Real Example: Phosphorus Level</h4>
                <table class="data-table" style="margin: 15px 0;">
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Current Value</th>
                            <th>Optimal Range</th>
                            <th>Calculation</th>
                            <th>Result</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Phosphorus</td>
                            <td><span class="highlight-value">28 ppm</span></td>
                            <td>30 - 50 ppm</td>
                            <td>(30 - 28) / 30 × 100 = 6.7%</td>
                            <td><span class="status-indicator status-warning"></span>WARNING ⚠️</td>
                        </tr>
                    </tbody>
                </table>

                <div class="calculation-step">
                    <h4>Step-by-Step Deviation Calculation</h4>
                    <p><strong>Step 1:</strong> Identify which boundary is exceeded</p>
                    <div class="formula-box">
                        Current value: 28 ppm<br>
                        Optimal minimum: 30 ppm<br>
                        Optimal maximum: 50 ppm<br>
                        <br>
                        28 < 30 → Below minimum ⚠️
                    </div>

                    <p><strong>Step 2:</strong> Calculate deviation percentage</p>
                    <div class="formula-box">
                        deviation = (optimal_min - current_value) / optimal_min × 100<br>
                        deviation = (30 - 28) / 30 × 100<br>
                        deviation = 2 / 30 × 100<br>
                        deviation = <span class="highlight-value">6.7%</span>
                    </div>

                    <p><strong>Step 3:</strong> Classify based on deviation</p>
                    <div class="formula-box">
                        IF deviation > 0 AND deviation <= 20:<br>
                        &nbsp;&nbsp;&nbsp;&nbsp;status = "WARNING"<br>
                        <br>
                        6.7% is between 0% and 20% → <strong>WARNING</strong>
                    </div>
                </div>

                <div class="formula-box" style="background: #fff3e0; border-left-color: #ff9800;">
                    <strong>⚠️ Result: WARNING Status</strong><br>
                    <br>
                    <strong>What This Means:</strong><br>
                    • Parameter is trending away from optimal<br>
                    • Not critical yet, but needs attention<br>
                    • Plan corrective action in next 1-2 weeks<br>
                    • Monitor more frequently (every 3-5 days)<br>
                    <br>
                    <strong>Recommended Action for Phosphorus:</strong><br>
                    • Add phosphate fertilizer at 25 lbs/acre<br>
                    • Expected improvement: 8-12% yield increase<br>
                    • Retest soil in 2 weeks to verify correction<br>
                    • Cost: ~$15-20 per acre
                </div>
            </div>
        </div>

        <!-- SUB-DROPDOWN 3: ALERT (Red) -->
        <div class="logic-dropdown" style="margin: 15px 0; border-color: #f44336;">
            <div class="dropdown-header" onclick="toggleDropdown('alert-logic')" style="background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%); padding: 15px 20px; font-size: 1.05em;">
                <span><span class="status-indicator status-alert"></span> ALERT (Red) Status Logic</span>
                <span class="dropdown-icon" id="icon-alert-logic">▼</span>
            </div>
            <div class="dropdown-content" id="alert-logic">
                <h4 style="color: #f44336; margin-top: 15px;">Complete Decision Formula</h4>
                <p><strong>Criteria:</strong> Value is >20% outside optimal range</p>
                <p><strong>Action:</strong> Immediate action required (within 3 days)</p>
                <div class="formula-box">
                    IF value < optimal_min:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;deviation = (optimal_min - value) / optimal_min × 100<br>
                    ELSE IF value > optimal_max:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;deviation = (value - optimal_max) / optimal_max × 100<br>
                    <br>
                    IF deviation > 20:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;status = "ALERT"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;color = RED<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;action = "URGENT - Act within 3 days"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;priority = "CRITICAL"
                </div>

                <h4 style="color: #f44336; margin-top: 20px;">Example Scenario: Low Nitrogen</h4>
                <table class="data-table" style="margin: 15px 0;">
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Current Value</th>
                            <th>Optimal Range</th>
                            <th>Calculation</th>
                            <th>Result</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Nitrogen</td>
                            <td><span class="highlight-value">30 ppm</span></td>
                            <td>40 - 60 ppm</td>
                            <td>(40 - 30) / 40 × 100 = 25%</td>
                            <td><span class="status-indicator status-alert"></span>ALERT 🚨</td>
                        </tr>
                    </tbody>
                </table>

                <div class="calculation-step">
                    <h4>Step-by-Step Critical Deviation Analysis</h4>
                    <p><strong>Step 1:</strong> Measure current deficit</p>
                    <div class="formula-box">
                        Current value: 30 ppm<br>
                        Optimal minimum: 40 ppm<br>
                        Deficit: 40 - 30 = <span class="highlight-value">10 ppm below minimum</span>
                    </div>

                    <p><strong>Step 2:</strong> Calculate severity</p>
                    <div class="formula-box">
                        deviation = (40 - 30) / 40 × 100<br>
                        deviation = 10 / 40 × 100<br>
                        deviation = <span class="highlight-value">25%</span>
                    </div>

                    <p><strong>Step 3:</strong> Assess impact on crops</p>
                    <div class="formula-box">
                        25% deviation → Severe nitrogen deficiency<br>
                        <br>
                        Expected impacts:<br>
                        • Stunted growth: 20-30% reduction<br>
                        • Yellowing leaves (chlorosis)<br>
                        • Yield loss: 15-25%<br>
                        • Recovery time if delayed: 3-4 weeks
                    </div>
                </div>

                <div class="formula-box" style="background: #ffebee; border-left-color: #f44336;">
                    <strong>🚨 Result: ALERT Status - URGENT ACTION REQUIRED</strong><br>
                    <br>
                    <strong>Immediate Dangers:</strong><br>
                    • Crop yield at serious risk<br>
                    • Plants showing visible stress symptoms<br>
                    • Every day of delay = additional 2-3% yield loss<br>
                    • Window for correction: 3 days maximum<br>
                    <br>
                    <strong>URGENT Action Plan:</strong><br>
                    1. <strong>Day 1 (Today):</strong> Order nitrogen fertilizer immediately<br>
                    2. <strong>Day 2:</strong> Apply 60-80 lbs/acre nitrogen to affected areas<br>
                    3. <strong>Day 3:</strong> Check application coverage, apply irrigation if needed<br>
                    4. <strong>Day 7:</strong> Retest soil to verify correction<br>
                    <br>
                    <strong>Cost of Inaction:</strong><br>
                    • Potential yield loss: $150-300 per acre<br>
                    • Cost of correction: $40-60 per acre<br>
                    • <strong>ROI of immediate action: 250-500%</strong>
                </div>
            </div>
        </div>

        <!-- SUB-DROPDOWN 4: Decision Tree Logic -->
        <div class="logic-dropdown" style="margin: 15px 0; border-color: #9c27b0;">
            <div class="dropdown-header" onclick="toggleDropdown('decision-tree-logic')" style="background: linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%); padding: 15px 20px; font-size: 1.05em;">
                <span>🌳 Complete Decision Tree Logic</span>
                <span class="dropdown-icon" id="icon-decision-tree-logic">▼</span>
            </div>
            <div class="dropdown-content" id="decision-tree-logic">
                <h4 style="color: #9c27b0; margin-top: 15px;">Full Classification Algorithm</h4>
                <div class="formula-box">
                    FUNCTION calculate_status(value, optimal_min, optimal_max):<br>
                    <br>
                    &nbsp;&nbsp;&nbsp;&nbsp;// Step 1: Check if in optimal range<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;IF value >= optimal_min AND value <= optimal_max:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;RETURN {<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;status: "OPTIMAL",<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;color: "GREEN",<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;action: "Continue monitoring",<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;priority: "LOW"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}<br>
                    <br>
                    &nbsp;&nbsp;&nbsp;&nbsp;// Step 2: Calculate deviation<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;IF value < optimal_min:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;deviation = ((optimal_min - value) / optimal_min) × 100<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;direction = "BELOW"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ELSE:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;deviation = ((value - optimal_max) / optimal_max) × 100<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;direction = "ABOVE"<br>
                    <br>
                    &nbsp;&nbsp;&nbsp;&nbsp;// Step 3: Classify based on deviation<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;IF deviation <= 20:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;RETURN {<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;status: "WARNING",<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;color: "ORANGE",<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;action: "Plan correction within 1-2 weeks",<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;priority: "MEDIUM",<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;deviation: deviation,<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;direction: direction<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ELSE:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;RETURN {<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;status: "ALERT",<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;color: "RED",<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;action: "URGENT - Act within 3 days",<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;priority: "CRITICAL",<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;deviation: deviation,<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;direction: direction<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}
                </div>

                <h4 style="color: #9c27b0; margin-top: 20px;">Visual Decision Flowchart</h4>
                <div class="formula-box" style="background: #f3e5f5; border-left-color: #9c27b0;">
                    <pre style="color: #9c27b0; line-height: 1.8;">
    START
      |
      V
    Is value within optimal range?
      |
      +--YES--> ✅ OPTIMAL (GREEN) --> Continue monitoring
      |
      +--NO--> Calculate deviation percentage
                |
                V
              Is deviation <= 20%?
                |
                +--YES--> ⚠️ WARNING (ORANGE) --> Plan action in 1-2 weeks
                |
                +--NO--> 🚨 ALERT (RED) --> URGENT - Act within 3 days
                    </pre>
                </div>
            </div>
        </div>

        <!-- SUB-DROPDOWN 5: Multiple Parameter Status -->
        <div class="logic-dropdown" style="margin: 15px 0; border-color: #2196f3;">
            <div class="dropdown-header" onclick="toggleDropdown('multi-param-logic')" style="background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%); padding: 15px 20px; font-size: 1.05em;">
                <span>📊 Multiple Parameter Status (Overall Health)</span>
                <span class="dropdown-icon" id="icon-multi-param-logic">▼</span>
            </div>
            <div class="dropdown-content" id="multi-param-logic">
                <h4 style="color: #2196f3; margin-top: 15px;">Aggregate Status Calculation</h4>
                <p><strong>When combining multiple parameters into overall health score:</strong></p>
                <div class="formula-box">
                    FUNCTION calculate_overall_status(all_parameters):<br>
                    <br>
                    &nbsp;&nbsp;&nbsp;&nbsp;// Count status types<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;alerts = count_parameters_with_status("ALERT")<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;warnings = count_parameters_with_status("WARNING")<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;optimal = count_parameters_with_status("OPTIMAL")<br>
                    <br>
                    &nbsp;&nbsp;&nbsp;&nbsp;// Determine overall status (worst-case priority)<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;IF alerts >= 1:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;overall_status = "ALERT"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;message = "Critical issues require immediate attention"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ELSE IF warnings >= 2:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;overall_status = "WARNING"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;message = "Multiple parameters need correction"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ELSE IF warnings == 1:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;overall_status = "OPTIMAL"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;message = "Excellent with 1 minor item to address"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;ELSE:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;overall_status = "OPTIMAL"<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;message = "All parameters within optimal range"<br>
                    <br>
                    &nbsp;&nbsp;&nbsp;&nbsp;RETURN {overall_status, message, alerts, warnings, optimal}
                </div>

                <h4 style="color: #2196f3; margin-top: 20px;">Current Farm Status Analysis</h4>
                <table class="data-table" style="margin: 15px 0;">
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Value</th>
                            <th>Status</th>
                            <th>Contribution to Overall</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>pH Level</td>
                            <td>6.8</td>
                            <td><span class="status-indicator status-good"></span>OPTIMAL</td>
                            <td>+16.7%</td>
                        </tr>
                        <tr>
                            <td>Moisture</td>
                            <td>68%</td>
                            <td><span class="status-indicator status-good"></span>OPTIMAL</td>
                            <td>+16.7%</td>
                        </tr>
                        <tr>
                            <td>Nitrogen</td>
                            <td>42 ppm</td>
                            <td><span class="status-indicator status-good"></span>OPTIMAL</td>
                            <td>+16.7%</td>
                        </tr>
                        <tr>
                            <td>Phosphorus</td>
                            <td>28 ppm</td>
                            <td><span class="status-indicator status-warning"></span>WARNING</td>
                            <td>+13.3%</td>
                        </tr>
                        <tr>
                            <td>Potassium</td>
                            <td>155 ppm</td>
                            <td><span class="status-indicator status-good"></span>OPTIMAL</td>
                            <td>+16.7%</td>
                        </tr>
                        <tr>
                            <td>Organic Matter</td>
                            <td>4.2%</td>
                            <td><span class="status-indicator status-good"></span>OPTIMAL</td>
                            <td>+16.7%</td>
                        </tr>
                    </tbody>
                </table>

                <div class="calculation-step">
                    <h4>Overall Status Calculation</h4>
                    <div class="formula-box">
                        Alerts: <span class="highlight-value">0</span><br>
                        Warnings: <span class="highlight-value">1</span> (Phosphorus)<br>
                        Optimal: <span class="highlight-value">5</span><br>
                        <br>
                        Since alerts = 0 AND warnings = 1:<br>
                        <strong>Overall Status: OPTIMAL (with 1 minor item to address)</strong>
                    </div>
                </div>

                <div class="formula-box" style="background: #e3f2fd; border-left-color: #2196f3;">
                    <strong>📊 Your Farm's Overall Health</strong><br>
                    <br>
                    <strong>Status:</strong> <span class="status-indicator status-good"></span> OPTIMAL with 1 warning<br>
                    <strong>Score:</strong> 8.4/10 (Excellent)<br>
                    <br>
                    <strong>Breakdown:</strong><br>
                    • 5 parameters are optimal (83.3%)<br>
                    • 1 parameter needs attention (16.7%)<br>
                    • 0 critical issues<br>
                    <br>
                    <strong>Action Priority:</strong><br>
                    1. Address phosphorus level in next 1-2 weeks<br>
                    2. Continue monitoring all other parameters<br>
                    3. Maintain current management practices for optimal parameters
                </div>
            </div>
        </div>

        <div class="formula-box" style="background: #e3f2fd; border-left-color: #2196f3; margin-top: 25px;">
            <strong>💡 Priority System Summary:</strong><br>
            <br>
            <span class="status-indicator status-alert"></span> <strong>RED (ALERT):</strong> >20% deviation → Act within 3 days → Yield at serious risk<br>
            <span class="status-indicator status-warning"></span> <strong>ORANGE (WARNING):</strong> 0-20% deviation → Plan within 1-2 weeks → Trending away from optimal<br>
            <span class="status-indicator status-good"></span> <strong>GREEN (OPTIMAL):</strong> Within range → Continue monitoring → Maintain current practices<br>
            <br>
            The AI continuously evaluates all parameters and provides color-coded status indicators to help you prioritize actions and maintain optimal farm performance.
        </div>
    </div>
</div>

        <script>
        function toggleDropdown(id) {
            const content = document.getElementById(id);
            const icon = document.getElementById('icon-' + id);
            
            if (content.classList.contains('active')) {
                content.classList.remove('active');
                icon.textContent = '▼';
            } else {
                // Optional: Close other dropdowns (uncomment if you want only one open at a time)
                // document.querySelectorAll('.dropdown-content').forEach(dc => dc.classList.remove('active'));
                // document.querySelectorAll('.dropdown-icon').forEach(ic => ic.textContent = '▼');
                
                content.classList.add('active');
                icon.textContent = '▲';
            }
        }
        </script>
        <script>
        function toggleDropdown(id) {
            const content = document.getElementById(id);
            const icon = document.getElementById('icon-' + id);
            
            if (content.classList.contains('active')) {
                content.classList.remove('active');
                icon.textContent = '▼';
            } else {
                content.classList.add('active');
                icon.textContent = '▲';
            }
        }
        </script>
    
    <script>
        function showPage(pageId) {
            const pages = document.querySelectorAll('.page');
            const buttons = document.querySelectorAll('.nav-btn');
            
            pages.forEach(page => page.classList.remove('active'));
            buttons.forEach(btn => btn.classList.remove('active'));
            
            document.getElementById(pageId).classList.add('active');
            event.target.classList.add('active');
        }

        async function loadCropData() {
            const select = document.getElementById('cropSelect');
            const crop = select.value;
            
            const response = await fetch(`/api/crop/${crop}`);
            const data = await response.json();
            
            const detailsDiv = document.getElementById('cropDetails');
            
            const actionsHtml = data.actions.map(action => 
                `<p><strong>${action.title}:</strong> ${action.description}</p>`
            ).join('');
            
            detailsDiv.innerHTML = `
                <h3>${data.name} - Current Status</h3>
                <div class="grid">
                    <div class="metric-card">
                        <div class="metric-label">Growth Stage</div>
                        <div class="metric-value">${data.stage}</div>
                        <div>${data.stage_detail}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Health Score</div>
                        <div class="metric-value">${data.health}%</div>
                        <div><span class="status-indicator status-good"></span>Excellent</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Expected Yield</div>
                        <div class="metric-value">${data.yield}</div>
                    </div>
                </div>
                <div class="recommendation-box info-box">
                    <h3>📖 What is Growth Stage?</h3>
                    <p><strong>Growth Stage</strong> tells you what phase your crop is in - from seedling to harvest. This helps determine the right time for watering, fertilizing, and pest control.</p>
                    <p><strong>Current Stage:</strong> ${data.explanation}</p>
                </div>
                <div class="recommendation-box">
                    <h3>🌱 What To Do Now</h3>
                    ${actionsHtml}
                </div>
                <div class="recommendation-box">
                    <h3>✅ Priority Actions This Week</h3>
                    <ol>
                        <li>Follow the recommendations above in order</li>
                        <li>Walk through your fields daily to spot problems early</li>
                        <li>Keep notes on what you observe and what actions you take</li>
                        <li>Check weather forecast to plan your activities</li>
                    </ol>
                </div>
            `;
        }

        // Load default crop data on page load
        window.onload = function() {
            loadCropData();
        };
    </script>
</body>
</html>
"""

# Routes
@app.route('/')
def index():
    soil = SoilData.get_current_metrics()
    weather = WeatherData.get_current()
    forecast = WeatherData.get_forecast()
    
    return render_template_string(
        HTML_TEMPLATE,
        soil=soil,
        weather=weather,
        forecast=forecast
    )

@app.route('/api/crop/<crop_type>')
def get_crop(crop_type):
    return jsonify(CropData.get_crop_info(crop_type))

if __name__ == '__main__':
    print("=" * 60)
    print("argiNINE-11 Agricultural AI System")
    print("=" * 60)
    print("\nStarting server...")
    print("\nOpen your browser and go to: http://localhost:5000")
    print("\nPress CTRL+C to stop the server")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)