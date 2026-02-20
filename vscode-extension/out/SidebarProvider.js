"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SidebarProvider = void 0;
const vscode = require("vscode");
const cp = require("child_process");
const fs = require("fs");
const path = require("path");
class SidebarProvider {
    constructor(_extensionUri) {
        this._extensionUri = _extensionUri;
        // --- Logic for running tasks ---
        this.contextFiles = new Set();
    }
    resolveWebviewView(webviewView, context, _token) {
        this._view = webviewView;
        webviewView.webview.options = {
            // Allow scripts in the webview
            enableScripts: true,
            localResourceRoots: [this._extensionUri],
        };
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
        webviewView.webview.onDidReceiveMessage(async (data) => {
            switch (data.type) {
                case "onCommand": {
                    if (data.command === "addContext") {
                        if (data.value)
                            this.addContext(data.value);
                    }
                    else {
                        if (data.value)
                            this.runPythonTask(data.value, data.options);
                    }
                    break;
                }
                case "onGenerateForm": {
                    if (!data.value) {
                        return;
                    }
                    this.runFormEngine(data.value, data.name);
                    break;
                }
                case "onStop": {
                    this.stopPythonTask();
                    break;
                }
                case "onInfo": {
                    if (data.value)
                        vscode.window.showInformationMessage(data.value);
                    break;
                }
                case "onError": {
                    if (data.value)
                        vscode.window.showErrorMessage(data.value);
                    break;
                }
                case "onBrowse": {
                    const options = {
                        canSelectMany: false,
                        openLabel: 'Select Path',
                        canSelectFiles: data.is_file ?? true,
                        canSelectFolders: data.is_dir ?? true
                    };
                    const fileUri = await vscode.window.showOpenDialog(options);
                    if (fileUri && fileUri[0]) {
                        webviewView.webview.postMessage({ type: 'setPath', value: fileUri[0].fsPath, target: data.target });
                    }
                    break;
                }
                case "onIngest": {
                    this.executeIngest(data.value);
                    break;
                }
                case "onUpdateConfig": {
                    this.updateConfig(data.configName, data.value);
                    break;
                }
                case "onSaveSettings": {
                    // Note: User requested that extension shouldn't change admin settings. 
                    // This is now handled by making the UI read-only or informational.
                    // But we keep the message handler for potential future allow-listed changes.
                    this.updateSettings(data.content);
                    break;
                }
            }
        });
    }
    revive(panel) {
        this._view = panel;
    }
    _getHtmlForWebview(webview) {
        const nonce = getNonce();
        const config = vscode.workspace.getConfiguration('aiOrchestrator');
        let apiBaseUrl = config.get('apiBaseUrl') || 'http://localhost:8000';
        if (apiBaseUrl.endsWith('/'))
            apiBaseUrl = apiBaseUrl.slice(0, -1);
        return `<!DOCTYPE html>
			<html lang="en">
			<head>
				<meta charset="UTF-8">
                <meta http-equiv="Content-Security-Policy" content="default-src 'none'; connect-src ${apiBaseUrl} http://127.0.0.1:8000; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}'; img-src ${webview.cspSource} https:;">
				<meta name="viewport" content="width=device-width, initial-scale=1.0">
				<title>AI Orchestrator Chat</title>
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@400;600&display=swap');

                    :root {
                        --step-bg: color-mix(in srgb, var(--vscode-editor-inactiveSelectionBackground), transparent 70%);
                        --step-border: var(--vscode-widget-border);
                        --text-main: var(--vscode-editor-foreground);
                        --text-sec: var(--vscode-descriptionForeground);
                        --accent: var(--vscode-button-background);
                        --accent-hover: var(--vscode-button-hoverBackground);
                        --bg-card: var(--vscode-sideBar-background);
                        --primary-gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
                    }

                    body {
                        padding: 0;
                        margin: 0;
                        font-family: 'Inter', var(--vscode-font-family), sans-serif;
                        color: var(--text-main);
                        font-size: 13px;
                        background: var(--vscode-editor-background);
                        overflow: hidden;
                    }

                    .app-container {
                        display: flex;
                        flex-direction: column;
                        height: 100vh;
                        background: radial-gradient(circle at top right, rgba(99, 102, 241, 0.05), transparent 40%),
                                    radial-gradient(circle at bottom left, rgba(168, 85, 247, 0.05), transparent 40%);
                    }

                    /* Premium Tabs */
                    .tabs-header {
                        display: flex;
                        background: var(--bg-card);
                        border-bottom: 1px solid var(--vscode-panel-border);
                        padding: 4px 12px 0;
                        gap: 16px;
                    }

                    .tab-btn {
                        padding: 10px 4px;
                        cursor: pointer;
                        border-bottom: 2px solid transparent;
                        color: var(--text-sec);
                        font-weight: 500;
                        font-size: 11px;
                        text-transform: uppercase;
                        letter-spacing: 0.8px;
                        transition: all 0.2s ease;
                        font-family: 'Outfit', sans-serif;
                    }

                    .tab-btn:hover { color: var(--text-main); }
                    .tab-btn.active {
                        color: var(--text-main);
                        border-bottom-color: #6366f1;
                        text-shadow: 0 0 8px rgba(99, 102, 241, 0.3);
                    }

                    .tab-content {
                        flex: 1;
                        display: none;
                        flex-direction: column;
                        overflow: hidden;
                    }

                    .tab-content.active { display: flex; animation: fadeIn 0.3s ease; }

                    @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

                    /* Chat Elements */
                    .chat-history {
                        flex: 1;
                        overflow-y: auto;
                        padding: 16px;
                        display: flex;
                        flex-direction: column;
                        gap: 20px;
                        scroll-behavior: smooth;
                    }

                    .chat-input-container {
                        padding: 16px;
                        background: var(--bg-card);
                        border-top: 1px solid var(--vscode-panel-border);
                        display: flex;
                        flex-direction: column;
                        gap: 12px;
                        box-shadow: 0 -4px 12px rgba(0,0,0,0.1);
                    }

                    .options-row { display: flex; gap: 8px; flex-wrap: wrap; }

                    .dropdown-group, .input-group {
                        display: flex;
                        align-items: center;
                        gap: 6px;
                        background: var(--vscode-input-background);
                        border: 1px solid var(--vscode-input-border);
                        border-radius: 6px;
                        padding: 4px 8px;
                        transition: border-color 0.2s;
                    }

                    .dropdown-group:hover { border-color: var(--accent); }

                    select, input {
                        background: transparent;
                        color: var(--vscode-input-foreground);
                        border: none;
                        outline: none;
                        font-size: 11px;
                        cursor: pointer;
                    }

                    .chat-input-area {
                        display: flex;
                        gap: 10px;
                        align-items: flex-end;
                        background: var(--vscode-input-background);
                        border: 1px solid var(--vscode-input-border);
                        border-radius: 12px;
                        padding: 6px 10px;
                        transition: all 0.2s;
                    }

                    .chat-input-area:focus-within {
                        border-color: #6366f1;
                        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
                    }

                    textarea {
                        flex: 1;
                        background: transparent;
                        color: var(--vscode-input-foreground);
                        border: none;
                        padding: 8px 4px;
                        resize: none;
                        height: 44px;
                        max-height: 250px;
                        font-family: inherit;
                        font-size: 13px;
                        line-height: 1.5;
                    }

                    .icon-btn {
                        background: transparent;
                        border: none;
                        color: var(--text-sec);
                        cursor: pointer;
                        padding: 6px;
                        border-radius: 6px;
                        display: flex;
                        align-items: center;
                        transition: all 0.2s;
                    }

                    .icon-btn:hover { background: var(--vscode-toolbar-hoverBackground); color: var(--text-main); }

                    #send-btn { 
                        background: var(--primary-gradient); 
                        color: white; 
                        border-radius: 8px; 
                        width: 32px; 
                        height: 32px; 
                        font-weight: bold;
                        box-shadow: 0 2px 6px rgba(99, 102, 241, 0.4);
                    }

                    #stop-btn { background: #ef4444; color: white; display: none; border-radius: 8px; width: 32px; height: 32px; }

                    /* Step Badges & Tiers */
                    .step-item {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        gap: 10px;
                        font-size: 11px;
                        padding: 10px 12px;
                        border-radius: 10px;
                        border: 1px solid var(--vscode-input-border);
                        background: var(--step-bg);
                        backdrop-filter: blur(4px);
                        margin-bottom: 6px;
                    }

                    .step-main { display: flex; align-items: center; gap: 8px; }

                    .tier-badge {
                        font-size: 9px;
                        font-weight: 600;
                        padding: 2px 6px;
                        border-radius: 4px;
                        background: rgba(99, 102, 241, 0.15);
                        color: #818cf8;
                        border: 1px solid rgba(129, 140, 248, 0.3);
                        text-transform: uppercase;
                    }

                    .tier-rules { color: #f59e0b; background: rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.3); }
                    .tier-tokens { color: #ec4899; background: rgba(236, 72, 153, 0.1); border-color: rgba(236, 72, 153, 0.3); }
                    .tier-components { color: #10b981; background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.3); }

                    /* Message Bubbles */
                    .message.user {
                        align-self: flex-end;
                        background: var(--primary-gradient);
                        color: white;
                        padding: 10px 16px;
                        border-radius: 18px 18px 4px 18px;
                        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
                        max-width: 85%;
                    }

                    .response-content {
                        background: var(--vscode-editor-background);
                        border: 1px solid var(--vscode-panel-border);
                        border-radius: 12px;
                        padding: 14px;
                        white-space: pre-wrap;
                        font-family: 'JetBrains Mono', var(--vscode-editor-font-family);
                        font-size: 12px;
                        line-height: 1.6;
                        box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
                    }

                    /* Knowledge & Settings */
                    .kb-container, .settings-container { padding: 20px; gap: 16px; }
                    .kb-title { font-family: 'Outfit', sans-serif; letter-spacing: 0.5px; margin-bottom: 12px; color: #a5b4fc; }
                    
                    .collection-item {
                        background: color-mix(in srgb, var(--vscode-list-hoverBackground), transparent 20%);
                        border: 1px solid var(--vscode-panel-border);
                        padding: 12px;
                        border-radius: 8px;
                        margin-bottom: 6px;
                        transition: transform 0.2s;
                    }
                    .collection-item:hover { transform: translateX(4px); border-color: #6366f1; }

                    .primary-btn {
                        background: var(--primary-gradient);
                        padding: 10px;
                        border-radius: 8px;
                        font-weight: 600;
                        transition: opacity 0.2s;
                    }
                    .primary-btn:hover { opacity: 0.9; }
                </style>
			</head>
			<body>
                <div class="app-container">
                    <div class="tabs-header">
                        <div class="tab-btn active" data-tab="chat">Assistant</div>
                        <div class="tab-btn" data-tab="form-studio">Form Studio</div>
                        <div class="tab-btn" data-tab="knowledge">Knowledge</div>
                        <div class="tab-btn" data-tab="settings">Settings</div>
                    </div>

                    <div id="tab-chat" class="tab-content active">
                        <div id="chat-history" class="chat-history">
                            <div class="message bot">
                                <div class="response-content" style="display: block;">Ready for new tasks. Powered by DynUI v2.1</div>
                            </div>
                        </div>
                        <div class="chat-input-container">
                            <div class="options-row">
                                <div class="dropdown-group" title="Execution Mode">
                                    <span>⚡</span>
                                    <select id="strategy-select">
                                        <option value="agentic">Agentic</option>
                                    </select>
                                </div>
                                <div class="dropdown-group" title="Model Selection">
                                    <span>🤖</span>
                                    <select id="model-select">
                                        <option value="gpt-5.2">Loading models...</option>
                                    </select>
                                </div>
                                <div class="dropdown-group" title="Local Budget">
                                    <input id="limit-input" type="number" step="0.5" placeholder="Limit" style="width: 45px;"/>
                                    <span style="font-size: 10px; color: #10b981">$</span>
                                </div>
                            </div>
                             <div class="chat-input-area">
                                <button id="browse-context-btn" class="icon-btn" title="Add files">📎</button>
                                <textarea id="chat-input" placeholder="Give me a requirement..."></textarea>
                                <div class="actions">
                                    <button id="send-btn">➔</button>
                                    <button id="stop-btn">■</button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Form Studio Tab -->
                    <div id="tab-form-studio" class="tab-content">
                        <div class="kb-container">
                            <div class="kb-title" style="display: flex; align-items: center; gap: 8px;">
                                <span style="font-size: 1.2em;">🪄</span>
                                <span>DynUI Form Architect</span>
                            </div>
                            <p style="color: var(--text-sec); font-size: 11px; margin-bottom: 20px;">
                                Provide a requirement in **natural language** OR paste a **JSON data model** below. The engine will infer the best field types and layout.
                            </p>
                            
                            <div class="form-field">
                                <label>Project Name</label>
                                <input type="text" id="form-project-name" placeholder="my-awesome-form" style="width: 100%; margin-bottom: 12px; background: var(--vscode-input-background); border: 1px solid var(--vscode-input-border); padding: 6px; border-radius: 4px;" />
                            </div>

                            <div class="form-field">
                                <label>Requirement / JSON Data</label>
                                <textarea id="form-prompt" placeholder='{ "firstName": "John", "age": 30 }  ... OR ...  "Create a membership form"' style="width: 100%; height: 120px; background: var(--vscode-input-background); border: 1px solid var(--vscode-input-border); padding: 8px; border-radius: 4px; margin-bottom: 16px; font-family: monospace; font-size: 12px;"></textarea>
                            </div>

                            <button class="primary-btn" style="width: 100%;" onclick="generateForm()">Generate DynUI Project</button>
                            
                            <div id="form-status" style="margin-top: 16px;"></div>
                        </div>
                    </div>

                    <!-- Knowledge Tab -->
                    <div id="tab-knowledge" class="tab-content">
                        <div class="kb-container">
                            <div class="kb-section">
                                <div class="kb-title" style="display: flex; justify-content: space-between;">
                                    <span>Stored Knowledge Tiers</span>
                                    <span style="cursor: pointer;" onclick="refreshCollections()">🔄</span>
                                </div>
                                <div id="collection-list" class="collection-list"></div>
                            </div>
                            <div class="kb-section">
                                <div class="kb-title">Data Ingestion</div>
                                <div class="ingest-form">
                                    <div class="form-field">
                                        <label>Target Domain</label>
                                        <select id="ingest-type">
                                            <option value="instruction_docs">Documentation (T1)</option>
                                            <option value="specialization_rules">Design Tokens (T2)</option>
                                            <option value="component_library">UI Components (T3)</option>
                                            <option value="database">DB Schema (T4)</option>
                                        </select>
                                    </div>
                                    <div class="form-field">
                                        <label>Source Path</label>
                                        <div class="input-with-browse">
                                            <input type="text" id="ingest-path" />
                                            <button class="browse-btn" onclick="vscode.postMessage({ type: 'onBrowse', target: 'ingest-path' })">...</button>
                                        </div>
                                    </div>
                                    <button class="primary-btn" onclick="vscode.postMessage({ type: 'onIngest', value: { type: document.getElementById('ingest-type').value, path: document.getElementById('ingest-path').value } })">Ingest to RAG</button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Settings Tab -->
                    <div id="tab-settings" class="tab-content">
                        <div class="settings-container">
                            <div class="kb-title">Admin Settings (Read-only)</div>
                            <p style="color: var(--text-sec); font-size: 11px; margin-bottom: 20px;">
                                These settings are synchronized with the **Admin Panel**. You can only apply more restrictive local limits in the Chat tab.
                            </p>
                            <div class="setting-item" style="opacity: 0.7;">
                                <label>Strict Budget Mode</label>
                                <input type="checkbox" id="strict-mode" disabled />
                            </div>
                            <div class="setting-item" style="opacity: 0.7;">
                                <label>Global Task Limit ($)</label>
                                <input type="number" id="global-task-limit" class="setting-input" disabled />
                            </div>
                            <div class="setting-item" style="opacity: 0.7;">
                                <label>Review Strategy</label>
                                <input type="checkbox" id="review-strategy" disabled />
                            </div>
                            <div class="setting-item" style="opacity: 0.7;">
                                <label>Consensus Mode</label>
                                <input type="checkbox" id="consensus-mode" disabled />
                            </div>
                            <div style="margin-top: 40px; text-align: center; opacity: 0.5; font-size: 10px;">
                                Orchestrator v4.3.0 • AI Layout Architect
                            </div>
                        </div>
                    </div>
                </div>

                <script nonce="${nonce}">
                    const vscode = acquireVsCodeApi();
                    const API_BASE_URL = "${apiBaseUrl}";
                    
                    function switchTab(tabId) {
                        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                        document.querySelector('.tab-btn[data-tab="' + tabId + '"]').classList.add('active');
                        document.getElementById('tab-' + tabId).classList.add('active');
                        if (tabId === 'knowledge') refreshCollections();
                    }

                    const chatHistory = document.getElementById('chat-history');
                    const chatInput = document.getElementById('chat-input');
                    const sendBtn = document.getElementById('send-btn');
                    const stopBtn = document.getElementById('stop-btn');
                    const strategySelect = document.getElementById('strategy-select');
                    const modelSelect = document.getElementById('model-select');
                    const limitInput = document.getElementById('limit-input');
                     const deepSearchCheck = document.getElementById('deep-search-check');
                    const strictMode = document.getElementById('strict-mode');
                    const globalTaskLimit = document.getElementById('global-task-limit');

                    let currentBotMessage = null;

                    const reviewStrategy = document.getElementById('review-strategy');
                    const consensusMode = document.getElementById('consensus-mode');
                    const ingestTypeSelect = document.getElementById('ingest-type');

                    async function loadSettings() {
                        try {
                            const res = await fetch(API_BASE_URL + '/config/client-settings');
                            if (res.ok) {
                                const data = await res.json();
                                
                                // Populate models
                                if (data.models) {
                                    modelSelect.innerHTML = '';
                                    data.models.forEach(m => {
                                        const opt = document.createElement('option');
                                        opt.value = m.id;
                                        opt.text = m.label;
                                        modelSelect.appendChild(opt);
                                    });
                                }

                                // Populate modes
                                if (data.modes) {
                                    strategySelect.innerHTML = '';
                                    data.modes.forEach(mode => {
                                        const opt = document.createElement('option');
                                        opt.value = mode;
                                        opt.text = mode.charAt(0).toUpperCase() + mode.slice(1);
                                        strategySelect.appendChild(opt);
                                    });
                                }

                                // Budget Limits
                                if (data.daily_spend) {
                                    const budget = data.daily_spend.limit_usd || 1.0;
                                    if (globalTaskLimit) globalTaskLimit.value = budget;
                                    if (limitInput) {
                                        limitInput.value = budget;
                                        limitInput.max = budget;
                                        limitInput.title = "Admin Max: $" + budget;
                                    }
                                }

                                // Advanced Options visually mapped
                                if (data.advanced_options) {
                                    if (reviewStrategy) reviewStrategy.checked = data.advanced_options.review_strategy;
                                    if (consensusMode) consensusMode.checked = data.advanced_options.consensus_mode;
                                }

                                // Allowed RAG Tiers
                                if (data.allowed_rag_tiers) {
                                    const allowed = data.allowed_rag_tiers;
                                    Array.from(ingestTypeSelect.options).forEach(opt => {
                                        // Simple heuristic if not exact match: T1/T2 are index < 2
                                        const val = opt.value;
                                        let tierStr = 't1';
                                        if (val === 'instruction_docs') tierStr = 't1';
                                        else if (val === 'specialization_rules') tierStr = 't2';
                                        else if (val === 'component_library') tierStr = 't3';
                                        else if (val === 'database') tierStr = 't4';

                                        if (!allowed.includes(tierStr)) {
                                            opt.disabled = true;
                                            opt.text += ' (Read-only)';
                                        }
                                    });
                                }
                                
                                // Form Studio visually mapped
                                if (data.form_studio_enabled === false) {
                                    document.querySelector('.tab-btn[data-tab="form-studio"]').style.display = 'none';
                                }
                            }
                        } catch (e) { console.error("Failed to load client settings", e); }
                    }

                    loadSettings();
                    refreshCollections();

                    async function refreshCollections() {
                        const listDiv = document.getElementById('collection-list');
                        listDiv.innerHTML = '<div style="font-size: 10px; opacity: 0.5;">Querying RAG store...</div>';
                        try {
                            const res = await fetch(API_BASE_URL + '/knowledge/collections');
                            if (res.ok) {
                                const data = await res.json();
                                listDiv.innerHTML = '';
                                data.collections.forEach(col => {
                                    const item = document.createElement('div');
                                    item.className = 'collection-item';
                                    item.innerHTML = '<span>' + col.name + '</span> <span class="col-stats">' + col.count + ' chunks</span>';
                                    listDiv.appendChild(item);
                                });
                            }
                        } catch (e) { listDiv.innerHTML = 'Offline'; }
                    }

                    function addStep(text, type = 'thinking', tier = null) {
                        if (!currentBotMessage) currentBotMessage = createBotMessageContainer();
                        
                        const stepItem = document.createElement('div');
                        stepItem.className = 'step-item ' + type;
                        
                        let icon = '●';
                        if (type === 'thinking') icon = '🧠';
                        if (type === 'analyzing') icon = '🔍';
                        if (type === 'editing') icon = '✍️';
                        if (type === 'done') icon = '✨';
                        
                        let tierHtml = '';
                        if (tier) {
                            const tierClass = tier.toLowerCase().includes('token') ? 'tier-tokens' : 
                                            tier.toLowerCase().includes('rule') ? 'tier-rules' : 
                                            tier.toLowerCase().includes('component') ? 'tier-components' : '';
                            tierHtml = '<span class="tier-badge ' + tierClass + '">' + tier + '</span>';
                        }
                        
                        stepItem.innerHTML = '<div class="step-main"><span class="icon">' + icon + '</span> <span>' + text + '</span></div>' + tierHtml;
                        currentBotMessage.steps.appendChild(stepItem);
                        chatHistory.scrollTop = chatHistory.scrollHeight;
                    }

                    function createBotMessageContainer() {
                        const msgDiv = document.createElement('div');
                        msgDiv.className = 'message bot';
                        const stepsDiv = document.createElement('div');
                        stepsDiv.className = 'steps-container';
                        msgDiv.appendChild(stepsDiv);
                        const contentDiv = document.createElement('div');
                        contentDiv.className = 'response-content';
                        msgDiv.appendChild(contentDiv);
                        chatHistory.appendChild(msgDiv);
                        return { steps: stepsDiv, content: contentDiv };
                    }

                    function appendToResponse(text) {
                        if (!currentBotMessage) currentBotMessage = createBotMessageContainer();
                        currentBotMessage.content.style.display = 'block';
                        currentBotMessage.content.textContent += text;
                        chatHistory.scrollTop = chatHistory.scrollHeight;
                    }

                    function generateForm() {
                        const prompt = document.getElementById('form-prompt');
                        const name = document.getElementById('form-project-name');
                        if (!prompt.value || !name.value) {
                            vscode.postMessage({ type: 'onError', value: 'Please provide both a name and a description.' });
                            return;
                        }
                        switchTab('chat');
                        vscode.postMessage({ type: 'onGenerateForm', value: prompt.value, name: name.value });
                        prompt.value = '';
                    }

                    window.addEventListener('message', event => {
                        const message = event.data;
                        switch (message.type) {
                            case 'appendResponse':
                                const raw = message.value;
                                if (raw.startsWith(':::STEP:')) {
                                    try {
                                        const stepData = JSON.parse(raw.replace(':::STEP:', '').replace(':::',''));
                                        addStep(stepData.text, stepData.type, stepData.tier);
                                    } catch(e) { appendToResponse(raw); }
                                } else if (raw.includes(':::FILES:')) {
                                    // Handle file review button
                                } else {
                                    appendToResponse(raw);
                                }
                                break;
                            case 'setRunning':
                                if (!message.value) addStep("Task Completed", "done");
                                break;
                            case 'setPath':
                                if (message.target === 'context') {
                                    vscode.postMessage({ type: 'onCommand', command: 'addContext', value: message.value });
                                    addStep("Added to context: " + message.value.split(/[\\\/]/).pop(), "done");
                                } else {
                                    const input = document.getElementById(message.target);
                                    if (input) input.value = message.value;
                                }
                                break;
                        }
                    });

                    // Tab switching listeners
                    document.querySelectorAll('.tab-btn').forEach(btn => {
                        btn.addEventListener('click', () => {
                            switchTab(btn.dataset.tab);
                        });
                    });

                    // Context Upload
                    const browseBtn = document.getElementById('browse-context-btn');
                    if (browseBtn) {
                        browseBtn.addEventListener('click', () => {
                            vscode.postMessage({ type: 'onBrowse', target: 'context' });
                        });
                    }

                    sendBtn.addEventListener('click', () => {
                        if (!chatInput.value) return;
                        const div = document.createElement('div');
                        div.className = 'message user';
                        div.textContent = chatInput.value;
                        chatHistory.appendChild(div);
                        
                        const localLimit = limitInput.value ? parseFloat(limitInput.value) : null;
                        const maxLimit = limitInput.max ? parseFloat(limitInput.max) : 999;

                        if (localLimit !== null && localLimit > maxLimit) {
                            vscode.postMessage({ 
                                type: 'onError', 
                                value: 'Local limit ($' + localLimit + ') cannot exceed Admin limit ($' + maxLimit + ')' 
                            });
                            return;
                        }

                        vscode.postMessage({ 
                            type: 'onCommand', 
                            value: chatInput.value,
                            options: { 
                                mode: strategySelect.value, 
                                model: modelSelect.value,
                                localLimit: localLimit,
                                deepSearch: strategySelect.value === 'deep-search'
                            }
                        });
                        chatInput.value = '';
                        currentBotMessage = null;
                    });
                </script>
			</body>
			</html>`;
    }
    addContext(filePath) {
        this.contextFiles.add(filePath);
        this._view?.webview.postMessage({ type: 'addResponse', value: `Added to context: ${path.basename(filePath)}` });
        this.updateStatusBar();
    }
    clearContext() {
        this.contextFiles.clear();
        this._view?.webview.postMessage({ type: 'addResponse', value: `Context cleared.` });
        this.updateStatusBar();
    }
    updateStatusBar() {
        if (this.statusBarItem) {
            if (this.contextFiles.size > 0) {
                this.statusBarItem.text = `$(list-flat) AI Context: ${this.contextFiles.size}`;
                this.statusBarItem.show();
            }
            else {
                this.statusBarItem.hide();
            }
        }
    }
    stopPythonTask() {
        if (this._currentProcess) {
            this._currentProcess.kill();
            this._currentProcess = undefined;
            this._view?.webview.postMessage({ type: 'setRunning', value: false });
            this._view?.webview.postMessage({ type: 'addResponse', value: "\n[Task Stopped by User]" });
        }
    }
    async executeIngest(value) {
        try {
            const config = vscode.workspace.getConfiguration('aiOrchestrator');
            const apiBaseUrl = config.get('apiBaseUrl') || 'http://localhost:8000';
            const response = await fetch(`${apiBaseUrl}/admin/ingest/execute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(value)
            });
            if (response.ok) {
                const result = await response.json();
                vscode.window.showInformationMessage(`Ingestion successful: ${result.documents_ingested} documents added.`);
                this._view?.webview.postMessage({ type: 'addResponse', value: `\n[Ingest Success]: ${result.documents_ingested} documents added to ${result.collection}` });
            }
            else {
                const err = await response.json();
                vscode.window.showErrorMessage(`Ingestion failed: ${err.detail?.errors?.join(', ') || err.detail || 'Unknown error'}`);
            }
        }
        catch (e) {
            vscode.window.showErrorMessage(`Failed to connect to backend: ${e}`);
        }
    }
    async updateSettings(value) {
        try {
            const config = vscode.workspace.getConfiguration('aiOrchestrator');
            const apiBaseUrl = config.get('apiBaseUrl') || 'http://localhost:8000';
            const response = await fetch(`${apiBaseUrl}/config/settings`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    models: {}, // Not changing models here
                    global_config: value
                })
            });
            if (response.ok) {
                vscode.window.showInformationMessage(`Settings updated successfully.`);
            }
            else {
                vscode.window.showErrorMessage(`Failed to update settings.`);
            }
        }
        catch (e) {
            vscode.window.showErrorMessage(`Failed to connect to backend: ${e}`);
        }
    }
    async updateConfig(configName, value) {
        try {
            const config = vscode.workspace.getConfiguration('aiOrchestrator');
            const apiBaseUrl = config.get('apiBaseUrl') || 'http://localhost:8000';
            const response = await fetch(`${apiBaseUrl}/admin/config/${configName}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: value })
            });
            if (response.ok) {
                vscode.window.showInformationMessage(`Configuration ${configName} updated successfully.`);
            }
            else {
                vscode.window.showErrorMessage(`Failed to update config ${configName}.`);
            }
        }
        catch (e) {
            vscode.window.showErrorMessage(`Failed to connect to backend: ${e}`);
        }
    }
    async runPythonTask(prompt, options) {
        if (!this._view) {
            vscode.window.showErrorMessage("Webview not initialized");
            return;
        }
        this._view.webview.postMessage({ type: 'addResponse', value: "Thinking..." });
        // Get Configuration
        const config = vscode.workspace.getConfiguration('aiOrchestrator');
        const pythonPath = config.get('pythonPath') || 'python';
        let projectRoot = config.get('projectRoot');
        if (!projectRoot) {
            if (vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders.length > 0) {
                projectRoot = vscode.workspace.workspaceFolders[0].uri.fsPath;
            }
            else {
                this._view.webview.postMessage({ type: 'addResponse', value: "Error: No workspace open or projectRoot configured." });
                this._view.webview.postMessage({ type: 'setRunning', value: false });
                return;
            }
        }
        // Auto-detect venv
        let finalPythonPath = pythonPath;
        if (finalPythonPath === 'python' || finalPythonPath === 'python3') {
            const possibleVenvWin = path.join(projectRoot, '.venv', 'Scripts', 'python.exe');
            const possibleVenvUnix = path.join(projectRoot, '.venv', 'bin', 'python');
            if (fs.existsSync(possibleVenvWin)) {
                finalPythonPath = possibleVenvWin;
            }
            else if (fs.existsSync(possibleVenvUnix)) {
                finalPythonPath = possibleVenvUnix;
            }
        }
        const scriptPath = path.join(projectRoot, 'scripts', 'run_task.py');
        if (!fs.existsSync(scriptPath)) {
            this._view.webview.postMessage({ type: 'addResponse', value: `Error: Script not found at: ${scriptPath}` });
            this._view.webview.postMessage({ type: 'setRunning', value: false });
            return;
        }
        // Build Arguments
        let args = ['-u', scriptPath, prompt];
        if (options) {
            if (options.mode) {
                args.push('--mode');
                args.push(options.mode);
            }
            if (options.model) {
                args.push('--model');
                args.push(options.model);
            }
            if (options.localLimit) {
                args.push('--local-limit');
                args.push(options.localLimit.toString());
            }
        }
        this.contextFiles.forEach(file => {
            args.push('--context');
            args.push(file);
        });
        this._currentProcess = cp.spawn(finalPythonPath, args, { cwd: projectRoot });
        // Helper to check for cost alerts
        const checkAlerts = (text) => {
            if (text.includes('[COST_ALERT]')) {
                try {
                    // Extract JSON from "[COST_ALERT] {...}"
                    const match = text.match(/\[COST_ALERT\] ({.*})/);
                    if (match && match[1]) {
                        const alert = JSON.parse(match[1]);
                        vscode.window.showWarningMessage(`⚠️ Budget Alert: ${alert.message}`);
                    }
                }
                catch (e) {
                    console.error("Failed to parse cost alert", e);
                }
            }
        };
        this._currentProcess.stdout?.on('data', (data) => {
            const str = data.toString();
            checkAlerts(str);
            this._view?.webview.postMessage({ type: 'appendResponse', value: str });
        });
        this._currentProcess.stderr?.on('data', (data) => {
            const str = data.toString();
            checkAlerts(str);
            this._view?.webview.postMessage({ type: 'appendResponse', value: `[Error]: ${str}` });
        });
        this._currentProcess.on('close', (code) => {
            this._currentProcess = undefined;
            this._view?.webview.postMessage({ type: 'setRunning', value: false });
            if (code === 0) {
                this._view?.webview.postMessage({ type: 'addResponse', value: `\n[Task Completed]` });
            }
            else if (code !== null) { // code is null if killed
                this._view?.webview.postMessage({ type: 'addResponse', value: `\n[Task Failed with code ${code}]` });
            }
        });
    }
    async runFormEngine(prompt, projectName) {
        if (!this._view)
            return;
        this._view.webview.postMessage({ type: 'addResponse', value: "Launching Form Engine Studio..." });
        const config = vscode.workspace.getConfiguration('aiOrchestrator');
        const pythonPath = config.get('pythonPath') || 'python';
        let projectRoot = config.get('projectRoot');
        if (!projectRoot && vscode.workspace.workspaceFolders) {
            projectRoot = vscode.workspace.workspaceFolders[0].uri.fsPath;
        }
        if (!projectRoot)
            return;
        let finalPythonPath = pythonPath;
        const possibleVenvWin = path.join(projectRoot, '.venv', 'Scripts', 'python.exe');
        if (fs.existsSync(possibleVenvWin))
            finalPythonPath = possibleVenvWin;
        const scriptPath = path.join(projectRoot, 'scripts', 'run_form_engine.py');
        this._currentProcess = cp.spawn(finalPythonPath, ['-u', scriptPath, prompt, '--name', projectName], { cwd: projectRoot });
        this._currentProcess.stdout?.on('data', (data) => {
            this._view?.webview.postMessage({ type: 'appendResponse', value: data.toString() });
        });
        this._currentProcess.stderr?.on('data', (data) => {
            this._view?.webview.postMessage({ type: 'appendResponse', value: `[Error]: ${data.toString()}` });
        });
        this._currentProcess.on('close', (code) => {
            this._currentProcess = undefined;
            this._view?.webview.postMessage({ type: 'setRunning', value: false });
            if (code === 0) {
                vscode.window.showInformationMessage("DynUI Form Project generated successfully!");
            }
        });
    }
}
exports.SidebarProvider = SidebarProvider;
function getNonce() {
    let text = "";
    const possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
//# sourceMappingURL=SidebarProvider.js.map