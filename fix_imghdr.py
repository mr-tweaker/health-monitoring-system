#!/usr/bin/env python3
"""
Fix for missing imghdr module in Python 3.13
This creates a mock imghdr module that Streamlit can use
"""

import sys
import types

def create_mock_imghdr():
    """Create a mock imghdr module"""
    imghdr = types.ModuleType('imghdr')
    
    # Mock the what function that Streamlit uses
    def mock_what(file, h=None):
        """Mock function that returns None (no image type detected)"""
        return None
    
    imghdr.what = mock_what
    
    # Add other common functions that might be expected
    imghdr.test_jpeg = lambda h, f: None
    imghdr.test_png = lambda h, f: None
    imghdr.test_gif = lambda h, f: None
    imghdr.test_bmp = lambda h, f: None
    
    return imghdr

# Create and install the mock module
if 'imghdr' not in sys.modules:
    mock_imghdr = create_mock_imghdr()
    sys.modules['imghdr'] = mock_imghdr
    print("✅ Mock imghdr module created and installed")

if __name__ == "__main__":
    print("imghdr fix applied successfully")
