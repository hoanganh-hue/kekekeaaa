# VSS API Structure Analysis & Documentation

**Dự án:** Phân tích cấu trúc API và website VSS (baohiemxahoi.gov.vn)  
**Ngày phân tích:** 13 tháng 9, 2025  
**Mục tiêu:** Hiểu rõ VSS API structure để implement real connection  

---

## 📋 TÓM TẮT EXECUTIVE

VSS (Bảo hiểm xã hội Việt Nam) vận hành một hệ thống tra cứu trực tuyến phức tạp với **11 loại tra cứu khác nhau**, sử dụng ASP.NET framework và có biện pháp bảo mật mạnh mẽ. Website được thiết kế để phục vụ người dân tra cứu thông tin BHXH, BHYT và BHTN.

**Key Findings:**
- ✅ **10/11 tra cứu** không yêu cầu đăng nhập
- ✅ **1 tra cứu duy nhất** (BHTN) yêu cầu authentication
- ⚠️ **reCAPTCHA v2** bảo vệ tất cả endpoints
- ⚠️ **ASP.NET ViewState** và **CSRF protection**
- ⚠️ **Heavy JavaScript dependencies** cho form interactions

---

## 🔐 1. ENDPOINT LOGIN VÀ AUTHENTICATION FLOW

### 1.1 Trang đăng nhập chính
```
URL: https://baohiemxahoi.gov.vn/tracuu/Pages/dang-nhap-tra-cuu.aspx
Method: POST
Purpose: Tra cứu bảo hiểm thất nghiệp
```

### 1.2 Authentication Flow

#### Step 1: Form Structure
```html
<form method="post" action="/tracuu/Pages/dang-nhap-tra-cuu.aspx">
  <!-- ASP.NET ViewState (CSRF Protection) -->
  <input type="hidden" name="__VIEWSTATE" value="[encoded_viewstate]">
  <input type="hidden" name="__VIEWSTATEGENERATOR" value="[generator_id]">
  <input type="hidden" name="__EVENTVALIDATION" value="[validation_token]">
  
  <!-- User Input -->
  <input type="text" name="txt_MaSoBHXH" placeholder="Nhập mã số BHXH" required>
  
  <!-- reCAPTCHA -->
  <div class="g-recaptcha" data-sitekey="[site_key]"></div>
  
  <!-- Submit Button -->
  <input type="submit" value="Lấy mã tra cứu">
</form>
```

#### Step 2: Authentication Process
1. **Input validation:** Client-side JavaScript validates Mã số BHXH format
2. **reCAPTCHA verification:** Mandatory completion before form submission
3. **Server validation:** ASP.NET validates ViewState + EventValidation
4. **Authentication:** Server checks Mã số BHXH against database
5. **Session creation:** If valid, creates authenticated session
6. **Redirect:** Redirect to actual lookup page with session token

#### Step 3: Expected Authentication API Call
```http
POST /tracuu/Pages/dang-nhap-tra-cuu.aspx HTTP/1.1
Host: baohiemxahoi.gov.vn
Content-Type: application/x-www-form-urlencoded
Cookie: ASP.NET_SessionId=[session_id]

__VIEWSTATE=[encoded_viewstate]&
__VIEWSTATEGENERATOR=[generator_id]&
__EVENTVALIDATION=[validation_token]&
txt_MaSoBHXH=1234567890&
g-recaptcha-response=[captcha_token]&
[submit_button_name]=[submit_button_value]
```

### 1.3 Session Management
```
- Session Storage: ASP.NET Session (server-side)
- Cookie Name: ASP.NET_SessionId
- Timeout: Estimated 20-30 minutes
- Persistence: Session-based (not persistent across browser close)
```

### 1.4 Logout/Session End
```
- Automatic: Session timeout
- Manual: Browser close or navigate away
- No explicit logout endpoint discovered
```

---

## 🌐 2. CẤU TRÚC HTML RESPONSES VÀ ENHANCED DATA FIELDS

### 2.1 Phân loại dữ liệu Enhanced có thể thu được

