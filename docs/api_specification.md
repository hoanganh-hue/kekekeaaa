**TÀI LIỆU HƯỚNG DẪN KẾT NỐI API **

**THÔNG QUA NGSP**

| Kiểu | Nội dung |
| --- | --- |
| Địa chỉ adapter | https://api.[DonVi].gov.vn |
| Key (Bear token) |  |

**Danh mục chung**

**API danh mục**** – Mã định danh hệ thống ****QLVBĐH cấp 1**

**Lấy cấu trúc danh mục**

| URL kết nối tới dịch vụ lấy cấu trúc danh mục qlvanbandieuhanhcap1 | URL kết nối tới dịch vụ lấy cấu trúc danh mục qlvanbandieuhanhcap1 |
| --- | --- |
| Url | https://api.quangbinh.gov.vn/dmdc/Metadata/qlvanbandieuhanhcap1 |
| Request header | Request header |
| Authorization | “Bearer access_token” Ví dụ: “Bearer 49d61ed6-a9e8-3755-81cd-8395ee511c87” |
| Accept | application/json |
| Method | GET |

Response body:

| [   {       "PropertyCode": "MaDinhDanhCap1",       "PropertyName": "Mã định danh cấp 1",       "PropertyType": "String"   },   {       "PropertyCode": "TenDonVi",       "PropertyName": "Tên đơn vị",       "PropertyType": "String"   },   {       "PropertyCode": "DiaChi",       "PropertyName": "Địa chỉ",       "PropertyType": "String"   },   {       "PropertyCode": "Email",       "PropertyName": "Email",       "PropertyType": "String"   },   {       "PropertyCode": "SoDienThoai",       "PropertyName": "Số điện thoại",       "PropertyType": "String"   },   {       "PropertyCode": "Fax",       "PropertyName": "Fax",       "PropertyType": "String"   },   {       "PropertyCode": "Website",       "PropertyName": "Website",       "PropertyType": "String"   },   {       "PropertyCode": "QdBanHanhQdSuaDoi",       "PropertyName": "QĐ ban hành/ QĐ sửa đổi",       "PropertyType": "String"   },   {       "PropertyCode": "NgayBanHanhQd",       "PropertyName": "Ngày ban hành QĐ",       "PropertyType": "DateTime"   },   {       "PropertyCode": "CoQuanBanHanhQd",       "PropertyName": "Cơ Quan ban hành QĐ",       "PropertyType": "String"   } ] |
| --- |

**Lấy dữ liệu**

| URL kết nối tới dịch vụ lấy dữ liệu qlvanbandieuhanhcap1 | URL kết nối tới dịch vụ lấy dữ liệu qlvanbandieuhanhcap1 |
| --- | --- |
| Url | https://api.quangbinh.gov.vn/dmdc/Category/qlvanbandieuhanhcap1 |
| Request header | Request header |
| Authorization | “Bearer access_token” Ví dụ: “Bearer 49d61ed6-a9e8-3755-81cd-8395ee511c87” |
| Accept | application/json |
| Method | GET |

Response body:

| [   {       "MaDinhDanhCap1": "000.00.00.H30",       "TenDonVi": "UBND tỉnh Hậu Giang",       "DiaChi": null,       "Email": null,       "SoDienThoai": null,       "Fax": null,       "Website": null,       "QdBanHanhQdSuaDoi": "1220/QĐ-UBND",       "NgayBanHanhQd": "16/08/2018",       "CoQuanBanHanhQd": "UBND tỉnh Hậu Giang"   } ] |
| --- |

**Bổ sung dữ liệu danh mục**

| URL kết nối tới dịch vụ lấy dữ liệu qlvanbandieuhanhcap1 | URL kết nối tới dịch vụ lấy dữ liệu qlvanbandieuhanhcap1 | URL kết nối tới dịch vụ lấy dữ liệu qlvanbandieuhanhcap1 |
| --- | --- | --- |
| Url | https://api.quangbinh.gov.vn/dmdc/Category/qlvanbandieuhanhcap1 | https://api.quangbinh.gov.vn/dmdc/Category/qlvanbandieuhanhcap1 |
| Request header | Request header | Request header |
| Authorization | “Bearer access_token” Ví dụ: “Bearer 49d61ed6-a9e8-3755-81cd-8395ee511c87” | “Bearer access_token” Ví dụ: “Bearer 49d61ed6-a9e8-3755-81cd-8395ee511c87” |
| Accept | application/json | application/json |
| Method | POST | POST |
| Request body | Request body | Request body |
| body | body | [   {       "MaDinhDanhCap1": "000.00.00.H30",       "TenDonVi": "UBND tỉnh Hậu Giang",       "DiaChi": null,       "Email": null,       "SoDienThoai": null,       "Fax": null,       "Website": null,       "QdBanHanhQdSuaDoi": "1220/QĐ-UBND",       "NgayBanHanhQd": "16/08/2018",       "CoQuanBanHanhQd": "UBND tỉnh Hậu Giang"   } ] |

**Response body**

