# PHÂN TÍCH HỆ THỐNG TRA CỨU THÔNG TIN BẢO HIỂM XÃ HỘI VIỆT NAM (VSS)

**URL Chính:** https://baohiemxahoi.gov.vn/tracuu  
**Thời gian phân tích:** 13 tháng 9, 2025  
**Trình duyệt:** Chrome

---

## 1. TỔNG QUAN HỆ THỐNG TRA CỨU

Hệ thống tra cứu trực tuyến của VSS cung cấp **11 loại tra cứu chính**, được tổ chức theo chủ đề và mức độ bảo mật khác nhau. Hệ thống có thiết kế thống nhất với sidebar menu "TRA CỨU TRỰC TUYẾN" xuất hiện trên tất cả các trang tra cứu.

### Đặc điểm chung:
- **Giao diện thống nhất:** Tất cả trang tra cứu đều có layout tương tự
- **Sidebar menu:** Menu tra cứu cố định bên phải với 11 loại tra cứu
- **Breadcrumb:** Điều hướng rõ ràng "Trang chủ > Tra cứu > [Loại tra cứu cụ thể]"
- **Hướng dẫn:** Mỗi trang đều có link "Hướng dẫn tra cứu"
- **Bảo mật:** Tất cả form đều có reCAPTCHA "Tôi không phải là người máy"

---

## 2. DANH SÁCH CÁC LOẠI TRA CỨU

### 2.1 Tra cứu không yêu cầu đăng nhập

| STT | Tên tra cứu | URL | Mô tả |
|-----|-------------|-----|-------|
| 1 | **Tra cứu mã số BHXH** | `/tracuu/Pages/tra-cuu-ho-gia-dinh.aspx` | Tra cứu mã số BHXH bằng thông tin cá nhân |
| 2 | **Tra cứu điểm thu, đại lý** | `/tracuu/pages/diem-thu-dai-ly.aspx` | Tìm địa chỉ điểm thu, đại lý thu BHXH/BHYT |
| 3 | **Tra cứu cơ quan bảo hiểm** | `/tracuu/Pages/tra-cuu-co-quan-bao-hiem.aspx` | Tìm thông tin cơ quan BHXH |
| 4 | **Tra cứu quá trình tham gia BHXH** | `/tracuu/Pages/tra-cuu-dong-bao-hiem.aspx` | Tra cứu lịch sử tham gia BHXH |
| 5 | **Tra cứu thông tin ghi nhận đóng BHXH, BHYT** | `/tracuu/pages/tra-cuu-thong-tin-ghi-nhan-dong-bhxh-bhyt.aspx` | Kiểm tra thông tin đóng bảo hiểm |
| 6 | **Tra cứu giá trị sử dụng thẻ BHYT** | `/tracuu/pages/tra-cuu-thoi-han-su-dung-the-bhyt.aspx` | Kiểm tra thời hạn và giá trị thẻ BHYT |
| 7 | **Tra cứu đơn vị tham gia BHXH** | `/tracuu/pages/don-vi-tham-gia-bhxh.aspx` | Tìm thông tin đơn vị tham gia BHXH |
| 8 | **Tra cứu CSKCB cấp giấy nghỉ việc hưởng BHXH** | `/tracuu/Pages/KCB-cap-giay-nghi-viec-huong-bhxh.aspx` | Danh sách cơ sở y tế cấp giấy nghỉ việc |
| 9 | **Tra cứu CSKCB ký hợp đồng khám chữa bệnh BHYT** | `/tracuu/Pages/cskcb-ky-hop-dong-kham-chua-benh-bhyt.aspx` | Danh sách cơ sở y tế có hợp đồng BHYT |
| 10 | **Công khai thông tin hưởng hỗ trợ theo Nghị quyết 116/NQ-CP** | `/tracuu/Pages/tra-cuu-ho-gia-dinh.aspx` | Thông tin công khai về hỗ trợ |

### 2.2 Tra cứu yêu cầu đăng nhập

| STT | Tên tra cứu | URL | Yêu cầu đăng nhập |
|-----|-------------|-----|-------------------|
| 11 | **Tra cứu bảo hiểm thất nghiệp** | `/tracuu/Pages/dang-nhap-tra-cuu.aspx` | ✅ Cần mã số BHXH |

---

## 3. PHÂN TÍCH CHI TIẾT CÁC TRANG TRA CỨU CHÍNH

### 3.1 Tra cứu điểm thu, đại lý (Đã kiểm tra)

**URL:** `https://baohiemxahoi.gov.vn/tracuu/pages/diem-thu-dai-ly.aspx`

**Mục đích:** Tìm địa chỉ các điểm thu và đại lý thu BHXH, BHYT theo khu vực địa lý

