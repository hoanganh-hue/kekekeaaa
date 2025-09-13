// test_bhxh_with_ma_so.js - Test gửi API BHXH với mã BHXH thay vì CCCD
const axios = require('axios');
const FormData = require('form-data');
const cheerio = require('cheerio');
const fs = require('fs');

// Cấu hình từ mã nguồn ban đầu
const BHXH_API_URL = 'https://baohiemxahoi.gov.vn/UserControls/BHXH/BaoHiemYTe/HienThiHoGiaDinh/pListKoOTP.aspx';
const CAPTCHA_WEBSITE_URL = 'https://baohiemxahoi.gov.vn';
const CAPTCHA_WEBSITE_KEY = '6Lcey5QUAAAAADcB0m7xYLj8W8HHi8ur4JQrTCUY';

// Đọc key CAPTCHA
function readCaptchaKey() {
    try {
        return fs.readFileSync('key-capcha.txt', 'utf-8').trim();
    } catch (error) {
        console.error('Lỗi đọc file key CAPTCHA:', error.message);
        return null;
    }
}

// Giải CAPTCHA (copy từ mã nguồn gốc)
async function solveRecaptcha(clientKey, websiteURL, websiteKey) {
    console.log('[INFO] Đang giải reCAPTCHA...');
    let taskId;
    try {
        const createTaskResponse = await axios.post('https://api.2captcha.com/createTask', {
            clientKey: clientKey,
            task: { type: "RecaptchaV2TaskProxyless", websiteURL: websiteURL, websiteKey: websiteKey }
        });
        if (createTaskResponse.data.errorId !== 0) {
            console.error('Lỗi tạo task 2Captcha:', createTaskResponse.data.errorCode || createTaskResponse.data.errorDescription);
            return null;
        }
        taskId = createTaskResponse.data.taskId;
        console.log(`[INFO] Task reCAPTCHA đã được tạo với ID: ${taskId}`);
    } catch (error) {
        console.error('Lỗi khi tạo task 2Captcha:', error.message);
        return null;
    }

    // Chờ giải CAPTCHA
    for (let attempt = 0; attempt < 24; attempt++) {
        await new Promise(resolve => setTimeout(resolve, 5000));
        try {
            const progressPercent = Math.round(((attempt + 1) / 24) * 100);
            console.log(`[CAPTCHA] Tiến trình giải: ${progressPercent}% (Lần thử ${attempt + 1}/24)`);

            const getResultResponse = await axios.post('https://api.2captcha.com/getTaskResult', { clientKey: clientKey, taskId: taskId });
            const { data } = getResultResponse;
            if (data.errorId !== 0) {
                console.error('Lỗi lấy kết quả 2Captcha:', data.errorCode || data.errorDescription);
                if (data.errorCode === 'ERROR_CAPTCHA_UNSOLVABLE' || data.errorCode === 'ERROR_NO_SLOT_AVAILABLE') return null;
            }
            if (data.status === 'ready') {
                console.log('[INFO] Đã giải thành công CAPTCHA!');
                return data.solution.gRecaptchaResponse;
            }
        } catch (error) {
            console.error('Lỗi khi lấy kết quả task 2Captcha:', error.message);
        }
    }
    console.error('[CAPTCHA] Giải reCAPTCHA thất bại hoặc hết thời gian chờ.');
    return null;
}