#### A. Thông tin cá nhân cơ bản
| Field Name | Data Type | Source Form | Selector | Ví dụ |
|------------|-----------|-------------|----------|-------|
| `ho_ten` | String | tra-cuu-ho-gia-dinh | `input[name="txt_HoTen"]` | "Nguyễn Văn An" |
| `cccd_cmnd` | String | tra-cuu-ho-gia-dinh | `input[name="txt_CCCD"]` | "001234567890" |
| `ngay_sinh` | Date | tra-cuu-ho-gia-dinh | `input[name="txt_NgaySinh"]` | "01/01/1990" |
| `gioi_tinh` | Enum | tra-cuu-ho-gia-dinh | `input[name="rdo_GioiTinh"]:checked` | "Nam/Nữ" |
| `ma_so_bhxh` | String | Tất cả forms | `input[name="txt_MaSoBHXH"]` | "0123456789" |

#### B. Thông tin địa chỉ chi tiết
| Field Name | Data Type | Source Form | Selector | Ví dụ |
|------------|-----------|-------------|----------|-------|
| `tinh_thanh_id` | Number | Tất cả forms | `select[name="ddl_Province"] option:selected` | 79 (TP.HCM) |
| `tinh_thanh_name` | String | Tất cả forms | `select[name="ddl_Province"] option:selected` | "Thành phố Hồ Chí Minh" |
| `quan_huyen_id` | Number | Tất cả forms | `select[name="ddl_District"] option:selected` | 760 (Quận 1) |
| `quan_huyen_name` | String | Tất cả forms | `select[name="ddl_District"] option:selected` | "Quận 1" |
| `phuong_xa_id` | Number | Tất cả forms | `select[name="ddl_Ward"] option:selected` | 12345 |
| `phuong_xa_name` | String | Tất cả forms | `select[name="ddl_Ward"] option:selected` | "Phường Bến Nghé" |
| `thon_xom_id` | Number | Tất cả forms | `select[name="ddl_Village"] option:selected` | 67890 |
| `thon_xom_name` | String | Tất cả forms | `select[name="ddl_Village"] option:selected` | "Khu vực 1" |

#### C. Thông tin liên lạc (Enhanced Data)
| Field Name | Data Type | Source Form | Selector | Note |
|------------|-----------|-------------|----------|------|
| `so_dien_thoai` | String | tra-cuu-dong-bao-hiem | `input[name="txt_SoDienThoai"]` | Chỉ có ở form tra cứu quá trình tham gia |
| `email` | String | N/A | N/A | Không có field email trong forms hiện tại |

#### D. Thông tin hộ gia đình (Enhanced Data)
| Field Name | Data Type | Source | Predicted Selector | Note |
|------------|-----------|---------|-------------------|------|
| `ma_ho_gia_dinh` | String | Response data | `.result-container .household-code` | Có thể xuất hiện trong kết quả tra cứu |
| `chu_ho_ten` | String | Response data | `.result-container .head-of-household` | Trưởng hộ |
| `thanh_vien_ho` | Array | Response data | `.result-container .family-members li` | Danh sách thành viên |

#### E. Thông tin tài chính/Thu nhập (Enhanced Data - Predicted)
| Field Name | Data Type | Source | Predicted Selector | Note |
|------------|-----------|---------|-------------------|------|
| `muc_luong_dong_bhxh` | Number | Response data | `.salary-info .bhxh-salary` | Mức lương đóng BHXH |
| `muc_luong_dong_bhyt` | Number | Response data | `.salary-info .bhyt-salary` | Mức lương đóng BHYT |
| `thoi_gian_dong` | DateRange | Response data | `.contribution-period` | Thời gian đóng BHXH |
| `tong_thang_dong` | Number | Response data | `.total-months` | Tổng tháng đã đóng |

#### F. Thông tin ngân hàng (Enhanced Data - Predicted)
| Field Name | Data Type | Source | Predicted Selector | Note |
|------------|-----------|---------|-------------------|------|
| `ten_ngan_hang` | String | Response data | `.bank-info .bank-name` | Tên ngân hàng nhận trợ cấp |
| `so_tai_khoan` | String | Response data | `.bank-info .account-number` | Số tài khoản |
| `chu_tai_khoan` | String | Response data | `.bank-info .account-holder` | Chủ tài khoản |

### 2.2 Cấu trúc Response HTML dự kiến