| TH1: Lỗi {     "MSG": "Data not insert: Record 1: MaDinhDanhCap1 "000.00.00.H30 is duplicate",     "Count": 0 } TH2: Thành công {     "MSG": "Done",     "Count": 1 } |
| --- |

**API ****các ****danh mục khác**

Khai thác các dịch vụ danh mục khác cũng tương tự như dịch vụ danh mục - mã định danh kết nối các hệ thống QLVBĐH cấp 1 với đường dẫn được mô tả theo danh sách sau:

| Tên | Endpoint |
| --- | --- |
| Danh mục và mã định danh kết nối các hệ thống QLVBĐH cấp 1 | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/qlvanbandieuhanhcap1 Get List https://api.quangbinh.gov.vn/dmdc/Category/qlvanbandieuhanhcap1 Post List https://api.quangbinh.gov.vn/dmdc/Category/qlvanbandieuhanhcap1 |
| Danh mục và mã định danh kết nối các hệ thống QLVBĐH cấp 2 | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/qlvanbandieuhanhcap2 Get List https://api.quangbinh.gov.vn/dmdc/Category/qlvanbandieuhanhcap2 Post List https://api.quangbinh.gov.vn/dmdc/Category/qlvanbandieuhanhcap2 |
| Danh mục và mã định danh kết nối các hệ thống QLVBĐH cấp 3 | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/qlvanbandieuhanhcap3 Get List https://api.quangbinh.gov.vn/dmdc/Category/qlvanbandieuhanhcap3 Post List https://api.quangbinh.gov.vn/dmdc/Category/qlvanbandieuhanhcap3 |
| Danh mục và mã định danh kết nối các hệ thống QLVBĐH cấp 4 | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/qlvanbandieuhanhcap4 Get List https://api.quangbinh.gov.vn/dmdc/Category/qlvanbandieuhanhcap4 Post List https://api.quangbinh.gov.vn/dmdc/Category/qlvanbandieuhanhcap4 |
| Danh mục và mã số các đơn vị hành chính Việt Nam cấp 1 (Tỉnh) | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/donvihanhchinhcap1 Get List https://api.quangbinh.gov.vn/dmdc/Category/donvihanhchinhcap1 Post List https://api.quangbinh.gov.vn/dmdc/Category/donvihanhchinhcap1 |
| Danh mục và mã số các đơn vị hành chính Việt Nam cấp 2 (Quận, Huyện) | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/donvihanhchinhcap2 Get List https://api.quangbinh.gov.vn/dmdc/Category/donvihanhchinhcap2 Post List https://api.quangbinh.gov.vn/dmdc/Category/donvihanhchinhcap2 |
| Danh mục và mã số các đơn vị hành chính Việt Nam cấp 3 (Phường, Xã) | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/donvihanhchinhcap3 Get List https://api.quangbinh.gov.vn/dmdc/Category/donvihanhchinhcap3 Post List https://api.quangbinh.gov.vn/dmdc/Category/donvihanhchinhcap3 |
| Danh mục Mã bưu chính vùng, khu vực | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/mabuuchinhvungkhuvuc Get List https://api.quangbinh.gov.vn/dmdc/Category/mabuuchinhvungkhuvuc Post List https://api.quangbinh.gov.vn/dmdc/Category/mabuuchinhvungkhuvuc |
| Danh mục Mã bưu chính cấp 1 (Tỉnh) | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/mabuuchinhcap1 Get List https://api.quangbinh.gov.vn/dmdc/Category/mabuuchinhcap1 Post List https://api.quangbinh.gov.vn/dmdc/Category/mabuuchinhcap1 |
| Danh mục Mã bưu chính cấp 2 (Quận, Huyện) | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/mabuuchinhcap2 Get List https://api.quangbinh.gov.vn/dmdc/Category/mabuuchinhcap2 Post List https://api.quangbinh.gov.vn/dmdc/Category/mabuuchinhcap2 |
| Danh mục Mã bưu chính cấp 3 (Phường, Xã) | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/mabuuchinhcap3 Get List https://api.quangbinh.gov.vn/dmdc/Category/mabuuchinhcap3 Post List https://api.quangbinh.gov.vn/dmdc/Category/mabuuchinhcap3 |
| Danh mục và mã các dân tộc | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/madantoc Get List https://api.quangbinh.gov.vn/dmdc/Category/madantoc Post List https://api.quangbinh.gov.vn/dmdc/Category/madantoc |
| Danh mục và mã các dân tộc và tên gọi khác | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/madantockhac Get List https://api.quangbinh.gov.vn/dmdc/Category/madantockhac Post List https://api.quangbinh.gov.vn/dmdc/Category/madantockhac |
| Danh mục và mã các tôn giáo | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/matongiao Get List https://api.quangbinh.gov.vn/dmdc/Category/matongiao Post List https://api.quangbinh.gov.vn/dmdc/Category/matongiao |
| Danh mục và mã giới tính | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/magioitinh Get List https://api.quangbinh.gov.vn/dmdc/Category/magioitinh Post List https://api.quangbinh.gov.vn/dmdc/Category/magioitinh |
| Danh mục và mã nhóm máu | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/manhommau Get List https://api.quangbinh.gov.vn/dmdc/Category/manhommau Post List https://api.quangbinh.gov.vn/dmdc/Category/manhommau |
| Danh mục và mã ý nghĩa nhóm máu | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/maynghianhommau Get List https://api.quangbinh.gov.vn/dmdc/Category/maynghianhommau Post List https://api.quangbinh.gov.vn/dmdc/Category/maynghianhommau |
| Danh mục và mã Quốc gia, quốc tịch | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/maquocgia Get List https://api.quangbinh.gov.vn/dmdc/Category/maquocgia Post List https://api.quangbinh.gov.vn/dmdc/Category/maquocgia |
| Danh mục và mã Tình trạng hôn nhân | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/matinhtranghonnhan Get List https://api.quangbinh.gov.vn/dmdc/Category/matinhtranghonnhan Post List https://api.quangbinh.gov.vn/dmdc/Category/matinhtranghonnhan |
| Danh mục giáo dục, đào tạo Việt Nam Cấp 1 | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/giaoducdaotaovncap1 Get List https://api.quangbinh.gov.vn/dmdc/Category/giaoducdaotaovncap1 Post List https://api.quangbinh.gov.vn/dmdc/Category/giaoducdaotaovncap1 |
| Danh mục giáo dục, đào tạo Việt Nam Cấp 2 | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/giaoducdaotaovncap2 Get List https://api.quangbinh.gov.vn/dmdc/Category/giaoducdaotaovncap2 Post List https://api.quangbinh.gov.vn/dmdc/Category/giaoducdaotaovncap2 |
| Danh mục giáo dục, đào tạo Việt Nam Cấp 3 | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/giaoducdaotaovncap3 Get List https://api.quangbinh.gov.vn/dmdc/Category/giaoducdaotaovncap3 Post List https://api.quangbinh.gov.vn/dmdc/Category/giaoducdaotaovncap3 |
| Danh mục giáo dục, đào tạo cấp IV trình độ cao đẳng, đại học | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/giaoducdaotaovncap4 Get List https://api.quangbinh.gov.vn/dmdc/Category/giaoducdaotaovncap4 Post List https://api.quangbinh.gov.vn/dmdc/Category/giaoducdaotaovncap4 |
| Danh mục giáo dục, đào tạo cấp IV trình độ thạc sĩ, tiến sĩ | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/giaoducdaotaovncap5 Get List https://api.quangbinh.gov.vn/dmdc/Category/giaoducdaotaovncap5 Post List https://api.quangbinh.gov.vn/dmdc/Category/giaoducdaotaovncap5 |
| Danh mục và mã chức danh trong các cơ quan Đảng cộng sản Việt Nam | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/machucdanhcqdcsvn Get List https://api.quangbinh.gov.vn/dmdc/Category/machucdanhcqdcsvn Post List https://api.quangbinh.gov.vn/dmdc/Category/machucdanhcqdcsvn |
| Danh mục bậc lương | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/mabacluong Get List https://api.quangbinh.gov.vn/dmdc/Category/mabacluong Post List https://api.quangbinh.gov.vn/dmdc/Category/mabacluong |
| Danh mục bảng lương | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/mabangluong Get List https://api.quangbinh.gov.vn/dmdc/Category/mabangluong Post List https://api.quangbinh.gov.vn/dmdc/Category/mabangluong |
| Danh mục loại công chức, viên chức, nhân viên, lãnh đạo | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/machucdanh Get List https://api.quangbinh.gov.vn/dmdc/Category/machucdanh Post List https://api.quangbinh.gov.vn/dmdc/Category/machucdanh |
| Danh mục nhóm lương | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/manhomluong Get List https://api.quangbinh.gov.vn/dmdc/Category/manhomluong Post List https://api.quangbinh.gov.vn/dmdc/Category/manhomluong |
| Danh mục và mã các hệ số lương | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/mahesoluong Get List https://api.quangbinh.gov.vn/dmdc/Category/mahesoluong Post List https://api.quangbinh.gov.vn/dmdc/Category/mahesoluong |
| Danh mục và mã mức lương tối thiểu vùng | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/mahesoluongvung Get List https://api.quangbinh.gov.vn/dmdc/Category/mahesoluongvung Post List https://api.quangbinh.gov.vn/dmdc/Category/mahesoluongvung |
| Danh mục mã thi đua khen thưởng | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/mathiduakhenthuong Get List https://api.quangbinh.gov.vn/dmdc/Category/mathiduakhenthuong Post List https://api.quangbinh.gov.vn/dmdc/Category/mathiduakhenthuong |
| Danh mục Mã loại văn bản theo quy định pháp luật | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/maloaivanbantheoqdpl Get List https://api.quangbinh.gov.vn/dmdc/Category/maloaivanbantheoqdpl Post List https://api.quangbinh.gov.vn/dmdc/Category/maloaivanbantheoqdpl |
| Danh mục Mã tên các loại văn bản quy phạm pháp luật | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/matenvanbantheoqdpl Get List https://api.quangbinh.gov.vn/dmdc/Category/matenvanbantheoqdpl Post List https://api.quangbinh.gov.vn/dmdc/Category/matenvanbantheoqdpl |
| Danh mục Mã tên các loại văn bản hành chính | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/matenvanbanhanhchinh Get List https://api.quangbinh.gov.vn/dmdc/Category/matenvanbanhanhchinh Post List https://api.quangbinh.gov.vn/dmdc/Category/matenvanbanhanhchinh |
| Danh mục Mã quy định độ khẩn văn bản | Metadata https://api.quangbinh.gov.vn/dmdc/Metadata/dokhanvanban Get List https://api.quangbinh.gov.vn/dmdc/Category/dokhanvanban Post List https://api.quangbinh.gov.vn/dmdc/Category/dokhanvanban |

**Dịch vụ hộ tịch**

**Dịch vụ đăng ký hộ tịch – dangKyHoTich**

| URL kết nối tới dịch vụ dangKyHoTich | URL kết nối tới dịch vụ dangKyHoTich |
| --- | --- |
| Url | https://api.quangbinh.gov.vn/apiHoTichTuPhap/dangKyHoTich |
| Request header | Request header |
| Authorization | “Bearer access_token” Ví dụ: “Bearer 49d61ed6-a9e8-3755-81cd-8395ee511c87” |
| Content-Type | application/json |
| Method | POST |
| Request body | Request body |
| body | {           "maDonVi": "", 	"module": "", 	"maHoSo": "", 	"ngayTiepNhan": "", 	"data": "" } |

| STT | Tham số | Kiểu dữ liệu | Mô tả |
| --- | --- | --- | --- |
| 1 | maDonVi | Long | Mã đơn vị tiếp nhận hồ sơ: - Là mã đơn vị hành chính của nơi đăng ký được ghi theo mã do Bộ tư pháp cung cấp trong dịch vụ danh mục; - Tên chính xác sẽ do Hệ thống tự động tính toán dựa theo thời điểm đăng ký. |
| 2 | module | String | Mã nghiệp vụ |
| 3 | maHoSo | String | Số phiếu tiếp nhận của hồ sơ trên Hệ thống thông tin một cửa điện tử. |
| 4 | ngayTiepNhan | Date | Ngày tiếp nhận hồ sơ. |
| 5 | data | String | Thông điệp dữ liệu dưới dạng XML (xem mô tả tại Mục 3.2.1). |

**Response body**

| Trạng thái | Mô tả trạng thái | Giá trị |
| --- | --- | --- |
| 1 | Gửi thông tin thành công | Khuyết |
| 0 | Đã có lỗi xảy ra trong quá trình gửi thông tin | Khuyết, hiển thị trường mã lỗi và mô tả lỗi |
| Biệt lệ (Exception): Trả về khi kết quả trạng thái trả về nhận được là 0 | Biệt lệ (Exception): Trả về khi kết quả trạng thái trả về nhận được là 0 | Biệt lệ (Exception): Trả về khi kết quả trạng thái trả về nhận được là 0 |
| Mã lỗi | Mô tả lỗi | Mô tả lỗi |
| 100 | AUTHEN_ERROR - Mã xác thực không chính xác | AUTHEN_ERROR - Mã xác thực không chính xác |
| 101 | IP_DISALLOWED - Địa chỉ IP không được phép truy cập | IP_DISALLOWED - Địa chỉ IP không được phép truy cập |
| 106 | AGENCY_ID_INCORRECT - Mã đơn vị không chính xác. | AGENCY_ID_INCORRECT - Mã đơn vị không chính xác. |
| 500 | DATA_INCORRECT – Hệ thống thông tin chủ động đưa ra lỗi chi tiết. | DATA_INCORRECT – Hệ thống thông tin chủ động đưa ra lỗi chi tiết. |

**Dịch vụ danh mục – danhMuc**

| URL kết nối tới dịch vụ danhMuc | URL kết nối tới dịch vụ danhMuc |
| --- | --- |
| Url | https://api.quangbinh.gov.vn/apiHoTichTuPhap/danhMuc |
| Request header | Request header |
| Authorization | “Bearer access_token” Ví dụ: “Bearer 49d61ed6-a9e8-3755-81cd-8395ee511c87” |
| Content-Type | application/json |
| Method | POST |
| Request body | Request body |
| body | {           "loaiDanhMuc": "" } |

Giải thích các tham số: Loại danh mục nhận 1 trong 5 giá trị như sau:

1 - Danh mục quốc tịch;

2 - Danh mục quốc gia;

3 - Danh mục dân tộc;

4 - Danh mục địa danh hành chính (cấp tỉnh);

5 - Danh mục giấy tờ tùy thân.

| Trạng thái | Mô tả trạng thái | Giá trị |
| --- | --- | --- |
| 1 | Giao dịch thành công | Chuỗi JSON mô tả dữ liệu danh mục. Cấu trúc JSON phụ thuộc từng loại danh mục. |
| 0 | Đã có lỗi xảy ra trong quá trình gửi thông tin | Khuyết, hiển thị trường mã lỗi và mô tả lỗi |
| Biệt lệ (Exception): Trả về khi kết quả trạng thái trả về nhận được là 0 | Biệt lệ (Exception): Trả về khi kết quả trạng thái trả về nhận được là 0 | Biệt lệ (Exception): Trả về khi kết quả trạng thái trả về nhận được là 0 |
| Mã lỗi | Mô tả lỗi | Mô tả lỗi |
| 100 | AUTHEN_ERROR - Mã xác thực không chính xác | AUTHEN_ERROR - Mã xác thực không chính xác |
| 101 | IP_DISALLOWED - Địa chỉ IP không được phép truy cập | IP_DISALLOWED - Địa chỉ IP không được phép truy cập |
| 302 | DATA_TYPE_INVALID - Loại dữ liệu danh mục không hợp lệ | DATA_TYPE_INVALID - Loại dữ liệu danh mục không hợp lệ |

**Dịch vụ tra trạng thái xử lý hồ sơ – traTrangThaiHoSo**

| URL kết nối tới dịch vụ traTrangThaiHoSo | URL kết nối tới dịch vụ traTrangThaiHoSo |
| --- | --- |
| Url | https://api.quangbinh.gov.vn/apiHoTichTuPhap/traTrangThaiHoSo |
| Request header | Request header |
| Authorization | “Bearer access_token” Ví dụ: “Bearer 49d61ed6-a9e8-3755-81cd-8395ee511c87” |
| Content-Type | application/json |
| Method | POST |
| Request body | Request body |
| body | {           "maDonVi": "",           "maHoSo": "" } |

Giải thích các tham số:

| STT | Tham số | Kiểu dữ liệu | Mô tả |
| --- | --- | --- | --- |
| 1 | maDonVi | Long | Mã đơn vị tiếp nhận hồ sơ: - Là mã đơn vị hành chính của nơi đăng ký được ghi theo mã do Bộ tư pháp cung cấp trong dịch vụ danh mục; - Tên chính xác sẽ do Hệ thống tự động tính toán dựa theo thời điểm đăng ký. |
| 2 | maHoSo | String | Số phiếu tiếp nhận của hồ sơ trên Hệ thống thông tin một cửa điện tử. |

Response body:

| Trạng thái | Mô tả trạng thái | Giá trị |
| --- | --- | --- |
| 1 | Đã tiếp nhận hồ sơ, chờ xử lý | Khuyết. |
| 2 | Hồ sơ cần bổ sung thông tin: … (trả về chi tiết thông tin cần bổ sung) | Khuyết. |
| 3 | Hồ sơ đủ điều kiện giải quyết | Khuyết. |
| 4 | Đã hoàn thành đăng ký | Khuyết. |
| 0 | Đã có lỗi xảy ra trong quá trình gửi thông tin | Khuyết, hiển thị trường mã lỗi và mô tả lỗi. |
| Biệt lệ (Exception): Trả về khi kết quả trạng thái trả về nhận được là 0 | Biệt lệ (Exception): Trả về khi kết quả trạng thái trả về nhận được là 0 | Biệt lệ (Exception): Trả về khi kết quả trạng thái trả về nhận được là 0 |
| Mã lỗi | Mô tả lỗi | Mô tả lỗi |
| 100 | AUTHEN_ERROR - Mã xác thực không chính xác. | AUTHEN_ERROR - Mã xác thực không chính xác. |
| 101 | IP_DISALLOWED - Địa chỉ IP không được phép truy cập. | IP_DISALLOWED - Địa chỉ IP không được phép truy cập. |
| 106 | AGENCY_ID_INCORRECT - Mã đơn vị không chính xác. | AGENCY_ID_INCORRECT - Mã đơn vị không chính xác. |
| 201 | RECORD_NOT_FOUND - Hồ sơ không tồn tại, đề nghị xem lại số phiếu tiếp nhận. | RECORD_NOT_FOUND - Hồ sơ không tồn tại, đề nghị xem lại số phiếu tiếp nhận. |

**Dịch vụ kết quả đăng ký hồ sơ – ketQuaDangKyHS**

| URL kết nối tới dịch vụ traTrangThaiHoSo | URL kết nối tới dịch vụ traTrangThaiHoSo |
| --- | --- |
| Url | https://api.quangbinh.gov.vn/apiHoTichTuPhap/ketQuaDangKyHS |
| Request header | Request header |
| Authorization | “Bearer access_token” Ví dụ: “Bearer 49d61ed6-a9e8-3755-81cd-8395ee511c87” |
| Content-Type | application/json |
| Method | POST |
| Request body | Request body |
| body | {           "maDonVi": "",           "maHoSo": "" } |

Giải thích các tham số:

| STT | Tham số | Kiểu dữ liệu | Mô tả |
| --- | --- | --- | --- |
| 1 | maDonVi | Long | Mã đơn vị tiếp nhận hồ sơ: - Là mã đơn vị hành chính của nơi đăng ký được ghi theo mã do Bộ tư pháp cung cấp; - Tên chính xác sẽ do Hệ thống tự động tính toán dựa theo thời điểm đăng ký. |
| 2 | maHoSo | String | Số phiếu tiếp nhận của hồ sơ trên Hệ thống thông tin một cửa điện tử. |

Response body:

| Trạng thái | Mô tả trạng thái | Giá trị |
| --- | --- | --- |
| 1 | Giao dịch thành công |  |
| 0 | Đã có lỗi xảy ra trong quá trình gửi thông tin hoặc hồ sơ chưa hoàn thành | Khuyết, hiển thị trường mã lỗi và mô tả lỗi. |
| Biệt lệ (Exception): Trả về khi kết quả trạng thái trả về nhận được là 0 | Biệt lệ (Exception): Trả về khi kết quả trạng thái trả về nhận được là 0 | Biệt lệ (Exception): Trả về khi kết quả trạng thái trả về nhận được là 0 |
| Mã lỗi | Mô tả lỗi | Mô tả lỗi |
| 100 | AUTHEN_ERROR - Mã xác thực không chính xác. | AUTHEN_ERROR - Mã xác thực không chính xác. |
| 101 | IP_DISALLOWED - Địa chỉ IP không được phép truy cập. | IP_DISALLOWED - Địa chỉ IP không được phép truy cập. |
| 106 | AGENCY_ID_INCORRECT - Mã đơn vị không chính xác. | AGENCY_ID_INCORRECT - Mã đơn vị không chính xác. |
| 200 | RECORD_UNCOMPLETE – Hồ sơ chưa hoàn thành đăng ký. | RECORD_UNCOMPLETE – Hồ sơ chưa hoàn thành đăng ký. |
| 201 | RECORD_NOT_FOUND - Hồ sơ không tồn tại, đề nghị xem lại số phiếu tiếp nhận. | RECORD_NOT_FOUND - Hồ sơ không tồn tại, đề nghị xem lại số phiếu tiếp nhận. |

**Dịch vụ lấy danh sách hồ sơ đã đăng ký – dsHoSoDangKy**

| URL kết nối tới dịch vụ dsHoSoDangKy | URL kết nối tới dịch vụ dsHoSoDangKy |
| --- | --- |
| Url | https://api.quangbinh.gov.vn/apiHoTichTuPhap/dsHoSoDangKy |
| Request header | Request header |
| Authorization | “Bearer access_token” Ví dụ: “Bearer 49d61ed6-a9e8-3755-81cd-8395ee511c87” |
| Content-Type | application/json |
| Method | POST |
| Request body | Request body |
| body | {           "module": "",           "ngayCapNhat": "" } |

Giải thích các tham số:

| STT | Tham số | Kiểu dữ liệu | Mô tả |
| --- | --- | --- | --- |
| 1 | module | String | Mã nghiệp vụ. |
| 2 | ngayCapNhat | Date | Ngày cập nhật hồ sơ – là ngày hồ sơ được tạo mới trên Hệ thống thông tin đăng ký và quản lý hộ tịch hoặc ngày hồ sơ được thay đổi thông tin gần nhất nếu hồ sơ đã được cập nhật, thay đổi nội dung. |

Response body

| Trạng thái | Mô tả trạng thái | Giá trị |
| --- | --- | --- |
| 1 | Giao dịch thành công | [ 	{ 		"id":"…", 		"maDonVi":"…" 	}, //Hồ sơ thứ nhất 	{ 		" id":"…", 		"maDonVi":"…" 	}, //Hồ sơ thứ hai… 	… ] |
| 0 | Đã có lỗi xảy ra trong quá trình gửi thông tin hoặc hồ sơ chưa hoàn thành | Khuyết, hiển thị trường mã lỗi và mô tả lỗi. |
| Biệt lệ (Exception): Trả về khi kết quả trạng thái trả về nhận được là 0 | Biệt lệ (Exception): Trả về khi kết quả trạng thái trả về nhận được là 0 | Biệt lệ (Exception): Trả về khi kết quả trạng thái trả về nhận được là 0 |
| Mã lỗi | Mô tả lỗi | Mô tả lỗi |
| 100 | AUTHEN_ERROR - Mã xác thực không chính xác. | AUTHEN_ERROR - Mã xác thực không chính xác. |
| 101 | IP_DISALLOWED - Địa chỉ IP không được phép truy cập. | IP_DISALLOWED - Địa chỉ IP không được phép truy cập. |
| 108 | PROVINCE_ID_INCORRECT – Mã tỉnh không chính xác. | PROVINCE_ID_INCORRECT – Mã tỉnh không chính xác. |

**Dịch vụ trả thông tin chi tiết từng hồ sơ đã lưu – traHoSo**

| URL kết nối tới dịch vụ traHoSo | URL kết nối tới dịch vụ traHoSo |
| --- | --- |
| Url | https://api.quangbinh.gov.vn/apiHoTichTuPhap/traHoSo |
| Request header | Request header |
| Authorization | “Bearer access_token” Ví dụ: “Bearer 49d61ed6-a9e8-3755-81cd-8395ee511c87” |
| Content-Type | application/json |
| Method | POST |
| Request body | Request body |
| body | {           "module": "",           "maHoSo": "" } |

Giải thích các tham số:

| STT | Tham số | Kiểu dữ liệu | Mô tả |
| --- | --- | --- | --- |
| 1 | module | String | Mã nghiệp vụ. |
| 2 | maHoSo | Long | Mã hồ sơ (ID của hồ sơ trên Hệ thống thông tin đăng ký và quản lý hộ tịch). |

Response body:

| Trạng thái | Mô tả trạng thái | Giá trị |
| --- | --- | --- |
| 1 | Giao dịch thành công | [  {    "id":"…",    "so":"…",    "quyenSo":"…",    "trangSo":"…",    …  }, //Hồ sơ thứ nhất  {    "id":"…",    "so":"…",    "quyenSo":"…",    "trangSo":"…",    …  }, //Hồ sơ thứ hai… nếu lấy danh sách qua dịch vụ traDanhSachHoSo    … ] |
| 0 | Đã có lỗi xảy ra trong quá trình gửi thông tin hoặc hồ sơ chưa hoàn thành | Khuyết, hiển thị trường mã lỗi và mô tả lỗi. |
| Biệt lệ (Exception): Trả về khi kết quả trạng thái trả về nhận được là 0 | Biệt lệ (Exception): Trả về khi kết quả trạng thái trả về nhận được là 0 | Biệt lệ (Exception): Trả về khi kết quả trạng thái trả về nhận được là 0 |
| Mã lỗi | Mô tả lỗi | Mô tả lỗi |
| 100 | AUTHEN_ERROR - Mã xác thực không chính xác. | AUTHEN_ERROR - Mã xác thực không chính xác. |
| 101 | IP_DISALLOWED - Địa chỉ IP không được phép truy cập. | IP_DISALLOWED - Địa chỉ IP không được phép truy cập. |
| 108 | PROVINCE_ID_INCORRECT – Mã tỉnh không chính xác. | PROVINCE_ID_INCORRECT – Mã tỉnh không chính xác. |
| 200 | RECORD_UNCOMPLETE – Hồ sơ chưa hoàn thành đăng ký. | RECORD_UNCOMPLETE – Hồ sơ chưa hoàn thành đăng ký. |
| 201 | RECORD_NOT_FOUND - Hồ sơ không tồn tại, đề nghị xem lại số phiếu tiếp nhận. | RECORD_NOT_FOUND - Hồ sơ không tồn tại, đề nghị xem lại số phiếu tiếp nhận. |

**Dịch vụ trả thông tin chi tiết danh sách các hồ sơ – traDanhSachHoSo**

| URL kết nối tới dịch vụ traDanhSachHoSo | URL kết nối tới dịch vụ traDanhSachHoSo |
| --- | --- |
| Url | https://api.quangbinh.gov.vn/apiHoTichTuPhap/traDanhSachHoSo |
| Request header | Request header |
| Authorization | “Bearer access_token” Ví dụ: “Bearer 49d61ed6-a9e8-3755-81cd-8395ee511c87” |
| Content-Type | application/json |
| Method | POST |
| Request body | Request body |
| body | {           "maTinh": "",           "module": "",           "dsMaHoSo": [""] } |

Giải thích các tham số:

| STT | Tham số | Kiểu dữ liệu | Mô tả |
| --- | --- | --- | --- |
| 1 | module | String | Mã nghiệp vụ. |
| 2 | dsMaHoSo | Long[] | Danh sách mã hồ sơ (ID của hồ sơ trên Hệ thống thông tin đăng ký và quản lý hộ tịch). |

Response body

| Trạng thái | Mô tả trạng thái | Giá trị |
| --- | --- | --- |
| 1 | Giao dịch thành công | [  {    "id":"…",    "so":"…",    "quyenSo":"…",    "trangSo":"…",    …  }, //Hồ sơ thứ nhất  {    "id":"…",    "so":"…",    "quyenSo":"…",    "trangSo":"…",    …  }, //Hồ sơ thứ hai… nếu lấy danh sách qua dịch vụ traDanhSachHoSo    … ] |
| 0 | Đã có lỗi xảy ra trong quá trình gửi thông tin hoặc hồ sơ chưa hoàn thành | Khuyết, hiển thị trường mã lỗi và mô tả lỗi. |
| Biệt lệ (Exception): Trả về khi kết quả trạng thái trả về nhận được là 0 | Biệt lệ (Exception): Trả về khi kết quả trạng thái trả về nhận được là 0 | Biệt lệ (Exception): Trả về khi kết quả trạng thái trả về nhận được là 0 |
| Mã lỗi | Mô tả lỗi | Mô tả lỗi |
| 100 | AUTHEN_ERROR - Mã xác thực không chính xác. | AUTHEN_ERROR - Mã xác thực không chính xác. |
| 101 | IP_DISALLOWED - Địa chỉ IP không được phép truy cập. | IP_DISALLOWED - Địa chỉ IP không được phép truy cập. |
| 108 | PROVINCE_ID_INCORRECT – Mã tỉnh không chính xác. | PROVINCE_ID_INCORRECT – Mã tỉnh không chính xác. |
| 201 | RECORD_NOT_FOUND - Hồ sơ không tồn tại, đề nghị xem lại số phiếu tiếp nhận. | RECORD_NOT_FOUND - Hồ sơ không tồn tại, đề nghị xem lại số phiếu tiếp nhận. |

**Dịch vụ lý lịch tư pháp**

| Kiểu | Nội dung |
| --- | --- |
| Địa chỉ adapter | https://api.quangbinh.gov.vn/apiLyLichTuPhap/ |
| Lĩnh vực | Lý lịch tư pháp |
| Phiên bản | 1.0 |

| TT | Chức năng | Mô tả |
| --- | --- | --- |
| 1 | nhanHoSoDangKy | Tiếp nhận thông tin tờ khai từ Phần mềm một cửa gửi sang Phần mềm Quản lý lý lịch tư pháp dùng chung để xử lý nghiệp vụ |
| 2 | traTrangThaiHs | Trả thông tin trạng thái của một hồ sơ cụ thể từ Phần mềm Quản lý lý lịch tư pháp dùng chung sang Phần mềm một cửa |
| 3 | traHoSo | Cung cấp thông tin từ khai từ Phân hệ đăng ký cấp Phiếu lý lịch tư pháp hoặc Phần mềm Quản lý Lý lịch tư pháp dùng chung sang Phần mềm một cửa |
| 4 | traDanhMuc | Trả thông tin danh mục |
| 5 | danhDauHsThanhCong | Cập nhật trạng thái Phần mềm một cửa đã lấy dữ liệu thành công từ Phần mềm Quản lý lý lịch tư pháp dùng chung |
| 6 | traDsTrangThaiHs | Trả danh sách trạng thái của các hồ sơ có thay đổi trạng thái từ Phần mềm Quản lý lý lịch tư pháp dùng chung sang Phần mềm một cửa |

Chung cho các hàm:

| Request header | Request header |
| --- | --- |
| Authorization | “Bearer access_token” Ví dụ: “Bearer 49d61ed6-a9e8-3755-81cd-8395ee511c87” |
| Content-Type | application/json |
| Method | POST |

**Nhận hồ sơ đăng ký – ****nhanHoSoDangKy**

| Tên hàm: | nhanHoSoDangKy | nhanHoSoDangKy | nhanHoSoDangKy |
| --- | --- | --- | --- |
| Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/nhanHoSoDangKy | Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/nhanHoSoDangKy | Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/nhanHoSoDangKy | Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/nhanHoSoDangKy |
| Tham số truyền vào | Tham số truyền vào | Tham số truyền vào | Tham số truyền vào |
| TT | Trường tham số | Kiểu dữ liệu | Mô tả |
| 1 | idMinistryJustice | String | Mã đơn vị |
| 2 | idReceivedDec | String | Số phiếu tiếp nhận (là duy nhất với mỗi hồ sơ tiếp nhận) |
| 3 | dateReceivedDec | String | Ngày tiếp nhận hồ sơ (tuân thủ định dạng "dd/mm/yyyy") |
| 4 | datePromissoryDec | String | Ngày hẹn trả Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) |
| 7 | idMoneyReceipt | String | Số biên lai thu tiền |
| Thông tin tờ khai | Thông tin tờ khai | Thông tin tờ khai | Thông tin tờ khai |
| 5 | declarationWSForm | JSON | Thông tin tờ khai - Tham chiếu phụ lục đính kèm |
| 6 | residenceWSForm | JSON | Thông tin quá trình cư trú - Tham chiếu phụ lục đính kèm |
| 7 | mandatorWSForm | JSON | Thông tin ủy quyền - Tham chiếu phụ lục đính kèm |
| Giá trị trả ra | Giá trị trả ra | Giá trị trả ra | Giá trị trả ra |
|  | Response | JSON | STATUS: Mã trạng thái, lỗi DESCRIPTION: Mô tả lỗi (nếu có) ID: Mã định danh trên hệ thống LLTP (ID mã hóa) |

**Trả trạng thái hồ sơ – ****traTrangThaiHs**

| Tên hàm | traTrangThaiHs | traTrangThaiHs | traTrangThaiHs |
| --- | --- | --- | --- |
| Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/LLTP-API- traTrangThaiHs | Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/LLTP-API- traTrangThaiHs | Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/LLTP-API- traTrangThaiHs | Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/LLTP-API- traTrangThaiHs |
| Tham số truyền vào | Tham số truyền vào | Tham số truyền vào | Tham số truyền vào |
| TT | Trường tham số | Kiểu dữ liệu | Mô tả |
| 1 | idReceivedDec | String | Là số hồ sơ (số phiếu tiếp nhận) trong trường hợp infoType = 2;  Là số phiếu hẹn trong trường hợp infoType = 1 |
| 2 | infoType | String | Loại thông tin tra cứu: [1] nộp hồ sơ không qua 1 cửa; [2] nộp hồ sơ qua 1 cửa |
| 3 | identifyNo | String | Số CMT/Hộ chiếu. Áp dụng trong trường hợp infoType = 1 (Không nộp hồ sơ qua 1 cửa thì tra cứu dựa trên số phiếu hẹn và số CMT/Hộ chiếu) |
| Giá trị trả ra | Giá trị trả ra | Giá trị trả ra | Giá trị trả ra |
|  | Response | JSON | STATUS: Mã trạng thái, lỗi DESCRIPTION: Nguyên nhân lỗi (nếu có) DEC_STATUS_ID:  [3] STP đã tiếp nhận: hồ sơ đã được gửi từ hệ thống một cửa điện tử sang hệ thống nghiệp vụ [4] Đang xử lý: STP đang xử lý hồ sơ [5] Đã có phiếu: STP đã xử lý xong và đã có phiếu DEC_STATUS_NAME: Tên trạng thái APPROVE_DATE: Ngày phê duyệt phiếu LLTP (trong trường hợp trạng thái là đã có phiếu). Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) ISSUE_DATE: Ngày cấp phiếu. Tuân thủ định dạng “DD/MM/YYYY” |

**Trả hồ sơ – ****traHoSo**

| Tên hàm: | traHoSo | traHoSo | traHoSo |
| --- | --- | --- | --- |
| Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/LLTP-API-traHoSo | Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/LLTP-API-traHoSo | Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/LLTP-API-traHoSo | Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/LLTP-API-traHoSo |
| Tham số truyền vào | Tham số truyền vào | Tham số truyền vào | Tham số truyền vào |
| TT | Trường tham số | Kiểu dữ liệu | Mô tả |
| 1 | infoType | String | [1]: trả hồ sơ nộp trực tuyến [2]: trả hồ sơ nộp trực tiếp |
| Giá trị trả ra | Giá trị trả ra | Giá trị trả ra | Giá trị trả ra |
|  | Response | JSON | declarationTraHoSoForm: Thông tin nhân thân residenceWSForm: Thông tin cư trú mandatorWSForm: Thông tin ủy quyền Tham khảo Phụ lục I |

**Tra danh mục – ****traDanhMuc**

| Tên hàm: | traDanhMuc | traDanhMuc | traDanhMuc |
| --- | --- | --- | --- |
| Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/LLTP-API- traDanhMuc | Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/LLTP-API- traDanhMuc | Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/LLTP-API- traDanhMuc | Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/LLTP-API- traDanhMuc |
| Tham số truyền vào | Tham số truyền vào | Tham số truyền vào | Tham số truyền vào |
| TT | Trường tham số | Kiểu dữ liệu | Mô tả |
| 1 | infoType | String | [1]: Danh mục hành chính [2]: Danh mục quốc tịch [3]: Danh mục dân tộc [4]: Danh mục cơ quan [5]: Danh mục đơn vị |
| Giá trị trả ra | Giá trị trả ra | Giá trị trả ra | Giá trị trả ra |
|  | Response | JSON | ID: Mã danh mục NAME: Tên danh mục |

**Đánh dấu hồ sơ thành công – ****danhDauHsThanhCong**

| Tên hàm: | danhDauHsThanhCong | danhDauHsThanhCong | danhDauHsThanhCong |
| --- | --- | --- | --- |
| Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/LLTP-API-danhDauHsThanhCong | Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/LLTP-API-danhDauHsThanhCong | Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/LLTP-API-danhDauHsThanhCong | Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/LLTP-API-danhDauHsThanhCong |
| Tham số truyền vào | Tham số truyền vào | Tham số truyền vào | Tham số truyền vào |
| TT | Trường tham số | Kiểu dữ liệu | Mô tả |
| 1 | declarationId | String | Danh sách ID (mã hóa) cần đánh dấu là đã lấy dữ liệu thành công. Các ID phân cách nhau bằng dấu ; |
| 2 | infoType | String | [1] Đánh dấu lấy hồ sơ nộp trực tiếp thành công [2] Đánh dấu lấy trạng thái hồ sơ thành công [3] Đánh dấu lấy hồ sơ nộp trực tuyến thành công |
| Giá trị trả ra | Giá trị trả ra | Giá trị trả ra | Giá trị trả ra |
|  | Response | JSON | STATUS: Mã trạng thái, lỗi DESCRIPTION: Mô tả lỗi (nếu có) |

**Trả danh sách trạng thái hồ sơ ****–**** ****traDsTrangThaiHs**

| Tên hàm: | traDsTrangThaiHs | traDsTrangThaiHs | traDsTrangThaiHs |
| --- | --- | --- | --- |
| Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/LLTP-API- traDsTrangThaiHs | Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/LLTP-API- traDsTrangThaiHs | Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/LLTP-API- traDsTrangThaiHs | Url: https://api.quangbinh.gov.vn/apiLyLichTuPhap/LLTP-API- traDsTrangThaiHs |
| Tham số truyền vào | Tham số truyền vào | Tham số truyền vào | Tham số truyền vào |
| TT | Trường tham số | Kiểu dữ liệu | Mô tả |
| 1 | infoType | String | [1]: Hồ sơ không qua 1 cửa [2]: Hồ sơ qua 1 cửa |
| Giá trị trả ra | Giá trị trả ra | Giá trị trả ra | Giá trị trả ra |
|  | Response | JSON | STATUS: Mã trạng thái, lỗi DESCRIPTION: Mô tả lỗi (nếu có) LISTCONTENT: Danh sách hồ sơ và trạng thái (Kiểu dữ liệu JSON) - DECLARATION_ID: ID của hồ sơ - DEC_STATUS_ID:       [3] STP đã tiếp nhận: hồ sơ đã được gửi từ hệ thống một cửa điện tử sang hệ thống nghiệp vụ      [4] Đang xử lý: STP đang xử lý hồ sơ      [5] Đã có phiếu: STP đã xử lý xong và đã có phiếu - DEC_STATUS_NAME: Tên trạng thái   - APPROVE_DATE: Ngày phê duyệt phiếu LLTP (trong trường hợp trạng thái là đã có phiếu). Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) - APPOINTMENT_NO: Số phiếu hẹn của STP (trong trường hợp lấy danh sách trạng thái của những hồ sơ không nộp qua một cửa) - RECEIVE_NO: Số phiếu tiếp nhận của một cửa (trong trường hợp lấy danh sách trạng thái của những hồ sơ nộp qua một cửa) - ISSUE_DATE: Ngày cấp phiếu. Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) |

