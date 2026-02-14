# Fix Extension Compatibility

The user is encountering an error when installing the extension: `Error: Unable to install extension 'ai-orchestrator.ai-code-orchestrator-client' as it is not compatible with the IDE '1.107.0'.`  This is likely because the `.vsix` package was built with an older `package.json` configuration that required a newer VS Code version.

## User Review Required
None. This is a fix for a reported issue.

## Proposed Changes
### VS Code Extension
#### [MODIFY] [package.json](file:///c:/Users/mgasic/Documents/AIProjects/ai-code-orchestrator/vscode-extension/package.json)
- Verify `engines.vscode` is set to `^1.90.0` or compatible version.
- Ensure `activationEvents` does not contain redundant entries.

## Verification Plan
### Automated Tests
- Run `npm run compile` to ensure the project builds without errors.

### Manual Verification
- Generate a new `.vsix` package using `npx vsce package`.
- Verify the `package.json` inside the VSIX (by inspecting it or just reinstalling).
- Ask user to retry installation.
