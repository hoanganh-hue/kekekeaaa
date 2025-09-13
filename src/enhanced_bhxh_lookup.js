// enhanced_bhxh_lookup.js - MỞ RỘNG THU THẬP DỮ LIỆU BHXH
const axios = require('axios');

class EnhancedBHXHLookup {
    constructor(bearerToken) {
        this.bearerToken = bearerToken; // Token API NGSP chính thức
        this.baseURL = 'https://api.quangbinh.gov.vn';
    }

    /**
     * API 1: Thu thập thông tin hộ gia đình từ mã BHXH
     * @param {string} maSoBhxh - Mã số BHXH (từ ứng dụng hiện tại)
     * @returns {Promise<Object>} Thông tin hộ gia đình
     */
    async getHouseholdInfoByBHXH(maSoBhxh) {
        try {
            console.log(`[API1] Đang tra cứu thông tin hộ gia đình cho BHXH: ${maSoBhxh}`);
            
            const response = await axios.post(
                `${this.baseURL}/apiBHXH/getTraCuuTtHgdByMaSoBhxh`,
                { maSoBhxh: maSoBhxh },
                {
                    headers: {
                        'Authorization': `Bearer ${this.bearerToken}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            const data = response.data;
            console.log(`[API1] Kết quả:`, {
                hoTen: data.hoTen,
                soSoCu: data.soSoCu,
                ngaySinh: data.ngaySinh,
                gioiTinh: this.formatGender(data.gioiTinh),
                diaDiem: `${data.maTinhKs}/${data.maHuyenKs}/${data.maXaKs}`,
                trangThai: data.trangThai
            });

            return data;
        } catch (error) {
            console.error(`[API1] Lỗi tra cứu hộ gia đình:`, error.message);
            return null;
        }
    }

    /**
     * API 2: Lấy mã BHXH theo tiêu chí (phương pháp thay thế)
     * @param {Object} criteria - Tiêu chí tìm kiếm
     * @returns {Promise<string>} Mã số BHXH
     */
    async getBHXHByCriteria(criteria) {
        try {
            console.log(`[API2] Đang tìm mã BHXH theo tiêu chí:`, criteria);
            
            const response = await axios.post(
                `${this.baseURL}/apiBHXH/getMaSoBhxhTheoTieuChi`,
                {
                    hoTen: criteria.hoTen,
                    ngaySinh: criteria.ngaySinh,
                    loaiNgaySinh: criteria.loaiNgaySinh || "0",
                    gioiTinh: criteria.gioiTinh,
                    maTinhKs: criteria.maTinhKs,
                    maHuyenKs: criteria.maHuyenKs || "",
                    maXaKs: criteria.maXaKs || "",
                    isKs: criteria.isKs || "0" // 0: hộ khẩu, 1: khai sinh
                },
                {
                    headers: {
                        'Authorization': `Bearer ${this.bearerToken}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            const data = response.data;
            console.log(`[API2] Tìm được mã BHXH:`, data.maSoBhxh);
            
            return data.maSoBhxh;
        } catch (error) {
            console.error(`[API2] Lỗi tìm mã BHXH:`, error.message);
            return null;
        }
    }

    /**
     * API 3: Thu thập thông tin hộ gia đình đầy đủ (bao gồm MÃ HỘ GIA ĐÌNH)
     * @param {Object} searchData - Dữ liệu tìm kiếm
     * @returns {Promise<Object>} Thông tin hộ gia đình đầy đủ
     */
    async getFullHouseholdInfo(searchData) {
        try {
            console.log(`[API3] Đang tra cứu thông tin hộ gia đình đầy đủ:`, searchData.hoTen);
            
            const response = await axios.post(
                `${this.baseURL}/apiBHXH/getTraCuuThongTinHgd`,
                {
                    maTinh: searchData.maTinh,
                    hoTen: searchData.hoTen,
                    ngaySinh: searchData.ngaySinh,
                    loaiNgaySinh: searchData.loaiNgaySinh || "0",
                    gioiTinh: searchData.gioiTinh,
                    soSo: searchData.soSo || "",
                    maThe: searchData.maThe || "",
                    isKs: searchData.isKs || "0"
                },
                {
                    headers: {
                        'Authorization': `Bearer ${this.bearerToken}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            const data = response.data;
            console.log(`[API3] 🎯 QUAN TRỌNG - MÃ HỘ GIA ĐÌNH:`, data.maHo);
            console.log(`[API3] Kết quả đầy đủ:`, {
                maSo: data.maSo,
                hoTen: data.hoTen,
                ngaySinh: data.ngaySinh,
                gioiTinh: this.formatGender(data.gioiTinh),
                maHoGiaDinh: data.maHo, // 🔥 QUAN TRỌNG!
                diaChi: data.diaChi,
                trangThai: data.trangThai
            });

            return data;
        } catch (error) {
            console.error(`[API3] Lỗi tra cứu thông tin hộ gia đình:`, error.message);
            return null;
        }
    }

    /**
     * QUY TRÌNH TÍCH HỢP VỚI ỨNG DỤNG HIỆN TẠI
     * @param {Object} currentResult - Kết quả từ ứng dụng hiện tại (mã BHXH + ngày sinh)
     * @param {Object} originalData - Dữ liệu gốc (CCCD, tên, địa chỉ)
     * @returns {Promise<Object>} Dữ liệu mở rộng
     */
    async enhanceCurrentResult(currentResult, originalData) {
        console.log('\n🚀 === BẮTĐẦU QUY TRÌNH MỞ RỘNG DỮ LIỆU ===');
        
        const enhancedData = {
            // Dữ liệu gốc từ ứng dụng hiện tại
            original: {
                cccd: originalData.cccd,
                hoTen: originalData.hoTen,
                diaChi: originalData.diaChi,
                maBHXH: currentResult.maBHXH,
                ngaySinh: currentResult.ngaySinh
            },
            // Dữ liệu mở rộng
            enhanced: {}
        };

        // BƯỚC 1: Lấy thông tin hộ gia đình từ mã BHXH
        const householdInfo = await this.getHouseholdInfoByBHXH(currentResult.maBHXH);
        if (householdInfo) {
            enhancedData.enhanced.phase1 = {
                soSoBHXHCu: householdInfo.soSoCu,
                gioiTinh: this.formatGender(householdInfo.gioiTinh),
                maTinhKaiSinh: householdInfo.maTinhKs,
                maHuyenKaiSinh: householdInfo.maHuyenKs,
                maXaKaiSinh: householdInfo.maXaKs,
                trangThai: householdInfo.trangThai
            };
        }

        // BƯỚC 2: Lấy thông tin hộ gia đình đầy đủ (bao gồm mã hộ)
        const fullHouseholdInfo = await this.getFullHouseholdInfo({
            maTinh: this.extractProvinceCode(originalData.diaChi),
            hoTen: originalData.hoTen,
            ngaySinh: this.formatBirthDate(currentResult.ngaySinh),
            gioiTinh: householdInfo?.gioiTinh || "1"
        });

        if (fullHouseholdInfo) {
            enhancedData.enhanced.phase2 = {
                maHoGiaDinh: fullHouseholdInfo.maHo, // 🔥 QUAN TRỌNG NHẤT!
                diaChiDayDu: fullHouseholdInfo.diaChi,
                trangThaiHo: fullHouseholdInfo.trangThai
            };
        }

        // BƯỚC 3: Tiềm năng tìm thành viên gia đình (dựa trên mã hộ)
        if (enhancedData.enhanced.phase2?.maHoGiaDinh) {
            enhancedData.enhanced.phase3 = {
                note: "Với mã hộ gia đình, có thể tìm kiếm các thành viên khác trong gia đình",
                maHoGiaDinh: enhancedData.enhanced.phase2.maHoGiaDinh,
                potentialQueries: [
                    "Tìm kiếm BHXH của các thành viên cùng mã hộ",
                    "Tra cứu thông tin gia đình mở rộng",
                    "Lấy danh sách đầy đủ thành viên"
                ]
            };
        }

        console.log('\n✅ === HOÀN THÀNH QUY TRÌNH MỞ RỘNG ===');
        return enhancedData;
    }

    // Helper methods
    formatGender(genderCode) {
        const genders = { "1": "Nam", "2": "Nữ", "3": "Khác" };
        return genders[genderCode] || "Không xác định";
    }

    formatBirthDate(birthString) {
        // Chuyển từ **/**/1973 thành 19730101 (hoặc format phù hợp)
        if (birthString.includes('**')) {
            const year = birthString.split('/').pop();
            return `${year}0101`; // Giả định ngày 1/1
        }
        return birthString;
    }

    extractProvinceCode(address) {
        // Tìm mã tỉnh từ địa chỉ (cần mapping với dữ liệu tỉnh thành)
        // Tạm thời return mã Hải Phòng làm ví dụ
        if (address.includes('Hải Phòng')) return '31';
        return '01'; // Default Hà Nội
    }
}

// VÍ DỤ SỬ DỤNG
async function demonstrateEnhancement() {
    console.log('🔧 === DEMO: MỞ RỘNG DỮ LIỆU BHXH ===\n');

    // Giả sử có Bearer Token hợp lệ (cần đăng ký từ NGSP)
    const bearerToken = "YOUR_NGSP_BEARER_TOKEN_HERE";
    const enhancer = new EnhancedBHXHLookup(bearerToken);

    // Dữ liệu từ ứng dụng hiện tại
    const currentResult = {
        maBHXH: "3116073353",
        ngaySinh: "**/**/1973"
    };

    const originalData = {
        cccd: "031173005014",
        hoTen: "Đỗ Thị Huyền", 
        diaChi: "thành phố Hải Phòng"
    };

    try {
        const enhancedResult = await enhancer.enhanceCurrentResult(currentResult, originalData);
        
        console.log('\n📊 === KẾT QUẢ CUỐI CÙNG ===');
        console.log(JSON.stringify(enhancedResult, null, 2));

    } catch (error) {
        console.error('❌ Lỗi trong quá trình demo:', error.message);
        console.log('\n💡 LƯU Ý: Demo này cần Bearer Token hợp lệ từ hệ thống NGSP');
    }
}

// Export module để sử dụng trong ứng dụng chính
module.exports = EnhancedBHXHLookup;

// Chạy demo nếu file được gọi trực tiếp
if (require.main === module) {
    demonstrateEnhancement();
}
