"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = require("vscode");
const path = require("path");
const SidebarProvider_1 = require("./SidebarProvider");
function activate(context) {
    console.log('AI Code Orchestrator is now active!');
    // Create the sidebar provider
    const sidebarProvider = new SidebarProvider_1.SidebarProvider(context.extensionUri);
    // Register the provider
    context.subscriptions.push(vscode.window.registerWebviewViewProvider("ai-orchestrator-sidebar", sidebarProvider));
    // Create status bar item
    sidebarProvider.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    sidebarProvider.statusBarItem.command = 'ai-orchestrator.runTask';
    context.subscriptions.push(sidebarProvider.statusBarItem);
    // Command: Add Context
    let addContextDisposable = vscode.commands.registerCommand('ai-orchestrator.addContext', (uri) => {
        if (uri && uri.fsPath) {
            sidebarProvider.addContext(uri.fsPath);
            vscode.window.showInformationMessage(`Added to context: ${path.basename(uri.fsPath)}`);
        }
        else {
            const activeEditor = vscode.window.activeTextEditor;
            if (activeEditor) {
                sidebarProvider.addContext(activeEditor.document.uri.fsPath);
                vscode.window.showInformationMessage(`Added to context: ${path.basename(activeEditor.document.uri.fsPath)}`);
            }
        }
    });
    // Command: Clear Context
    let clearContextDisposable = vscode.commands.registerCommand('ai-orchestrator.clearContext', () => {
        sidebarProvider.clearContext();
        vscode.window.showInformationMessage('Context cleared.');
    });
    // Command: Run Task (Focuses the sidebar)
    let runTaskDisposable = vscode.commands.registerCommand('ai-orchestrator.runTask', async () => {
        // Focus the sidebar view
        await vscode.commands.executeCommand('ai-orchestrator-sidebar.focus');
    });
    context.subscriptions.push(addContextDisposable);
    context.subscriptions.push(clearContextDisposable);
    context.subscriptions.push(runTaskDisposable);
}
function deactivate() { }
//# sourceMappingURL=extension.js.map