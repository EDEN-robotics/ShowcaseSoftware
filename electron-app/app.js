// API Configuration
const API_BASE = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws';

// State
let graph = null;
let ws = null;
let currentTab = 'graph';
let currentUser = 'User'; // Track current user name

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initTitleBar();
    initTabs();
    initGraph();
    initChat();
    initPersonality();
    connectWebSocket();
    loadGraphState();
});

// Title Bar Controls
function initTitleBar() {
    document.getElementById('minimize-btn').addEventListener('click', () => {
        window.electronAPI.minimizeWindow();
    });

    document.getElementById('maximize-btn').addEventListener('click', () => {
        window.electronAPI.maximizeWindow();
    });

    document.getElementById('close-btn').addEventListener('click', () => {
        window.electronAPI.closeWindow();
    });
}

// Tab Navigation
function initTabs() {
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Map old tab names to new ones
    if (tabName === 'chat') {
        tabName = 'interact';
    }
    
    // Update nav
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    const tabElement = document.querySelector(`[data-tab="${tabName}"]`);
    if (tabElement) {
        tabElement.classList.add('active');
    }

    // Update content
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    const contentElement = document.getElementById(`${tabName}-tab`);
    if (contentElement) {
        contentElement.classList.add('active');
    }

    currentTab = tabName;

    // Refresh graph when switching to it
    if (tabName === 'graph') {
        loadGraphState();
    }
}

// WebSocket Connection
function connectWebSocket() {
    try {
        ws = new WebSocket(WS_URL);

        ws.onopen = () => {
            updateConnectionStatus(true);
            console.log('WebSocket connected');
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
            // Graph updates handled here, planning/interaction updates are handled via API responses
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            updateConnectionStatus(false);
        };

        ws.onclose = () => {
            updateConnectionStatus(false);
            // Reconnect after 3 seconds
            setTimeout(connectWebSocket, 3000);
        };
    } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        updateConnectionStatus(false);
    }
}

function updateConnectionStatus(connected) {
    const status = document.getElementById('connection-status');
    const dot = status.querySelector('.status-dot');
    const text = status.querySelector('.status-text');

    if (connected) {
        dot.classList.add('connected');
        text.textContent = 'Connected';
    } else {
        dot.classList.remove('connected');
        text.textContent = 'Disconnected';
    }
}

function handleWebSocketMessage(data) {
    if (data.type === 'initial_state' || data.type === 'graph_updated') {
        updateGraph(data.data);
    }
    // Planning and interactions are now handled via API responses, not WebSocket
}

// Graph Visualization
function initGraph() {
    const container = document.getElementById('graph-visualization');
    
    if (!container) {
        console.error('Graph container not found!');
        return;
    }
    
    // Check if ForceGraph3D is available
    if (typeof ForceGraph3D === 'undefined') {
        console.error('ForceGraph3D not loaded! Check CDN connection.');
        container.innerHTML = '<div style="color: white; padding: 20px;">Error: 3D Force Graph library not loaded. Check internet connection.</div>';
        return;
    }
    
    try {
        // Try 3D first - use simpler approach that works with default rendering
        graph = ForceGraph3D()
            .nodeLabel(node => {
                // Extract one-word label
                const oneWordLabel = getOneWordLabel(node);
                const content = node.content || '';
                return `${oneWordLabel}: ${content.substring(0, 50)}...`;
            })
            .nodeColor(node => getNodeColor(node))
            .nodeVal(node => {
                const importance = node.importance || 0.5;
                return importance * 10 + 5;
            })
            .linkColor(() => 'rgba(255, 255, 255, 0.5)')
            .linkWidth(link => {
                // Thicker lines based on link value/weight
                return (link.value || 1) * 3 + 2;
            })
            .linkDirectionalParticles(2)
            .linkDirectionalParticleSpeed(0.01)
            .backgroundColor('#0a0a0f')
            (container);
        
        
        console.log('3D Graph initialized successfully');
    } catch (error) {
        console.error('Error initializing 3D graph:', error);
        console.log('Falling back to 2D graph...');
        
        // Fallback to 2D if 3D fails
        try {
            if (typeof ForceGraph === 'undefined') {
                // Load 2D version
                const script = document.createElement('script');
                script.src = 'https://unpkg.com/force-graph@1.43.3/dist/force-graph.min.js';
                script.onload = () => {
                    init2DGraph(container);
                };
                script.onerror = () => {
                    container.innerHTML = `<div style="color: white; padding: 20px;">
                        <p>Error: Could not initialize graph visualization.</p>
                        <p>WebGL Error: ${error.message}</p>
                        <p>Please check your GPU drivers or use a different browser.</p>
                    </div>`;
                };
                document.head.appendChild(script);
            } else {
                init2DGraph(container);
            }
        } catch (fallbackError) {
            container.innerHTML = `<div style="color: white; padding: 20px;">
                <p>Error initializing graph: ${error.message}</p>
                <p>Fallback also failed: ${fallbackError.message}</p>
            </div>`;
        }
    }

    document.getElementById('refresh-graph').addEventListener('click', loadGraphState);
    document.getElementById('reset-camera').addEventListener('click', () => {
        if (graph && graph.cameraPosition) {
            graph.cameraPosition({ x: 0, y: 0, z: 200 });
        }
    });
}