// Test gửi API với mã BHXH thay vì CCCD
async function testBhxhWithMaSo() {
    console.log('🔍 === KIỂM TRA API BHXH VỚI MÃ SỐ BHXH ===\n');
    
    // Đọc key CAPTCHA
    const captchaKey = readCaptchaKey();
    if (!captchaKey) {
        console.error('Không có CAPTCHA key. Kết thúc test.');
        return;
    }

    // Dữ liệu test
    const testData = {
        matinh: '31TTT', // Hải Phòng
        tennhankhau: 'Đỗ Thị Huyền',
        cmnd: '3116073353', // 🔥 ĐÂY LÀ THAY ĐỔI: Dùng mã BHXH thay vì CCCD
        typetext: 'CoDau'
    };

    console.log('📋 Dữ liệu test:');
    console.log(`   - Mã tỉnh: ${testData.matinh}`);
    console.log(`   - Tên: ${testData.tennhankhau}`);
    console.log(`   - CMND (THỰC TẾ LÀ MÃ BHXH): ${testData.cmnd} 🔥`);
    console.log(`   - Type text: ${testData.typetext}\n`);

    // Giải CAPTCHA
    console.log('⏳ Bước 1: Giải CAPTCHA...');
    const tokenRecaptcha = await solveRecaptcha(captchaKey, CAPTCHA_WEBSITE_URL, CAPTCHA_WEBSITE_KEY);
    
    if (!tokenRecaptcha) {
        console.error('❌ Không giải được CAPTCHA. Kết thúc test.');
        return;
    }

    console.log('✅ CAPTCHA đã được giải thành công!\n');

    // Gửi request tới API BHXH
    console.log('🚀 Bước 2: Gửi request tới API BHXH...');
    
    const formData = new FormData();
    formData.append('matinh', testData.matinh);
    formData.append('tennhankhau', testData.tennhankhau);
    formData.append('cmnd', testData.cmnd); // Mã BHXH thay vì CCCD
    formData.append('tokenRecaptch', tokenRecaptcha);
    formData.append('typetext', testData.typetext);

    try {
        console.log(`📤 Đang gửi POST request tới: ${BHXH_API_URL}`);
        console.log('📋 Form data:');
        console.log(`   - matinh: ${testData.matinh}`);
        console.log(`   - tennhankhau: ${testData.tennhankhau}`);
        console.log(`   - cmnd: ${testData.cmnd} (MÃ BHXH)`);
        console.log(`   - typetext: ${testData.typetext}`);
        console.log(`   - tokenRecaptch: ${tokenRecaptcha.substring(0, 50)}...\n`);

        const response = await axios.post(BHXH_API_URL, formData, {
            headers: {
                ...formData.getHeaders(),
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        });

        console.log(`📥 Response Status: ${response.status}`);
        console.log(`📏 Response Length: ${response.data.length} characters\n`);

        if (response.status === 200 && response.data) {
            console.log('✅ Đã nhận được response thành công! Đang phân tích...\n');
            
            // Lưu raw HTML để debug
            fs.writeFileSync('response_with_ma_bhxh.html', response.data);
            console.log('💾 Raw HTML đã được lưu vào: response_with_ma_bhxh.html\n');

            // Phân tích HTML
            const $ = cheerio.load(response.data);
            
            // Kiểm tra số kết quả
            const resultsCountText = $('#kqtracuu').text();
            console.log(`🔢 Text kết quả: "${resultsCountText}"`);
            
            const resultsCountMatch = resultsCountText.match(/\((\d+)\)/);
            const numberOfResults = resultsCountMatch ? parseInt(resultsCountMatch[1], 10) : 0;
            console.log(`🎯 Số kết quả tìm được: ${numberOfResults}\n`);

            if (numberOfResults === 0) {
                console.log('❌ Không tìm thấy kết quả nào.');
                console.log('💡 Có thể máy chủ không chấp nhận mã BHXH trong trường CMND\n');
                
                // Tìm thông báo lỗi nếu có
                const errorMessages = [];
                $('*').each(function() {
                    const text = $(this).text().trim();
                    if (text.includes('lỗi') || text.includes('Lỗi') || text.includes('không') || text.includes('Không')) {
                        if (text.length < 200 && text.length > 10) {
                            errorMessages.push(text);
                        }
                    }
                });
                
                if (errorMessages.length > 0) {
                    console.log('⚠️ Các thông báo có thể liên quan:');
                    errorMessages.forEach((msg, index) => {
                        console.log(`   ${index + 1}. ${msg}`);
                    });
                }
            } else {
                console.log('🎉 Tìm được kết quả! Đang trích xuất các trường dữ liệu...\n');
                
                // Trích xuất tất cả các dòng trong bảng kết quả
                const rows = $('#contentChiTietHGD tr');
                console.log(`📊 Số dòng trong bảng: ${rows.length}\n`);
                
                if (rows.length > 0) {
                    console.log('🗂️ === PHÂN TÍCH CẤU TRÚC BẢNG ===');
                    
                    rows.each(function(index) {
                        const cells = $(this).find('td, th');
                        if (cells.length > 0) {
                            console.log(`📋 Dòng ${index + 1}:`);
                            cells.each(function(cellIndex) {
                                const cellText = $(this).text().trim();
                                console.log(`   Cột ${cellIndex + 1}: "${cellText}"`);
                            });
                            console.log('');
                        }
                    });
                }
                
                // Tìm tất cả các thẻ có id hoặc class đặc biệt
                console.log('🏷️ === CÁC ELEMENTS CÓ ID/CLASS ĐẶC BIỆT ===');
                $('*[id], *[class]').each(function() {
                    const id = $(this).attr('id');
                    const className = $(this).attr('class');
                    const text = $(this).text().trim();
                    
                    if (text.length > 0 && text.length < 200) {
                        if (id) console.log(`🆔 ID "${id}": ${text}`);
                        if (className && !id) console.log(`🎨 Class "${className}": ${text}`);
                    }
                });
            }

        } else {
            console.log('❌ Response không hợp lệ hoặc không có dữ liệu');
            console.log(`Status: ${response.status}`);
        }

    } catch (error) {
        console.error('💥 LỖI KHI GỬI REQUEST:');
        console.error(`Error Type: ${error.name}`);
        console.error(`Error Message: ${error.message}`);
        
        if (error.response) {
            console.error(`HTTP Status: ${error.response.status}`);
            console.error(`Status Text: ${error.response.statusText}`);
            console.error(`Response Data Length: ${error.response.data ? error.response.data.length : 'N/A'}`);
            
            if (error.response.data) {
                fs.writeFileSync('error_response_with_ma_bhxh.html', error.response.data);
                console.error('💾 Error response HTML đã được lưu vào: error_response_with_ma_bhxh.html');
            }
        }
    }

    console.log('\n🏁 === HOÀN TẤT TEST ===');
}

// Chạy test
if (require.main === module) {
    testBhxhWithMaSo().catch(console.error);
}

module.exports = testBhxhWithMaSo;
