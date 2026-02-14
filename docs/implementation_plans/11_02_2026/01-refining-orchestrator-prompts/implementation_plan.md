# Implementation Plan: Fix Anthropic Model 404 Error

## Problem Description

The AI Code Orchestrator is configured to use `claude-3-5-sonnet-latest` for the analyst, architect, and review phases. However, Anthropic's API is returning a **404 error** with the message:

```
Error code: 404 - {'type': 'error', 'error': {'type': 'not_found_error', 'message': 'model: claude-3-5-sonnet-latest'}}
```

This indicates that either:
1. The model ID `claude-3-5-sonnet-latest` is not recognized by Anthropic
2. The API key doesn't have access to this model
3. The alias `latest` is not supported in the current API version

## Investigation Steps

### 1. Check Anthropic Model Naming Convention

According to Anthropic's documentation, Claude 3.5 Sonnet models use versioned identifiers like:
- `claude-3-5-sonnet-20241022` (specific version)
- `claude-3-5-sonnet-20240620` (older version)

The `-latest` suffix may not be supported.

### 2. Verify API Key Access

Test the API key with a known working model ID to confirm it has proper permissions.

## Proposed Solution

### Option 1: Use Specific Version (User Provided)

Update all configuration files to use the specific version provided by the user:

**Model ID:** `claude-sonnet-4-5-20250929`

## Proposed Changes

### [MODIFY] [model_mapping.yaml](file:///c:/Users/mgasic/Documents/AIProjects/ai-code-orchestrator/config/model_mapping.yaml)

Replace all instances of `claude-3-5-sonnet-latest` (or `gpt-4o` fallback) with `claude-sonnet-4-5-20250929`:

```yaml
routing:
  phase:
    analyst:
      model: claude-sonnet-4-5-20250929
      provider: anthropic
    architect:
      model: claude-sonnet-4-5-20250929
      provider: anthropic
```

### [MODIFY] [model_mapping_v2.yaml](file:///c:/Users/mgasic/Documents/AIProjects/ai-code-orchestrator/config/model_mapping_v2.yaml)

Apply the same changes to the v2 configuration file.

## Verification Plan

### 1. Configuration Update
- Update both YAML files with the custom model ID

### 2. Server Restart
- Manually restart uvicorn server to ensure changes are applied

### 3. API Test
- Submit a test query: "Koliko komponenti imamo?"
- Verify `Analyst` phase correctly processes the request (fixing the protocol mismatch issue)

## Rollback Plan

If the specific version also fails:
1. Test with `claude-3-opus-20240229`
2. If Anthropic models are completely inaccessible, switch to `gpt-4o` for all phases
3. Document the API key limitation for future reference

## Next Steps

1. **Immediate:** Update configuration files with `claude-3-5-sonnet-20241022`
2. **Test:** Restart server and verify functionality
3. **Monitor:** Check logs for any remaining errors
4. **Document:** Record the working model ID for future deployments
