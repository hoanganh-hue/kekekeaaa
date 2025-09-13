#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSS Browser Automation - Example Usage
=====================================

Ví dụ sử dụng VSS Browser Automation Framework
"""

import os
import sys
sys.path.append('/workspace/src')

from vss_browser_automation import VSSBrowserAutomation, BrowserConfig
from selenium.webdriver.common.by import By
import time

def example_basic_usage():
    """Example sử dụng cơ bản của framework"""
    print("=== VSS Browser Automation - Basic Usage Example ===")
    
    # Tạo config với headless mode off để xem browser (nếu có display)
    config = BrowserConfig()
    
    with VSSBrowserAutomation(config) as automation:
        # Start browser
        print("1. Khởi động browser...")
        if not automation.start_browser():
            print("❌ Failed to start browser")
            return
        
        print("✅ Browser started successfully")
        
        # Navigate to a test page
        print("\n2. Navigate to test page...")
        test_url = "data:text/html,<html><body><h1>Test Page</h1><form><input id='test-input' placeholder='Enter text'><button id='test-btn'>Submit</button></form></body></html>"
        
        if automation.navigate_to(test_url):
            print("✅ Navigation successful")
        else:
            print("❌ Navigation failed")
            return
        
        # Take screenshot
        print("\n3. Taking screenshot...")
        screenshot_path = automation.take_screenshot("basic_usage_test.png")
        if screenshot_path:
            print(f"✅ Screenshot saved: {screenshot_path}")
        
        # Find and interact with elements
        print("\n4. Testing element interactions...")
        
        # Fill form field
        input_text = "Hello VSS Automation!"
        if automation.fill_form_field(By.ID, "test-input", input_text):
            print(f"✅ Filled input field with: {input_text}")
        
        # Click button
        if automation.click_element(By.ID, "test-btn"):
            print("✅ Clicked submit button")
        
        # Get page source
        print("\n5. Getting page information...")
        page_source = automation.get_page_source()
        if page_source:
            print(f"✅ Page source length: {len(page_source)} characters")
        
        # Execute JavaScript
        result = automation.execute_javascript("return document.title;")
        print(f"✅ Page title via JavaScript: {result}")
        
        # Session info
        print("\n6. Session Information:")
        session_info = automation.get_session_info()
        for key, value in session_info.items():
            print(f"   {key}: {value}")
        
        print("\n✅ Basic usage example completed successfully!")

def example_vss_simulation():
    """Example simulation VSS workflow (với mock data)"""
    print("\n=== VSS Workflow Simulation ===")
    
    config = BrowserConfig()
    
    with VSSBrowserAutomation(config) as automation:
        if not automation.start_browser():
            print("❌ Failed to start browser")
            return
        
        # Simulate VSS lookup form
        mock_vss_html = """
        <html>
        <head><title>VSS Lookup Simulation</title></head>
        <body>
            <h1>Tra cứu thông tin Bảo hiểm xã hội</h1>
            <form id="lookup-form">
                <div>
                    <label>Số thẻ BHXH:</label>
                    <input type="text" id="card-number" name="cardNumber" placeholder="Nhập số thẻ BHXH">
                </div>
                <div>
                    <label>Họ và tên:</label>
                    <input type="text" id="full-name" name="fullName" placeholder="Nhập họ và tên">
                </div>
                <div>
                    <label>Ngày sinh:</label>
                    <input type="date" id="birth-date" name="birthDate">
                </div>
                <div>
                    <label>Tỉnh thành:</label>
                    <select id="province" name="province">
                        <option value="">Chọn tỉnh thành</option>
                        <option value="01">Hà Nội</option>
                        <option value="31">Hải Phòng</option>
                        <option value="48">Đà Nẵng</option>
                        <option value="79">TP. Hồ Chí Minh</option>
                    </select>
                </div>
                <button type="submit" id="search-btn">Tra cứu</button>
            </form>
            <div id="results" style="display:none;">
                <h3>Kết quả tra cứu</h3>
                <p>Thông tin BHXH được tìm thấy!</p>
            </div>
        </body>
        </html>
        """
        
        # Navigate to mock VSS page
        print("1. Loading VSS simulation page...")
        if not automation.navigate_to(f"data:text/html,{mock_vss_html}"):
            print("❌ Failed to load page")
            return
        
        # Take initial screenshot
        automation.take_screenshot("vss_simulation_initial.png")
        
        # Fill form với mock data
        print("2. Filling VSS lookup form...")
        test_data = {
            "card-number": "ABC123456789",
            "full-name": "Nguyễn Văn A",
            "birth-date": "1990-01-01"
        }
        
        for field_id, value in test_data.items():
            if automation.fill_form_field(By.ID, field_id, value):
                print(f"   ✅ Filled {field_id}: {value}")
                time.sleep(0.5)  # Delay giữa các field
        
        # Select province
        if automation.select_dropdown_option(By.ID, "province", option_value="01"):
            print("   ✅ Selected province: Hà Nội")
        
        # Take screenshot after filling form
        automation.take_screenshot("vss_simulation_filled.png")
        
        # Submit form
        print("3. Submitting form...")
        if automation.click_element(By.ID, "search-btn"):
            print("   ✅ Form submitted")
        
        # Wait for potential results (in real scenario)
        time.sleep(2)
        
        # Take final screenshot
        automation.take_screenshot("vss_simulation_final.png")
        
        print("✅ VSS workflow simulation completed!")

def main():
    """Main function chạy các examples"""
    try:
        # Basic usage example
        example_basic_usage()
        
        # VSS simulation example
        example_vss_simulation()
        
        print("\n🎉 All examples completed successfully!")
        print(f"📁 Screenshots saved in: /workspace/browser/screenshots/")
        
    except KeyboardInterrupt:
        print("\n⚠️ Examples interrupted by user")
    except Exception as e:
        print(f"❌ Example failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
