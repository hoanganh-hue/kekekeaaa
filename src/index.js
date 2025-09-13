// index.js
const XLSX = require('xlsx');
const fs = require('fs');
const fsPromises = require('fs').promises;
const path = require('path');
const axios = require('axios');
const FormData = require('form-data');
const cheerio = require('cheerio'); // Thêm cheerio

// Tích hợp module API chính thức BHXH
const EnhancedBHXHLookup = require('./enhanced_bhxh_lookup.js');

// --- Configuration ---
const EXCEL_INPUT_FILE_PATH = 'data-input.xlsx'; // Your Excel file name
const EXCEL_OUTPUT_FILE_PATH = 'data-output.xlsx'; // Output Excel file
const TINH_THANH_FILE_PATH = 'tinh-thanh.json'; // Your province/city JSON file
const KEY_CAPTCHA_FILE_PATH = 'key-capcha.txt'; // Path to your 2captcha clientKey file
const CAPTCHA_WEBSITE_URL = 'https://baohiemxahoi.gov.vn';
const CAPTCHA_WEBSITE_KEY = '6Lcey5QUAAAAADcB0m7xYLj8W8HHi8ur4JQrTCUY';
const BHXH_API_URL = 'https://baohiemxahoi.gov.vn/UserControls/BHXH/BaoHiemYTe/HienThiHoGiaDinh/pListKoOTP.aspx';
const LUONG_XULY_FILE_PATH = 'luong-xuly.txt'; // Path to the file specifying concurrent processing threads
// const DEFAULT_CAPTCHA_SOLVERS = 10; // Không cần nữa vì mỗi tác vụ tự giải CAPTCHA

// --- Helper Functions ---

/**
 * Reads the CAPTCHA client key from a file.
 * @param {string} filePath Path to the key file.
 * @returns {string|null} The client key or null on error.
 */
function readCaptchaKeyFromFile(filePath) {
    try {
        return fs.readFileSync(filePath, 'utf-8').trim();
    } catch (error) {
        console.error(`Lỗi: Không thể đọc file key CAPTCHA tại ${filePath}:`, error.message);
        return null;
    }
}

/**
 * Reads the number of concurrent processing threads from a file.
 * @param {string} filePath Path to the file.
 * @param {number} defaultValue Default value if file reading fails or content is invalid.
 * @returns {number} The number of threads.
 */
function readConcurrentProcessingLimit(filePath, defaultValue) {
    try {
        const content = fs.readFileSync(filePath, 'utf-8').trim();
        const value = parseInt(content, 10);
        return Number.isInteger(value) && value > 0 ? value : defaultValue;
    } catch (error) {
        console.warn(`Lỗi: Không thể đọc file số luồng xử lý tại ${filePath} (${error.message}). Sử dụng giá trị mặc định: ${defaultValue}`);
        return defaultValue;
    }
}

/**
 * Reads data from an Excel file.
 * @param {string} filePath Path to the Excel file.
 * @returns {object|null} An object with sheet names as keys and arrays of row objects as values, or null on error.
 */
function readExcelFile(filePath) {
    try {
        if (!fs.existsSync(filePath)) {
            console.error(`Lỗi: File không tồn tại tại đường dẫn: ${filePath}`);
            return null;
        }
        const workbook = XLSX.readFile(filePath);
        const allSheetsData = {};
        workbook.SheetNames.forEach(sheetName => {
            const worksheet = workbook.Sheets[sheetName];
            const jsonData = XLSX.utils.sheet_to_json(worksheet, { defval: "" });
            allSheetsData[sheetName] = jsonData;
        });
        return allSheetsData;
    } catch (error) {
        console.error("Đã xảy ra lỗi khi đọc file Excel:", error);
        return null;
    }
}

/**
 * Finds the province/city code from an address string.
 * @param {string} address The address string.
 * @param {Array<object>} provincesList List of province objects {code, name}.
 * @returns {{code: string, name: string}|null} An object with province code and name, or null if not found.
 */
