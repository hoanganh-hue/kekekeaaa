#!/usr/bin/env python3
"""
Tạo visualization cho VSS endpoint testing results

Author: MiniMax Agent
Date: 2025-09-12
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Load kết quả testing
with open('data/quick_analysis_20250912_121220.json', 'r', encoding='utf-8') as f:
    analysis = json.load(f)

with open('data/quick_test_results_20250912_121220.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# Create comprehensive visualization
fig = plt.figure(figsize=(20, 16))

# 1. Status Code Distribution (Pie Chart)
ax1 = plt.subplot(3, 4, 1)
status_codes = analysis['status_distribution']
colors = ['#2E8B57', '#FF6B6B', '#FFD93D']  # Green for 200, Red for 404, Yellow for 500
wedges, texts, autotexts = ax1.pie(status_codes.values(), labels=[f'HTTP {code}' for code in status_codes.keys()], 
                                   autopct='%1.1f%%', colors=colors, startangle=90)
ax1.set_title('Status Code Distribution\n(Total: 28 requests)', fontsize=12, fontweight='bold')

# 2. Response Time Analysis (Box Plot)
ax2 = plt.subplot(3, 4, 2)
response_times_by_status = {
    '200': [r['response_time'] for r in results if r['status_code'] == 200],
    '404': [r['response_time'] for r in results if r['status_code'] == 404],  
    '500': [r['response_time'] for r in results if r['status_code'] == 500]
}

data_for_boxplot = []
labels_for_boxplot = []
for status, times in response_times_by_status.items():
    if times:  # Only add if we have data
        data_for_boxplot.extend(times)
        labels_for_boxplot.extend([f'HTTP {status}'] * len(times))

df_response = pd.DataFrame({'Response Time (s)': data_for_boxplot, 'Status': labels_for_boxplot})
sns.boxplot(data=df_response, x='Status', y='Response Time (s)', ax=ax2)
ax2.set_title('Response Time by Status Code', fontsize=12, fontweight='bold')
ax2.set_ylabel('Response Time (seconds)')

# 3. Content Length Analysis (Bar Chart)
ax3 = plt.subplot(3, 4, 3)
accessible_endpoints = analysis['accessible']
endpoint_names = [ep['path'] if ep['path'] else 'main' for ep in accessible_endpoints]
content_lengths = [ep['content_length'] for ep in accessible_endpoints]

bars = ax3.bar(range(len(endpoint_names)), content_lengths, 
               color=['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336'])
ax3.set_xticks(range(len(endpoint_names)))
ax3.set_xticklabels(endpoint_names, rotation=45, ha='right')
ax3.set_title('Content Length of Accessible Endpoints', fontsize=12, fontweight='bold')
ax3.set_ylabel('Content Length (bytes)')

# Add value labels on bars
for i, bar in enumerate(bars):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 50,
             f'{int(height)}', ha='center', va='bottom', fontsize=9)

# 4. Endpoint Categories (Stacked Bar)
ax4 = plt.subplot(3, 4, 4)
categories = {
    'Geographic API': 8,  # api/provinces, api/districts, etc.
    'Authentication': 4,  # api/user, api/login, etc.
    'Administrative': 4,  # api/hospitals, api/users, etc.
    'Non-RESTful': 4,    # admin/*, dashboard/*, reports/*
    'Security Files': 3,  # test.php, phpinfo.php, .env
    'Basic Pages': 3      # main, login, logout
}

y_pos = np.arange(len(categories))
values = list(categories.values())
colors_cat = plt.cm.Set3(np.linspace(0, 1, len(categories)))

bars = ax4.barh(y_pos, values, color=colors_cat)
ax4.set_yticks(y_pos)
ax4.set_yticklabels(categories.keys())
ax4.set_xlabel('Number of Endpoints Tested')
ax4.set_title('Endpoint Categories Tested', fontsize=12, fontweight='bold')

# Add value labels
for i, bar in enumerate(bars):
    width = bar.get_width()
    ax4.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
             f'{int(width)}', ha='left', va='center', fontsize=9)

# 5. Security Analysis - Accessible vs Protected vs Not Found
ax5 = plt.subplot(3, 4, 5)
security_data = {
    'Accessible (200)': len(analysis['accessible']),
    'Protected (401/403)': len(analysis['protected']), 
    'Not Found (404)': len(analysis['not_found']),
    'Server Error (500)': len(analysis['server_errors'])
}

colors_sec = ['#4CAF50', '#FF9800', '#9E9E9E', '#F44336']
bars = ax5.bar(range(len(security_data)), security_data.values(), color=colors_sec)
ax5.set_xticks(range(len(security_data)))
ax5.set_xticklabels(security_data.keys(), rotation=45, ha='right')
ax5.set_title('Security Analysis Overview', fontsize=12, fontweight='bold')
ax5.set_ylabel('Number of Endpoints')

# Add value labels
for i, bar in enumerate(bars):
    height = bar.get_height()
    ax5.text(bar.get_x() + bar.get_width()/2., height + 0.2,
             f'{int(height)}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# 6. Response Time Distribution (Histogram)
ax6 = plt.subplot(3, 4, 6)
all_response_times = [r['response_time'] for r in results if r['response_time'] > 0]
ax6.hist(all_response_times, bins=15, color='skyblue', alpha=0.7, edgecolor='black')
ax6.set_xlabel('Response Time (seconds)')
ax6.set_ylabel('Frequency')
ax6.set_title('Response Time Distribution', fontsize=12, fontweight='bold')
ax6.axvline(np.mean(all_response_times), color='red', linestyle='--', 
            label=f'Mean: {np.mean(all_response_times):.2f}s')
ax6.legend()

# 7. Laravel Pattern Analysis (Horizontal Bar)
ax7 = plt.subplot(3, 4, 7)
pattern_analysis = {
    'Standard RESTful': 0,  # None found
    'Versioned API': 0,     # v1, v2 - None found
    'Laravel Sanctum': 0,   # sanctum/* - Not found
    'Admin Panel': 0,       # admin/* - Not found
    'Dashboard': 0,         # dashboard/* - Not found
    'Reports': 0,           # reports/* - Not found
    'Debug Files': 2        # test.php, test1.php - FOUND!
}

y_pos = np.arange(len(pattern_analysis))
values = list(pattern_analysis.values())
colors_pattern = ['#FF4444' if v == 0 else '#44FF44' for v in values]

bars = ax7.barh(y_pos, values, color=colors_pattern)
ax7.set_yticks(y_pos)
ax7.set_yticklabels(pattern_analysis.keys())
ax7.set_xlabel('Endpoints Found')
ax7.set_title('Laravel Pattern Analysis', fontsize=12, fontweight='bold')

# Add value labels and status
for i, bar in enumerate(bars):
    width = bar.get_width()
    status = 'FOUND' if width > 0 else 'NOT FOUND'
    color = 'green' if width > 0 else 'red'
    ax7.text(width + 0.05, bar.get_y() + bar.get_height()/2.,
             f'{int(width)} ({status})', ha='left', va='center', 
             fontsize=8, color=color, fontweight='bold')

# 8. Critical Security Findings (Text Summary)
ax8 = plt.subplot(3, 4, 8)
ax8.axis('off')
ax8.set_title('Critical Security Findings', fontsize=12, fontweight='bold', color='red')

security_text = """
🔴 CRITICAL VULNERABILITIES:

