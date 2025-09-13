const axios = require('axios');
const https = require('https');

// Tạo agent để bỏ qua SSL verification
const httpsAgent = new https.Agent({
  rejectUnauthorized: false
});

async function quickAPITest() {
  console.log('=== KIỂM TRA NHANH CÁC DOMAIN VSS ===\n');

  // Test domain chính trước
  const mainDomain = 'https://baohiemxahoi.gov.vn';
  
  try {
    console.log('🔍 Testing main domain:', mainDomain);
    const response = await axios({
      method: 'GET',
      url: mainDomain,
      timeout: 5000,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36'
      }
    });
    
    console.log('✅ Domain chính hoạt động bình thường');
    console.log(`Status: ${response.status}`);
    
    // Kiểm tra có API endpoints không
    const apiPaths = [
      '/api',
      '/mobile/api', 
      '/app/api',
      '/services/api',
      '/bhxh/api'
    ];
    
    console.log('\n🔍 Kiểm tra API paths trên domain chính:');
    for (let path of apiPaths) {
      try {
        const apiResponse = await axios({
          method: 'GET',
          url: mainDomain + path,
          timeout: 3000,
          headers: {
            'User-Agent': 'VssID-Mobile-App/1.0',
            'Accept': 'application/json'
          }
        });
        console.log(`✅ ${path} - Status: ${apiResponse.status}`);
        
        if (apiResponse.data) {
          console.log('   Data preview:', JSON.stringify(apiResponse.data).substring(0, 200));
        }
      } catch (error) {
        const status = error.response?.status || 'FAIL';
        console.log(`❌ ${path} - Status: ${status}`);
      }
    }
    
  } catch (error) {
    console.log('❌ Domain chính không truy cập được:', error.message);
  }

  // Kiểm tra Google API key
  console.log('\n=== KIỂM TRA GOOGLE API KEY ===');
  const googleApiKey = 'AIzaSyB77JtJ_MOdCOEhF9ZYk7p0Jrzq8mozM5g';
  
  try {
    // Test với Google Maps Geocoding API
    const googleResponse = await axios({
      method: 'GET',
      url: `https://maps.googleapis.com/maps/api/geocode/json?address=hanoi&key=${googleApiKey}`,
      timeout: 5000
    });
    
    console.log('✅ Google API Key hoạt động!');
    console.log(`Status: ${googleResponse.status}`);
    console.log('Response preview:', JSON.stringify(googleResponse.data).substring(0, 300));
    
  } catch (error) {
    console.log('❌ Google API Key không hoạt động:', error.message);
    if (error.response?.data) {
      console.log('Error details:', JSON.stringify(error.response.data));
    }
  }

  // Thử kiểm tra các domain khác với phương pháp khác
  console.log('\n=== KIỂM TRA CÁC DOMAIN NỘI BỘ ===');
  
  const internalDomains = [
    { name: 'VSS App Backend', url: 'http://vssapp.teca.vn:8088' },
    { name: 'VSS Internal IP', url: 'http://222.252.27.89:1111' },
    { name: 'VSS Bot Service', url: 'https://bot.vss.gov.vn' }
  ];
  
  for (let domain of internalDomains) {
    console.log(`🔍 Testing ${domain.name}: ${domain.url}`);
    
    try {
      // Thử kết nối nhanh với timeout ngắn
      const response = await axios({
        method: 'HEAD', // Chỉ lấy header thôi
        url: domain.url,
        timeout: 3000,
        httpsAgent: httpsAgent,
        headers: {
          'User-Agent': 'VssID-App'
        }
      });
      
      console.log(`   ✅ Có thể kết nối - Status: ${response.status}`);
      console.log(`   Server: ${response.headers.server || 'Unknown'}`);
      
    } catch (error) {
      if (error.code === 'ECONNREFUSED') {
        console.log('   ❌ Connection refused - Service không chạy');
      } else if (error.code === 'ETIMEOUT') {
        console.log('   ⏱️ Timeout - Có thể service chạy nhưng chậm');
      } else if (error.code === 'ENOTFOUND') {
        console.log('   ❌ Domain không tồn tại');
      } else {
        console.log(`   ❌ Lỗi: ${error.message}`);
      }
    }
  }
}

quickAPITest().catch(console.error);