#!/bin/bash
# Podemos Installation Script
# Automates the setup of Podemos, including whisper.cpp and Python dependencies.

set -e

echo "🚀 Podemos Installation Script"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
  echo -e "${BLUE}ℹ️ $1${NC}";
}

log_success() {
  echo -e "${GREEN}✅ $1${NC}";
}

log_warning() {
  echo -e "${YELLOW}⚠️ $1${NC}";
}

log_error() {
  echo -e "${RED}❌ $1${NC}";
}

# Check for command existence
check_cmd() {
  if ! command -v "$1" &> /dev/null;
  then
    log_error "$1 could not be found. Please install it and try again."
    exit 1
  fi
}

log_info "Checking prerequisites..."
check_cmd "ffmpeg"
check_cmd "git"
check_cmd "python3"
log_success "All prerequisites found."

# Navigate to the podclean directory
# Assuming this script is run from the Podemos root directory
cd podclean

log_info "Cloning and building whisper.cpp..."
if [ ! -d "whisper.cpp" ]; then
  git clone https://github.com/ggerganov/whisper.cpp
else
  log_warning "whisper.cpp directory already exists. Skipping clone."
fi

cd whisper.cpp
log_info "Building whisper.cpp with Core ML support..."
make -j$(sysctl -n hw.ncpu) WHISPER_COREML=1
log_success "whisper.cpp built successfully."

log_info "Downloading whisper.cpp models..."
bash ./models/download-ggml-model.sh small.en
bash ./models/download-ggml-model.sh medium
log_success "whisper.cpp models downloaded."

cd .. # Go back to podclean directory

log_info "Installing Python dependencies..."
pip install -r requirements.txt
log_success "Python dependencies installed."

log_info "Initializing database..."
PYTHONPATH=./ python3 src/main.py --init-db
log_success "Database initialized."

echo ""
echo "🎉 Podemos Installation Complete!"
echo "=================================="
echo ""
log_success "You can now start the Podemos server:"
echo -e "  ${GREEN}PYTHONPATH=./ python3 src/main.py --serve &${NC}"
echo ""
log_info "Access the web dashboard at: http://localhost:8080/"
log_info "Access the podcast feed at: http://<YOUR_MAC_IP_ADDRESS>:8080/feed.xml"
log_warning "Remember to replace <YOUR_MAC_IP_ADDRESS> with your Mac's actual local IP address for phone access."
