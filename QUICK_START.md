# Hướng Dẫn Khởi Động Nhanh - VSS Enhanced Extractor v2.1

## Cài Đặt Nhanh

### 1. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

### 2. Test hệ thống:
```bash
python tests/test_refactored_extractor.py
```

## Sử Dụng Cơ Bản

### Cách 1: Sử dụng file chính (tương thích code cũ)
```python
# Import và sử dụng như phiên bản cũ
exec(open('vss_enhanced_extractor.py').read())

# Hoặc nếu đã cấu hình PYTHONPATH
from vss_enhanced_extractor import VSSEnhancedExtractor
extractor = VSSEnhancedExtractor()
results = extractor.extract_data("data/data-input.xlsx")
```

### Cách 2: Sử dụng phiên bản mới (v2.1)
```python
import sys
sys.path.append('src')

from vss_enhanced_extractor_v2 import VssEnhancedExtractorV2

# Khởi tạo extractor
extractor = VssEnhancedExtractorV2()

# Trích xuất dữ liệu
results = extractor.extract_data("data/data-input.xlsx")
```

## File Input Mẫu

Sử dụng file `data/data-input.xlsx` như template. Format yêu cầu:

| Cột | Tên | Bắt buộc |
|-----|-----|----------|
| A | Mã thẻ BHYT | Có |
| B | Mã định danh cá nhân | Có |
| C | Họ và tên | Có |
| D | Ngày sinh | Có |

## Kết Quả Output

Hệ thống sẽ tạo ra:
- File Excel với dữ liệu đầy đủ 15+ trường
- File JSON với validation results
- File log chi tiết

## Test và Kiểm Tra

```bash
# Test phiên bản mới
python tests/test_refactored_extractor.py

# Test tích hợp tổng thể
python tests/test_enhanced_extractor.py

# Demo với dữ liệu mẫu
python examples/demo_enhanced_extractor.py
```

## Cấu Hình

### Cấu hình cơ bản:
Chỉnh sửa `config/vss_config.yaml`:

```yaml
delays:
  between_requests: 2  # Giây giữa các request
  after_captcha: 3     # Giây sau khi giải captcha
  
retries:
  max_attempts: 3      # Số lần thử lại tối đa
  backoff_factor: 2    # Hệ số tăng delay

browser:
  headless: true       # Chạy ẩn browser
  timeout: 30         # Timeout mỗi thao tác
```

### Sử dụng proxy (tùy chọn):
Cập nhật `config/proxy.txt`:
```
http://proxy-server:port
http://username:password@proxy-server:port
```

## Khắc Phục Sự Cố

### Lỗi thường gặp:

1. **"Module not found"**
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
   ```

2. **"Connection timeout"**
   - Kiểm tra kết nối internet
   - Tăng timeout trong config
   - Sử dụng proxy

3. **"Captcha failed"**
   - Cập nhật `config/key-capcha.txt`
   - Giảm tốc độ request

### Logs và Debug:
- Check logs trong thư mục `logs/`
- Sử dụng `test_output/` để xem validation reports
- Xem charts trong `charts/` để phân tích performance

## Liên Hệ Hỗ Trợ

- Tài liệu chi tiết: `docs/ARCHITECTURE_V2.1.md`
- Hướng dẫn đầy đủ: `README_COMPREHENSIVE.md`
- Migration guide: `tools/migration_script.py`

---
**Version**: v2.1  
**Last Updated**: 2025-09-13  
**Author**: MiniMax Agent