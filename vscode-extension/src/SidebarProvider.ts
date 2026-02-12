import * as vscode from "vscode";
import * as cp from "child_process";
import * as fs from "fs";
import * as path from "path";

export class SidebarProvider implements vscode.WebviewViewProvider {
    _view?: vscode.WebviewView;
    _doc?: vscode.TextDocument;

    constructor(private readonly _extensionUri: vscode.Uri) { }

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ) {
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
                    this.runPythonTask(data.value);
                    break;
                }
                case "onInfo": {
                    if (!data.value) {
                        return;
                    }
                    vscode.window.showInformationMessage(data.value);
                    break;
                }
                case "onError": {
                    if (!data.value) {
                        return;
                    }
                    vscode.window.showErrorMessage(data.value);
                    break;
                }
            }
        });
    }

    public revive(panel: vscode.WebviewView) {
        this._view = panel;
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        const styleResetUri = webview.asWebviewUri(
            vscode.Uri.joinPath(this._extensionUri, "media", "reset.css")
        );
        const styleVSCodeUri = webview.asWebviewUri(
            vscode.Uri.joinPath(this._extensionUri, "media", "vscode.css")
        );
        const scriptUri = webview.asWebviewUri(
            vscode.Uri.joinPath(this._extensionUri, "media", "main.js")
        );
        // Use a nonce to only allow a specific script to be run.
        const nonce = getNonce();

        return `<!DOCTYPE html>
			<html lang="en">
			<head>
				<meta charset="UTF-8">
				<!--
					Use a content security policy to only allow loading images from https or from our extension directory,
					and only allow scripts that have a specific nonce.
				-->
                <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
				<meta name="viewport" content="width=device-width, initial-scale=1.0">
				<title>AI Orchestrator Chat</title>
                <style>
                    body {
                        padding: 0;
                        margin: 0;
                        font-family: var(--vscode-font-family);
                    }
                    .chat-container {
                        display: flex;
                        flex-direction: column;
                        height: 100vh;
                        max-height: 100vh;
                        overflow: hidden;
                    }
                    .chat-history {
                        flex: 1;
                        overflow-y: auto;
                        padding: 10px;
                        display: flex;
                        flex-direction: column;
                        gap: 10px;
                    }
                    .chat-input-area {
                        padding: 10px;
                        background: var(--vscode-editor-background);
                        border-top: 1px solid var(--vscode-widget-border);
                        display: flex;
                        gap: 5px;
                    }
                    textarea {
                        flex: 1;
                        background: var(--vscode-input-background);
                        color: var(--vscode-input-foreground);
                        border: 1px solid var(--vscode-input-border);
                        padding: 5px;
                        resize: none;
                        height: 40px;
                        font-family: inherit;
                    }
                    textarea:focus {
                        outline: none;
                        border-color: var(--vscode-focusBorder);
                    }
                    button {
                        background: var(--vscode-button-background);
                        color: var(--vscode-button-foreground);
                        border: none;
                        padding: 5px 10px;
                        cursor: pointer;
                    }
                    button:hover {
                        background: var(--vscode-button-hoverBackground);
                    }
                    .message {
                        padding: 8px 12px;
                        border-radius: 6px;
                        max-width: 85%;
                        word-wrap: break-word;
                        white-space: pre-wrap;
                        font-family: var(--vscode-editor-font-family);
                    }
                    .message.user {
                        align-self: flex-end;
                        background: var(--vscode-button-background);
                        color: var(--vscode-button-foreground);
                    }
                    .message.bot {
                        align-self: flex-start;
                        background: var(--vscode-editor-inactiveSelectionBackground);
                        color: var(--vscode-editor-foreground);
                        border: 1px solid var(--vscode-widget-border);
                    }
                    .context-badge {
                        display: inline-block;
                        font-size: 0.8em;
                        padding: 2px 6px;
                        border-radius: 4px;
                        background: var(--vscode-badge-background);
                        color: var(--vscode-badge-foreground);
                        margin-bottom: 5px;
                    }
                </style>
			</head>
			<body>
                <div class="chat-container">
                    <div id="chat-history" class="chat-history">
                        <div class="message bot">Hello! I am your AI Orchestrator. How can I help you?</div>
                    </div>
                    <div class="chat-input-area">
                        <textarea id="chat-input" placeholder="Type your instruction or question..."></textarea>
                        <button id="send-btn">Send</button>
                    </div>
                </div>
                <script nonce="${nonce}">
                    const vscode = acquireVsCodeApi();
                    const chatHistory = document.getElementById('chat-history');
                    const chatInput = document.getElementById('chat-input');
                    const sendBtn = document.getElementById('send-btn');

                    function addMessage(text, sender) {
                        const div = document.createElement('div');
                        div.className = 'message ' + sender;
                        div.textContent = text;
                        chatHistory.appendChild(div);
                        chatHistory.scrollTop = chatHistory.scrollHeight;
                    }

                    sendBtn.addEventListener('click', () => {
                        const text = chatInput.value;
                        if (text) {
                            addMessage(text, 'user');
                            vscode.postMessage({ type: 'onCommand', value: text });
                            chatInput.value = '';
                        }
                    });

                    chatInput.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            sendBtn.click();
                        }
                    });

                    window.addEventListener('message', event => {
                        const message = event.data;
                        switch (message.type) {
                            case 'addResponse':
                                addMessage(message.value, 'bot');
                                break;
                            case 'appendResponse':
                                // Find last bot message or create new
                                let lastMsg = chatHistory.lastElementChild;
                                if (!lastMsg || !lastMsg.classList.contains('bot')) {
                                    addMessage(message.value, 'bot');
                                } else {
                                    lastMsg.textContent += message.value;
                                    chatHistory.scrollTop = chatHistory.scrollHeight;
                                }
                                break;
                        }
                    });
                </script>
			</body>
			</html>`;
    }

    // --- Logic for running tasks ---

    public contextFiles: Set<string> = new Set();
    public statusBarItem: vscode.StatusBarItem | undefined;

    public addContext(filePath: string) {
        this.contextFiles.add(filePath);
        this._view?.webview.postMessage({ type: 'addResponse', value: `Added to context: ${path.basename(filePath)}` });
        this.updateStatusBar();
    }

    public clearContext() {
        this.contextFiles.clear();
        this._view?.webview.postMessage({ type: 'addResponse', value: `Context cleared.` });
        this.updateStatusBar();
    }

    public updateStatusBar() {
        if (this.statusBarItem) {
            if (this.contextFiles.size > 0) {
                this.statusBarItem.text = `$(list-flat) AI Context: ${this.contextFiles.size}`;
                this.statusBarItem.show();
            } else {
                this.statusBarItem.hide();
            }
        }
    }

    private async runPythonTask(prompt: string) {
        if (!this._view) {
            vscode.window.showErrorMessage("Webview not initialized");
            return;
        }

        this._view.webview.postMessage({ type: 'addResponse', value: "Thinking..." });

        // Get Configuration
        const config = vscode.workspace.getConfiguration('aiOrchestrator');
        const pythonPath = config.get<string>('pythonPath') || 'python';
        let projectRoot = config.get<string>('projectRoot');

        if (!projectRoot) {
            if (vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders.length > 0) {
                projectRoot = vscode.workspace.workspaceFolders[0].uri.fsPath;
            } else {
                this._view.webview.postMessage({ type: 'addResponse', value: "Error: No workspace open or projectRoot configured." });
                return;
            }
        }

        // Auto-detect venv if config is default 'python'
        let finalPythonPath = pythonPath;
        if (finalPythonPath === 'python' || finalPythonPath === 'python3') {
            // Check for Windows venv
            const possibleVenvWin = path.join(projectRoot, '.venv', 'Scripts', 'python.exe');
            // Check for Unix venv
            const possibleVenvUnix = path.join(projectRoot, '.venv', 'bin', 'python');

            if (fs.existsSync(possibleVenvWin)) {
                finalPythonPath = possibleVenvWin;
            } else if (fs.existsSync(possibleVenvUnix)) {
                finalPythonPath = possibleVenvUnix;
            }
        }

        const scriptPath = path.join(projectRoot, 'scripts', 'run_task.py');

        if (!fs.existsSync(scriptPath)) {
            this._view.webview.postMessage({ type: 'addResponse', value: `Error: Script not found at: ${scriptPath}` });
            return;
        }

        // Build Arguments
        // Add -u for unbuffered output so we get streaming responses
        let args = ['-u', scriptPath, prompt];
        this.contextFiles.forEach(file => {
            args.push('--context');
            args.push(file);
        });

        const process = cp.spawn(finalPythonPath, args, { cwd: projectRoot });

        process.stdout.on('data', (data) => {
            // Send output to chat
            this._view?.webview.postMessage({ type: 'appendResponse', value: data.toString() });
        });

        process.stderr.on('data', (data) => {
            this._view?.webview.postMessage({ type: 'appendResponse', value: `[Error]: ${data.toString()}` });
        });

        process.on('close', (code) => {
            if (code === 0) {
                this._view?.webview.postMessage({ type: 'addResponse', value: `\n[Task Completed]` });
            } else {
                this._view?.webview.postMessage({ type: 'addResponse', value: `\n[Task Failed with code ${code}]` });
            }
        });

    }
}

function getNonce() {
    let text = "";
    const possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