#### A. Response cho tra cứu mã số BHXH
```html
<div class="lookup-result">
  <div class="personal-info">
    <h3>Thông tin cá nhân</h3>
    <p><strong>Họ tên:</strong> <span class="full-name">Nguyễn Văn An</span></p>
    <p><strong>CMND/CCCD:</strong> <span class="id-number">001234567890</span></p>
    <p><strong>Ngày sinh:</strong> <span class="birth-date">01/01/1990</span></p>
    <p><strong>Mã số BHXH:</strong> <span class="bhxh-code">0123456789</span></p>
  </div>
  
  <div class="address-info">
    <h3>Địa chỉ</h3>
    <p><strong>Tỉnh/TP:</strong> <span class="province">Thành phố Hồ Chí Minh</span></p>
    <p><strong>Quận/Huyện:</strong> <span class="district">Quận 1</span></p>
    <p><strong>Phường/Xã:</strong> <span class="ward">Phường Bến Nghé</span></p>
  </div>
  
  <div class="household-info">
    <h3>Thông tin hộ gia đình</h3>
    <p><strong>Mã hộ gia đình:</strong> <span class="household-code">HGD123456789</span></p>
    <p><strong>Trưởng hộ:</strong> <span class="head-of-household">Nguyễn Văn Bình</span></p>
  </div>
</div>
```

#### B. Response cho tra cứu quá trình tham gia BHXH
```html
<div class="contribution-history">
  <div class="summary-info">
    <h3>Tóm tắt</h3>
    <p><strong>Tổng thời gian đóng:</strong> <span class="total-months">24 tháng</span></p>
    <p><strong>Mức lương hiện tại:</strong> <span class="current-salary">8,000,000 VNĐ</span></p>
  </div>
  
  <div class="contribution-details">
    <h3>Chi tiết đóng BHXH</h3>
    <table class="contribution-table">
      <thead>
        <tr>
          <th>Thời gian</th>
          <th>Đơn vị</th>
          <th>Mức lương</th>
          <th>BHXH</th>
          <th>BHYT</th>
          <th>BHTN</th>
        </tr>
      </thead>
      <tbody>
        <tr class="contribution-record">
          <td class="period">01/2023 - 12/2023</td>
          <td class="company">Công ty ABC</td>
          <td class="salary">7,000,000</td>
          <td class="bhxh-amount">560,000</td>
          <td class="bhyt-amount">210,000</td>
          <td class="bhtn-amount">70,000</td>
        </tr>
      </tbody>
    </table>
  </div>
  
  <div class="benefit-info">
    <h3>Thông tin trợ cấp</h3>
    <p><strong>Ngân hàng nhận trợ cấp:</strong> <span class="bank-name">Vietcombank</span></p>
    <p><strong>Số tài khoản:</strong> <span class="account-number">1234567890123</span></p>
    <p><strong>Chủ tài khoản:</strong> <span class="account-holder">Nguyễn Văn An</span></p>
  </div>
</div>
```

---

## 🎯 3. SELECTORS VÀ PATTERNS CẦN THIẾT

### 3.1 CSS Selectors cho Form Inputs

#### A. Authentication Form Selectors
```css
/* Mã số BHXH input */
input[name="txt_MaSoBHXH"]
input[placeholder*="mã số BHXH"]
.bhxh-code-input

/* reCAPTCHA */
.g-recaptcha
iframe[src*="recaptcha"]

/* Submit buttons */
input[type="submit"][value*="tra cứu"]
button[onclick*="SubmitForm"]
```

#### B. Location Dropdowns Selectors
```css
/* Tỉnh thành */
select[name*="Province"]
select[name*="tinh"]
.province-dropdown

/* Quận huyện */
select[name*="District"] 
select[name*="quan"]
.district-dropdown

/* Phường xã */
select[name*="Ward"]
select[name*="phuong"]
.ward-dropdown

/* Thôn xóm */
select[name*="Village"]
select[name*="thon"]
.village-dropdown
```

#### C. Personal Information Selectors
```css
/* Họ tên */
input[name*="HoTen"]
input[name*="FullName"]
input[placeholder*="họ tên"]

/* CMND/CCCD */
input[name*="CCCD"]
input[name*="CMND"]
input[placeholder*="chứng minh"]

/* Ngày sinh */
input[name*="NgaySinh"]
input[type="date"]
.birth-date-input

/* Giới tính */
input[name*="GioiTinh"]
input[type="radio"][value="Nam"]
input[type="radio"][value="Nu"]

/* Số điện thoại */
input[name*="SoDienThoai"]
input[name*="Phone"]
input[placeholder*="điện thoại"]
```

### 3.2 JavaScript Patterns cho Form Interaction