• Debug Files Exposed:
  - test.php (accessible)
  - test1.php (DB schema exposed)

• Server Error Indicating Endpoint:
  - /api/user returns 500 (exists!)

• No API Protection:
  - Standard Laravel APIs not found
  - No authentication endpoints

⚠️  RECOMMENDATIONS:
• Remove debug files immediately
• Implement proper API security
• Review error handling
"""

ax8.text(0.05, 0.95, security_text, transform=ax8.transAxes, fontsize=9,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle="round,pad=0.5", facecolor="lightcoral", alpha=0.3))

# 9. Response Size Analysis
ax9 = plt.subplot(3, 4, 9)
status_codes_for_size = [r['status_code'] for r in results]
content_lengths_all = [r['content_length'] for r in results]

df_size = pd.DataFrame({
    'Status Code': [f'HTTP {code}' for code in status_codes_for_size],
    'Content Length': content_lengths_all
})

sns.boxplot(data=df_size, x='Status Code', y='Content Length', ax=ax9)
ax9.set_title('Response Size by Status Code', fontsize=12, fontweight='bold')
ax9.set_ylabel('Content Length (bytes)')

# 10. Endpoint Accessibility Heatmap
ax10 = plt.subplot(3, 4, 10)

# Create matrix for heatmap
endpoint_categories = ['Basic Pages', 'Geographic API', 'Auth Endpoints', 'Admin Endpoints', 'Debug Files']
status_types = ['200 OK', '404 Not Found', '500 Error']

# Data matrix (số lượng endpoints trong mỗi category và status)
heatmap_data = np.array([
    [3, 0, 0],    # Basic Pages: 3 accessible, 0 not found, 0 error
    [0, 8, 0],    # Geographic API: 0 accessible, 8 not found, 0 error  
    [0, 3, 1],    # Auth Endpoints: 0 accessible, 3 not found, 1 error
    [0, 4, 0],    # Admin Endpoints: 0 accessible, 4 not found, 0 error
    [2, 3, 0]     # Debug Files: 2 accessible, 3 not found, 0 error
])

im = ax10.imshow(heatmap_data, cmap='RdYlGn', aspect='auto')
ax10.set_xticks(range(len(status_types)))
ax10.set_xticklabels(status_types)
ax10.set_yticks(range(len(endpoint_categories)))
ax10.set_yticklabels(endpoint_categories)
ax10.set_title('Endpoint Accessibility Heatmap', fontsize=12, fontweight='bold')

# Add text annotations
for i in range(len(endpoint_categories)):
    for j in range(len(status_types)):
        text = ax10.text(j, i, heatmap_data[i, j], ha="center", va="center",
                        color="black", fontweight='bold')

# 11. Test Coverage Summary
ax11 = plt.subplot(3, 4, 11)
ax11.axis('off')
ax11.set_title('Test Coverage Summary', fontsize=12, fontweight='bold')

coverage_text = f"""
📊 TESTING STATISTICS:

