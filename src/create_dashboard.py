#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard VSS Data Visualization
Created by: MiniMax Agent
Date: 2025-09-12
"""

import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
from datetime import datetime

class VSSDataDashboard:
    """Lớp tạo dashboard trực quan cho dữ liệu VSS"""
    
    def __init__(self):
        self.load_analysis_data()
    
    def load_analysis_data(self):
        """Tải dữ liệu phân tích"""
        # Tải dữ liệu chi tiết
        analysis_file = "data/vss_data_analysis_detailed.json"
        if os.path.exists(analysis_file):
            with open(analysis_file, 'r', encoding='utf-8') as f:
                self.analysis_data = json.load(f)
        
        # Tải bảng tổng hợp tỉnh thành
        csv_file = "data/provinces_summary.csv"
        if os.path.exists(csv_file):
            self.provinces_df = pd.read_csv(csv_file)
    
    def create_overview_stats(self):
        """Tạo thống kê tổng quan"""
        stats = self.analysis_data.get('statistics', {})
        
        overview_html = f"""
        <div style="display: flex; justify-content: space-around; margin: 20px 0; flex-wrap: wrap;">
            <div style="text-align: center; padding: 20px; border: 2px solid #4CAF50; border-radius: 10px; margin: 10px; min-width: 200px; background: linear-gradient(135deg, #4CAF50, #45a049);">
                <h3 style="color: white; margin: 0;">Tỉnh thành</h3>
                <h2 style="color: white; margin: 5px 0;">{stats.get('total_provinces_analyzed', 0)}</h2>
                <p style="color: white; margin: 0; font-size: 14px;">đã phân tích</p>
            </div>
            
            <div style="text-align: center; padding: 20px; border: 2px solid #2196F3; border-radius: 10px; margin: 10px; min-width: 200px; background: linear-gradient(135deg, #2196F3, #1976D2);">
                <h3 style="color: white; margin: 0;">HTTP Requests</h3>
                <h2 style="color: white; margin: 5px 0;">{stats.get('total_http_requests', 0)}</h2>
                <p style="color: white; margin: 0; font-size: 14px;">tổng số requests</p>
            </div>
            
            <div style="text-align: center; padding: 20px; border: 2px solid #FF9800; border-radius: 10px; margin: 10px; min-width: 200px; background: linear-gradient(135deg, #FF9800, #F57C00);">
                <h3 style="color: white; margin: 0;">Tỷ lệ thành công</h3>
                <h2 style="color: white; margin: 5px 0;">{stats.get('data_quality_score', 0)}%</h2>
                <p style="color: white; margin: 0; font-size: 14px;">chất lượng dữ liệu</p>
            </div>
            
            <div style="text-align: center; padding: 20px; border: 2px solid #9C27B0; border-radius: 10px; margin: 10px; min-width: 200px; background: linear-gradient(135deg, #9C27B0, #7B1FA2);">
                <h3 style="color: white; margin: 0;">File dữ liệu</h3>
                <h2 style="color: white; margin: 5px 0;">{stats.get('total_data_files', 0)}</h2>
                <p style="color: white; margin: 0; font-size: 14px;">đã được xử lý</p>
            </div>
        </div>
        """
        return overview_html
    
    def create_success_rate_chart(self):
        """Tạo biểu đồ tỷ lệ thành công theo tỉnh"""
        fig = px.bar(
            self.provinces_df, 
            x='Tên tỉnh', 
            y='Tỷ lệ thành công (%)',
            color='Miền',
            title='Tỷ lệ thành công thu thập dữ liệu theo tỉnh thành',
            color_discrete_map={
                'north': '#FF6B6B',
                'central': '#4ECDC4',
                'south': '#45B7D1'
            }
        )
        
        fig.update_layout(
            xaxis_title="Tỉnh thành",
            yaxis_title="Tỷ lệ thành công (%)",
            template='plotly_white',
            height=400
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='inline')
    
    def create_requests_distribution(self):
        """Tạo biểu đồ phân bố requests"""
        fig = make_subplots(
            rows=1, cols=2, 
            specs=[[{"type": "bar"}, {"type": "pie"}]],
            subplot_titles=('Phân bố Requests theo Tỉnh', 'Tỷ lệ Thành công/Thất bại')
        )
        
        # Biểu đồ cột cho số lượng requests
        fig.add_trace(
            go.Bar(
                x=self.provinces_df['Tên tỉnh'],
                y=self.provinces_df['Thành công'],
                name='Thành công',
                marker_color='#4CAF50'
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=self.provinces_df['Tên tỉnh'],
                y=self.provinces_df['Thất bại'],
                name='Thất bại',
                marker_color='#F44336'
            ),
            row=1, col=1
        )
        
        # Biểu đồ tròn tổng quan
        total_success = self.provinces_df['Thành công'].sum()
        total_failed = self.provinces_df['Thất bại'].sum()
        
        fig.add_trace(
            go.Pie(
                labels=['Thành công', 'Thất bại'],
                values=[total_success, total_failed],
                marker_colors=['#4CAF50', '#F44336']
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text="Phân tích chi tiết Requests",
            template='plotly_white',
            height=500
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='inline')
    
    def create_timeline_chart(self):
        """Tạo biểu đồ timeline thu thập dữ liệu"""
        # Chuyển đổi timestamp thành datetime
        self.provinces_df['Datetime'] = pd.to_datetime(self.provinces_df['Lần thu thập cuối'])
        
        fig = px.timeline(
            self.provinces_df,
            x_start='Datetime',
            x_end='Datetime',
            y='Tên tỉnh',
            color='Miền',
            title='Timeline thu thập dữ liệu theo tỉnh thành'
        )
        
        fig.update_layout(
            xaxis_title="Thời gian thu thập",
            yaxis_title="Tỉnh thành",
            template='plotly_white',
            height=400
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='inline')
    
    def create_status_code_analysis(self):
        """Tạo phân tích status codes"""
        http_analysis = self.analysis_data.get('http_responses', {})
        status_codes = http_analysis.get('status_codes', {})
        
        if status_codes:
            labels = list(status_codes.keys())
            values = list(status_codes.values())
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=[f"HTTP {code}" for code in labels],
                    values=values,
                    hole=.3,
                    marker_colors=['#4CAF50' if code == 200 else '#F44336' for code in labels]
                )
            ])
            
            fig.update_layout(
                title="Phân bố HTTP Status Codes",
                template='plotly_white',
                height=400
            )
            
            return fig.to_html(full_html=False, include_plotlyjs='inline')
        
        return "<p>Không có dữ liệu status codes</p>"
    
    def create_provinces_table(self):
        """Tạo bảng chi tiết tỉnh thành"""
        # Tạo bảng HTML với styling đẹp
        table_html = """
        <div style="overflow-x: auto; margin: 20px 0;">
            <table style="width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">
                <thead style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                    <tr>
        """
        
        # Header columns
        for col in self.provinces_df.columns:
            table_html += f'<th style="padding: 15px; text-align: left; font-weight: 600;">{col}</th>'
        
        table_html += """
                    </tr>
                </thead>
                <tbody>
        """
        
        # Data rows
        for i, row in self.provinces_df.iterrows():
            bg_color = "#f8f9fa" if i % 2 == 0 else "white"
            table_html += f'<tr style="background-color: {bg_color};">'
            
            for col in self.provinces_df.columns:
                value = row[col]
                if col == 'Tỷ lệ thành công (%)':
                    # Màu sắc cho tỷ lệ thành công
                    color = "#4CAF50" if value >= 50 else "#FF9800" if value >= 20 else "#F44336"
                    table_html += f'<td style="padding: 12px; border-bottom: 1px solid #dee2e6; color: {color}; font-weight: 600;">{value}%</td>'
                elif col == 'Miền':
                    # Màu sắc cho miền
                    color = "#FF6B6B" if value == "north" else "#4ECDC4" if value == "central" else "#45B7D1"
                    table_html += f'<td style="padding: 12px; border-bottom: 1px solid #dee2e6; color: {color}; font-weight: 500;">{value.capitalize()}</td>'
                else:
                    table_html += f'<td style="padding: 12px; border-bottom: 1px solid #dee2e6;">{value}</td>'
            
            table_html += '</tr>'
        
        table_html += """
                </tbody>
            </table>
        </div>
        """
        
        return table_html
    
    def generate_complete_dashboard(self):
        """Tạo dashboard hoàn chỉnh"""
        dashboard_html = f"""
        <!DOCTYPE html>
        <html lang="vi">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>VSS Data Analysis Dashboard</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    overflow: hidden;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                
                .header h1 {{
                    margin: 0;
                    font-size: 2.5em;
                    font-weight: 700;
                }}
                
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 1.1em;
                    opacity: 0.9;
                }}
                
                .content {{
                    padding: 30px;
                }}
                
                .section {{
                    margin: 40px 0;
                }}
                
                .section h2 {{
                    color: #333;
                    border-left: 5px solid #667eea;
                    padding-left: 15px;
                    margin-bottom: 25px;
                    font-size: 1.8em;
                }}
                
                .chart-container {{
                    margin: 20px 0;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                }}
                
                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #666;
                    border-top: 1px solid #dee2e6;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔍 VSS Data Analysis Dashboard</h1>
                    <p>Phân tích toàn diện dữ liệu Bảo hiểm Xã hội Việt Nam</p>
                    <p>Tạo bởi: MiniMax Agent | {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                </div>
                
                <div class="content">
                    <div class="section">
                        <h2>📊 Tổng quan thống kê</h2>
                        {self.create_overview_stats()}
                    </div>
                    
                    <div class="section">
                        <h2>📈 Tỷ lệ thành công theo tỉnh thành</h2>
                        <div class="chart-container">
                            {self.create_success_rate_chart()}
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>📊 Phân bố Requests</h2>
                        <div class="chart-container">
                            {self.create_requests_distribution()}
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>🌐 Phân tích HTTP Status Codes</h2>
                        <div class="chart-container">
                            {self.create_status_code_analysis()}
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>📋 Bảng chi tiết tỉnh thành</h2>
                        {self.create_provinces_table()}
                    </div>
                    
                    <div class="section">
                        <h2>📊 Cấu trúc dữ liệu đã thu thập</h2>
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #28a745;">
                            <h4>Các file dữ liệu chính:</h4>
                            <ul>
                                <li><strong>vss_collection_results_20250912_131954.json</strong> - Kết quả thu thập chính từ 3 tỉnh thành</li>
                                <li><strong>intermediate_results_2.json</strong> - Dữ liệu trung gian trong quá trình thu thập</li>
                                <li><strong>simple_test_results.json</strong> - Kết quả test kết nối và endpoint</li>
                                <li><strong>quick_analysis_*.json</strong> - Phân tích nhanh các endpoint có sẵn</li>
                                <li><strong>provinces_summary.csv</strong> - Bảng tổng hợp đã được chuẩn hóa</li>
                            </ul>
                            
                            <h4>Các trường dữ liệu chính được thu thập:</h4>
                            <ul>
                                <li><strong>Province Info:</strong> Mã tỉnh, Tên tỉnh, Miền địa lý</li>
                                <li><strong>HTTP Response Data:</strong> Status codes, Headers, Content</li>
                                <li><strong>Session Info:</strong> Timestamp, Proxy config, Runtime</li>
                                <li><strong>Request Statistics:</strong> Success/Failed counts, Success rate</li>
                                <li><strong>HTML Content:</strong> Form structures, Links, Scripts</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>🚀 Khuyến nghị phát triển tiếp</h2>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                            <div style="background: #e8f5e8; padding: 20px; border-radius: 10px; border-left: 5px solid #28a745;">
                                <h4 style="color: #155724; margin-top: 0;">✅ Điểm mạnh hiện tại</h4>
                                <ul style="color: #155724;">
                                    <li>Hạ tầng thu thập dữ liệu hoàn chỉnh</li>
                                    <li>Hệ thống proxy hoạt động ổn định</li>
                                    <li>Dữ liệu được chuẩn hóa và phân tích chi tiết</li>
                                    <li>Dashboard trực quan và thân thiện</li>
                                </ul>
                            </div>
                            
                            <div style="background: #fff3cd; padding: 20px; border-radius: 10px; border-left: 5px solid #ffc107;">
                                <h4 style="color: #856404; margin-top: 0;">⚠️ Cần cải thiện</h4>
                                <ul style="color: #856404;">
                                    <li>Tỷ lệ thành công còn thấp (20%)</li>
                                    <li>Cần tìm các API endpoint thực tế</li>
                                    <li>Xử lý authentication</li>
                                    <li>Mở rộng ra 63 tỉnh thành</li>
                                </ul>
                            </div>
                            
                            <div style="background: #d1ecf1; padding: 20px; border-radius: 10px; border-left: 5px solid #17a2b8;">
                                <h4 style="color: #0c5460; margin-top: 0;">🔮 Bước tiếp theo</h4>
                                <ul style="color: #0c5460;">
                                    <li>Phân tích JavaScript để tìm API thực</li>
                                    <li>Nghiên cứu cơ chế login của hệ thống</li>
                                    <li>Xây dựng crawler thông minh hơn</li>
                                    <li>Tích hợp AI để phân tích nội dung</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <p>© 2025 MiniMax Agent | VSS Data Analysis Dashboard</p>
                    <p>Dữ liệu được cập nhật: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Lưu dashboard
        dashboard_file = "docs/VSS_Data_Dashboard.html"
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
        
        return dashboard_file

if __name__ == "__main__":
    dashboard = VSSDataDashboard()
    dashboard_file = dashboard.generate_complete_dashboard()
    print(f"Dashboard đã được tạo tại: {dashboard_file}")
