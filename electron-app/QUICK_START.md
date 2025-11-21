# Quick Start - EDEN Electron Dashboard

## Prerequisites

1. Node.js installed (v16+)
2. Cognitive Layer server running (`brain_server.py`)

## Setup (One Time)

```bash
cd electron-app
npm install
```

## Run

**Terminal 1 - Start Cognitive Layer:**
```bash
cd /home/vedantso/ShowcaseSoftware
POPULATE_TEST_DATA=true python3 brain_server.py
```

**Terminal 2 - Start Electron App:**
```bash
cd /home/vedantso/ShowcaseSoftware/electron-app
npm start
```

## Features

### 🕸️ Knowledge Graph Tab
- Real-time 3D visualization
- Shows all nodes and connections
- Color-coded by node type
- Interactive camera controls

### 💬 Interact Tab
- Chat with EDEN
- Uses cognitive layer memory
- Real-time responses

### 📋 Planning Tab
- Enter goals
- Generate action plans
- View reasoning and confidence
- See which memories were used

### ⚡ Personality Tab (GOD MODE)
- Adjust Big 5 personality traits
- Real-time graph updates
- Inject trauma/kindness events

## Troubleshooting

**App won't connect?**
- Make sure `brain_server.py` is running on port 8000
- Check connection status indicator in sidebar

**Graph not showing?**
- Click "Refresh" button
- Check browser console (DevTools: `npm run dev`)

**Planning times out?**
- Planning takes ~45 seconds with Ollama
- Make sure planning layer is running on port 8001