Total Requests: {analysis['total_tests']}
Success Rate: {len(analysis['accessible'])/analysis['total_tests']*100:.1f}%
Average Response Time: {np.mean(all_response_times):.2f}s

🎯 ENDPOINT CATEGORIES:
✅ Basic Pages: 3/3 accessible
❌ Geographic APIs: 0/8 found  
❌ Auth Endpoints: 0/4 found
❌ Admin Panels: 0/4 found
⚠️  Debug Files: 2/5 found

🔍 KEY DISCOVERIES:
• test1.php: 4,765 bytes (DB schema)
• /api/user: 500 error (endpoint exists!)
• No standard Laravel API found
"""

ax11.text(0.05, 0.95, coverage_text, transform=ax11.transAxes, fontsize=9,
          verticalalignment='top', fontfamily='monospace',
          bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.3))

# 12. VSS System Architecture Analysis
ax12 = plt.subplot(3, 4, 12)
ax12.axis('off')
ax12.set_title('VSS System Architecture', fontsize=12, fontweight='bold')

arch_text = """
🏗️ SYSTEM ARCHITECTURE:

Framework: Laravel (confirmed)
Web Server: Apache
Database: Oracle (from schema)
Authentication: Session-based

📁 DIRECTORY STRUCTURE:
/ → Main portal (3,614 bytes)
/login → Auth page (accessible) 
/logout → Session termination
/test.php → Debug file (10 bytes)
/test1.php → DB schema (4,765 bytes)

🔐 SECURITY POSTURE:
• CSRF protection likely enabled
• API endpoints not publicly exposed
• Debug files present (vulnerability)
• Standard Laravel structure absent

🎯 NEXT STEPS:
• Investigate /api/user error
• Find actual API patterns  
• Test authenticated access
"""

ax12.text(0.05, 0.95, arch_text, transform=ax12.transAxes, fontsize=8,
          verticalalignment='top', fontfamily='monospace',
          bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.3))

plt.tight_layout(pad=3.0)
plt.suptitle('VSS Internal System - Endpoint Testing Comprehensive Analysis\n' + 
            f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | Target: vssapp.teca.vn:8088',
            fontsize=16, fontweight='bold', y=0.98)

plt.savefig('charts/vss_endpoint_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

print("📊 Comprehensive analysis chart saved to: charts/vss_endpoint_analysis.png")