**Phụ lục: Danh sách tham số**

| STT | Tên trường | Mô tả |
| --- | --- | --- |
| Thông tin tờ khai (declarationWSForm) | Thông tin tờ khai (declarationWSForm) | Thông tin tờ khai (declarationWSForm) |
| 1 | fullName | Họ tên người đăng ký cấp phiếu Bắt buộc |
| 2 | genderId | Giới tính của người đăng ký cấp phiếu [1] Nam; [0] Nữ Bắt buộc (Định dạng số) |
| 3 | birthDateStr | Ngày sinh của người đăng ký cấp phiếu Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) hoặc "mm/yyyy" hoặc "yyyy" Bắt buộc (đối với năm sinh) |
| 4 | birthPlace | Nơi sinh của người đăng ký cấp phiếu |
| 5 | nationalityId | Mã Quốc tịch của người đăng ký Danh mục Quốc tịch, tham khảo hàm lấy danh mục (Định dạng số) Bắt buộc |
| 6 | ethnicId | Mã Dân tộc của người đăng ký Danh mục Dân tộc, tham khảo hàm lấy danh mục (Định dạng số) |
| 7 | residence | Địa chỉ chi tiết nơi thường trú |
| 8 | reRegionId | Mã Địa phương của nơi thường trú Danh mục Hành chính, tham khảo hàm lấy danh mục (Định dạng số) |
| 9 | residenceTemporary | Địa chỉ chi tiết nơi tạm trú |
| 10 | rtRegionId | Mã  Địa phương của nơi tạm trú Danh mục Hành chính, tham khảo hàm lấy danh mục (Định dạng số) |
| 11 | idTypeId | ID Loại giấy tờ tùy thân [1]CMND; [0]Hộ chiếu;[2]Thẻ thường trú;[3]Thẻ căn cước công dân (Định dạng số) Bắt buộc |
| 12 | identifyNo | Số giấy tờ tùy thân Bắt buộc |
| 13 | idIssueDate | Ngày cấp giấy tờ tùy thân Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) |
| 14 | idIssuePlace | Nơi cấp giấy tờ tùy thân |
| 15 | dadName | Họ tên cha |
| 16 | dadDob | Ngày sinh của cha Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) hoặc "MM/YYYY" (tháng/năm) hoặc "YYYY" (năm) |
| 17 | momName | Họ tên mẹ |
| 18 | momDob | Ngày sinh của mẹ Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) hoặc "MM/YYYY" (tháng/năm) hoặc "YYYY" (năm) |
| 19 | partnerName | Họ tên vợ/chồng |
| 20 | partnerDob | Ngày sinh của vợ/chồng Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) hoặc "MM/YYYY" (tháng/năm) hoặc "YYYY" (năm) |
| 21 | phone | Số điện thoại (Định dạng số) Bắt buộc |
| 22 | email | Địa chỉ email Tuân thủ định dạng, ví dụ: a@abc.def |
| 23 | ministryJusticeId | Đơn vị nhận hồ sơ (Đơn vị nhận hồ sơ được xác định từ thông tin của đơn vị người sử dụng, mapping với mã của hệ thống QLLLTP) (Định dạng số) |
| 24 | declareDate | Ngày làm đơn Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) Bắt buộc |
| 25 | declareTypeId | Loại tờ khai [3846]Cá nhân; [3845]Ủy quyền; [3847]Cơ quan tổ chức; [3844]Cơ quan tiến hành tố tụng (Định dạng số) Bắt buộc |
| 26 | requestQty | Số lượng phiếu yêu cầu (Định dạng số) Bắt buộc |
| 27 | requestQtyAdd | Số lượng phiếu yêu cầu cấp thêm (Định dạng số) |
| 28 | objectRequestId | Đối tượng yêu cầu [72]Công dân Việt Nam; [71]Nước ngoài; [74]Cơ quan tiến hành tố tụng; [73]Cơ quan tổ chức (Định dạng số) Bắt buộc |
| 29 | agencyRequestId | Cơ quan đề nghị Mã danh mục Cơ quan (Định dạng số) Tham khảo hàm lấy danh mục |
| 30 | regionRequestId | Trụ sở Cơ quan đề nghị Mã danh mục Hành chính (Định dạng số) Tham khảo hàm lấy danh mục |
| 31 | formType | Loại phiếu yêu cầu (Định dạng số) [1] Loại phiếu số 1; [2]Loại phiếu số 2 Bắt buộc |
| 32 | isBanPosition | Nội dung yêu cầu cấm đảm nhiệm chức vụ (Định dạng số) [0] Không yêu cầu; [1]Có yêu cầu |
| 34 | delivery | Đăng ký dịch vụ trả kết quả (Định dạng số) [1]Có đăng ký, [0] Không đăng ký |
| 35 | deliveryAddress | Địa chỉ trả kết quả qua bưu chính |
| 36 | deliveryDistrict | Địa phương của địa chỉ trả kết quả qua bưu chính Mã danh mục hành chính (Định dạng số) Tham khảo hàm lấy danh mục |
| 37 | note | Ghi chú |
| 38 | purpose | Mục đích yêu cầu cấp phiếu |
| 39 | receiveNo | Mã số phiếu tiếp nhận do hệ thống 1 cửa gửi lên (duy nhất để tra cứu) |
| 40 | declarationPortalID | Mã số ID của hệ thống trực tuyến (mã hóa) TH công dân đăng ký trực tuyến và đến 1 cửa nộp hồ sơ thì phải gửi thông tin này. |
| 41 | otherName | Tên gọi khác |
| Thông tin ủy quyền (mandatorWSForm) | Thông tin ủy quyền (mandatorWSForm) | Thông tin ủy quyền (mandatorWSForm) |
| 1 | fullName | Họ tên của người được ủy quyền Bắt buộc |
| 2 | genderId | Giới tính [0] Nữ; [1] Nam (Định dạng số) |
| 3 | birthDateStr | Ngày sinh của người được khai sinh. Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) hoặc "MM/YYYY" (tháng/năm) hoặc "YYYY" (năm) |
| 4 | birthPlaceId | ID địa phương của nơi sinh Mã danh mục hành chính Tham khảo hàm lấy danh mục  (Định dạng số) |
| 5 | residence | Địa chỉ nơi thường trú |
| 6 | regionId | ID địa phương nơi thường trú Mã danh mục hành chính Tham khảo hàm lấy danh mục   (Định dạng số) |
| 7 | idTypeId | Loại giấy tờ tùy thân [1]CMND; [0]Hộ chiếu;[2]Thẻ thường trú;[3]Thẻ căn cước công dân (Định dạng số) |
| 8 | identifyNo | Số giấy tờ tùy thân |
| 9 | idIssueDate | Ngày cấp giấy tờ tùy thân Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) |
| 10 | idIssuePlace | Nơi cấp giấy tờ tùy thân |
| 11 | mandatorRelation | Quan hệ với người ủy quyền |
| 12 | mandatorDate | Ngày ký ủy quyền Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) |
| Thông tin cư trú (residenceWSForm) | Thông tin cư trú (residenceWSForm) | Thông tin cư trú (residenceWSForm) |
| 1 | fromDateStr | Từ ngày Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) hoặc "MM/YYYY" (tháng/năm) hoặc "YYYY" (năm) Bắt buộc |
| 2 | toDateStr | Đến ngày Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) hoặc "MM/YYYY" (tháng/năm) hoặc "YYYY" (năm) Bắt buộc |
| 3 | residencePlace | Địa chỉ chi tiết nơi thường trú/tạm trú Bắt buộc |
| 4 | jobName | Nghề nghiệp |
| 5 | workPlace | Nơi làm việc |