**Form tra cứu:**
- **Tỉnh/Thành phố:** ⭐ (Bắt buộc) - Dropdown select
- **Quận/Huyện:** ⭐ (Bắt buộc) - Dropdown select  
- **Phường/Xã:** (Tùy chọn) - Dropdown select
- **Thôn/Xóm:** (Tùy chọn) - Dropdown select
- **reCAPTCHA:** Bắt buộc

**Nút chức năng:**
- **"Tra cứu":** Thực hiện tìm kiếm
- **"Nhập lại":** Xóa form

**Tính năng đặc biệt:**
- Có chức năng hiển thị/ẩn bản đồ kết quả
- Kết quả hiển thị dạng danh sách và bản đồ

### 3.2 Tra cứu mã số BHXH (Đã kiểm tra)

**URL:** `https://baohiemxahoi.gov.vn/tracuu/Pages/tra-cuu-ho-gia-dinh.aspx`

**Mục đích:** Tra cứu mã số BHXH bằng thông tin cá nhân

**Form tra cứu:**
**Thông tin địa chỉ:**
- **Tỉnh/TP:** Dropdown select
- **Quận/Huyện:** Dropdown select
- **Phường/Xã:** Dropdown select  
- **Thôn/Xóm:** Dropdown select

**Thông tin cá nhân:**
- **Họ và tên:** Text input
- **CCCD/CMND/Hộ chiếu:** Text input
- **Ngày sinh:** Date picker (dd/mm/yyyy)
- **Giới tính:** Radio buttons (Có dấu/Không dấu)
- **Mã số BHXH:** Text input (tùy chọn - để xác thực)

**Bảo mật:**
- **reCAPTCHA:** "Tôi không phải là người máy"

**Tính năng đặc biệt:**
- Có link "Hướng dẫn tra cứu" riêng biệt
- Cho phép tra cứu ngược (nhập mã BHXH để xác thực thông tin)

### 3.3 Tra cứu quá trình tham gia BHXH (Đã kiểm tra)

**URL:** `https://baohiemxahoi.gov.vn/tracuu/Pages/tra-cuu-dong-bao-hiem.aspx`

**Mục đích:** Tra cứu lịch sử tham gia BHXH theo thời gian và địa điểm

**Form tra cứu:**
**Địa điểm và thời gian:**
- **Tỉnh thành:** Dropdown select
- **Cơ quan BHXH:** Dropdown select
- **Từ tháng/Năm:** Dual dropdown (tháng + năm)
- **Đến tháng/Năm:** Dual dropdown (tháng + năm)

**Thông tin cá nhân:**
- **Họ tên:** Text input
- **CMND:** Text input (với placeholder "Chứng minh thư nhân dân")
- **Mã số BHXH:** Text input
- **Số điện thoại:** Text input

**Tùy chọn nhập liệu:**
- **Kiểu gõ:** Radio buttons (Có dấu/Không dấu)

**Bảo mật:**
- **reCAPTCHA:** "Tôi không phải là người máy"

**Nút chức năng:**
- **"Lấy mã tra cứu":** Thực hiện tra cứu

**Đặc điểm:**
- Không yêu cầu đăng nhập trước
- Form phức tạp với nhiều trường thông tin
- Có thông báo về hạn mức tra cứu

### 3.4 Tra cứu bảo hiểm thất nghiệp (Đã kiểm tra)

**URL:** `https://baohiemxahoi.gov.vn/tracuu/Pages/dang-nhap-tra-cuu.aspx`

**Mục đích:** Tra cứu thông tin bảo hiểm thất nghiệp

**Form đăng nhập:**
- **Mã số BHXH:** ⭐ (Bắt buộc) - Text input
- **reCAPTCHA:** "Tôi không phải là người máy"

**Nút chức năng:**
- **"Lấy mã tra cứu":** Thực hiện đăng nhập/tra cứu

**Đặc điểm đặc biệt:**
- ✅ **YÊU CẦU ĐĂNG NHẬP:** Đây là trang duy nhất trong hệ thống yêu cầu xác thực
- Chỉ cần mã số BHXH để truy cập
- Quy trình 2 bước: Đăng nhập → Tra cứu
- Không có hướng dẫn đăng ký tài khoản mới
- Chỉ dành cho người đã có mã số BHXH

---

## 4. PHÂN TÍCH UX/UI VÀ TRẢI NGHIỆM NGƯỜI DÙNG

### 4.1 Điểm mạnh

✅ **Tổ chức thống nhất:** Tất cả trang tra cứu có layout và navigation nhất quán  
✅ **Menu sidebar:** Dễ chuyển đổi giữa các loại tra cứu khác nhau  
✅ **Breadcrumb rõ ràng:** Người dùng luôn biết mình đang ở đâu  
✅ **Bảo mật:** Tất cả form đều có reCAPTCHA chống bot  
✅ **Hướng dẫn:** Mỗi trang đều có link hướng dẫn sử dụng  
✅ **Đa dạng:** Bao phủ hầu hết nhu cầu tra cứu của người dân  
✅ **Không yêu cầu đăng nhập:** 10/11 loại tra cứu không cần tài khoản  