function init2DGraph(container) {
    graph = ForceGraph()
        .nodeLabel(node => {
            // Extract one-word label
            const oneWordLabel = getOneWordLabel(node);
            const content = node.content || '';
            return `${oneWordLabel}: ${content.substring(0, 50)}...`;
        })
        .nodeLabelMode('always')  // Always show labels (2D force-graph supports this)
        .nodeColor(node => getNodeColor(node))
        .nodeVal(node => {
            const importance = node.importance || 0.5;
            return importance * 10 + 5;
        })
        .linkColor(() => 'rgba(255, 255, 255, 0.5)')
        .linkWidth(link => {
            // Thicker lines based on link value/weight
            return (link.value || 1) * 3 + 2;
        })
        .backgroundColor('#0a0a0f')
        (container);
    
    console.log('2D Graph initialized as fallback');
}

function getNodeColor(node) {
    /**
     * Get color for a node based on its type
     */
    if (node.id === 'SELF') return '#6366f1';
    if (node.type === 'threat' || node.type === 'trauma') return '#ef4444';
    if (node.type === 'joy') return '#10b981';
    return '#8b5cf6';
}

function getOneWordLabel(node) {
    /**
     * Extract a one-word label from a node.
     * Priority: node.id (if single word) -> first word of content -> fallback
     */
    const nodeId = node.id || '';
    
    // If ID is a single word or short identifier, use it
    if (nodeId && !nodeId.includes(' ') && nodeId.length < 20) {
        // Clean up common prefixes/suffixes
        const cleanId = nodeId.replace(/^(user_|memory_|event_)/i, '').replace(/_/g, ' ');
        const words = cleanId.split(' ');
        if (words.length === 1) {
            return words[0].charAt(0).toUpperCase() + words[0].slice(1).toLowerCase();
        }
    }
    
    // Extract first meaningful word from content
    const content = node.content || '';
    if (content) {
        // Remove common prefixes and get first word
        const words = content.trim().split(/\s+/);
        if (words.length > 0) {
            const firstWord = words[0].replace(/[^a-zA-Z0-9]/g, '');
            if (firstWord.length > 0) {
                return firstWord.charAt(0).toUpperCase() + firstWord.slice(1).toLowerCase();
            }
        }
    }
    
    // Fallback: use first part of ID
    if (nodeId) {
        const parts = nodeId.split(/[_\s-]/);
        if (parts.length > 0) {
            return parts[0].charAt(0).toUpperCase() + parts[0].slice(1).toLowerCase();
        }
    }
    
    return 'Node';
}

// Removed createTextTexture - using simpler approach with default node rendering

async function loadGraphState() {
    try {
        const response = await fetch(`${API_BASE}/api/graph/state`);
        const data = await response.json();
        updateGraph(data);
    } catch (error) {
        console.error('Failed to load graph:', error);
    }
}

function updateGraph(data) {
    if (!graph) {
        console.warn('Graph not initialized yet');
        return;
    }
    
    if (!data || !data.nodes) {
        console.warn('No graph data received:', data);
        return;
    }

    try {
        const nodes = data.nodes.map(n => ({
            id: n.id || String(Math.random()),
            content: n.content || '',
            type: n.type || n.node_type || 'memory',
            node_type: n.type || n.node_type || 'memory',
            importance: n.importance || 0.5
        }));
        
        const links = (data.links || []).map(l => ({
            source: l.source || l.from || l[0],
            target: l.target || l.to || l[1],
            value: l.weight || l.value || 1
        }));

        console.log(`Updating graph with ${nodes.length} nodes and ${links.length} links`);
        
        graph.graphData({ nodes, links });

        // Update stats
        const nodeCountEl = document.getElementById('node-count');
        const edgeCountEl = document.getElementById('edge-count');
        if (nodeCountEl) nodeCountEl.textContent = nodes.length;
        if (edgeCountEl) edgeCountEl.textContent = links.length;
    } catch (error) {
        console.error('Error updating graph:', error);
    }
}