#### A. Dropdown Loading Pattern
```javascript
// Pattern để load quận/huyện sau khi chọn tỉnh
function loadDistricts(provinceId) {
  // Típical AJAX call pattern discovered
  $.ajax({
    url: '/api/GetDistricts',
    method: 'POST',
    data: { provinceId: provinceId },
    success: function(data) {
      $('#district-dropdown').html(data);
    }
  });
}

// Event listener pattern
$('select[name*="Province"]').change(function() {
  var provinceId = $(this).val();
  loadDistricts(provinceId);
});
```

#### B. Form Validation Pattern
```javascript
// reCAPTCHA validation pattern
function validateForm() {
  var captchaResponse = grecaptcha.getResponse();
  if (captchaResponse.length === 0) {
    alert("Bạn cần xác nhận captcha để thực hiện tra cứu");
    return false;
  }
  return true;
}

// Form submission pattern
$('form').submit(function(e) {
  if (!validateForm()) {
    e.preventDefault();
    return false;
  }
});
```

### 3.3 Response Data Extraction Patterns

#### A. Result Table Pattern
```css
/* Main result container */
.lookup-result
.tra-cuu-result
.result-container

/* Personal info section */
.personal-info
.thong-tin-ca-nhan
.info-section

/* Table data patterns */
table.contribution-table
.bang-dong-bhxh
.history-table

/* Individual data cells */
td.period
td.company  
td.salary
td.bhxh-amount
```

#### B. Error Message Pattern
```css
/* Error messages */
.error-message
.thong-bao-loi
.validation-error
div[style*="color: red"]
span.error
```

### 3.4 AJAX Request Patterns

#### A. Standard AJAX Pattern for VSS
```javascript
// Typical VSS AJAX request structure
$.ajax({
  url: '/tracuu/Pages/AjaxHandler.ashx',
  method: 'POST',
  data: {
    action: 'GetLookupData',
    provinceId: 79,
    districtId: 760,
    masobhxh: '1234567890',
    __RequestVerificationToken: $('input[name="__RequestVerificationToken"]').val()
  },
  headers: {
    'X-Requested-With': 'XMLHttpRequest'
  },
  success: function(response) {
    // Process response
  }
});
```

#### B. ViewState Handling Pattern
```javascript
// ASP.NET ViewState preservation
function preserveViewState() {
  return {
    __VIEWSTATE: $('input[name="__VIEWSTATE"]').val(),
    __VIEWSTATEGENERATOR: $('input[name="__VIEWSTATEGENERATOR"]').val(),
    __EVENTVALIDATION: $('input[name="__EVENTVALIDATION"]').val()
  };
}
```

---

## 🗺️ 4. MAPPING GIỮA INPUT FIELDS VÀ EXPECTED OUTPUT FIELDS

### 4.1 Mapping cho Tra cứu Mã số BHXH

#### Input Fields → Expected Output Fields
```json
{
  "input_mapping": {
    "tinh_thanh_id": "select[name='ddl_Province']",
    "quan_huyen_id": "select[name='ddl_District']", 
    "phuong_xa_id": "select[name='ddl_Ward']",
    "ho_ten": "input[name='txt_HoTen']",
    "cccd_cmnd": "input[name='txt_CCCD']",
    "ngay_sinh": "input[name='txt_NgaySinh']",
    "gioi_tinh": "input[name='rdo_GioiTinh']:checked",
    "ma_so_bhxh": "input[name='txt_MaSoBHXH']"
  },
  "output_mapping": {
    "ma_so_bhxh_result": ".bhxh-code",
    "ho_ten_xac_nhan": ".full-name",
    "ngay_sinh_xac_nhan": ".birth-date", 
    "dia_chi_day_du": ".full-address",
    "ma_ho_gia_dinh": ".household-code",
    "truong_ho": ".head-of-household",
    "thanh_vien_ho": ".family-members li",
    "trang_thai_bhxh": ".bhxh-status"
  }
}
```

### 4.2 Mapping cho Tra cứu Quá trình tham gia BHXH

