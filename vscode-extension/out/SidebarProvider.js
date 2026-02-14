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
                    if (!data.value) {
                        return;
                    }
                    this.runPythonTask(data.value, data.options);
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
                case "onReviewChanges": {
                    // Logic for reviewing changes (existing)
                    break;
                }
            }
        });
    }
    revive(panel) {
        this._view = panel;
    }
    _getHtmlForWebview(webview) {
        // Use a nonce to only allow a specific script to be run.
        const nonce = getNonce();
        const config = vscode.workspace.getConfiguration('aiOrchestrator');
        // Ensure strictly no trailing slash to avoid double slashes in URLs
        let apiBaseUrl = config.get('apiBaseUrl') || 'http://localhost:8000';
        if (apiBaseUrl.endsWith('/')) {
            apiBaseUrl = apiBaseUrl.slice(0, -1);
        }
        return `<!DOCTYPE html>
			<html lang="en">
			<head>
				<meta charset="UTF-8">
                <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
				<meta name="viewport" content="width=device-width, initial-scale=1.0">
				<title>AI Orchestrator Chat</title>
                <style>
                    :root {
                        --step-bg: var(--vscode-editor-inactiveSelectionBackground);
                        --step-border: var(--vscode-widget-border);
                        --text-main: var(--vscode-editor-foreground);
                        --text-sec: var(--vscode-descriptionForeground);
                        --accent: var(--vscode-button-background);
                    }
                    body {
                        padding: 0;
                        margin: 0;
                        font-family: var(--vscode-font-family);
                        color: var(--text-main);
                        font-size: 13px;
                    }
                    .app-container {
                        display: flex;
                        flex-direction: column;
                        height: 100vh;
                        overflow: hidden;
                    }
                    /* Tabs Header */
                    .tabs-header {
                        display: flex;
                        background: var(--vscode-sideBar-background);
                        border-bottom: 1px solid var(--vscode-widget-border);
                        padding: 0 8px;
                    }
                    .tab-btn {
                        padding: 8px 12px;
                        cursor: pointer;
                        border-bottom: 2px solid transparent;
                        color: var(--text-sec);
                        font-weight: 500;
                        font-size: 11px;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                    }
                    .tab-btn.active {
                        color: var(--text-main);
                        border-bottom-color: var(--accent);
                    }
                    .tab-content {
                        flex: 1;
                        display: none;
                        flex-direction: column;
                        overflow: hidden;
                    }
                    .tab-content.active {
                        display: flex;
                    }

                    /* Chat Content */
                    .chat-history {
                        flex: 1;
                        overflow-y: auto;
                        padding: 12px;
                        display: flex;
                        flex-direction: column;
                        gap: 16px;
                    }
                    .chat-input-container {
                        padding: 12px;
                        background: var(--vscode-sideBar-background);
                        border-top: 1px solid var(--vscode-widget-border);
                        display: flex;
                        flex-direction: column;
                        gap: 10px;
                    }
                    .options-row {
                        display: flex;
                        gap: 6px;
                        flex-wrap: wrap;
                    }
                    .dropdown-group, .input-group {
                        display: flex;
                        align-items: center;
                        gap: 4px;
                        background: var(--vscode-input-background);
                        border: 1px solid var(--vscode-input-border);
                        border-radius: 4px;
                        padding: 2px 6px;
                    }
                    select, input {
                        background: transparent;
                        color: var(--vscode-input-foreground);
                        border: none;
                        outline: none;
                        font-size: 11px;
                    }
                    .chat-input-area {
                        display: flex;
                        gap: 8px;
                        align-items: flex-end;
                        background: var(--vscode-input-background);
                        border: 1px solid var(--vscode-input-border);
                        border-radius: 8px;
                        padding: 4px 8px;
                    }
                    textarea {
                        flex: 1;
                        background: transparent;
                        color: var(--vscode-input-foreground);
                        border: none;
                        padding: 8px;
                        resize: none;
                        height: 40px;
                        max-height: 200px;
                        font-family: inherit;
                        font-size: 13px;
                    }
                    .icon-btn {
                        background: transparent;
                        border: none;
                        color: var(--text-sec);
                        cursor: pointer;
                        padding: 4px;
                        border-radius: 4px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    .icon-btn:hover { background: var(--vscode-toolbar-hoverBackground); }
                    #send-btn { background: var(--accent); color: var(--vscode-button-foreground); border-radius: 4px; width: 28px; height: 28px; }
                    #stop-btn { background: var(--vscode-errorForeground); color: white; display: none; border-radius: 4px; width: 28px; height: 28px; }

                    /* Knowledge Tab Styles */
                    .kb-container { padding: 12px; overflow-y: auto; height: 100%; display: flex; flex-direction: column; gap: 16px; }
                    .kb-section { display: flex; flex-direction: column; gap: 8px; }
                    .kb-title { font-weight: bold; font-size: 11px; text-transform: uppercase; color: var(--text-sec); border-bottom: 1px solid var(--vscode-widget-border); padding-bottom: 4px; margin-bottom: 4px; }
                    .collection-list { display: flex; flex-direction: column; gap: 4px; }
                    .collection-item { background: var(--vscode-list-hoverBackground); padding: 8px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; font-size: 12px; }
                    .col-stats { font-size: 10px; color: var(--text-sec); }
                    
                    .ingest-form { display: flex; flex-direction: column; gap: 8px; background: var(--vscode-sideBar-background); border: 1px solid var(--vscode-widget-border); padding: 10px; border-radius: 4px; }
                    .form-field { display: flex; flex-direction: column; gap: 4px; }
                    .form-field label { font-size: 10px; color: var(--text-sec); }
                    .input-with-browse { display: flex; gap: 4px; }
                    .input-with-browse input { flex: 1; background: var(--vscode-input-background); border: 1px solid var(--vscode-input-border); border-radius: 4px; padding: 4px 8px; color: var(--vscode-input-foreground); }
                    .browse-btn { padding: 4px 8px; background: var(--vscode-button-secondaryBackground); color: var(--vscode-button-secondaryForeground); border: none; border-radius: 4px; cursor: pointer; font-size: 10px; }
                    .primary-btn { margin-top: 8px; padding: 6px; background: var(--accent); color: var(--vscode-button-foreground); border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
                    
                    /* Settings Tab Styles */
                    .settings-container { padding: 12px; display: flex; flex-direction: column; gap: 12px; }
                    .setting-item { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
                    .setting-item label { font-size: 12px; }
                    .setting-input { width: 60px; background: var(--vscode-input-background); border: 1px solid var(--vscode-input-border); color: var(--vscode-input-foreground); padding: 2px 4px; border-radius: 4px; }

                    /* Message Styles */
                    .message { max-width: 95%; line-height: 1.5; font-size: 13px; }
                    .message.user { align-self: flex-end; background: var(--accent); color: var(--vscode-button-foreground); padding: 8px 12px; border-radius: 12px 12px 2px 12px; }
                    .message.bot { align-self: flex-start; width: 100%; }
                    .steps-container { margin-bottom: 8px; display: flex; flex-direction: column; gap: 4px; }
                    .step-item { display: flex; align-items: center; gap: 8px; font-size: 11px; padding: 4px 8px; border-radius: 4px; border: 1px solid var(--vscode-input-border); background: var(--vscode-editor-inactiveSelectionBackground); opacity: 0.8; }
                    .step-item.done { border-left: 3px solid #2ecc71; background: transparent; border-color: transparent; }
                    .response-content { display: none; background: var(--vscode-editor-background); border: 1px solid var(--vscode-widget-border); border-radius: 6px; padding: 10px; white-space: pre-wrap; font-family: var(--vscode-editor-font-family); }
                    .error-box { color: var(--vscode-errorForeground); font-size: 12px; padding: 8px; border: 1px solid var(--vscode-errorForeground); border-radius: 4px; margin: 4px 0; }
                </style>
			</head>
			<body>
                <div class="app-container">
                    <div class="tabs-header">
                        <div class="tab-btn active" onclick="switchTab('chat')">Chat</div>
                        <div class="tab-btn" onclick="switchTab('knowledge')">Knowledge</div>
                        <div class="tab-btn" onclick="switchTab('settings')">Settings</div>
                    </div>

                    <!-- Chat Tab -->
                    <div id="tab-chat" class="tab-content active">
                        <div id="chat-history" class="chat-history">
                            <div class="message bot">
                                <div class="response-content">Hello! I am your AI Orchestrator. How can I help you today?</div>
                            </div>
                        </div>
                        <div class="chat-input-container">
                            <div class="options-row">
                                <div class="dropdown-group" title="Execution Strategy">
                                    <span>⚡</span>
                                    <select id="strategy-select">
                                        <option value="adaptive">Adaptive</option>
                                        <option value="planning">Planning</option>
                                        <option value="fast">Fast</option>
                                    </select>
                                </div>
                                <div class="dropdown-group" title="Model Selection">
                                    <span>🤖</span>
                                    <select id="model-select">
                                        <option value="gpt-4o">GPT-4o</option>
                                        <option value="gpt-4o-mini">GPT-4o Mini</option>
                                        <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
                                    </select>
                                </div>
                                <div class="dropdown-group" title="Session Budget Limit (USD)">
                                    <span>💰</span>
                                    <input id="limit-input" type="number" step="0.5" min="0" placeholder="∞" style="width: 35px;"/>
                                </div>
                            </div>
                            <div class="chat-input-area">
                                <button class="icon-btn" title="Add files to context" onclick="vscode.postMessage({ type: 'onBrowse', target: 'context' })">📎</button>
                                <textarea id="chat-input" placeholder="Ask anything..."></textarea>
                                <div class="actions">
                                    <button id="send-btn" title="Send (Enter)">➔</button>
                                    <button id="stop-btn" title="Stop Task">■</button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Knowledge Tab -->
                    <div id="tab-knowledge" class="tab-content">
                        <div class="kb-container">
                            <div class="kb-section">
                                <div class="kb-title" style="display: flex; justify-content: space-between;">
                                    <span>Active Collections</span>
                                    <span style="cursor: pointer;" onclick="refreshCollections()">🔄</span>
                                </div>
                                <div id="collection-list" class="collection-list">
                                    <div style="font-size: 10px; color: var(--text-sec);">Loading collections...</div>
                                </div>
                            </div>

                            <div class="kb-section">
                                <div class="kb-title">Add Knowledge (Ingest)</div>
                                <div class="ingest-form">
                                    <div class="form-field">
                                        <label>Source Type</label>
                                        <select id="ingest-type">
                                            <option value="instruction_docs">Instruction Docs (MD/TXT)</option>
                                            <option value="specialization_rules">Specialization Rules (YAML/JSON)</option>
                                            <option value="project_codebase">Full Codebase</option>
                                            <option value="database">Database Schema (C# Models)</option>
                                            <option value="component_library">Component Library (TSX/JSX)</option>
                                        </select>
                                    </div>
                                    <div class="form-field">
                                        <label>Path</label>
                                        <div class="input-with-browse">
                                            <input type="text" id="ingest-path" placeholder="C:/path/to/docs" />
                                            <button class="browse-btn" onclick="vscode.postMessage({ type: 'onBrowse', target: 'ingest-path' })">Browse</button>
                                        </div>
                                    </div>
                                    <div class="form-field">
                                        <label>Target Collection (Optional)</label>
                                        <input type="text" id="ingest-collection" placeholder="e.g. project_rules" style="background: var(--vscode-input-background); border: 1px solid var(--vscode-input-border); border-radius: 4px; padding: 4px 8px; color: var(--vscode-input-foreground); font-size: 11px;" />
                                    </div>
                                    <button class="primary-btn" onclick="executeIngest()">Start Ingestion</button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Settings Tab -->
                    <div id="tab-settings" class="tab-content">
                        <div class="settings-container">
                            <div class="kb-title">Global Budget Limits (Admin)</div>
                            <div class="setting-item">
                                <label>Task Limit (USD)</label>
                                <input type="number" id="global-task-limit" class="setting-input" step="0.1" value="1.0" />
                            </div>
                            <div class="setting-item">
                                <label>Hourly Limit (USD)</label>
                                <input type="number" id="global-hour-limit" class="setting-input" step="1" value="10.0" />
                            </div>
                            <div class="setting-item">
                                <label>Daily Limit (USD)</label>
                                <input type="number" id="global-day-limit" class="setting-input" step="5" value="50.0" />
                            </div>
                            
                            <div class="kb-title" style="margin-top: 10px;">Execution Defaults</div>
                            <div class="setting-item">
                                <label>Deep Search Enabled</label>
                                <input type="checkbox" id="deep-search-check" checked />
                            </div>
                            
                            <button class="primary-btn" onclick="saveSettings()">Save Configuration</button>
                            
                            <div style="margin-top: auto; font-size: 10px; color: var(--text-sec); text-align: center;">
                                AI Orchestrator Client v0.0.7
                            </div>
                        </div>
                    </div>
                </div>
                <script nonce="${nonce}">
                    const vscode = acquireVsCodeApi();
                    const API_BASE_URL = "${apiBaseUrl}";
                    
                    // Tab switching logic
                    function switchTab(tabId) {
                        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                        
                        document.querySelector('.tab-btn[onclick*="' + tabId + '"]').classList.add('active');
                        document.getElementById('tab-' + tabId).classList.add('active');
                        
                        if (tabId === 'knowledge') refreshCollections();
                        if (tabId === 'settings') loadSettings();
                    }

                    const chatHistory = document.getElementById('chat-history');
                    const chatInput = document.getElementById('chat-input');
                    const sendBtn = document.getElementById('send-btn');
                    const stopBtn = document.getElementById('stop-btn');
                    const strategySelect = document.getElementById('strategy-select');
                    const modelSelect = document.getElementById('model-select');
                    const limitInput = document.getElementById('limit-input');
                    const deepSearchCheck = document.getElementById('deep-search-check');

                    let currentBotMessage = null;
                    let pendingFiles = [];
                    let GLOBAL_TASK_LIMIT = null;

                    // Knowledge management
                    async function refreshCollections() {
                        const listDiv = document.getElementById('collection-list');
                        listDiv.innerHTML = '<div style="font-size: 10px; color: var(--text-sec);">Loading...</div>';
                        try {
                            const res = await fetch(API_BASE_URL + '/knowledge/collections');
                            if (res.ok) {
                                const data = await res.json();
                                listDiv.innerHTML = '';
                                if (data.collections.length === 0) {
                                    listDiv.innerHTML = '<div style="font-size: 10px; color: var(--text-sec);">No collections found.</div>';
                                    return;
                                }
                                data.collections.forEach(col => {
                                    const item = document.createElement('div');
                                    item.className = 'collection-item';
                                    item.innerHTML = '<span>' + col.name + '</span> <span class="col-stats">' + col.count + ' docs</span>';
                                    listDiv.appendChild(item);
                                });
                            } else {
                                listDiv.innerHTML = '<div style="color: var(--vscode-errorForeground);">Backend not reachable.</div>';
                            }
                        } catch (e) { listDiv.innerHTML = '<div style="color: var(--vscode-errorForeground);">Error loading collections.</div>'; }
                    }

                    function executeIngest() {
                        const type = document.getElementById('ingest-type').value;
                        const path = document.getElementById('ingest-path').value;
                        const collection = document.getElementById('ingest-collection').value;
                        
                        if (!path) {
                            vscode.postMessage({ type: 'onError', value: 'Path is required for ingestion.' });
                            return;
                        }
                        
                        vscode.postMessage({ 
                            type: 'onIngest', 
                            value: { type, path, collection } 
                        });
                    }

                    // Settings management
                    async function loadSettings() {
                        try {
                            const res = await fetch(API_BASE_URL + '/admin/config/limits');
                            if (res.ok) {
                                const json = await res.json();
                                const data = json.data;
                                const taskBudget = data.global?.per_task_budget || 0.25;
                                
                                document.getElementById('global-task-limit').value = taskBudget;
                                document.getElementById('global-hour-limit').value = data.global?.per_hour_budget || 1.0;
                                document.getElementById('global-day-limit').value = data.global?.per_day_budget || 2.0;
                                deepSearchCheck.checked = data.global?.deep_search ?? true;

                                GLOBAL_TASK_LIMIT = taskBudget;
                                const limitInp = document.getElementById('limit-input');
                                limitInp.placeholder = 'Max ' + taskBudget;
                                limitInp.max = taskBudget;
                            }
                        } catch (e) { console.error("Could not load settings"); }
                    }

                    function saveSettings() {
                        const taskLimit = parseFloat(document.getElementById('global-task-limit').value);
                        const hourLimit = parseFloat(document.getElementById('global-hour-limit').value);
                        const dayLimit = parseFloat(document.getElementById('global-day-limit').value);
                        
                        vscode.postMessage({ 
                            type: 'onUpdateConfig', 
                            configName: 'limits',
                            value: {
                                global: {
                                    per_task_budget: taskLimit,
                                    per_hour_budget: hourLimit,
                                    per_day_budget: dayLimit,
                                    deep_search: deepSearchCheck.checked,
                                    temperature: 0.0,
                                    max_retries: 3,
                                    max_feedback_iterations: 3
                                },
                                budgets: { max_input_tokens: 6000, max_output_tokens: 1000 },
                                concurrency: { max_workers: 2 },
                                retrieval: { chunk_chars: 800, chunk_overlap: 120, top_k: 4 }
                            }
                        });
                    }

                    // Load models from API on startup
                    async function loadModels() {
                        try {
                            const controller = new AbortController();
                            const timeoutId = setTimeout(() => controller.abort(), 2000);
                            const res = await fetch(API_BASE_URL + '/admin/models', { signal: controller.signal });
                            clearTimeout(timeoutId);
                            
                            if (res.ok) {
                                const data = await res.json();
                                if (data.models && data.models.length > 0) {
                                    modelSelect.innerHTML = '';
                                    data.models.forEach(m => {
                                        const opt = document.createElement('option');
                                        opt.value = m;
                                        const priceInfo = data.pricing && data.pricing[m] 
                                            ? ' ($' + data.pricing[m].input_per_million + '/$' + data.pricing[m].output_per_million + ')' 
                                            : '';
                                        opt.text = m + priceInfo;
                                        if (m === 'gpt-4o') opt.selected = true;
                                        modelSelect.appendChild(opt);
                                    });
                                }
                            }
                        } catch (e) { console.log('Using default models'); }
                    }
                    loadModels();
                    loadSettings();

                    function createBotMessageContainer() {
                        const msgDiv = document.createElement('div');
                        msgDiv.className = 'message bot';
                        
                        const stepsDiv = document.createElement('div');
                        stepsDiv.className = 'steps-container';
                        msgDiv.appendChild(stepsDiv);
                        
                        const contentDiv = document.createElement('div');
                        contentDiv.className = 'response-content';
                        contentDiv.style.display = 'none';
                        msgDiv.appendChild(contentDiv);
                        
                        const actionsDiv = document.createElement('div');
                        actionsDiv.className = 'review-actions';
                        actionsDiv.style.display = 'none';
                        msgDiv.appendChild(actionsDiv);

                        chatHistory.appendChild(msgDiv);
                        chatHistory.scrollTop = chatHistory.scrollHeight;
                        return { container: msgDiv, steps: stepsDiv, content: contentDiv, actions: actionsDiv };
                    }

                    function addStep(text, type = 'thinking') {
                        if (!currentBotMessage) {
                            currentBotMessage = createBotMessageContainer();
                        }
                        
                        const stepItem = document.createElement('div');
                        stepItem.className = 'step-item ' + type;
                        
                        let icon = '●';
                        if (type === 'thinking') icon = '💭';
                        if (type === 'analyzing') icon = '🔍';
                        if (type === 'editing') icon = '📝';
                        if (type === 'done') icon = '✅';
                        
                        stepItem.innerHTML = '<span class="icon">' + icon + '</span> <span>' + text + '</span>';
                        currentBotMessage.steps.appendChild(stepItem);
                        chatHistory.scrollTop = chatHistory.scrollHeight;
                    }

                    function appendToResponse(text) {
                        if (!currentBotMessage) {
                            currentBotMessage = createBotMessageContainer();
                        }
                        currentBotMessage.content.style.display = 'block';
                        currentBotMessage.content.textContent += text;
                        chatHistory.scrollTop = chatHistory.scrollHeight;
                    }

                    function showReviewButton(files) {
                        if (!currentBotMessage) return;
                        pendingFiles = files;
                        currentBotMessage.actions.style.display = 'flex';
                        currentBotMessage.actions.innerHTML = '<button class="review-btn" onclick="reviewChanges()">🔎 Review ' + files.length + ' Changes</button>';
                        chatHistory.scrollTop = chatHistory.scrollHeight;
                    }

                    window.reviewChanges = () => {
                        vscode.postMessage({ type: 'onReviewChanges', value: pendingFiles });
                    };

                    function addMessage(text, sender) {
                        if (sender === 'user') {
                            const div = document.createElement('div');
                            div.className = 'message user';
                            div.textContent = text;
                            chatHistory.appendChild(div);
                            currentBotMessage = null;
                        } else {
                            appendToResponse(text);
                        }
                        chatHistory.scrollTop = chatHistory.scrollHeight;
                    }


                    function setRunning(isRunning) {
                        if (isRunning) {
                            sendBtn.style.display = 'none';
                            stopBtn.style.display = 'block';
                            chatInput.disabled = true;
                        } else {
                            sendBtn.style.display = 'block';
                            stopBtn.style.display = 'none';
                            chatInput.disabled = false;
                            chatInput.focus();
                        }
                    }

                    sendBtn.addEventListener('click', () => {
                        const text = chatInput.value;
                        const localLimit = limitInput.value ? parseFloat(limitInput.value) : null;
                        
                        if (localLimit && GLOBAL_TASK_LIMIT && localLimit > GLOBAL_TASK_LIMIT) {
                            vscode.postMessage({ type: 'onError', value: 'Local budget ($' + localLimit + ') cannot exceed global limit ($' + GLOBAL_TASK_LIMIT + ').' });
                            return;
                        }

                        if (text) {
                            addMessage(text, 'user');
                            vscode.postMessage({ 
                                type: 'onCommand', 
                                value: text,
                                options: { 
                                    strategy: strategySelect.value, 
                                    model: modelSelect.value,
                                    localLimit: limitInput.value ? parseFloat(limitInput.value) : null,
                                    deepSearch: deepSearchCheck.checked
                                }
                            });
                            chatInput.value = '';
                            setRunning(true);
                        }
                    });

                    stopBtn.addEventListener('click', () => {
                        vscode.postMessage({ type: 'onStop' });
                        addStep("Stopping task...", "thinking");
                    });

                    chatInput.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            if (sendBtn.style.display !== 'none') sendBtn.click();
                        }
                    });

                    window.addEventListener('message', event => {
                        const message = event.data;
                        switch (message.type) {
                            case 'addResponse':
                                appendToResponse(message.value);
                                break;
                            case 'setRunning':
                                setRunning(message.value);
                                if (!message.value) addStep("Done", "done");
                                break;
                            case 'setPath':
                                if (message.target === 'ingest-path') {
                                    document.getElementById('ingest-path').value = message.value;
                                } else if (message.target === 'context') {
                                    vscode.postMessage({ type: 'onInfo', value: 'File added to task context.' });
                                }
                                break;
                            case 'appendResponse':
                                const raw = message.value;
                                if (raw.startsWith(':::STEP:')) {
                                    try {
                                        const stepData = JSON.parse(raw.replace(':::STEP:', '').replace(':::',''));
                                        addStep(stepData.text, stepData.type);
                                    } catch(e) { appendToResponse(raw); }
                                } else if (raw.includes(':::FILES:')) {
                                     try {
                                         const parts = raw.split(':::FILES:');
                                         const files = JSON.parse(parts[1].replace(':::',''));
                                         showReviewButton(files);
                                     } catch(e) { appendToResponse(raw); }
                                } else if (raw.includes('[INFO]') || raw.includes('[Error]')) {
                                   if (raw.includes('Executing phase')) addStep(raw.split('- INFO - ')[1] || raw, 'analyzing');
                                   else if (raw.includes('Starting phase')) addStep(raw.split('- INFO - ')[1] || raw, 'thinking');
                                   else if (raw.includes('Quality score')) addStep(raw.split('- INFO - ')[1] || raw, 'thinking');
                                   else if (raw.includes('[Error]')) {
                                       const errDiv = document.createElement('div');
                                       errDiv.className = 'error-box';
                                       errDiv.textContent = raw;
                                       currentBotMessage?.container.appendChild(errDiv);
                                   }
                                   else appendToResponse(raw);
                                } else {
                                    appendToResponse(raw);
                                }
                                break;
                        }
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
            const response = await fetch('http://localhost:8000/admin/ingest/execute', {
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
            if (options.strategy) {
                args.push('--strategy');
                args.push(options.strategy);
            }
            if (options.model) {
                args.push('--model');
                args.push(options.model);
            }
            if (options.localLimit) {
                args.push('--local-limit');
                args.push(options.localLimit.toString());
            }
            if (options.deepSearch) {
                args.push('--deep-search');
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