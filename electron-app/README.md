# EDEN Cognitive Dashboard - Electron App

Modern desktop application for the EDEN Cognitive Layer with beautiful UI and real-time visualization.

## Features

- **Knowledge Graph Tab**: 3D visualization of the cognitive layer's knowledge graph
- **Interact Tab**: Chat interface to interact with EDEN
- **Planning Tab**: Generate and view action plans from the planning layer
- **Personality Tab**: Real-time personality adjustment (GOD MODE)

## Installation

```bash
cd electron-app
npm install
```

## Running

Make sure the cognitive layer server is running:
```bash
cd /home/vedantso/ShowcaseSoftware
POPULATE_TEST_DATA=true python3 brain_server.py
```

Then start the Electron app:
```bash
npm start
```

For development with DevTools:
```bash
npm run dev
```

## Building

Build for your platform:
```bash
npm run build
```

Outputs will be in the `dist/` directory.

## Architecture

- **main.js**: Electron main process (window management)
- **preload.js**: Secure IPC bridge
- **index.html**: Main UI structure
- **styles.css**: Modern styling with CSS variables
- **app.js**: Frontend logic and API integration

## API Integration

The app connects to:
- **REST API**: `http://localhost:8000` (Cognitive Layer)
- **WebSocket**: `ws://localhost:8000/ws` (Real-time updates)

## Design

- Frameless window with custom title bar
- Modern rounded corners and shadows
- Smooth animations and transitions
- Dark theme optimized for long sessions
- Responsive layout