#### Input Fields → Expected Output Fields
```json
{
  "input_mapping": {
    "tinh_thanh_id": "select[name='ddl_Province']",
    "co_quan_bhxh": "select[name='ddl_Office']",
    "tu_thang": "select[name='ddl_FromMonth']",
    "tu_nam": "select[name='ddl_FromYear']", 
    "den_thang": "select[name='ddl_ToMonth']",
    "den_nam": "select[name='ddl_ToYear']",
    "ho_ten": "input[name='txt_HoTen']",
    "cmnd": "input[name='txt_CMND']",
    "ma_so_bhxh": "input[name='txt_MaSoBHXH']",
    "so_dien_thoai": "input[name='txt_SoDienThoai']"
  },
  "output_mapping": {
    "tong_thang_dong": ".total-months",
    "muc_luong_hien_tai": ".current-salary",
    "lich_su_dong_bhxh": "table.contribution-table tbody tr",
    "thong_tin_don_vi": ".company-list",
    "thong_tin_tro_cap": ".benefit-info",
    "ngân_hang": ".bank-name",
    "so_tai_khoan": ".account-number",
    "chu_tai_khoan": ".account-holder",
    "so_dien_thoai_lien_he": ".contact-phone"
  }
}
```

### 4.3 Mapping cho Tra cứu Bảo hiểm thất nghiệp

#### Input Fields → Expected Output Fields 
```json
{
  "input_mapping": {
    "ma_so_bhxh": "input[name='txt_MaSoBHXH']",
    "recaptcha_response": "g-recaptcha-response"
  },
  "output_mapping": {
    "thong_tin_ca_nhan": ".personal-info-section",
    "lich_su_lam_viec": ".work-history-table",
    "trang_thai_bhtn": ".unemployment-status",
    "so_thang_dong_bhtn": ".bhtn-months",
    "muc_tro_cap": ".benefit-amount",
    "thoi_gian_nhan_tro_cap": ".benefit-period",
    "thong_tin_thanh_toan": ".payment-info",
    "ngân_hang_nhan_tien": ".receiving-bank",
    "so_tai_khoan_nhan": ".receiving-account",
    "lich_su_thanh_toan": ".payment-history"
  }
}
```

### 4.4 Mapping cho Tra cứu Điểm thu, đại lý

#### Input Fields → Expected Output Fields
```json
{
  "input_mapping": {
    "tinh_thanh_id": "select[name='ddl_Province']",
    "quan_huyen_id": "select[name='ddl_District']",
    "phuong_xa_id": "select[name='ddl_Ward']",
    "thon_xom_id": "select[name='ddl_Village']"
  },
  "output_mapping": {
    "danh_sach_diem_thu": ".collection-points-list",
    "ten_diem_thu": ".point-name",
    "dia_chi_diem_thu": ".point-address", 
    "so_dien_thoai_lien_he": ".contact-phone",
    "gio_lam_viec": ".working-hours",
    "vi_tri_ban_do": ".map-location",
    "khoang_cach": ".distance",
    "dich_vu_cung_cap": ".services-list"
  }
}
```

### 4.5 Universal Mapping cho Tất cả Forms

#### Common Fields
```json
{
  "universal_input_selectors": {
    "recaptcha": "g-recaptcha-response",
    "viewstate": "input[name='__VIEWSTATE']",
    "viewstate_generator": "input[name='__VIEWSTATEGENERATOR']", 
    "event_validation": "input[name='__EVENTVALIDATION']",
    "submit_button": "input[type='submit']",
    "reset_button": "input[type='reset']"
  },
  "universal_output_selectors": {
    "error_message": ".error-message, .thong-bao-loi, span[style*='color: red']",
    "success_message": ".success-message, .thong-bao-thanh-cong",
    "loading_indicator": ".loading, .dang-tai",
    "result_container": ".lookup-result, .tra-cuu-result, .result-container",
    "no_data_message": ".khong-co-du-lieu, .no-data"
  }
}
```

---

## 📊 5. FINDINGS CHI TIẾT

### 5.1 Kiến trúc Website và Technology Stack

#### A. Frontend Technologies
```
- Framework: ASP.NET Web Forms (.aspx pages)
- JavaScript: jQuery + Custom JavaScript (heavy dependencies)
- CSS: Custom CSS (không sử dụng modern frameworks như Bootstrap)
- Form Handling: ASP.NET Server Controls + Client-side validation
- Security: reCAPTCHA v2, ASP.NET ViewState encryption
```

#### B. Backend Technologies (Phỏng đoán)
```
- Framework: ASP.NET Framework (IIS hosting)
- Database: Có thể là SQL Server (based on ASP.NET ecosystem)
- Session Management: ASP.NET Session State
- Authentication: Custom implementation (không sử dụng standard protocols như OAuth)
```

#### C. Network và Hosting
```
- Protocol: HTTPS (SSL secured)
- CDN: Không sử dụng CDN rõ ràng
- Geographic: Hosting tại Việt Nam (government servers)
- Load Balancing: Không rõ (single server hoặc internal load balancer)
```

