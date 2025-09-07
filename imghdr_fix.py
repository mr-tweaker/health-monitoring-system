#!/usr/bin/env python3
"""
Python 3.13 Compatibility Fix for Streamlit
This module provides a replacement for the removed imghdr module
"""

import sys
import types
import os

def create_imghdr_module():
    """Create a mock imghdr module that provides the functions Streamlit needs"""
    
    # Create the module
    imghdr = types.ModuleType('imghdr')
    
    # Mock functions that Streamlit uses
    def mock_what(file, h=None):
        """Mock function that returns None (no image type detected)"""
        return None
    
    def mock_test_jpeg(h, f):
        """Mock JPEG test function"""
        return None
    
    def mock_test_png(h, f):
        """Mock PNG test function"""
        return None
    
    def mock_test_gif(h, f):
        """Mock GIF test function"""
        return None
    
    def mock_test_bmp(h, f):
        """Mock BMP test function"""
        return None
    
    def mock_test_tiff(h, f):
        """Mock TIFF test function"""
        return None
    
    def mock_test_webp(h, f):
        """Mock WebP test function"""
        return None
    
    # Add all the functions to the module
    imghdr.what = mock_what
    imghdr.test_jpeg = mock_test_jpeg
    imghdr.test_png = mock_test_png
    imghdr.test_gif = mock_test_gif
    imghdr.test_bmp = mock_test_bmp
    imghdr.test_tiff = mock_test_tiff
    imghdr.test_webp = mock_test_webp
    
    # Add any other attributes that might be expected
    imghdr.__version__ = "1.0.0"
    imghdr.__file__ = __file__
    
    return imghdr

def install_imghdr_fix():
    """Install the imghdr fix into sys.modules"""
    if 'imghdr' not in sys.modules:
        mock_imghdr = create_imghdr_module()
        sys.modules['imghdr'] = mock_imghdr
        print("✅ imghdr compatibility fix installed")
        return True
    return False

def create_imghdr_package():
    """Create a proper imghdr package directory structure"""
    import site
    
    # Get user site-packages directory
    user_site = site.getusersitepackages()
    imghdr_dir = os.path.join(user_site, 'imghdr')
    
    # Create the directory
    os.makedirs(imghdr_dir, exist_ok=True)
    
    # Create __init__.py
    init_file = os.path.join(imghdr_dir, '__init__.py')
    with open(init_file, 'w') as f:
        f.write('''"""
imghdr module for Python 3.13 compatibility
This is a mock implementation for Streamlit compatibility
"""

def what(file, h=None):
    """Mock function that returns None (no image type detected)"""
    return None

def test_jpeg(h, f):
    """Mock JPEG test function"""
    return None

def test_png(h, f):
    """Mock PNG test function"""
    return None

def test_gif(h, f):
    """Mock GIF test function"""
    return None

def test_bmp(h, f):
    """Mock BMP test function"""
    return None

def test_tiff(h, f):
    """Mock TIFF test function"""
    return None

def test_webp(h, f):
    """Mock WebP test function"""
    return None

__version__ = "1.0.0"
''')
    
    print(f"✅ Created imghdr package at: {imghdr_dir}")
    return imghdr_dir

if __name__ == "__main__":
    print("🔧 Installing Python 3.13 compatibility fixes...")
    
    # Method 1: Runtime fix
    install_imghdr_fix()
    
    # Method 2: Create package
    create_imghdr_package()
    
    print("✅ All compatibility fixes installed!")
    print("You can now run Streamlit with: python streamlit_runner.py")
