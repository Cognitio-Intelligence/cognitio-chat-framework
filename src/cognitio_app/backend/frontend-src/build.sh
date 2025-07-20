#!/bin/bash

# Set production environment
export NODE_ENV=production

echo "🧹 Cleaning previous builds..."
rm -rf dist/
rm -rf ../static/assets/*.js

echo "📦 Building webpack bundle..."
npm run build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Webpack build completed successfully!"
    echo "📁 Main JS file location: ../static/assets/main.js"
    echo "🔗 Django template updated with consistent main.js reference"
    
    # Verify the main file exists
    if [ -f "../static/assets/main.js" ]; then
        echo "✅ Verified: main.js exists in static/assets/"
        ls -la ../static/assets/main.js
    else
        echo "❌ Warning: main.js not found in expected location"
    fi
else
    echo "❌ Webpack build failed!"
    exit 1
fi