#!/bin/bash
# MirrorCore Relationship Therapist System - Install Demo Dependencies
# Created: June 4, 2025

echo "🧠 MirrorCore Relationship Therapist - Demo Dependencies Installer"
echo "=================================================================="

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check for Python 3.7+
if ! command_exists python3; then
  echo "❌ Python 3 is required but not installed."
  echo "Please install Python 3.7 or higher and try again."
  exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]); then
  echo "❌ Python 3.7+ is required. Found Python $PYTHON_VERSION"
  echo "Please upgrade Python and try again."
  exit 1
fi

echo "✅ Found Python $PYTHON_VERSION"

# Check for pip
if ! command_exists pip3; then
  echo "❌ pip3 is required but not installed."
  echo "Please install pip for Python 3 and try again."
  exit 1
fi

echo "✅ Found pip3"

# Install required packages
echo "📦 Installing required Python packages..."

# Create a temporary requirements file
cat > temp_demo_requirements.txt << EOF
websockets>=10.0
colorama>=0.4.4
requests>=2.25.1
fastapi>=0.95.0
uvicorn>=0.22.0
python-dotenv>=1.0.0
pydantic>=2.0.0
EOF

# Install requirements
pip3 install -r temp_demo_requirements.txt

# Check installation status
if [ $? -eq 0 ]; then
  echo "✅ Successfully installed required packages."
else
  echo "❌ Failed to install some packages. Please check the error messages above."
  rm temp_demo_requirements.txt
  exit 1
fi

# Remove temporary requirements file
rm temp_demo_requirements.txt

# Make demo scripts executable
echo "🔧 Making demo scripts executable..."
chmod +x demo_script.sh
chmod +x test_websocket.py
chmod +x test_api_interactive.py

# Check if main_simple.py exists
if [ -f "main_simple.py" ]; then
  echo "✅ Found main_simple.py server script."
else
  echo "⚠️ main_simple.py not found. The server script may be missing or have a different name."
fi

echo ""
echo "🚀 Installation complete! You can now run the demo scripts:"
echo ""
echo "  1. Start the server:           python3 main_simple.py"
echo "  2. Run API tests:              ./demo_script.sh"
echo "  3. Run WebSocket test:         ./test_websocket.py"
echo "  4. Run interactive API tester: ./test_api_interactive.py"
echo ""
echo "📚 See DEMO_README.md for more information and usage examples."
echo "=================================================================="