function findProvinceCode(address, provincesList) {
    if (!address || typeof address !== 'string') {
        console.warn('Địa chỉ không hợp lệ hoặc bị thiếu.');
        return null;
    }
    const sortedProvinces = [...provincesList].sort((a, b) => b.name.length - a.name.length); // Sort by length to match longer names first
    for (const province of sortedProvinces) {
        if (address.includes(province.name)) {
            const addressParts = address.split(',').map(p => p.trim());
            if (addressParts.some(part => part === province.name) || address.endsWith(province.name)) { // Added check for address ending with province name
                console.log(`[INFO] Tỉnh/thành phố: "${province.name}" - ${province.code}`);
                return { code: province.code, name: province.name };
            }
        }
    }
    const parts = address.split(',').map(p => p.trim());
    if (parts.length > 0) {
        const lastPart = parts[parts.length - 1];
        const foundProvince = provincesList.find(p => p.name === lastPart);
        if (foundProvince) { // Fallback: check if the last part of the address is a province name
            console.log(`Tìm thấy tỉnh/thành phố (fallback) khớp: "${foundProvince.name}" với mã: ${foundProvince.code}`);
            return { code: foundProvince.code, name: foundProvince.name };
        }
    }
    console.warn(`Không tìm thấy mã tỉnh/thành phố cho địa chỉ: "${address}"`);
    return null;
}

/**
 * Solves reCAPTCHA using 2captcha API.
 * @param {string} clientKey Your 2captcha client key.
 * @param {string} websiteURL The URL of the website with reCAPTCHA.
 * @param {string} websiteKey The reCAPTCHA site key.
 * @param {string} logPrefix Prefix for log messages to distinguish concurrent calls.
 * @param {number} pollIntervalMs Interval for polling results (milliseconds).
 * @param {number} maxAttempts Maximum polling attempts.
 * @returns {Promise<string|null>} The reCAPTCHA token or null on failure/timeout.
 */
async function solveRecaptcha(clientKey, websiteURL, websiteKey, logPrefix = "", pollIntervalMs = 5000, maxAttempts = 24) {
    console.log(`${logPrefix}[INFO] Đang giải reCAPTCHA...`);
    let taskId;
    try {
        const createTaskResponse = await axios.post('https://api.2captcha.com/createTask', {
            clientKey: clientKey,
            task: { type: "RecaptchaV2TaskProxyless", websiteURL: websiteURL, websiteKey: websiteKey }
        });
        if (createTaskResponse.data.errorId !== 0) {
            console.error(`${logPrefix}Lỗi tạo task 2Captcha:`, createTaskResponse.data.errorCode || createTaskResponse.data.errorDescription);
            return null;
        }
        taskId = createTaskResponse.data.taskId;
        console.log(`${logPrefix}[INFO] Task reCAPTCHA đã được tạo với ID: ${taskId}`);
    } catch (error) {
        console.error(`${logPrefix}Lỗi khi tạo task 2Captcha:`, error.message);
        return null;
    }
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
        await new Promise(resolve => setTimeout(resolve, pollIntervalMs));
        try {
            // Thanh tiến trình có thể gây rối khi nhiều luồng cùng ghi ra console.
            // Cân nhắc hiển thị đơn giản hơn hoặc đảm bảo mỗi luồng ghi vào dòng riêng nếu cần thiết.
            // Hiện tại, để đơn giản, sẽ log tiến trình trên dòng mới mỗi lần.
            const progressPercent = Math.round(((attempt + 1) / maxAttempts) * 100);
            console.log(`${logPrefix}[CAPTCHA] Tiến trình giải: ${progressPercent}% (Lần thử ${attempt + 1}/${maxAttempts})`);

            const getResultResponse = await axios.post('https://api.2captcha.com/getTaskResult', { clientKey: clientKey, taskId: taskId });
            const { data } = getResultResponse;
            if (data.errorId !== 0) {
                console.error(`${logPrefix}Lỗi lấy kết quả 2Captcha:`, data.errorCode || data.errorDescription);
                if (data.errorCode === 'ERROR_CAPTCHA_UNSOLVABLE' || data.errorCode === 'ERROR_NO_SLOT_AVAILABLE') return null;
            }
            if (data.status === 'ready') {
                console.log(`${logPrefix}[INFO] Đã giải thành công CAPTCHA!`);
                return data.solution.gRecaptchaResponse;
            } else if (data.status === 'processing') {
                // Tiếp tục chờ
            } else {
                console.error(`${logPrefix}Trạng thái 2Captcha không xác định:`, data.status, data);
                return null;
            }
        } catch (error) {
            console.error('Lỗi khi lấy kết quả task 2Captcha:', error.message);
        }
    }
    // Xóa dòng progress bar nếu giải thất bại
    console.error(`${logPrefix}[CAPTCHA] Giải reCAPTCHA thất bại hoặc hết thời gian chờ.`);
    return null;
}

