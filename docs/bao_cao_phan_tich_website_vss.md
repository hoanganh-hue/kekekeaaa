# Báo cáo phân tích website Bảo hiểm xã hội Việt Nam

## Thông tin cơ bản
- **Website**: https://baohiemxahoi.gov.vn
- **Thời gian phân tích**: 13/09/2025
- **Mục tiêu**: Phân tích cấu trúc website và khám phá API endpoints của các chức năng tra cứu

## 1. Phân tích trang chủ

### Giao diện chính
- **Layout**: Chuẩn government website với header, navigation menu, content area
- **Menu chính**: Giới thiệu, Tin tức, Văn bản, Chỉ đạo-Điều hành, PBGDPL, Những điều cần biết, Diễn đàn
- **Tính năng tra cứu**: Có link chính tại `/tracuu` để truy cập portal tra cứu

### Các tính năng tra cứu được xác định
1. Tra cứu mã số BHXH
2. Tra cứu quá trình tham gia BHXH  
3. Tra cứu bảo hiểm thất nghiệp (yêu cầu login)
4. Tra cứu điểm thu, đại lý
5. Tra cứu cơ sở khám chữa bệnh
6. Tra cứu đơn vị tham gia BHXH

## 2. Phân tích chức năng tra cứu bảo hiểm thất nghiệp

### URL và cấu trúc
- **URL**: `/tracuu/Pages/dang-nhap-tra-cuu.aspx`
- **Yêu cầu**: Đăng nhập người dùng
- **Form inputs**:
  - Mã số BHXH (text input)
  - Button "Lấy mã tra cứu"
  - reCAPTCHA verification

### Kết quả test
- **Input test**: `1234567890` (mã số BHXH giả)
- **Kết quả**: Form submission bị block bởi reCAPTCHA
- **Thông báo lỗi**: "Bạn cần xác nhận captcha để thực hiện tra cứu"
- **Hạn chế**: Không thể phân tích API do CAPTCHA protection

## 3. Phân tích chức năng tra cứu điểm thu, đại lý

### URL và cấu trúc  
- **URL**: `/tracuu/pages/diem-thu-dai-ly.aspx`
- **Loại**: Public lookup (không cần login)
- **Form structure**:
```
Tỉnh/TP: [Dropdown] - Custom JavaScript dropdown
├── Input hidden: value (ID của tỉnh)
└── Display button: Tên tỉnh đã chọn

Quận/Huyện: [Dropdown] - Được load sau khi chọn tỉnh
├── Options được cập nhật AJAX based trên tỉnh
└── Hiển thị các quận/huyện của tỉnh đã chọn

Phường/Xã: [Dropdown] - Optional
Thôn/Xóm: [Dropdown] - Optional  
reCAPTCHA: Required
```

### Test case thực hiện
- **Tỉnh thành**: Thành phố Hồ Chí Minh (value: 79)
- **Quận huyện**: Quận 1 (value: 760)
- **Kết quả**: Form submission bị block bởi reCAPTCHA
- **Thông báo**: "Bạn cần xác nhận captcha để thực hiện tra cứu"

### Cấu trúc dropdown phát hiện được
```javascript
// Dropdown tỉnh thành - Custom implementation
Element [121]: button với text hiển thị tỉnh đã chọn
Element [189]: select element (backend value)
Element [120]: input hidden chứa ID tỉnh (79 = TP.HCM)

// Dropdown quận huyện - AJAX loaded
Element [191]: select với options được load từ server
Các quận của TP.HCM: Bình Chánh, Cần Giờ, Củ Chi, Hóc Môn, Nhà Bè, 
Quận 1, Quận 10, v.v.
```

## 4. Kết luận về bảo mật và API

### Biện pháp bảo mật
1. **reCAPTCHA protection**: Tất cả forms tra cứu đều có CAPTCHA
2. **Client-side validation**: Validation trước khi gửi request
3. **Authentication**: Một số chức năng yêu cầu login
4. **Anti-automation**: Ngăn chặn scraping/automation tools

### Hạn chế trong việc phân tích API
- **CAPTCHA blocking**: Không thể submit forms để quan sát network calls
- **JavaScript dependencies**: Forms sử dụng heavy JavaScript
- **Rate limiting**: Có thể có rate limiting ở server side

### Dự đoán cấu trúc API (chưa verify được)
Dựa trên cấu trúc form, có thể dự đoán:

```http
POST /tracuu/pages/diem-thu-dai-ly.aspx
Content-Type: application/x-www-form-urlencoded

Payload có thể bao gồm:
- ProvinceID: 79 (TP.HCM)
- DistrictID: 760 (Quận 1) 
- WardID: (optional)
- VillageID: (optional)
- CaptchaResponse: (reCAPTCHA token)
- ViewState: (ASP.NET viewstate)
```

## 5. Khuyến nghị

### Để phân tích API thêm:
1. **Manual testing**: Sử dụng browser thật với DevTools
2. **CAPTCHA solving services**: Tích hợp 2captcha hoặc tương tự
3. **Mobile app analysis**: Nếu có app mobile, có thể bypass CAPTCHA
4. **Official API documentation**: Tìm kiếm tài liệu API chính thức

### Cho research purposes:
1. **Respect robots.txt**: Tuân thủ quy định của website
2. **Rate limiting**: Không spam requests
3. **Legal compliance**: Đảm bảo hoạt động trong khung pháp lý

## 6. Files tạo ra trong quá trình phân tích

1. `dropdown_open.png` - Screenshot dropdown tỉnh thành khi mở
2. `tracuu_results.png` - Screenshot sau khi submit form  
3. `tracuu_bottom_page.png` - Screenshot cuối trang
4. `tra_cuu_diem_thu_dai_ly_quan_1_tphcm.json` - Extracted content

## 7. Tóm tắt kỹ thuật

### Website stack:
- **Framework**: ASP.NET (dựa trên .aspx extensions)
- **Frontend**: Heavy JavaScript, custom dropdowns
- **Security**: reCAPTCHA v2, ViewState protection
- **Architecture**: Traditional server-side rendering

### Điểm đáng chú ý:
- Cascading dropdowns (tỉnh → quận → phường)  
- AJAX calls để load options
- reCAPTCHA làm barrier chống automation
- Form validation client-side và server-side

---

**Kết luận**: Website VSS sử dụng các biện pháp bảo mật mạnh để ngăn chặn automated access. Để phân tích API đầy đủ cần tools và approach khác ngoài basic automation.