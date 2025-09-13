// Đọc và hiển thị kết quả từ file Excel
const XLSX = require('xlsx');

// Đọc file kết quả
const workbook = XLSX.readFile('data-output.xlsx');
const sheetName = workbook.SheetNames[0];
const worksheet = workbook.Sheets[sheetName];
const data = XLSX.utils.sheet_to_json(worksheet);

console.log('=== KẾT QUẢ TRA CỨU BHXH ===');
console.log(JSON.stringify(data, null, 2));