**Phụ lục: Danh sách tham số trả hồ sơ**

| STT | Tên trường | Mô tả |
| --- | --- | --- |
| Thông tin tờ khai (DeclarationTraHoSoForm) | Thông tin tờ khai (DeclarationTraHoSoForm) | Thông tin tờ khai (DeclarationTraHoSoForm) |
| 1 | fullName | Họ tên người đăng ký cấp phiếu |
| 2 | genderId | Giới tính của người đăng ký cấp phiếu [1] Nam; [0]  (Định dạng số) |
| 3 | birthDateStr | Ngày sinh của người đăng ký cấp phiếu Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm)  Bắt buộc (đối với năm sinh) |
| 4 | birthPlace | Mã Nơi sinh, tuân thủ định dạng “Mã phường/xã,  mã quận/huyện, mã tỉnh/thành phố” của hệ thống danh mục hành chính Tham khảo hàm lấy danh mục   (Định dạng số) |
| 5 | nationalityId | Mã Quốc tịch của người đăng ký Danh mục Quốc tịch, Tham khảo hàm lấy danh mục |
| 6 | ethnicId | Mã Dân tộc của người đăng ký Danh mục Dân tộc, Tham khảo hàm lấy danh mục  (Định dạng số) |
| 7 | residence | Địa chỉ chi tiết nơi thường trú |
| 8 | reRegionId | Mã Địa phương của nơi thường trú Danh mục Hành chính, Tham khảo hàm lấy danh mục  (Định dạng số) |
| 9 | residenceTemporary | Địa chỉ chi tiết nơi tạm trú |
| 10 | rtRegionId | Mã  Địa phương của nơi tạm trú Danh mục Hành chính, Tham khảo hàm lấy danh mục  (Định dạng số) |
| 11 | idTypeId | ID Loại giấy tờ tùy thân [1]CMND; [0]Hộ chiếu;[2]Thẻ thường trú;[3]Thẻ căn cước công dân (Định dạng số) |
| 12 | identifyNo | Số giấy tờ tùy thân |
| 13 | idIssueDate | Ngày cấp giấy tờ tùy thân Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) |
| 14 | idIssuePlace | Nơi cấp giấy tờ tùy thân |
| 15 | dadName | Họ tên cha |
| 16 | dadDob | Ngày sinh của cha Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) |
| 17 | momName | Họ tên mẹ |
| 18 | momDob | Ngày sinh của mẹ Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) |
| 19 | partnerName | Họ tên vợ/chồng |
| 20 | partnerDob | Ngày sinh của vợ/chồng Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) |
| 21 | phone | Số điện thoại |
| 22 | email | Địa chỉ email |
| 23 | ministryJusticeId | Đơn vị nhận hồ sơ (Đơn vị nhận hồ sơ được xác định từ thông tin của đơn vị người sử dụng, mapping với mã của hệ thống QLLLTP) (Định dạng số) |
| 24 | declareDate | Ngày làm đơn Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) |
| 25 | declareTypeId | Loại tờ khai [3846]Cá nhân; [3845]Ủy quyền; [3847]Cơ quan tổ chức; [3844]Cơ quan tiến hành tố tụng (Định dạng số) |
| 26 | requestQty | Số lượng phiếu yêu cầu (Định dạng số) |
| 27 | requestQtyAdd | Số lượng phiếu yêu cầu cấp thêm (Định dạng số) |
| 28 | objectRequestId | Đối tượng yêu cầu [72]Công dân Việt Nam; [71]Nước ngoài; [74]Cơ quan tiến hành tố tụng; [73]Cơ quan tổ chức (Định dạng số) |
| 29 | agencyRequestId | Cơ quan đề nghị Mã danh mục Cơ quan (Định dạng số) Tham khảo hàm lấy danh mục |
| 30 | regionRequestId | Trụ sơ Cơ quan đề nghị Mã danh mục Hành chính (Định dạng số) Tham khảo hàm lấy danh mục |
| 31 | formType | Loại phiếu yêu cầu (Định dạng số) [1] Loại phiếu số 1; [2]Loại phiếu số 2 |
| 32 | isBanPosition | Nội dung yêu cầu cấm đảm nhiệm chức vụ (Định dạng số) [0] Không yêu cầu; [1]Có yêu cầu |
| 34 | delivery | Đăng ký dịch vụ trả kết quả (Định dạng số) [1]Có đăng ký, [0] Không đăng ký |
| 35 | deliveryAddress | Địa chỉ trả kết quả qua bưu chính |
| 36 | deliveryDistrict | Địa phương của địa chỉ trả kết quả qua bưu chính Mã danh mục hành chính (Định dạng số) Tham khảo hàm lấy danh mục |
| 37 | declarationCode | Mã số trực tuyến Là mã hệ thống trực tuyến tự sinh theo cấu trúc (Định dạng số) [Số tăng dần gồm 5 chữ số] TH lấy hồ sơ trực tuyến |
| 38 | appointmentNo | Mã số phiếu hẹn do phần mềm LLTP sinh. TH lấy hồ sơ STP trực tiếp tiếp nhận. |
| 39 | giveProfileType | Đăng ký dịch vụ nộp hồ sơ tại nhà [1]Có đăng ký, [0]Không đăng ký TH lấy hồ sơ trực tuyến  (Định dạng số) |
| 40 | giveProfileAddress | Địa chỉ nộp hồ sơ qua bưu chính TH lấy hồ sơ trực tuyến |
| 41 | giveProfileDistrict | Địa phương của địa chỉ nộp hồ sơ qua bưu chính Mã danh mục hành chính Tham khảo hàm lấy danh mục  TH lấy hồ sơ trực tuyến  (Định dạng số) |
| 42 | declarationId | Thông tin mã ID định danh của hệ thống LLTP |
| 43 | declarationPortalID | Mã số ID của hệ thống trực tuyến (mã hóa. TH 1 cửa lấy hồ sơ trực tuyến và TH 1 cửa chỉ lấy hồ sơ STP trực tiếp tiếp nhận. |
| 44 | receiveDate | Ngày tiếp nhận hồ sơ Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) TH lấy hồ sơ STP trực tiếp tiếp nhận. |
| 45 | appointmentDate | Ngày hẹn trả kết quả Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) TH lấy hồ sơ STP trực tiếp tiếp nhận. |
| 46 | issueDate | Ngày cấp phiếu Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) TH lấy hồ sơ STP trực tiếp tiếp nhận. |
| 47 | decStatusId | Mã trạng thái hồ sơ  [3] STP đã tiếp nhận: hồ sơ đã được gửi từ hệ thống một cửa điện tử sang hệ thống nghiệp vụ [4] Đang xử lý: STP đang xử lý hồ sơ [5] Đã có phiếu: STP đã xử lý xong và đã có phiếu TH lấy hồ sơ STP trực tiếp tiếp nhận. |
| 48 | decStatusName | Tên trạng thái TH lấy hồ sơ STP trực tiếp tiếp nhận. |
| Thông tin ủy quyền (mandatorWSForm) | Thông tin ủy quyền (mandatorWSForm) | Thông tin ủy quyền (mandatorWSForm) |
| 1 | fullName | Họ tên của người được ủy quyền |
| 2 | genderId | Giới tính [0] Nữ; [1] Nam (Định dạng số) |
| 3 | birthDateStr | Ngày sinh của người được khai sinh. Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) |
| 4 | birthPlaceId | ID địa phương của nơi sinh Mã danh mục hành chính Tham khảo hàm lấy danh mục  (Định dạng số) |
| 5 | residence | Địa chỉ nơi thường trú |
| 6 | regionId | ID địa phương nơi thường trú Mã danh mục hành chính Tham khảo hàm lấy danh mục (Định dạng số) |
| 7 | idTypeId | Loại giấy tờ tùy thân [1]CMND; [0]Hộ chiếu;[2]Thẻ thường trú;[3]Thẻ căn cước công dân (Định dạng số) |
| 8 | identifyNo | Số giấy tờ tùy thân |
| 9 | idIssueDate | Ngày cấp giấy tờ tùy thân |
| 10 | idIssuePlace | Nơi cấp giấy tờ tùy thân |
| 11 | mandatorRelation | Quan hệ với người ủy quyền |
| 12 | mandatorDate | Ngày ký ủy quyền |
| Thông tin cư trú (residenceWSForm) | Thông tin cư trú (residenceWSForm) | Thông tin cư trú (residenceWSForm) |
| 1 | fromDateStr | Từ ngày Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) |
| 2 | toDateStr | Đến ngày Tuân thủ định dạng “DD/MM/YYYY” (ngày/tháng/năm) |
| 3 | residencePlace | Mã Nơi thường trú/Tạm trú Mã danh mục hành chính Tham khảo hàm lấy danh mục |
| 4 | jobName | Nghề nghiệp |
| 5 | workPlace | Nơi làm việc |