/**
 * Submits data to the BHXH API and parses the HTML response.
 * @param {string} matinh Province code.
 * @param {string} tennhankhau Full name.
 * @param {string} cmnd ID card number.
 * @param {string} tokenRecaptch reCAPTCHA token.
 * @returns {Promise<{maBHXH: string|null, ngaySinh: string|null}|null>} Extracted data or null on error.
 */
async function postToBhxhAndParse(matinh, tennhankhau, cmnd, tokenRecaptch) {
    const formData = new FormData();
    formData.append('matinh', matinh);
    formData.append('tennhankhau', tennhankhau);
    formData.append('cmnd', cmnd);
    formData.append('tokenRecaptch', tokenRecaptch);
    formData.append('typetext', 'CoDau');

    try {
        console.log(`[INFO] Đang gửi dữ liệu tới BHXH cho: ${tennhankhau}, CCCD: ${cmnd}, Mã tỉnh: ${matinh}`);
        const response = await axios.post(BHXH_API_URL, formData, {
            headers: {
                ...formData.getHeaders(),
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        });
        // console.log('Phản hồi từ API BHXH - Status:', response.status);f

        if (response.status === 200 && response.data) {
            console.log("[INFO] Gửi dữ liệu lên BHXH thành công! Đang phân tích HTML...");
            const html = response.data;
            const $ = cheerio.load(html);

            const resultsCountText = $('#kqtracuu').text(); // "Số kết quả(1)"
            const resultsCountMatch = resultsCountText.match(/\((\d+)\)/);
            const numberOfResults = resultsCountMatch ? parseInt(resultsCountMatch[1], 10) : 0;

            if (numberOfResults === 0) {
                console.log("  Không tìm thấy kết quả nào từ BHXH.");
                return { maBHXH: "không đăng ký BHXH", ngaySinh: "không đăng ký BHXH" };
            }
            
            // Lấy dữ liệu từ dòng đầu tiên trong bảng kết quả
            const firstRow = $('#contentChiTietHGD tr').first();
            if (firstRow.length) {
                const maBHXH = firstRow.find('td').eq(1).text().trim(); // Cột thứ 2
                const ngaySinh = firstRow.find('td').eq(4).text().trim(); // Cột thứ 5
                console.log(`[INFO] Trích xuất: Mã BHXH = ${maBHXH}, Ngày sinh = ${ngaySinh}`);
                return { maBHXH, ngaySinh };
            } else {
                console.warn("  Không tìm thấy bảng dữ liệu hoặc dòng dữ liệu trong phản hồi BHXH.");
                return { maBHXH: "Lỗi phân tích HTML", ngaySinh: "Lỗi phân tích HTML" };
            }
        } else {
            console.warn("Gửi dữ liệu lên BHXH có phản hồi không mong muốn hoặc không có dữ liệu:", response.status);
            return null;
        }
    } catch (error) {
        console.error('Lỗi khi gửi dữ liệu tới API BHXH hoặc phân tích HTML:');
        if (error.response) {
            console.error('Status:', error.response.status);
        } else if (error.request) {
            console.error('Yêu cầu đã được gửi nhưng không nhận được phản hồi:', error.request);
        } else {
            console.error('Lỗi:', error.message);
        }
        return null;
    }
}

/**
 * Writes data to an Excel file.
 * @param {Array<object>} dataToWrite Array of objects to write to Excel.
 * @param {string} outputPath Path for the output Excel file.
 * @param {number} maxRetries Số lần thử lại tối đa nếu file bị khóa.
 * @param {number} retryDelayMs Thời gian chờ giữa các lần thử lại (tính bằng mili giây).
 * @returns {Promise<boolean>} True nếu ghi thành công, false nếu thất bại sau tất cả các lần thử.
 */
async function writeToExcel(dataToWrite, outputPath, maxRetries = 3, retryDelayMs = 2000) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            // Tạo một workbook mới
            const newWorkbook = XLSX.utils.book_new();
            // Chuyển đổi mảng object thành worksheet
            const newWorksheet = XLSX.utils.json_to_sheet(dataToWrite);
            // Thêm worksheet vào workbook
            XLSX.utils.book_append_sheet(newWorkbook, newWorksheet, "KetQua"); // Tên sheet là "KetQua"

            // Ghi workbook ra file
            XLSX.writeFile(newWorkbook, outputPath);
            console.log(`[INFO] Dữ liệu đã được ghi thành công vào file: ${outputPath} (lần thử ${attempt})`);
            return true; // Ghi thành công
        } catch (error) {
            if (error.code === 'EBUSY' && attempt < maxRetries) {
                console.warn(`Lỗi khi ghi dữ liệu ra file Excel (${outputPath}): File đang bị khóa (EBUSY). Đang thử lại sau ${retryDelayMs / 1000} giây... (lần thử ${attempt}/${maxRetries})`);
                await new Promise(resolve => setTimeout(resolve, retryDelayMs));
            } else {
                console.error(`Lỗi khi ghi dữ liệu ra file Excel (${outputPath}) sau ${attempt} lần thử:`, error);
                return false; // Ghi thất bại
            }
        }
    }
    console.error(`Không thể ghi vào file ${outputPath} sau ${maxRetries} lần thử do file vẫn bị khóa.`);
    return false; // Ghi thất bại sau tất cả các lần thử
}

