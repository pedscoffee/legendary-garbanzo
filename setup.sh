#!/bin/bash

echo "======================================"
echo "Pediatric Charting Tool Setup"
echo "======================================"
echo

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3 first:"
    echo "  Mac: brew install python3"
    echo "  Linux: sudo apt install python3 python3-pip"
    exit 1
fi

python3 --version
echo

echo "Installing required packages..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install packages"
    exit 1
fi

# Check for tkinter on Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo
    echo "Checking for tkinter..."
    python3 -c "import tkinter" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "WARNING: tkinter not found"
        echo "Please install it:"
        echo "  Ubuntu/Debian: sudo apt-get install python3-tk"
        echo "  Fedora: sudo dnf install python3-tkinter"
    fi
    
    echo "Checking for clipboard support..."
    if ! command -v xclip &> /dev/null && ! command -v xsel &> /dev/null; then
        echo "WARNING: No clipboard tool found"
        echo "Please install one:"
        echo "  Ubuntu/Debian: sudo apt-get install xclip"
        echo "  Or: sudo apt-get install xsel"
    fi
fi

echo
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo
echo "To run the application:"
echo "  python3 peds_charting_tool.py"
echo
echo "Or make the script executable:"
echo "  chmod +x run_app.sh"
echo "  ./run_app.sh"
echo
