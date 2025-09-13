#!/usr/bin/env python3
"""
Simple VSS endpoint analysis visualization

Author: MiniMax Agent
Date: 2025-09-12
"""

import json
import matplotlib.pyplot as plt
import numpy as np

# Load results
with open('data/quick_analysis_20250912_121220.json', 'r', encoding='utf-8') as f:
    analysis = json.load(f)

# Create simple visualization
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

# 1. Status Code Distribution
status_codes = analysis['status_distribution']
colors = ['#2E8B57', '#FF6B6B', '#FFD93D']
ax1.pie(status_codes.values(), labels=[f'HTTP {code}' for code in status_codes.keys()], 
        autopct='%1.1f%%', colors=colors, startangle=90)
ax1.set_title('Status Code Distribution\n(Total: 28 requests)', fontweight='bold')

# 2. Endpoint Categories
categories = {
    'Accessible (200)': len(analysis['accessible']),
    'Not Found (404)': len(analysis['not_found']),
    'Server Error (500)': len(analysis['server_errors']),
    'Protected (401/403)': len(analysis['protected'])
}

colors_cat = ['#4CAF50', '#9E9E9E', '#F44336', '#FF9800']
bars = ax2.bar(range(len(categories)), categories.values(), color=colors_cat)
ax2.set_xticks(range(len(categories)))
ax2.set_xticklabels(categories.keys(), rotation=45, ha='right')
ax2.set_title('Security Analysis Overview', fontweight='bold')
ax2.set_ylabel('Number of Endpoints')

# Add value labels
for i, bar in enumerate(bars):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
             f'{int(height)}', ha='center', va='bottom', fontweight='bold')

# 3. Accessible Endpoints Analysis
accessible = analysis['accessible']
names = [ep['path'] if ep['path'] else 'main' for ep in accessible]
sizes = [ep['content_length'] for ep in accessible]

bars = ax3.bar(range(len(names)), sizes, 
               color=['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336'])
ax3.set_xticks(range(len(names)))
ax3.set_xticklabels(names, rotation=45, ha='right')
ax3.set_title('Content Length of Accessible Endpoints', fontweight='bold')
ax3.set_ylabel('Content Length (bytes)')

# Add value labels
for i, bar in enumerate(bars):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 50,
             f'{int(height)}', ha='center', va='bottom', fontsize=9)

# 4. Key Findings Summary
ax4.axis('off')
ax4.set_title('Key Findings Summary', fontweight='bold', fontsize=14)

findings_text = """
CRITICAL DISCOVERIES:

✓ ACCESSIBLE ENDPOINTS (5):
  • Main page (/) - 3,614 bytes
  • Login page (/login) - 3,614 bytes  
  • Logout (/logout) - 3,614 bytes
  • test.php - 10 bytes (DEBUG FILE)
  • test1.php - 4,765 bytes (DB SCHEMA)

⚠ INTERESTING RESPONSE:
  • /api/user → 500 Error (endpoint exists!)

✗ NOT FOUND (22 endpoints):
  • All standard Laravel API patterns
  • Geographic data endpoints
  • Admin panel endpoints
  • Authentication APIs

🔴 SECURITY CONCERNS:
  • Debug files exposed in production
  • Database schema publicly accessible
  • No standard API protection found
"""

ax4.text(0.05, 0.95, findings_text, transform=ax4.transAxes, fontsize=10,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle="round,pad=0.5", facecolor="lightcyan", alpha=0.8))

plt.tight_layout()
plt.suptitle('VSS Internal System - Endpoint Testing Analysis\nTarget: vssapp.teca.vn:8088', 
             fontsize=16, fontweight='bold', y=0.98)

# Save to current directory instead
plt.savefig('vss_endpoint_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

print("Chart saved to: vss_endpoint_analysis.png")