**Dịch vụ bảo hiểm xã hội**

**API tra cứu thông tin hộ gia đình từ mã số bảo hiểm xã hội ****–**** getTraCuuTtHgdByMaSoBhxh**

| URL kết nối tới dịch vụ getTraCuuTtHgdByMaSoBhxh | URL kết nối tới dịch vụ getTraCuuTtHgdByMaSoBhxh |
| --- | --- |
| Url | https://api.quangbinh.gov.vn/apiBHXH/getTraCuuTtHgdByMaSoBhxh |
| Request header | Request header |
| Authorization | “Bearer access_token” Ví dụ: “Bearer 49d61ed6-a9e8-3755-81cd-8395ee511c87” |
| Content-Type | application/json |
| Method | POST |
| Request body | Request body |
| body | {     maSoBhxh: Mã số BHXH cần tra cứu thông tin hộ gia đình } |

Response body:

| Tên trường | Kiểu | Mô tả |
| --- | --- | --- |
| hoTen | string | Họ tên |
| soSoCu | string | Số sổ BHXH cũ |
| ngaySinh | string | Ngày tháng năm sinh theo thứ tự Năm – tháng – ngày viết liền. vd: 19890812 |
| loaiNgaySinh | string | Nhận 3 giá trị: 0: đầy đủ ngày, tháng, năm sinh 1: chỉ có năm sinh 2: chỉ có năm, tháng sinh |
| gioiTinh | string | Nhận 3 giá trị: 1: Nam 2: Nữ 3: Khác |
| maTinhKs | string | Mã tỉnh theo quy định của tổng cục thống kê |
| maHuyenKs | string | Mã huyện theo quy định của tổng cục thống kê |
| maXaKs | string | Mã xã theo quy định của tổng cục thống kê |
| trangThai | string | Trạng thái |

