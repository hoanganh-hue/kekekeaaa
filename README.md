# VSS Enhanced Extractor - Phiên Bản Hoàn Chỉnh

## Tổng Quan
Đây là phiên bản hoàn chỉnh của VSS Enhanced Extractor (v2.1) - một hệ thống trích xuất dữ liệu từ website Bảo hiểm Xã hội Việt Nam với kiến trúc module hóa và tính năng nâng cao.

## Cấu Trúc Thư Mục

```
VSS_Enhanced_Extractor_Complete/
├── README_COMPREHENSIVE.md       # Hướng dẫn toàn diện
├── README.md                    # Hướng dẫn cơ bản
├── CHANGELOG.md                 # Lịch sử thay đổi
├── requirements.txt             # Dependencies Python
├── vss_enhanced_extractor.py    # File chính (tương thích ngược)
│
├── src/                         # Mã nguồn modular (v2.1)
│   ├── config/                  # Cấu hình
│   │   ├── constants.py         # Hằng số
│   │   ├── data_models.py       # Mô hình dữ liệu
│   │   └── patterns.py          # Pattern regex
│   ├── extractors/              # Logic trích xuất
│   │   └── base_extractor.py
│   ├── normalizers/             # Chuẩn hóa dữ liệu
│   │   └── field_normalizers.py
│   ├── validators/              # Validation
│   │   └── field_validators.py
│   └── vss_enhanced_extractor_v2.py  # Extractor v2.1
│
├── config/                      # Cấu hình hệ thống
│   ├── vss_config.yaml         # Cấu hình chính
│   ├── provinces.json          # Dữ liệu tỉnh thành
│   ├── key-capcha.txt          # Cấu hình captcha
│   └── proxy.txt               # Cấu hình proxy
│
├── data/                       # Dữ liệu mẫu
│   ├── input_excel_files/      # File đầu vào mẫu
│   ├── data-input.xlsx         # Dữ liệu đầu vào
│   ├── data-output.xlsx        # Kết quả đầu ra
│   └── enhanced_output_complete.xlsx
│
├── tests/                      # Kiểm thử
│   ├── test_refactored_extractor.py  # Test version mới
│   ├── test_enhanced_extractor.py    # Test tổng hợp
│   └── test_results_enhanced_extractor.json
│
├── docs/                       # Tài liệu
│   ├── ARCHITECTURE_V2.1.md    # Kiến trúc hệ thống
│   ├── ARCHITECTURE_V2.1.pdf   # Kiến trúc (PDF)
│   └── [các file tài liệu khác]
│
├── examples/                   # Ví dụ sử dụng
│   ├── demo_enhanced_extractor.py
│   ├── main_vss_enhanced.py
│   └── basic_usage.py
│
├── scripts/                    # Scripts tiện ích
│   ├── setup.sh               # Setup môi trường
│   └── run.sh                 # Chạy ứng dụng
│
├── charts/                     # Biểu đồ và trực quan hóa
│   ├── success_rate_chart.png
│   └── system_architecture.png
│
└── tools/                     # Công cụ hỗ trợ
    └── migration_script.py    # Script di chuyển dữ liệu
```

## Cài Đặt và Sử Dụng

### 1. Cài Đặt Dependencies
```bash
pip install -r requirements.txt
```

### 2. Cấu Hình
- Chỉnh sửa `config/vss_config.yaml` theo môi trường của bạn
- Cập nhật `config/proxy.txt` nếu sử dụng proxy

### 3. Sử Dụng Cơ Bản

#### Sử dụng file chính (tương thích với code cũ):
```python
from vss_enhanced_extractor import VSSEnhancedExtractor

extractor = VSSEnhancedExtractor()
results = extractor.extract_data("path/to/input.xlsx")
```

#### Sử dụng phiên bản mới (v2.1):
```python
from src.vss_enhanced_extractor_v2 import VssEnhancedExtractorV2

extractor = VssEnhancedExtractorV2()
results = extractor.extract_data("path/to/input.xlsx")
```

### 4. Chạy Tests
```bash
python tests/test_refactored_extractor.py
python tests/test_enhanced_extractor.py
```

## Tính Năng Chính

### Phiên Bản v2.1 (Mới)
- ✅ **Kiến trúc Modular**: Tách biệt concerns, dễ bảo trì
- ✅ **Trích xuất 15+ trường dữ liệu**: Thông tin cá nhân, BHXH, BHYT, BHTN
- ✅ **Xử lý lỗi thông minh**: Retry logic và error handling
- ✅ **Chuẩn hóa dữ liệu**: Format consistency
- ✅ **Validation tự động**: Data integrity checks
- ✅ **Tương thích ngược**: Không phá vỡ code cũ

### Dữ Liệu Trích Xuất
1. **Thông tin cá nhân**: Họ tên, CCCD, địa chỉ
2. **Thông tin BHXH**: Mã số, thời gian tham gia
3. **Thông tin BHYT**: Mã thẻ, hiệu lực
4. **Thông tin BHTN**: Trạng thái, thời gian
5. **Thông tin công việc**: Đơn vị, chức vụ

## So Sánh Phiên Bản

| Tính năng | v2.0 (Cũ) | v2.1 (Mới) |
|-----------|-----------|------------|
| Kiến trúc | Monolithic | Modular |
| Maintainability | Khó | Dễ |
| Testability | Hạn chế | Tốt |
| Extensibility | Khó | Dễ |
| Performance | Tốt | Tốt hơn |
| Backward Compatibility | - | 100% |

## Hỗ Trợ và Bảo Trì

### Logs và Debug
- Logs được lưu trong `logs/`
- Sử dụng `tools/migration_script.py` để di chuyển từ v2.0 sang v2.1

### Troubleshooting
1. **Lỗi kết nối**: Kiểm tra proxy và network
2. **Lỗi dữ liệu**: Xem validation reports trong `test_output/`
3. **Performance**: Sử dụng các file trong `charts/` để phân tích

## Phát Triển Tiếp

### Roadmap
- [ ] Unit tests chi tiết cho các module
- [ ] API documentation hoàn chỉnh
- [ ] Web interface
- [ ] Real-time monitoring

### Đóng Góp
Tham khảo `docs/` để hiểu kiến trúc hệ thống trước khi đóng góp.

## Tác Giả
- **Phát triển**: MiniMax Agent
- **Phiên bản**: v2.1
- **Ngày cập nhật**: 2025-09-13

---

**Lưu ý**: Đây là phiên bản hoàn chỉnh bao gồm tất cả tính năng, tài liệu và dữ liệu cần thiết để triển khai và sử dụng VSS Enhanced Extractor.