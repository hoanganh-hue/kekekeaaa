// Tạo file Excel test với dữ liệu thực tế
const XLSX = require('xlsx');

// Dữ liệu test từ người dùng
const testData = [
    {
        'Số ĐIện Thoại': '', // Không có số điện thoại
        'Số CCCD': '031173005014',
        'HỌ VÀ TÊN ': 'Đỗ Thị Huyền',
        'ĐỊA CHỈ': 'thành phố Hải Phòng'
    }
];

// Tạo workbook và worksheet
const workbook = XLSX.utils.book_new();
const worksheet = XLSX.utils.json_to_sheet(testData);

// Thêm worksheet vào workbook
XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1');

// Ghi file
XLSX.writeFile(workbook, 'data-input.xlsx');

console.log('Đã tạo file data-input.xlsx với dữ liệu test');
console.log('Dữ liệu:', testData[0]);
