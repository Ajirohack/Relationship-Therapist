#!/bin/bash

# Script to copy MirrorCore components to the React app

# Set paths
SOURCE_DIR="../frontend/components"
DEST_DIR="./src/components/mirrorcore"
API_SOURCE="../frontend/utils/api.js"
API_DEST="./src/utils"

# Create destination directories if they don't exist
mkdir -p "$DEST_DIR"
mkdir -p "$API_DEST"

# Copy component files
echo "Copying MirrorCore components..."
cp "$SOURCE_DIR/MirrorCoreApp.jsx" "$DEST_DIR/"
cp "$SOURCE_DIR/MirrorCoreChatBot.jsx" "$DEST_DIR/"
cp "$SOURCE_DIR/SessionDashboard.jsx" "$DEST_DIR/"

# Copy API utilities
echo "Copying API utilities..."
cp "$API_SOURCE" "$API_DEST/"

# Create index.js for easy imports
echo "Creating index.js for MirrorCore components..."
cat > "$DEST_DIR/index.js" << EOL
import MirrorCoreApp from './MirrorCoreApp';
import MirrorCoreChatBot from './MirrorCoreChatBot';
import SessionDashboard from './SessionDashboard';

export {
  MirrorCoreApp,
  MirrorCoreChatBot,
  SessionDashboard
};
EOL

echo "Done! MirrorCore components have been copied to the React app."