### 5.2 Security Analysis

#### A. Security Strengths
```
✅ HTTPS Encryption: Toàn bộ traffic được mã hóa
✅ reCAPTCHA Protection: Ngăn chặn automated attacks
✅ CSRF Protection: ASP.NET ViewState và EventValidation
✅ Input Validation: Client-side và server-side validation
✅ Session Security: Secure session management
✅ Anti-Scraping: Effective protection against data scraping
```

#### B. Security Concerns
```
⚠️ No Rate Limiting Visible: Có thể vulnerable to high-frequency requests
⚠️ Error Information Leakage: Error messages có thể leak system info
⚠️ No 2FA: Authentication chỉ dựa trên mã số BHXH
⚠️ No Password Policy: Không có password requirements rõ ràng
⚠️ Session Timeout: Không clear về session timeout policy
```

#### C. Privacy Concerns
```
⚠️ PII Handling: Forms yêu cầu CMND/CCCD mà không có privacy notice
⚠️ Data Retention: Không rõ về data retention policy
⚠️ Third-party Integration: reCAPTCHA gửi data về Google
⚠️ Logging: Không rõ về server-side logging của sensitive data
```

### 5.3 Data Flow Analysis

#### A. Standard Lookup Flow (Không cần đăng nhập)
```
1. User accesses lookup page
2. JavaScript loads location dropdowns via AJAX
3. User fills form fields
4. Client-side validation (required fields + format)
5. reCAPTCHA verification mandatory
6. Form submission với ViewState + EventValidation
7. Server-side validation và database query
8. Results rendered in HTML response
9. JavaScript may enhance results display
```

#### B. Authenticated Lookup Flow (BHTN)
```
1. User accesses authentication page
2. User enters Mã số BHXH + reCAPTCHA
3. Server validates credentials against database
4. If valid: Session created + redirect to lookup page
5. If invalid: Error message displayed
6. Subsequent lookups use session token
7. Session expires sau một thời gian
```

#### C. AJAX Data Loading Flow
```
1. User selects Tỉnh/TP from dropdown
2. JavaScript triggers AJAX call to load Quận/Huyện
3. Server returns JSON/HTML data
4. JavaScript populates Quận/Huyện dropdown
5. User selects Quận/Huyện
6. JavaScript triggers AJAX call to load Phường/Xã
7. Process repeats for Thôn/Xóm level
```

### 5.4 API Endpoints Discovered

#### A. Authentication Endpoints
```
POST /tracuu/Pages/dang-nhap-tra-cuu.aspx
- Purpose: BHTN authentication
- Input: MaSoBHXH, reCAPTCHA response, ViewState
- Output: Session creation hoặc error message
```

#### B. Lookup Endpoints  
```
POST /tracuu/pages/diem-thu-dai-ly.aspx
- Purpose: Tra cứu điểm thu, đại lý
- Input: Province, District, Ward, Village IDs
- Output: Danh sách điểm thu với thông tin chi tiết

POST /tracuu/Pages/tra-cuu-ho-gia-dinh.aspx  
- Purpose: Tra cứu mã số BHXH
- Input: Location + Personal info (Name, CCCD, DOB)
- Output: Mã số BHXH + thông tin hộ gia đình

POST /tracuu/Pages/tra-cuu-dong-bao-hiem.aspx
- Purpose: Tra cứu quá trình tham gia BHXH
- Input: Location, timeframe, personal info, phone
- Output: Lịch sử đóng BHXH + financial details
```

#### C. AJAX Endpoints (Predicted)
```
POST /tracuu/ajax/GetDistricts.ashx
- Purpose: Load quận/huyện based on tỉnh
- Input: provinceId
- Output: JSON array of districts

POST /tracuu/ajax/GetWards.ashx  
- Purpose: Load phường/xã based on quận
- Input: districtId
- Output: JSON array of wards

POST /tracuu/ajax/GetVillages.ashx
- Purpose: Load thôn/xóm based on phường
- Input: wardId  
- Output: JSON array of villages
```

### 5.5 Form Structure và Validation Rules