// --- TokenManager Class đã được loại bỏ ---

/**
 * Gọi API chính thức BHXH để mở rộng dữ liệu
 * @param {string} maBHXH - Mã BHXH từ phương pháp CAPTCHA cũ
 * @param {string} ngaySinh - Ngày sinh từ phương pháp CAPTCHA cũ 
 * @param {Object} originalData - Dữ liệu gốc (CCCD, tên, địa chỉ)
 * @param {string} logPrefix - Prefix cho log
 */
async function callOfficialBhxhApi(maBHXH, ngaySinh, originalData, logPrefix) {
    try {
        console.log(`${logPrefix}[API CHÍNH THỨC] Khởi tạo EnhancedBHXHLookup...`);
        
        // Tạm thời hardcode Bearer Token rỗng như yêu cầu
        const bearerToken = "";
        const enhancer = new EnhancedBHXHLookup(bearerToken);
        
        console.log(`${logPrefix}[API CHÍNH THỨC] Đang gọi getTraCuuThongTinHgd...`);
        
        // Chuẩn bị dữ liệu cho API getTraCuuThongTinHgd
        const searchData = {
            maTinh: extractProvinceCodeFromAddress(originalData.diaChi),
            hoTen: originalData.hoTen,
            ngaySinh: formatBirthDateForApi(ngaySinh),
            loaiNgaySinh: "0",
            gioiTinh: "1", // Mặc định Nam
            soSo: "",
            maThe: "",
            isKs: "0"
        };
        
        // Log đầy đủ request như yêu cầu
        console.log(`${logPrefix}[API CHÍNH THỨC] === CHI TIẾT REQUEST ===`);
        console.log(`${logPrefix}[API CHÍNH THỨC] Endpoint: https://api.quangbinh.gov.vn/apiBHXH/getTraCuuThongTinHgd`);
        console.log(`${logPrefix}[API CHÍNH THỨC] Headers:`, {
            'Authorization': `Bearer ${bearerToken}`,
            'Content-Type': 'application/json'
        });
        console.log(`${logPrefix}[API CHÍNH THỨC] Body:`, JSON.stringify(searchData, null, 2));
        console.log(`${logPrefix}[API CHÍNH THỨC] === KẾT THÚC REQUEST LOG ===`);
        
        // Gọi API (sẽ fail do Bearer Token rỗng nhưng ta sẽ log response/error)
        const result = await enhancer.getFullHouseholdInfo(searchData);
        
        // Log response
        if (result) {
            console.log(`${logPrefix}[API CHÍNH THỨC] === RESPONSE THÀNH CÔNG ===`);
            console.log(`${logPrefix}[API CHÍNH THỨC] Response:`, JSON.stringify(result, null, 2));
            if (result.maHo) {
                console.log(`${logPrefix}[API CHÍNH THỨC] 🎯 QUAN TRỌNG - MÃ HỘ GIA ĐÌNH: ${result.maHo}`);
            }
        } else {
            console.log(`${logPrefix}[API CHÍNH THỨC] === RESPONSE NULL (EXPECTED) ===`);
            console.log(`${logPrefix}[API CHÍNH THỨC] Lý do: Bearer Token rỗng - đây là hành vi mong đợi trong giai đoạn 1`);
        }
        
    } catch (error) {
        console.log(`${logPrefix}[API CHÍNH THỨC] === LỖI (EXPECTED) ===`);
        console.log(`${logPrefix}[API CHÍNH THỨC] Error Type:`, error.name);
        console.log(`${logPrefix}[API CHÍNH THỨC] Error Message:`, error.message);
        if (error.response) {
            console.log(`${logPrefix}[API CHÍNH THỨC] HTTP Status:`, error.response.status);
            console.log(`${logPrefix}[API CHÍNH THỨC] Response Data:`, error.response.data);
        }
        console.log(`${logPrefix}[API CHÍNH THỨC] Lý do lỗi: Bearer Token rỗng - đây là hành vi mong đợi trong giai đoạn 1`);
    }
}

