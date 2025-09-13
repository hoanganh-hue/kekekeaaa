// test_bhxh_with_cccd.js - Test nhanh với CCCD thực để so sánh
const axios = require('axios');
const FormData = require('form-data');
const cheerio = require('cheerio');
const fs = require('fs');

const BHXH_API_URL = 'https://baohiemxahoi.gov.vn/UserControls/BHXH/BaoHiemYTe/HienThiHoGiaDinh/pListKoOTP.aspx';

// Test nhanh với CCCD (không cần giải CAPTCHA lại)
async function quickTestWithCCCD() {
    console.log('🔍 === TEST NHANH VỚI CCCD THỰC ===\n');
    
    // Đọc dữ liệu từ file kết quả trước đó
    let existingData;
    try {
        const excelData = JSON.parse(fs.readFileSync('check_result.js').toString().match(/JSON\.stringify\((.*?), null, 2\)/s)[1]);
        if (excelData && excelData.length > 0) {
            existingData = excelData[0];
            console.log('📋 Sử dụng dữ liệu từ kết quả trước:');
            console.log(`   - CCCD: ${existingData['Số CCCD'].replace("'", "")}`);
            console.log(`   - Tên: ${existingData['HỌ VÀ TÊN ']}`);
            console.log(`   - Địa chỉ: ${existingData['ĐỊA CHỈ']}`);
            console.log(`   - Mã BHXH đã có: ${existingData['MÃ BHXH'].replace("'", "")}\n`);
        }
    } catch (error) {
        console.log('⚠️ Không đọc được dữ liệu cũ, sử dụng dữ liệu mặc định\n');
        existingData = {
            'Số CCCD': "'031173005014",
            'HỌ VÀ TÊN ': 'Đỗ Thị Huyền',
            'ĐỊA CHỈ': 'thành phố Hải Phòng',
            'MÃ BHXH': "'3116073353"
        };
    }

    // Tạo request giả lập nhanh (không có CAPTCHA token)
    const testData = {
        matinh: '31TTT',
        tennhankhau: existingData['HỌ VÀ TÊN '],
        cmnd: existingData['Số CCCD'].replace("'", ""), // CCCD thực
        typetext: 'CoDau'
    };

    console.log('📋 Dữ liệu test với CCCD:');
    console.log(`   - CMND: ${testData.cmnd} (CCCD THỰC)`);
    console.log(`   - So sánh với mã BHXH: ${existingData['MÃ BHXH'].replace("'", "")}\n`);

    // Tạo form data
    const formData = new FormData();
    formData.append('matinh', testData.matinh);
    formData.append('tennhankhau', testData.tennhankhau);
    formData.append('cmnd', testData.cmnd);
    formData.append('tokenRecaptch', ''); // Rỗng để test
    formData.append('typetext', testData.typetext);

    try {
        console.log('🚀 Gửi request test (không có CAPTCHA token)...');
        const response = await axios.post(BHXH_API_URL, formData, {
            headers: {
                ...formData.getHeaders(),
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        });

        console.log(`📥 Response Status: ${response.status}`);
        console.log(`📏 Response Length: ${response.data.length} characters\n`);

        // Lưu response để so sánh
        fs.writeFileSync('response_with_cccd_no_captcha.html', response.data);
        console.log('💾 Response với CCCD (no CAPTCHA) đã lưu vào: response_with_cccd_no_captcha.html\n');

        // Phân tích nhanh
        const $ = cheerio.load(response.data);
        const bodyText = $('body').text().trim();
        
        console.log('📄 === NỘI DUNG RESPONSE ===');
        console.log(bodyText);
        console.log('\n');

        // So sánh với response mã BHXH
        const bhxhResponseLength = fs.readFileSync('response_with_ma_bhxh.html').length;
        console.log('📊 === SO SÁNH RESPONSE ===');
        console.log(`Response với CCCD (no CAPTCHA): ${response.data.length} chars`);
        console.log(`Response với mã BHXH: ${bhxhResponseLength} chars`);
        
        if (response.data.length === bhxhResponseLength) {
            console.log('✅ Độ dài response giống nhau - có thể cùng loại thông báo lỗi');
        } else {
            console.log('❓ Độ dài response khác nhau - có thể có sự khác biệt');
        }

    } catch (error) {
        console.error('💥 LỖI:', error.message);
        if (error.response) {
            console.error(`HTTP Status: ${error.response.status}`);
            
            // Kiểm tra response lỗi
            const $ = cheerio.load(error.response.data);
            const errorText = $('body').text().trim();
            console.log('\n📄 Nội dung response lỗi:');
            console.log(errorText);
        }
    }

    console.log('\n🏁 === HOÀN TẤT TEST SO SÁNH ===');
}

quickTestWithCCCD().catch(console.error);