**API lấy mã số bảo hiểm theo tiêu chí - getMaSoBhxhTheoTieuChi**

| URL kết nối tới dịch vụ getMaSoBhxhTheoTieuChi | URL kết nối tới dịch vụ getMaSoBhxhTheoTieuChi |
| --- | --- |
| Url | https://api.quangbinh.gov.vn/apiBHXH/getMaSoBhxhTheoTieuChi |
| Request header | Request header |
| Authorization | “Bearer access_token” Ví dụ: “Bearer 49d61ed6-a9e8-3755-81cd-8395ee511c87” |
| Content-Type | application/json |
| Method | POST |
| Request body | Request body |
| body | {     "hoTen": "",     "ngaySinh": "",     "loaiNgaySinh": "",     "gioiTinh": "",     "maTinhKs": "",     "maHuyenKs": "",     "maXaKs": "",     "isKs": "" } |

Giải thích tham số:

| Tên trường | Kiểu | Mô tả |
| --- | --- | --- |
| hoTen | string | Họ tên |
| ngaySinh | string | Ngày tháng năm sinh theo thứ tự Năm – tháng – ngày viết liền. vd: 19890812 |
| loaiNgaySinh | string | Nhận 3 giá trị: 0: đầy đủ ngày, tháng, năm sinh 1: chỉ có năm sinh 2: chỉ có năm, tháng sinh |
| gioiTinh | string | Nhận 3 giá trị: 1: Nam 2: Nữ 3: Khác |
| maTinhKs | string | Mã tỉnh theo quy định của tổng cục thống kê |
| maHuyenKs | string | Mã huyện theo quy định của tổng cục thống kê |
| maXaKs | string | Mã xã theo quy định của tổng cục thống kê |
| isKs | string | Nhận 2 giá trị: 1: tra cứu theo địa chỉ khai sinh 0: tra cứu theo địa chỉ hộ khẩu |

