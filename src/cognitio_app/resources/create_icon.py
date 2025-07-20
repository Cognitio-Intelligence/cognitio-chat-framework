#!/usr/bin/env python3
"""
Create a simple placeholder icon for WebLLM Chat application.
This script creates a basic PNG icon that can be used during development.
"""

import os
from pathlib import Path

def create_simple_icon():
    """Create a simple icon using PIL if available, otherwise create an empty file."""
    icon_path = Path(__file__).parent / "LOGO-light-vertical.png"
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a 256x256 image with purple background
        size = (256, 256)
        img = Image.new('RGB', size, color='#8F4ACF')
        draw = ImageDraw.Draw(img)
        
        # Draw a simple robot icon
        # Head circle
        draw.ellipse([64, 64, 192, 192], fill='#ffffff', outline='#7C3AED', width=4)
        
        # Eyes
        draw.ellipse([88, 100, 112, 124], fill='#8F4ACF')
        draw.ellipse([144, 100, 168, 124], fill='#8F4ACF')
        
        # Mouth
        draw.arc([100, 140, 156, 170], start=0, end=180, fill='#8F4ACF', width=4)
        
        # Save the icon
        img.save(icon_path, 'PNG')
        print(f"✅ Created icon: {icon_path}")
        return True
        
    except ImportError:
        # PIL not available, create a simple text-based icon description
        try:
            with open(icon_path.with_suffix('.txt'), 'w') as f:
                f.write("WebLLM Chat Icon Placeholder\n")
                f.write("This is a placeholder for the application icon.\n")
                f.write("Replace with actual icon file in PNG, ICO, or ICNS format.\n")
            print(f"ℹ️  Created icon placeholder: {icon_path.with_suffix('.txt')}")
        except Exception as e:
            print(f"⚠️  Could not create icon placeholder: {e}")
        return False

if __name__ == '__main__':
    create_simple_icon()