// Chat Interface
function initChat() {
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');

    const sendMessage = () => {
        const message = input.value.trim();
        if (!message) return;

        input.value = '';

        // Send to API (user message will be added in sendChatRequest)
        sendChatRequest(message);
    };

    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
}

function addChatMessage(role, content, messageType = 'system') {
    const messages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role} message-${messageType}`;
    
    // Format content (handle HTML)
    const formattedContent = content.replace(/\n/g, '<br>');
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <p>${formattedContent}</p>
        </div>
    `;
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}

function addDecisionMessage(reasoning) {
    const messages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message decision';
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="decision-header">🤔 Decision</div>
            <p>${reasoning}</p>
        </div>
    `;
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}

function addOutputMessage(willProceed, message) {
    /**
     * Add yellow "Output" box showing whether EDEN will proceed with planning
     */
    const messages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message output';
    const proceedText = willProceed ? 'Yes, I will do it!' : 'No, I will not proceed.';
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="output-header">📤 Output</div>
            <p><strong>${proceedText}</strong></p>
            ${message ? `<p style="margin-top: 4px; color: var(--text-secondary);">${message}</p>` : ''}
        </div>
    `;
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}

function addPlanningLoadingMessage() {
    /**
     * Add loading message while planning is being generated
     */
    const messages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message planning-loading';
    messageDiv.id = 'planning-loading-message';
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="planning-loading-header">⏳ Planning...</div>
            <p>Generating action plan. This may take 30-60 seconds.</p>
        </div>
    `;
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
    return messageDiv;
}

function removePlanningLoadingMessage() {
    /**
     * Remove the planning loading message
     */
    const loadingMsg = document.getElementById('planning-loading-message');
    if (loadingMsg) {
        loadingMsg.remove();
    }
}

function addPlanMessage(plan) {
    const messages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message plan';
    
    const actions = plan.actions || [];
    const actionsDetailed = plan.actions_detailed || [];
    const modelUsed = plan.model_used || 'unknown';
    const isCosmos = modelUsed.toLowerCase().includes('cosmos');
    const modelBadge = isCosmos 
        ? '<span style="color: #10b981; font-weight: bold;">🤖 COSMOS</span>' 
        : '<span style="color: #8b5cf6;">🦙 Ollama</span>';
    
    // Format actions
    let actionsHTML = '';
    if (actionsDetailed && actionsDetailed.length > 0) {
        actionsHTML = actionsDetailed.map((item, i) => {
            const actionText = typeof item === 'object' ? item.action : item;
            return `
                <div class="plan-action-item">
                    <div class="plan-action-number">${i + 1}.</div>
                    <div class="plan-action-content">
                        <div class="plan-action-text">${actionText}</div>
                    </div>
                </div>
            `;
        }).join('');
    } else {
        actionsHTML = actions.map((action, i) => `
            <div class="plan-action-item">
                <div class="plan-action-number">${i + 1}.</div>
                <div class="plan-action-content">
                    <div class="plan-action-text">${action}</div>
                </div>
            </div>
        `).join('');
    }
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="plan-header">
                <div class="plan-goal">📋 Action Plan</div>
                <div class="plan-meta">
                    ${modelBadge} | 
                    Confidence: ${(plan.confidence || 0).toFixed(2)}
                    ${plan.inference_time ? ` | Time: ${plan.inference_time.toFixed(1)}s` : ''}
                </div>
            </div>
            <div class="plan-actions">
                ${actionsHTML}
            </div>
        </div>
    `;
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}

