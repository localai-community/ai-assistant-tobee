#!/bin/bash

# Installation script for LocalAI Community with fallback options

echo "🚀 Installing LocalAI Community dependencies..."

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: Not in a virtual environment. Consider creating one first."
    echo "   python -m venv venv"
    echo "   source venv/bin/activate  # On Unix/macOS"
    echo "   venv\\Scripts\\activate     # On Windows"
fi

# Function to install with fallback
install_with_fallback() {
    local package=$1
    local fallback=$2
    
    echo "📦 Installing $package..."
    if pip install "$package"; then
        echo "✅ Successfully installed $package"
    elif [[ -n "$fallback" ]]; then
        echo "⚠️  Failed to install $package, trying fallback: $fallback"
        if pip install "$fallback"; then
            echo "✅ Successfully installed fallback: $fallback"
        else
            echo "❌ Failed to install both $package and $fallback"
            return 1
        fi
    else
        echo "❌ Failed to install $package"
        return 1
    fi
}

# Install core dependencies first
echo "📦 Installing core dependencies..."
pip install -r backend/requirements.txt

# Try to install PyMuPDF with different approaches
echo "📄 Installing PDF processing libraries..."

# Method 1: Try the latest version
if ! pip install "pymupdf>=1.24.0"; then
    echo "⚠️  PyMuPDF installation failed, trying alternative methods..."
    
    # Method 2: Try with specific version
    if ! pip install "pymupdf==1.23.8"; then
        echo "⚠️  Specific version failed, trying without version constraint..."
        
        # Method 3: Try without version constraint
        if ! pip install pymupdf; then
            echo "⚠️  PyMuPDF installation failed, installing pdfplumber as alternative..."
            
            # Method 4: Install pdfplumber as alternative
            if pip install "pdfplumber>=0.9.0"; then
                echo "✅ Installed pdfplumber as PDF processing alternative"
            else
                echo "❌ Failed to install any PDF processing library"
            fi
        else
            echo "✅ Installed PyMuPDF without version constraint"
        fi
    else
        echo "✅ Installed PyMuPDF version 1.23.8"
    fi
else
    echo "✅ Installed PyMuPDF successfully"
fi

# Install MCP if not already installed
echo "🔧 Installing MCP..."
if ! pip install "mcp>=1.0.0"; then
    echo "⚠️  MCP installation failed, trying alternative..."
    pip install mcp
fi

# Install frontend dependencies
echo "🎨 Installing frontend dependencies..."
if [[ -f "frontend/requirements.txt" ]]; then
    pip install -r frontend/requirements.txt
fi

echo "✅ Installation complete!"
echo ""
echo "🔍 To verify installation, run:"
echo "   python test_mcp_integration.py"
echo ""
echo "🚀 To start the backend:"
echo "   cd backend && python -m uvicorn app.main:app --reload"
echo ""
echo "🎨 To start the frontend:"
echo "   cd frontend && streamlit run app.py" 