Response body:

| Tên trường | Kiểu | Mô tả |
| --- | --- | --- |
| maSoBhxh | string | Mã số BHXH |
| trangThai | string | Trạng thái |
| errorCode | string | Mã lỗi |

**API tra cứu thông tin hộ gia đình - getTraCuuThongTinHgd**

| URL kết nối tới dịch vụ getTraCuuThongTinHgd | URL kết nối tới dịch vụ getTraCuuThongTinHgd |
| --- | --- |
| Url | https://api.quangbinh.gov.vn/apiBHXH/getTraCuuThongTinHgd |
| Request header | Request header |
| Authorization | “Bearer access_token” Ví dụ: “Bearer 49d61ed6-a9e8-3755-81cd-8395ee511c87” |
| Content-Type | application/json |
| Method | POST |
| Request body | Request body |
| body | {     " maTinh": "",     "hoTen": "",     "ngaySinh": "",     "loaiNgaySinh": "",     "gioiTinh": "",     "soSo": "",     "maThe": "",     "isKs": "" } |

Giải thích tham số

| Tên trường | Kiểu | Mô tả |
| --- | --- | --- |
| maTinh | string | Mã tỉnh theo quy định của tổng cục thống kê |
| hoTen | string | Họ tên |
| ngaySinh | string | Ngày tháng năm sinh theo thứ tự Năm – tháng – ngày viết liền. vd: 19890812 |
| loaiNgaySinh | string | Nhận 3 giá trị: 0: đầy đủ ngày, tháng, năm sinh 1: chỉ có năm sinh 2: chỉ có năm, tháng sinh |
| gioiTinh | string | Nhận 3 giá trị: 1: Nam 2: Nữ 3: Khác |
| soSo | string | Số sổ BHXH |
| maThe | string | Mã thẻ BHXH |
| isKs | string | Nhận 2 giá trị: 1: tra cứu theo địa chỉ khai sinh 0: tra cứu theo địa chỉ hộ khẩu |

Response body:

| Tên trường | Kiểu | Mô tả |
| --- | --- | --- |
| maSo | string | Mã số |
| hoTen | string | Họ tên |
| ngaySinh | string | Ngày tháng năm sinh theo thứ tự Năm – tháng – ngày viết liền. vd: 19890812 |
| loaiNgaySinh | string | Nhận 3 giá trị: 0: đầy đủ ngày, tháng, năm sinh 1: chỉ có năm sinh 2: chỉ có năm, tháng sinh |
| gioiTinh | string | Nhận 3 giá trị: 1: Nam 2: Nữ 3: Khác |
| maHo | string | Mã hộ gia đình |
| diaChi | string | Địa chỉ |
| trangThai | string | Trạng thái |

**Dịch vụ đăng ký doanh nghiệp**

**API cung cấp thông tin chi tiết mới nhất của 01 doanh nghiệp**

| URL kết nối tới dịch vụ chiTietDoanhNghiep | URL kết nối tới dịch vụ chiTietDoanhNghiep |
| --- | --- |
| Url | https://api.quangbinh.gov.vn/apiCSDLDKDN/chiTietDoanhNghiep?msdn={msdn} |
| Request header | Request header |
| Authorization | “Bearer access_token” Ví dụ: “Bearer 49d61ed6-a9e8-3755-81cd-8395ee511c87” |
| Content-Type | application/json |
| Method | GET |
| Query string | Query string |
| msdn | Mã số doanh nghiệp |