function addMemoryMessage(memory) {
    const messages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message memory';
    
    const userContext = memory.user_context ? ` (from ${memory.user_context})` : '';
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="memory-header">💾 Added to Memory${userContext}</div>
            <p>${memory.content}</p>
        </div>
    `;
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}

function updateCurrentUserIndicator(userName) {
    /**
     * Update the current user indicator at the top of the chat
     */
    const indicator = document.getElementById('current-user-indicator');
    const nameSpan = document.getElementById('current-user-name');
    
    if (indicator && nameSpan) {
        if (userName && userName !== 'User') {
            nameSpan.textContent = `talking to ${userName}`;
            indicator.style.display = 'flex';
        } else {
            indicator.style.display = 'none';
        }
    }
}

async function sendChatRequest(message) {
    const sendBtn = document.getElementById('send-btn');
    const input = document.getElementById('chat-input');
    
    // Disable input while processing
    sendBtn.disabled = true;
    input.disabled = true;
    
    // Add user message
    addChatMessage('user', message, 'user');
    
    try {
        const response = await fetch(`${API_BASE}/api/interact`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user: currentUser, // Send current user name
                action: message
            }),
            timeout: 120000  // 2 minute timeout for planning
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        
        // Update current user if detected in response
        if (data.memory_added && data.memory_added.user_context && data.memory_added.user_context !== 'User') {
            currentUser = data.memory_added.user_context;
            updateCurrentUserIndicator(currentUser);
        }
        
        // Show decision if present
        if (data.decision && data.decision.reasoning) {
            addDecisionMessage(data.decision.reasoning);
            
            // Show Output box after decision - clearly state if proceeding or not
            const willProceed = data.decision.proceed === true;
            const outputMessage = willProceed 
                ? "I'll proceed with generating a plan for you."
                : "I've decided not to proceed with this request.";
            addOutputMessage(willProceed, outputMessage);
            
            // If proceeding, show planning loading message immediately
            if (willProceed) {
                addPlanningLoadingMessage();
            }
        }
        
        // Show response
        const responseText = data.response || 'No response received';
        addChatMessage('system', responseText, 'system');
        
        // Remove loading message if plan is ready
        removePlanningLoadingMessage();
        
        // Show plan if generated
        if (data.plan && data.plan.actions && data.plan.actions.length > 0) {
            addPlanMessage(data.plan);
        }
        
        // Show memory addition if present
        if (data.memory_added) {
            addMemoryMessage(data.memory_added);
        }
        
        // Reload graph to show new memory
        setTimeout(loadGraphState, 500);
    } catch (error) {
        console.error('Chat error:', error);
        addChatMessage('system', `Error: ${error.message}\n\nMake sure the cognitive layer server is running on port 8000.`, 'error');
    } finally {
        // Re-enable input
        sendBtn.disabled = false;
        input.disabled = false;
        input.focus();
    }
}


// Personality Controls
async function initPersonality() {
    // Load current personality
    try {
        const response = await fetch(`${API_BASE}/api/graph/state`);
        const data = await response.json();
        const selfNode = data.nodes.find(n => n.id === 'SELF');
        
        if (selfNode && selfNode.personality) {
            setupPersonalitySliders(selfNode.personality);
        } else {
            setupPersonalitySliders({
                Openness: 0.5,
                Conscientiousness: 0.5,
                Extroversion: 0.5,
                Agreeableness: 0.5,
                Neuroticism: 0.5
            });
        }
    } catch (error) {
        console.error('Failed to load personality:', error);
        setupPersonalitySliders({
            Openness: 0.5,
            Conscientiousness: 0.5,
            Extroversion: 0.5,
            Agreeableness: 0.5,
            Neuroticism: 0.5
        });
    }

    document.getElementById('inject-trauma-btn').addEventListener('click', () => {
        fetch(`${API_BASE}/api/interact`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user: 'System',
                action: 'Inject Trauma'
            })
        });
    });

    document.getElementById('inject-kindness-btn').addEventListener('click', () => {
        fetch(`${API_BASE}/api/interact`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user: 'System',
                action: 'Inject Kindness'
            })
        });
    });
}

function setupPersonalitySliders(personality) {
    const container = document.getElementById('personality-sliders');
    container.innerHTML = '';

    const traits = ['Openness', 'Conscientiousness', 'Extroversion', 'Agreeableness', 'Neuroticism'];
    
    traits.forEach(trait => {
        const value = personality[trait] || 0.5;
        const sliderDiv = document.createElement('div');
        sliderDiv.className = 'slider-group';
        
        const label = trait === 'Agreeableness' ? 'Agreeableness (Kindness)' : 
                     trait === 'Neuroticism' ? 'Neuroticism (Anxiety)' : trait;
        
        sliderDiv.innerHTML = `
            <div class="slider-label">
                <span>${label}</span>
                <span class="slider-value" id="${trait.toLowerCase()}-value">${value.toFixed(2)}</span>
            </div>
            <input type="range" 
                   class="slider" 
                   id="${trait.toLowerCase()}-slider" 
                   min="0" 
                   max="1" 
                   step="0.01" 
                   value="${value}">
        `;
        
        container.appendChild(sliderDiv);

        const slider = document.getElementById(`${trait.toLowerCase()}-slider`);
        const valueDisplay = document.getElementById(`${trait.toLowerCase()}-value`);

        slider.addEventListener('input', (e) => {
            const val = parseFloat(e.target.value);
            valueDisplay.textContent = val.toFixed(2);
            updatePersonalityTrait(trait, val);
        });
    });
}

async function updatePersonalityTrait(trait, value) {
    try {
        await fetch(`${API_BASE}/api/god_mode/set_personality`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                trait: trait,
                value: value
            })
        });
        
        // Reload graph to see changes
        setTimeout(loadGraphState, 500);
    } catch (error) {
        console.error('Failed to update personality:', error);
    }
}