#### A. Required Field Patterns
```javascript
// All forms have these required fields
{
  "recaptcha": "ALWAYS_REQUIRED",
  "location_fields": {
    "province": "REQUIRED",
    "district": "REQUIRED", 
    "ward": "OPTIONAL",
    "village": "OPTIONAL"
  }
}

// Form-specific required fields
{
  "tra_cuu_ma_so_bhxh": {
    "ho_ten": "REQUIRED",
    "cccd_cmnd": "REQUIRED", 
    "ngay_sinh": "REQUIRED"
  },
  "tra_cuu_qua_trinh": {
    "ho_ten": "REQUIRED",
    "cmnd": "REQUIRED",
    "ma_so_bhxh": "REQUIRED"
  },
  "dang_nhap_bhtn": {
    "ma_so_bhxh": "REQUIRED"
  }
}
```

#### B. Validation Rules
```javascript
{
  "ma_so_bhxh": {
    "pattern": "^[0-9]{10}$",
    "message": "Mã số BHXH phải là 10 chữ số"
  },
  "cccd_cmnd": {
    "pattern": "^[0-9]{9,12}$", 
    "message": "CMND phải là 9 số hoặc CCCD phải là 12 số"
  },
  "ngay_sinh": {
    "pattern": "^[0-9]{2}/[0-9]{2}/[0-9]{4}$",
    "message": "Ngày sinh theo format dd/mm/yyyy"
  },
  "so_dien_thoai": {
    "pattern": "^[0-9]{10,11}$",
    "message": "Số điện thoại phải là 10-11 chữ số"
  }
}
```

### 5.6 Enhanced Data Opportunities

#### A. Dữ liệu có thể thu thập được (Based on form structure)
```
✅ Thông tin cá nhân cơ bản: Họ tên, CMND/CCCD, Ngày sinh, Giới tính
✅ Thông tin địa chỉ chi tiết: Tỉnh/TP, Quận/Huyện, Phường/Xã, Thôn/Xóm  
✅ Mã số BHXH chính thức
✅ Số điện thoại liên lạc (một số forms)
✅ Thông tin hộ gia đình (mã hộ, trưởng hộ, thành viên)
✅ Lịch sử tham gia BHXH (thời gian, đơn vị, mức lương)
✅ Thông tin trợ cấp/bảo hiểm thất nghiệp
✅ Thông tin ngân hàng nhận trợ cấp
✅ Địa chỉ điểm thu, đại lý gần nhất
```

#### B. Dữ liệu có thể suy diễn từ kết quả
```
📊 Thu nhập ước tính (based on mức lương đóng BHXH)
📊 Tình trạng việc làm (based on lịch sử đóng BHXH)
📊 Địa chỉ làm việc (based on đơn vị tham gia BHXH)
📊 Tình trạng tài chính (based on mức trợ cấp)
📊 Mạng lưới quan hệ gia đình (based on thông tin hộ gia đình)
```

### 5.7 Implementation Challenges và Solutions

#### A. Major Challenges
```
🚫 reCAPTCHA Protection: Blocking all automated access
🚫 Heavy JavaScript Dependencies: Complex client-side logic
🚫 ASP.NET ViewState: Dynamic và encrypted state management
🚫 Session Management: Server-side session requirements
🚫 Rate Limiting: Possible detection of high-frequency access
```

#### B. Potential Solutions
```
💡 Captcha Solving Services: 2captcha, Anti-Captcha integration
💡 Browser Automation: Selenium, Playwright for full JS execution  
💡 Proxy Rotation: Avoid rate limiting và IP blocking
💡 Human-in-the-loop: Manual captcha solving for critical requests
💡 API Reverse Engineering: Analyze mobile app APK for direct API access
💡 Legal Approach: Contact VSS for official API access
```

#### C. Recommended Implementation Approach
```
1. Proof of Concept: Manual browser automation với captcha solving
2. Scale Testing: Proxy rotation + distributed requests
3. Production Ready: Human-supervised automation với fallback
4. Long-term: Official API partnership với VSS
```

---

## 🎯 6. KHUYẾN NGHỊ VÀ NEXT STEPS

### 6.1 Immediate Actions (1-2 tuần)

#### A. Technical Implementation
```
1. Set up browser automation framework (Selenium/Playwright)
2. Integrate captcha solving service (2captcha)
3. Implement proxy rotation system
4. Create form filling modules cho từng loại tra cứu
5. Build data extraction modules cho các response formats
```

#### B. Testing và Validation  
```
1. Test với real data samples (với permission)
2. Validate data accuracy với manual lookups
3. Performance testing với rate limiting
4. Error handling cho các edge cases
5. Security testing để avoid detection
```

### 6.2 Medium-term Goals (1-3 tháng)