/**
 * Trích xuất mã tỉnh từ địa chỉ
 */
function extractProvinceCodeFromAddress(address) {
    if (address.includes('Hải Phòng')) return '31';
    if (address.includes('Hà Nội')) return '01';
    if (address.includes('Hồ Chí Minh')) return '79';
    if (address.includes('Đà Nẵng')) return '48';
    // Mặc định về Hà Nội
    return '01';
}

/**
 * Format ngày sinh cho API
 */
function formatBirthDateForApi(birthString) {
    if (birthString.includes('**')) {
        const year = birthString.split('/').pop();
        return `${year}0101`; // Giả định ngày 1/1
    }
    return birthString;
}

// --- Main Logic ---
async function main() {
    const CAPTCHA_CLIENT_KEY = readCaptchaKeyFromFile(path.join(__dirname, KEY_CAPTCHA_FILE_PATH));
    if (!CAPTCHA_CLIENT_KEY) {
        console.error('Không tìm thấy hoặc không thể đọc CAPTCHA_CLIENT_KEY từ file. Vui lòng kiểm tra file key-capcha.txt.');
        process.exit(1); // Thoát chương trình nếu không có key
    }
    console.log('[INFO] Đã đọc CAPTCHA_CLIENT_KEY từ file.');

    const MAX_CONCURRENT_ROW_PROCESSING = readConcurrentProcessingLimit(
        path.join(__dirname, LUONG_XULY_FILE_PATH),
        10 // Giá trị mặc định nếu file không tồn tại hoặc nội dung không hợp lệ
    );
    console.log(`[INFO] Số luồng xử lý đồng thời tối đa được đặt là: ${MAX_CONCURRENT_ROW_PROCESSING}`);

    let tinhThanhData;
    try {
        const rawTinhThanh = await fsPromises.readFile(path.join(__dirname, TINH_THANH_FILE_PATH), 'utf-8');
        tinhThanhData = JSON.parse(rawTinhThanh);
        console.log('[INFO] Đã tải dữ liệu tỉnh thành.');
    } catch (error) {
        console.error(`Không thể đọc file ${TINH_THANH_FILE_PATH}:`, error);
        return;
    }

    const excelSheetsData = readExcelFile(path.join(__dirname, EXCEL_INPUT_FILE_PATH));
    if (!excelSheetsData) {
        console.error('Không thể đọc dữ liệu từ file Excel đầu vào. Kết thúc chương trình.');
        return;
    }

    const { default: pLimit } = await import('p-limit'); // Sử dụng dynamic import

    const allOutputData = []; // Mảng để lưu tất cả dữ liệu sẽ ghi ra file output
    const limit = pLimit(MAX_CONCURRENT_ROW_PROCESSING); // Giới hạn số tác vụ đồng thời
    const processingPromises = [];

    for (const sheetName in excelSheetsData) {
        console.log(`\n[INFO] --- Đang xử lý Sheet: "${sheetName}" ---`);
        const rows = excelSheetsData[sheetName];
        let rowCount = 0;

        for (const rowData of rows) { // Đổi tên biến để tránh nhầm lẫn với 'row' trong scope khác
            rowCount++;
            const currentRowNum = rowCount; // Capture current row number for logging inside promise
            const logPrefixForRow = `[Dòng ${currentRowNum} Sheet "${sheetName}"] `;

            const task = limit(async () => {
                console.log(`\n[INFO] Bắt đầu xử lý dòng ${currentRowNum} (Sheet: "${sheetName}")`);

                const soDienThoai = rowData['Số ĐIện Thoại'] ? String(rowData['Số ĐIện Thoại']).trim() : "";
                const soCCCD = rowData['Số CCCD'] ? String(rowData['Số CCCD']).trim() : "";
                const hoVaTen = rowData['HỌ VÀ TÊN '] ? String(rowData['HỌ VÀ TÊN ']).trim() : "";
                const diaChi = rowData['ĐỊA CHỈ'] ? String(rowData['ĐỊA CHỈ']).trim() : "";

                let maBHXH = "N/A";
                let ngaySinhBHXH = "N/A";
                let tenTinhThanhLog = "Không xác định";
                let maTinh = null;

                const provinceInfo = findProvinceCode(diaChi, tinhThanhData);
                if (provinceInfo) {
                    maTinh = provinceInfo.code;
                    tenTinhThanhLog = provinceInfo.name;
                }

                console.log(`${logPrefixForRow}Dữ liệu: [SĐT=${soDienThoai}] [CCCD=${soCCCD}] [Tên=${hoVaTen}] [Tỉnh/TP=${tenTinhThanhLog}]`);

                if (!soCCCD || !hoVaTen || !diaChi) {
                    console.warn(`${logPrefixForRow}Bỏ qua do thiếu CCCD, Họ Tên, hoặc Địa chỉ.`);
                } else if (!maTinh) {
                    console.warn(`${logPrefixForRow}Không tìm thấy mã tỉnh cho địa chỉ: "${diaChi}".`);
                    maBHXH = "Lỗi tìm mã tỉnh";
                    ngaySinhBHXH = "Lỗi tìm mã tỉnh";
                } else {
                    console.log(`${logPrefixForRow}Đang yêu cầu giải CAPTCHA cho ${hoVaTen}...`);
                    const tokenRecaptcha = await solveRecaptcha(
                        CAPTCHA_CLIENT_KEY,
                        CAPTCHA_WEBSITE_URL,
                        CAPTCHA_WEBSITE_KEY,
                        logPrefixForRow // Truyền prefix log vào hàm giải CAPTCHA
                    );

                    if (!tokenRecaptcha) {
                        console.error(`${logPrefixForRow}Không giải được reCAPTCHA cho ${hoVaTen}.`);
                        maBHXH = "Lỗi reCAPTCHA";
                        ngaySinhBHXH = "Lỗi reCAPTCHA";
                    } else {
                        console.log(`${logPrefixForRow}Đã giải CAPTCHA thành công cho ${hoVaTen}.`);
                        const bhxhResult = await postToBhxhAndParse(maTinh, hoVaTen, soCCCD, tokenRecaptcha);

                        if (bhxhResult) {
                            maBHXH = bhxhResult.maBHXH || "N/A";
                            ngaySinhBHXH = bhxhResult.ngaySinh || "N/A";
                            
                            // 🚀 GIAI ĐOẠN 1: Tích hợp API chính thức BHXH
                            console.log(`\n${logPrefixForRow}=== BẮT ĐẦU GIAI ĐOẠN 1: TÍCH HỢP API CHÍNH THỨC ===`);
                            await callOfficialBhxhApi(maBHXH, ngaySinhBHXH, {
                                cccd: soCCCD,
                                hoTen: hoVaTen,
                                diaChi: diaChi
                            }, logPrefixForRow);
                            console.log(`${logPrefixForRow}=== KẾT THÚC GIAI ĐOẠN 1 ===\n`);
                            
                        } else {
                            console.warn(`${logPrefixForRow}Lỗi khi gọi API BHXH cho ${hoVaTen}.`);
                            maBHXH = "Lỗi API BHXH";
                            ngaySinhBHXH = "Lỗi API BHXH";
                        }
                    }
                }

                allOutputData.push({
                    'Số ĐIện Thoại': "'" + soDienThoai,
                    'Số CCCD': "'" + soCCCD,
                    'HỌ VÀ TÊN ': hoVaTen,
                    'ĐỊA CHỈ': diaChi,
                    'NGÀY THÁNG NĂM SINH': ngaySinhBHXH,
                    'MÃ BHXH': "'" + maBHXH,
                });
                await writeToExcel(allOutputData, path.join(__dirname, EXCEL_OUTPUT_FILE_PATH)); // Ghi ngay lập tức
                console.log(`${logPrefixForRow}Hoàn thành xử lý. Kết quả: BHXH=${maBHXH}, Sinh=${ngaySinhBHXH}`);
            });
            processingPromises.push(task);
        }
    }
    
    await Promise.all(processingPromises);
    console.log('\n[INFO] --- Tất cả các dòng đã được đưa vào hàng đợi xử lý ---');
    console.log('[INFO] --- Đang chờ hoàn tất các tác vụ còn lại... ---');

    // (Optional) Wait for p-limit to clear its queue if there's a way,
    // or just wait for all promises pushed to processingPromises.
    // p-limit returns a promise from the task, so Promise.all(processingPromises) handles this.

    console.log('[INFO] --- Hoàn thành xử lý tất cả các dòng ---');

    // Không cần ghi lại toàn bộ dữ liệu ở cuối vì đã ghi theo từng dòng

    console.log('\n[INFO] --- Chương trình hoàn tất ---');
}

main().catch(error => {
    console.error("Đã xảy ra lỗi không mong muốn trong quá trình thực thi chính:", error);
});