Response body:

| Trường thông tin | Mô tả | Kiểu dữ liệu | Độ dài tối đa (ký tự) |
| --- | --- | --- | --- |
| MainInformation | Thông tin cơ bản |  |  |
| ENTERPRISE_ID | ID của doanh nghiệp | number | 10,0 |
| ENTERPRISE_GDT_CODE | Mã số doanh nghiệp (Mã số ĐKKD và MST đã gộp làm một) | string | 100 |
| IMP_BUSINESS_CODE | Số Giấy chứng nhận ĐKKD cũ | string | 100 |
| ENTERPRISE_TYPE_ID | Loại hình doanh nghiệp | string | 10 |
| ENTERPRISE_TYPE_NAME | Tên loại hình doanh nghiệp | string | 100 |
| NAME | Tên tiếng Việt | string | 1000 |
| SHORT_NAME | Tên viết tắt | string | 1000 |
| NAME_F | Tên bằng tiếng nước ngoài | string | 1000 |
| FOUNDING_DATE | Ngày thành lập (dd/MM/yyy) | date |  |
| LAST_AMEND_DATE | Ngày đăng ký thay đổi gần nhất (dd/MM/yyy) | date |  |
| NUMBER_CHANGES | Số lần đăng ký thay đổi | number | 10,0 |
| ENTERPRISE_STATUS | Tình trạng hoạt động của doanh nghiệp | string | 10 |
| LEGAL_NAMES | Tên của người đại diện pháp luật (trường hợp nhiều đại diện thì ghép xâu, cách nhau bởi dấu chấm phẩy) | string | 1000 |
| CAPITAL_AMOUNT | Vốn điều lệ | number | 21,3 |
| HOAdress | Địa chỉ trụ sở chính |  |  |
| CityID | Mã tỉnh/thành phố | number | 10,0 |
| CityName | Tên tỉnh/thành phố | string | 200 |
| DistrictID | Mã quận/huyện | number | 10,0 |
| DistrictName | Tên quận/huyện | string | 200 |
| WardID | Mã phường/xã | number | 10,0 |
| WardName | Tên phường/xã | string | 200 |
| StreetNumber | Địa chỉ số nhà, thôn ấp… | string | 200 |
| AddressFullText | Địa chỉ đầy đủ | string | 1000 |
| BusinessActivity | Ngành nghề kinh doanh |  |  |
| CODE | Mã ngành | string | 100 |
| NAME | Tên ngành | string | 1000 |
| IS_MAIN | Có phải ngành chính (Y/N) | string | 2 |
| Member | Khối danh sách thành viên góp vốn |  |  |
| MEMBER_NAME | Tên thành viên | string | 1000 |
| AMOUNT | Vốn góp (VNĐ) | number | 21,3 |
| RATIO_PERCENT | Tỷ lệ phần trăm vốn góp | number | 5,2 |
| COUNTRY | Quốc gia | string | 100 |
| DataCount | Số bản ghi | number |  |
| Status | Trạng thái thông điệp(1: thành công, 0: thất bại) | string |  |
| Message | Nội dung thông điệp (success hoặc mô tả lỗi) | string |  |

**API cung cấp danh sách các hồ sơ xử lý trong ngày**

| URL kết nối tới dịch vụ danhSachHoSoTrongNgay | URL kết nối tới dịch vụ danhSachHoSoTrongNgay |
| --- | --- |
| Url | https://api.quangbinh.gov.vn/apiCSDLDKDN/danhSachHoSoTrongNgay?from_ts={from_ts}&to_ts={to_ts}&offset={offset}&limit={limit} |
| Request header | Request header |
| Authorization | “Bearer access_token” Ví dụ: “Bearer 49d61ed6-a9e8-3755-81cd-8395ee511c87” |
| Content-Type | application/json |
| Method | GET |
| Query string | Query string |
| from_ts | Từ thời gian, định dạng (HH:mm), lưu ý HH định dạng 24 giờ |
| to_ts | Đến thời gian, định dạng (HH:mm), lưu ý HH định dạng 24 giờ |
| limit | Số bản ghi tối đa lấy về trong 1 phiên gọi dịch vụ |
| offset | Số dịch chuyển bản ghi đầu tiên |

Response body:

| Tên trường | Kiểu | Mô tả |
| --- | --- | --- |
| MainInformation |  | Thông tin cơ bản |
| IN_JOURNAL_NO | number | Mã số biên nhận của hồ sơ |
| DOCUMENT_TYPE | string | Loại hình đăng ký |
| ENTERPRISE_GDT_CODE | string | Mã số doanh nghiệp |
| NAME | string | Tên doanh nghiệp |
| SITE_ID | number | Mã cơ quan cấp đăng ký |
| PROCESS_STATUS | string | Tình trạng xử lý hồ sơ |
| PROCESSED_DATE | date | Ngày thay đổi tình trạng hồ sơ |
| DataCount | number | Số bản ghi |
| Status | string | Trạng thái thông điệp(1: thành công, 0: thất bại) |
| Message | string | Nội dung thông điệp (success hoặc mô tả lỗi) |

**API cung cấp danh sách các hồ sơ tiếp nhận trong khoảng thời gian**

| URL kết nối tới dịch vụ danhSachHoSo | URL kết nối tới dịch vụ danhSachHoSo |
| --- | --- |
| Url | https://api.quangbinh.gov.vn/apiCSDLDKDN/danhSachHoSo? from_date={from_date}&to_date={to_date}&offset={offset}&limit={limit} |
| Request header | Request header |
| Authorization | “Bearer access_token” Ví dụ: “Bearer 49d61ed6-a9e8-3755-81cd-8395ee511c87” |
| Content-Type | application/json |
| Method | GET |
| Query string | Query string |
| from_date | Ngày bắt đầu, định dạng (dd/MM/yyyy), lưu ý ngày tháng phải đủ 2 chữ số, năm đủ 4 chữ số |
| to_date | Ngày kết thúc, định dạng (dd/MM/yyyy), lưu ý ngày tháng phải đủ 2 chữ số, năm đủ 4 chữ số |
| limit | Số bản ghi tối đa lấy về trong 1 phiên gọi dịch vụ |
| offset | Số dịch chuyển bản ghi đầu tiên |

**Ràng buộc: khoảng thời gian giữa from_date và to_date tối đa 05 ngày**.

Response body:

| Tên trường | Kiểu | Mô tả |
| --- | --- | --- |
| MainInformation |  | Thông tin cơ bản |
| IN_JOURNAL_NO | number | Mã số biên nhận của hồ sơ |
| DOCUMENT_TYPE | string | Loại hồ sơ đăng ký (đăng ký mới, đăng ký thay đổi, tạm ngừng, giải thể, hoạt động trở lại) |
| ENTERPRISE_CODE | string | Mã số nội bộ |
| ENTERPRISE_GDT_CODE | string | Mã số doanh nghiệp |
| NAME | string | Tên doanh nghiệp |
| SITE_ID | number | Mã cơ quan cấp đăng ký |
| RECEIPT_DATE | date | Ngày tiếp nhận |
| PLAN_DATE | date | Ngày hẹn trả kết quả |
| PROCESS_STATUS | string | Tình trạng xử lý hồ sơ |
| DataCount | number | Số bản ghi |
| Status | string | Trạng thái thông điệp(1: thành công, 0: thất bại) |
| Message | string | Nội dung thông điệp (success hoặc mô tả lỗi) |

**API cung cấp thông tin chi tiết tiếp nhận của 01 hồ sơ đăng ký doanh nghiệp**

| URL kết nối tới dịch vụ tinhTrangHoSo | URL kết nối tới dịch vụ tinhTrangHoSo |
| --- | --- |
| Url | https://api.quangbinh.gov.vn/apiCSDLDKDN/tinhTrangHoSo? in_journal_no={in_journal_no} |
| Request header | Request header |
| Authorization | “Bearer access_token” Ví dụ: “Bearer 49d61ed6-a9e8-3755-81cd-8395ee511c87” |
| Content-Type | application/json |
| Method | GET |
| Query string | Query string |
| in_journal_no | Mã hồ sơ |

Response body:

| Tên trường | Kiểu | Mô tả |
| --- | --- | --- |
| MainInformation |  | Thông tin cơ bản |
| IN_JOURNAL_NO | number | Mã số biên nhận của hồ sơ |
| DOCUMENT_TYPE | string | Loại hồ sơ đăng ký (đăng ký mới, đăng ký thay đổi, tạm ngừng, giải thể, hoạt động trở lại) |
| ENTERPRISE_CODE | string | Mã số nội bộ |
| ENTERPRISE_GDT_CODE | string | Mã số doanh nghiệp |
| NAME | string | Tên doanh nghiệp |
| ENTERPRISE_TYPE_ID | string | Loại hình doanh nghiệp |
| SITE_ID | number | Mã cơ quan cấp đăng ký |
| RECEIPT_DATE | date | Ngày tiếp nhận |
| PLAN_DATE | date | Ngày hẹn trả kết quả |
| PROCESS_STATUS | string | Tình trạng xử lý hồ sơ |
| REGISTRATION_DATE | date | Ngày chấp thuận hồ sơ |
| SUPPLEMENT_DATE | date | Ngày phòng ĐKKD tiếp nhận hồ sơ bổ sung |
| SUBMISSION_TYPE | string | Kiểu tiếp nhận hồ sơ |
| CONTACT_FULL_NAME | string | Họ tên người nộp hồ sơ |
| CONTACT_ADDRESS | string | Địa chỉ người nộp |
| CONTACT_ID_NO | string | Số CMND/CCCD của người nộp |
| CONTACT_PHONE | string | Điện thoại người nộp |
| CONTACT_EMAIL | string | Email người nộp |
| DataCount | number | Số bản ghi |
| Status | string | Trạng thái thông điệp(1: thành công, 0: thất bại) |
| Message | string | Nội dung thông điệp (success hoặc mô tả lỗi) |