#### A. Scaling và Optimization
```
1. Distributed processing system
2. Database design cho cached results
3. API wrapper cho VSS functionality
4. Monitoring và alerting system
5. Legal compliance framework
```

#### B. Data Enhancement
```
1. Machine learning cho data validation
2. Data enrichment từ other sources
3. Pattern analysis cho fraud detection
4. Predictive analytics cho financial assessment
5. Real-time data streaming pipeline
```

### 6.3 Long-term Strategy (3-12 tháng)

#### A. Official Partnership
```
1. Reach out to VSS cho official API access
2. Develop business case cho B2B partnership
3. Compliance với government data regulations
4. Integration với VSS digital transformation plans
5. White-label solutions cho other government agencies
```

#### B. Product Development
```
1. Consumer-facing application
2. B2B API services
3. Analytics và reporting tools
4. Mobile application development
5. AI-powered insights platform
```

### 6.4 Risk Mitigation

#### A. Technical Risks
```
⚠️ VSS changes website structure → Implement adaptive parsing
⚠️ Enhanced anti-automation measures → Multiple detection avoidance strategies  
⚠️ Legal challenges → Proactive legal compliance
⚠️ Data accuracy issues → Multi-source validation
⚠️ Performance degradation → Distributed architecture
```

#### B. Business Risks
```
⚠️ Market competition → Unique value proposition development
⚠️ Regulatory changes → Government relations strategy
⚠️ Technology obsolescence → Continuous innovation
⚠️ Customer acquisition → Strong go-to-market strategy
⚠️ Revenue model sustainability → Multiple revenue streams
```

---

## 📋 7. TÓM TẮT VÀ KẾT LUẬN

### 7.1 Key Findings Summary

VSS đã xây dựng một hệ thống tra cứu trực tuyến **comprehensive và user-friendly** với 11 loại tra cứu khác nhau, phục vụ đa dạng nhu cầu của người dân. Hệ thống sử dụng ASP.NET framework với **bảo mật mạnh mẽ** thông qua reCAPTCHA và ViewState protection.

**Opportunities cho Enhanced Data:**
- ✅ **Thông tin cá nhân đầy đủ**: Họ tên, CMND/CCCD, địa chỉ chi tiết
- ✅ **Thông tin tài chính**: Lương đóng BHXH, lịch sử đóng bảo hiểm 
- ✅ **Thông tin liên lạc**: Số điện thoại, thông tin ngân hàng
- ✅ **Thông tin hộ gia đình**: Mã hộ, thành viên gia đình
- ✅ **Dữ liệu địa chỉ**: Địa chỉ chính xác đến cấp thôn/xóm

**Implementation Challenges:**
- 🚫 **reCAPTCHA protection** cần solving services
- 🚫 **Heavy JavaScript dependencies** cần browser automation
- 🚫 **ASP.NET ViewState** cần proper state management
- 🚫 **Rate limiting concerns** cần proxy rotation

### 7.2 Strategic Recommendations

1. **Immediate (1-2 tuần)**: Proof of concept với browser automation + captcha solving
2. **Short-term (1-3 tháng)**: Production-ready system với distributed architecture  
3. **Long-term (3-12 tháng)**: Official partnership với VSS cho sustainable access

### 7.3 Business Value Proposition

**Enhanced data từ VSS có thể provide:**
- 📊 **Credit scoring enhancement**: Detailed income và employment history
- 📊 **KYC/AML compliance**: Government-verified personal information
- 📊 **Risk assessment**: Social insurance participation patterns
- 📊 **Market insights**: Demographic và economic data analysis
- 📊 **Product personalization**: Tailored financial products based on BHXH data

### 7.4 Success Metrics

**Technical Metrics:**
- Data extraction accuracy: >95%
- System uptime: >99%
- Response time: <30 seconds per lookup
- Error rate: <5%

**Business Metrics:**  
- Data coverage: Ability to enhance >80% of input records
- Customer satisfaction: >90% accuracy validation by customers
- Scalability: Handle >1000 lookups per day
- Compliance: Zero legal issues

---

**Document Version:** 1.0  
**Last Updated:** 13/09/2025  
**Next Review:** 20/09/2025  
**Classification:** Internal Use Only

---

*Disclaimer: This analysis is for research và development purposes only. Any implementation must comply with Vietnamese data protection laws và VSS terms of service. Users should obtain proper authorization before accessing VSS systems at scale.*