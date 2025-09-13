const axios = require('axios');
const https = require('https');

// Tạo agent để bỏ qua SSL verification cho một số domain
const httpsAgent = new https.Agent({
  rejectUnauthorized: false
});

async function testAPIEndpoints() {
  console.log('=== KIỂM TRA CÁC API ENDPOINTS TỪ ỨNG DỤNG VSS ===\n');

  const endpoints = [
    {
      name: 'BHXH Official Portal',
      url: 'https://baohiemxahoi.gov.vn/tin-tuc-app/Pages/default.aspx',
      method: 'GET'
    },
    {
      name: 'VSS App Backend',
      url: 'http://vssapp.teca.vn:8088/',
      method: 'GET'
    },
    {
      name: 'VSS Bot Service',
      url: 'https://bot.vss.gov.vn/',
      method: 'GET'
    },
    {
      name: 'VSS Internal Service',
      url: 'http://222.252.27.89:1111/',
      method: 'GET'
    },
    {
      name: 'User Avatar Endpoint',
      url: 'http://vssapp.teca.vn:8088/user/avata?id=50a012380e72b6337a72f51a7c9136a9',
      method: 'GET'
    },
    {
      name: 'VSS Bot Root',
      url: 'https://bot.vss.gov.vn/user/avata?id=50a012380e72b6337a72f51a7c9136a9',
      method: 'GET'
    }
  ];

  const googleApiKey = 'AIzaSyB77JtJ_MOdCOEhF9ZYk7p0Jrzq8mozM5g';

  for (let endpoint of endpoints) {
    console.log(`🔍 Testing: ${endpoint.name}`);
    console.log(`📍 URL: ${endpoint.url}\n`);
    
    try {
      const config = {
        method: endpoint.method,
        url: endpoint.url,
        timeout: 10000,
        httpsAgent: httpsAgent,
        headers: {
          'User-Agent': 'VssID-Mobile-App/1.0 (Android)',
          'Accept': 'application/json, text/plain, */*',
          'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
          'Connection': 'keep-alive'
        }
      };

      // Thêm Google API key vào header nếu cần
      if (endpoint.url.includes('google') || endpoint.url.includes('api')) {
        config.headers['Authorization'] = `Bearer ${googleApiKey}`;
        config.headers['X-API-Key'] = googleApiKey;
      }

      const response = await axios(config);
      
      console.log('✅ Kết nối thành công!');
      console.log(`📊 Status: ${response.status} ${response.statusText}`);
      console.log('📋 Headers:');
      Object.keys(response.headers).forEach(key => {
        console.log(`   ${key}: ${response.headers[key]}`);
      });
      
      let responseData = response.data;
      if (typeof responseData === 'string') {
        console.log(`📄 Content Type: ${response.headers['content-type']}`);
        console.log('📝 Response Preview (first 500 chars):');
        console.log(responseData.substring(0, 500) + (responseData.length > 500 ? '...' : ''));
        
        // Kiểm tra nếu response chứa thông tin nhạy cảm
        if (responseData.includes('token') || 
            responseData.includes('api_key') || 
            responseData.includes('secret') ||
            responseData.includes('password') ||
            responseData.includes('auth') ||
            responseData.toLowerCase().includes('bhxh') ||
            responseData.toLowerCase().includes('cccd') ||
            responseData.toLowerCase().includes('cmnd')) {
          console.log('🔴 PHÁT HIỆN THÔNG TIN NHẠY CẢM!');
        }
      } else {
        console.log('📊 JSON Response:');
        console.log(JSON.stringify(responseData, null, 2));
      }
      
    } catch (error) {
      console.log('❌ Lỗi kết nối:');
      console.log(`   Status: ${error.response?.status || 'N/A'}`);
      console.log(`   Message: ${error.message}`);
      
      if (error.response && error.response.data) {
        console.log('📄 Error Response:');
        console.log(error.response.data);
      }
    }
    
    console.log('\n' + '='.repeat(80) + '\n');
  }
}

// Test thêm các endpoint phổ biến
async function testCommonAPIEndpoints() {
  console.log('=== KIỂM TRA CÁC ENDPOINT PHỔ BIẾN ===\n');
  
  const commonEndpoints = [
    '/api/user/info',
    '/api/auth/login',
    '/api/bhxh/lookup',
    '/api/citizen/info',
    '/user/profile',
    '/auth/token',
    '/api/v1/user',
    '/mobile/api/user'
  ];
  
  const baseUrls = [
    'http://vssapp.teca.vn:8088',
    'https://bot.vss.gov.vn',
    'http://222.252.27.89:1111'
  ];
  
  for (let baseUrl of baseUrls) {
    console.log(`🏢 Testing base: ${baseUrl}`);
    
    for (let endpoint of commonEndpoints) {
      const fullUrl = `${baseUrl}${endpoint}`;
      console.log(`   🔗 ${endpoint}`);
      
      try {
        const response = await axios({
          method: 'GET',
          url: fullUrl,
          timeout: 5000,
          httpsAgent: httpsAgent,
          headers: {
            'User-Agent': 'VssID-Mobile-App/1.0',
            'Accept': 'application/json'
          }
        });
        
        console.log(`      ✅ ${response.status} - ${response.data ? 'Has Data' : 'No Data'}`);
        
      } catch (error) {
        const status = error.response?.status || 'TIMEOUT';
        console.log(`      ❌ ${status}`);
      }
    }
    console.log();
  }
}

// Chạy tất cả tests
async function main() {
  await testAPIEndpoints();
  await testCommonAPIEndpoints();
  
  console.log('🎯 HOÀN THÀNH KIỂM TRA TẤT CẢ ENDPOINTS!');
}

main().catch(console.error);