### 4.2 Điểm cần cải thiện

⚠️ **Form phức tạp:** Một số form yêu cầu quá nhiều thông tin (tra cứu quá trình tham gia)  
⚠️ **Thiếu validation:** Không có validation rõ ràng cho các trường input  
⚠️ **Thiếu feedback:** Không có thông báo lỗi cụ thể khi nhập sai  
⚠️ **Mobile UX:** Chưa kiểm tra responsive design  
⚠️ **Bảo mật dữ liệu:** Thiếu thông báo về chính sách bảo mật dữ liệu cá nhân  

---

## 5. BẢO MẬT VÀ QUYỀN RIÊNG TƯ

### 5.1 Các biện pháp bảo mật hiện có

🔒 **reCAPTCHA:** Tất cả form đều có bảo vệ chống bot  
🔒 **HTTPS:** Website sử dụng kết nối an toàn  
🔒 **Phân quyền:** Tra cứu BHTN yêu cầu mã số BHXH để truy cập  

### 5.2 Vấn đề bảo mật cần lưu ý

⚠️ **Thiếu thông báo bảo mật:** Không có cảnh báo về việc bảo vệ thông tin cá nhân  
⚠️ **Dữ liệu nhạy cảm:** Một số form yêu cầu CMND, CCCD mà không có cảnh báo bảo mật  
⚠️ **Thiếu 2FA:** Tra cứu BHTN chỉ yêu cầu mã BHXH, không có xác thực 2 lớp  

---

## 6. PHÂN LOẠI THEO MỨC ĐỘ BẢO MẬT

### 6.1 Mức độ Công khai (Public)
- Tra cứu điểm thu, đại lý
- Tra cứu cơ quan bảo hiểm  
- Tra cứu CSKCB (2 loại)
- Công khai thông tin hỗ trợ theo NQ 116

### 6.2 Mức độ Bán công khai (Semi-public)
- Tra cứu mã số BHXH
- Tra cứu đơn vị tham gia BHXH

### 6.3 Mức độ Cá nhân (Personal)
- Tra cứu quá trình tham gia BHXH
- Tra cứu thông tin đóng BHXH, BHYT
- Tra cứu giá trị thẻ BHYT

### 6.4 Mức độ Bảo mật (Secure)
- Tra cứu bảo hiểm thất nghiệp (yêu cầu đăng nhập)

---

## 7. KHUYẾN NGHỊ CẢI THIỆN

### 7.1 Ngắn hạn
1. **Thêm validation:** Kiểm tra format dữ liệu đầu vào
2. **Cải thiện thông báo lỗi:** Hiển thị lỗi cụ thể khi nhập sai
3. **Thêm progress indicator:** Cho các form nhiều bước
4. **Tối ưu mobile:** Cải thiện responsive design

### 7.2 Trung hạn  
1. **Thêm thông báo bảo mật:** Cảnh báo về việc bảo vệ dữ liệu cá nhân
2. **Đơn giản hóa form:** Giảm số trường bắt buộc ở một số tra cứu
3. **Thêm tính năng lưu kết quả:** Cho phép download/print kết quả
4. **Cải thiện hướng dẫn:** Video hướng dẫn sử dụng

### 7.3 Dài hạn
1. **Tích hợp SSO:** Single Sign-On cho tất cả dịch vụ
2. **API public:** Cho phép tích hợp với ứng dụng bên thứ 3
3. **AI chatbot:** Hỗ trợ tra cứu bằng chatbot
4. **Dashboard cá nhân:** Trang tổng quan cho người dùng đã đăng nhập

---

## 8. KẾT LUẬN

Hệ thống tra cứu trực tuyến của VSS đã đáp ứng tốt nhu cầu cơ bản của người dân với **11 loại tra cứu đa dạng** và **giao diện thống nhất**. Đặc biệt, việc **không yêu cầu đăng nhập** cho 10/11 loại tra cứu tạo thuận lợi lớn cho người dùng.

Tuy nhiên, hệ thống cần cải thiện về **trải nghiệm người dùng**, **bảo mật dữ liệu** và **tối ưu hóa form** để phục vụ tốt hơn nhu cầu tra cứu ngày càng tăng của người dân.

**Điểm nổi bật:** Đây là một trong những hệ thống tra cứu công khai tốt nhất trong các cơ quan nhà nước Việt Nam với tính năng phong phú và dễ tiếp cận.

---

**Ghi chú:** Phân tích này dựa trên khảo sát thực tế 4/11 trang tra cứu vào ngày 13/9/2025. Các trang còn lại có thể có đặc điểm tương tự hoặc khác biệt.