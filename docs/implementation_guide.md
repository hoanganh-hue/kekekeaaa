# VSS BHXH Data Collector - Implementation Guide

## Tổng quan

Hệ thống VSS BHXH Data Collector là một giải pháp tự động để thu thập dữ liệu bảo hiểm xã hội (BHXH) từ website chính thức của Bảo hiểm Xã hội Việt Nam (VSS).

## Kiến trúc hệ thống

### Các thành phần chính

1. **Configuration Module (`config.py`)**
   - Quản lý cấu hình hệ thống
   - Thiết lập proxy, browser, request parameters
   - Định nghĩa các tỉnh thành và formats dữ liệu

2. **Authentication Module (`vss_authenticator.py`)**
   - Xác thực và quản lý session với VSS
   - Hỗ trợ cả requests session và browser automation
   - Anti-detection và proxy management

3. **Data Collection Module (`vss_bhxh_collector.py`)**
   - Thu thập dữ liệu BHXH từ website VSS
   - Parse và standardize dữ liệu Vietnamese
   - Export sang Excel và JSON formats

4. **Main Script (`run_vss_collection.py`)**
   - Script chính để chạy toàn bộ hệ thống
   - Command line interface
   - Logging và error handling

## Cài đặt và Cấu hình

### Requirements

```bash
pip install -r requirements.txt
```

### Packages chính

- `undetected-chromedriver`: Anti-detection cho browser automation
- `hrequests`: Session management với TLS fingerprinting
- `beautifulsoup4` + `lxml`: HTML parsing
- `xlsxwriter` + `openpyxl`: Excel export
- `fake-useragent`: User agent rotation
- `selenium`: Browser automation

### Cấu hình Proxy

System sử dụng proxy `ip.mproxy.vn:12301` mặc định. Có thể thay đổi trong `config.py`:

```python
PROXY_CONFIG = {
    "http": "http://your-proxy:port",
    "https": "http://your-proxy:port", 
    "enabled": True
}
```

## Sử dụng

### Command Line Interface

```bash
# Chạy với cấu hình mặc định (Hà Nội)
python run_vss_collection.py

# Chỉ định tỉnh thành
python run_vss_collection.py --province "Hồ Chí Minh"

# Chạy không sử dụng proxy
python run_vss_collection.py --no-proxy

# Chạy với browser hiển thị (non-headless)
python run_vss_collection.py --headless false

# Chỉ định thư mục output
python run_vss_collection.py --output-dir /path/to/output

# Giới hạn số records
python run_vss_collection.py --max-records 50
```

### Python API

```python
from vss_bhxh_collector import VSSDataCollector

# Khởi tạo collector
collector = VSSDataCollector(use_proxy=True, headless=True)

# Thu thập dữ liệu cho một tỉnh
province_info = {"name": "Hà Nội", "code": "01"}
success = collector.collect_province_data(province_info)

if success:
    # Export Excel
    excel_path = collector.export_to_excel()
    
    # Lưu JSON
    json_path = collector.save_results_json()
    
    # Xem summary
    summary = collector.get_collection_summary()
    print(summary)

# Cleanup
collector.close()
```

## Cấu trúc Output Files

### Excel File Format

File Excel bao gồm 3 sheets:

1. **Tổng quan**: Dữ liệu chính với các cột:
   - STT, Họ tên, Ngày sinh, Giới tính
   - Số BHXH, Số thẻ BHYT, Nơi cấp
   - Tình trạng, Thời gian thu thập

2. **Chi tiết**: Tất cả fields được thu thập
3. **Thông tin thu thập**: Metadata và statistics

### JSON Format

```json
{
  "collection_stats": {
    "total_records": 10,
    "successful_queries": 8,
    "failed_queries": 2,
    "province": "Hà Nội",
    "start_time": "2025-09-12T14:30:00",
    "end_time": "2025-09-12T14:35:00"
  },
  "collected_data": [
    {
      "ho_ten": "Nguyễn Văn A",
      "ngay_sinh": "01/01/1980",
      "so_bhxh": "1234567890",
      "collection_time": "2025-09-12T14:30:15"
    }
  ]
}
```

