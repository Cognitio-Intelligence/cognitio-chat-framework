const fs = require('fs');
const path = require('path');

// Define paths
const distDir = path.join(__dirname, 'dist');
const templatePath = path.join(__dirname, '../templates/index.html');
const staticAssetsDir = path.join(__dirname, '../../static/assets');

console.log('🧹 Starting post-build cleanup and file organization...');

// Ensure dist directory exists
if (!fs.existsSync(distDir)) {
  console.error('❌ Dist directory not found. Build may have failed.');
  process.exit(1);
}

// Ensure templates directory exists
const templatesDir = path.dirname(templatePath);
if (!fs.existsSync(templatesDir)) {
  fs.mkdirSync(templatesDir, { recursive: true });
  console.log('📁 Created templates directory');
}

// Get all JS files from dist directory
const allFiles = fs.readdirSync(distDir);
const jsFiles = allFiles.filter(file => file.endsWith('.js'));

console.log('📁 Found files in dist/:', allFiles);
console.log('📄 JS files:', jsFiles);

// Ensure we have main.js
const mainJsFile = jsFiles.find(file => file === 'main.js');
if (!mainJsFile) {
  console.error('❌ main.js not found in build output');
  process.exit(1);
}

// Filter out any unwanted chunk files (keep only main.js for consistency)
const validJsFiles = jsFiles.filter(file => {
  const filePath = path.join(distDir, file);
  const stats = fs.statSync(filePath);
  
  // Keep main.js and any file larger than 1KB (to avoid empty chunks)
  return file === 'main.js' || stats.size > 1024;
});

console.log('✅ Valid JS files (after filtering):', validJsFiles);

// Create static/assets directory if it doesn't exist
if (!fs.existsSync(staticAssetsDir)) {
  fs.mkdirSync(staticAssetsDir, { recursive: true });
  console.log('📁 Created static/assets directory');
}

// Clean existing JS files in static/assets to avoid duplicates
const existingAssets = fs.existsSync(staticAssetsDir) ? fs.readdirSync(staticAssetsDir) : [];
existingAssets.forEach(file => {
  if (file.endsWith('.js')) {
    const filePath = path.join(staticAssetsDir, file);
    fs.unlinkSync(filePath);
    console.log(`🗑️  Removed old JS file: ${file}`);
  }
});

// Copy only valid JS files to static/assets
validJsFiles.forEach(file => {
  const srcPath = path.join(distDir, file);
  const destPath = path.join(staticAssetsDir, file);
  fs.copyFileSync(srcPath, destPath);
  console.log(`📄 Copied ${file} to static/assets/`);
});

// Create or update Django template
const templateContent = `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Cognitio Chat Framework</title>
    <meta name="description" content="Privacy-first Cognitio Chat Framework" />
    
    <!-- Preload Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    
    <!-- Base URL for the React app -->
    <base href="/">
    
    <!-- Environment variables for React -->
    <script>
        // Global configuration for frontend
        window.APP_CONFIG = {
            API_BASE_URL: "{{ BACKEND_API_URL|default:'http://127.0.0.1:3927/api/v1' }}",
            DEBUG: {{ DEBUG|yesno:"true,false" }},
            VERSION: "1.0.0"
        };
    </script>
  </head>
  <body>
    <div id="root">
        <!-- Loading screen while React app loads -->
        <div style="display: flex; justify-content: center; align-items: center; height: 100vh; font-family: Inter, sans-serif;">
            <div style="text-align: center;">
                <div style="width: 40px; height: 40px; border: 3px solid #f3f3f3; border-top: 3px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px;"></div>
                <p style="color: #666; font-size: 16px;">Loading Cognitio Chat Framework...</p>
            </div>
        </div>
    </div>
    
    <!-- CSS for loading spinner -->
    <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
    
    <!-- Load React app -->
    <script src="/static/assets/main.js"></script>
  </body>
</html>`;

// Write template
fs.writeFileSync(templatePath, templateContent);

console.log('✅ Post-build complete:');
console.log(`📄 Created/updated Django template: ${templatePath}`);
console.log(`📁 Files in static/assets/: ${validJsFiles.length} JS files`);
console.log(`🎯 Single entry point: /static/assets/main.js`);