## Features Nâng cao

### Anti-Detection

- Sử dụng `undetected-chromedriver`
- Random user agent rotation
- Request delay và timing randomization
- Browser fingerprint obfuscation

### Session Management

- Laravel CSRF token handling
- Cookie persistence
- Session timeout management
- Automatic retry với exponential backoff

### Data Processing

- Vietnamese text normalization
- Date format standardization
- Administrative division validation
- Missing data handling

### Error Handling

- Comprehensive logging system
- Automatic retry mechanisms
- Graceful failure handling
- Detailed error reporting

## Logging

Logs được ghi vào `logs/collection_log.txt` với format:

```
2025-09-12 14:30:00,123 - vss_collector - INFO - Bắt đầu thu thập dữ liệu cho tỉnh: Hà Nội
2025-09-12 14:30:01,234 - vss_authenticator - INFO - Kết nối VSS thành công - Status: 200
2025-09-12 14:30:02,345 - vss_collector - INFO - Thu thập thành công: Nguyễn Văn A
```

## Troubleshooting

### Common Issues

1. **Connection Timeout**
   ```bash
   # Thử không sử dụng proxy
   python run_vss_collection.py --no-proxy
   ```

2. **Browser Issues**
   ```bash
   # Chạy browser visible để debug
   python run_vss_collection.py --headless false
   ```

3. **CSRF Token Problems**
   - Kiểm tra logs để xem token extraction
   - System sẽ tự động retry với browser method

4. **Proxy Issues**
   - Verify proxy connectivity
   - Check proxy credentials if required

### Debug Mode

```python
# Enable debug logging
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## Performance Tuning

### Optimization Settings

```python
# Trong config.py
BROWSER_CONFIG = {
    "disable_images": True,    # Tắt tải ảnh để tăng tốc
    "disable_javascript": False, # Giữ JS cho compatibility 
    "window_size": (1920, 1080)
}

REQUEST_CONFIG = {
    "timeout": 30,           # Timeout cho requests
    "max_retries": 3,       # Số lần retry
    "retry_delay": 2,       # Delay giữa các retry
}
```

### Scaling Considerations

- Implement rate limiting để tránh overload VSS servers
- Use distributed collection cho multiple provinces
- Cache session tokens để giảm authentication overhead

## Security Considerations

- Không hardcode credentials
- Use environment variables cho sensitive configs
- Rotate user agents và proxy regularly
- Respect website terms of service

## Maintenance

### Regular Tasks

1. **Update dependencies**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

2. **Check logs for errors**
   ```bash
   tail -f logs/collection_log.txt
   ```

3. **Verify output data quality**
   ```bash
   python -c "from vss_bhxh_collector import VSSDataCollector; collector = VSSDataCollector(); collector.test_connection()"
   ```

### Monitoring

- Monitor success/failure rates
- Check data completeness
- Track collection performance
- Monitor proxy health

## Development

### Adding New Features

1. **Extend data fields**: Modify `_parse_bhxh_response()` method
2. **Add new export formats**: Extend export methods
3. **Improve anti-detection**: Update browser configuration

### Testing

```bash
# Run basic test
python code/vss_authenticator.py

# Run collector test  
python code/vss_bhxh_collector.py

# Run full integration test
python run_vss_collection.py --max-records 5
```

## Legal Compliance

- Đảm bảo tuân thủ Terms of Service của VSS
- Respect rate limits và không gây overload
- Chỉ thu thập dữ liệu public/authorized
- Bảo vệ privacy và data security

## Support

Nếu gặp vấn đề:

1. Check logs trong `logs/collection_log.txt`
2. Verify network connectivity và proxy settings
3. Test với browser visible mode để debug
4. Check VSS website status

---

*Phiên bản: 1.0.0 | Cập nhật: 2025-09-12*
