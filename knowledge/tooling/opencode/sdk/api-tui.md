---
title: "SDK TUI API"
status: draft
author: "Khalid"
date: 2026-06-07
tags:
  - opencode
  - sdk
  - javascript
  - typescript
  - api
  - tui
sources:
  - url: "https://opencode.ai/docs/sdk"
    title: "OpenCode SDK Documentation"
  - url: "https://opencode.ai/docs/server"
    title: "OpenCode Server Documentation"
last_audit_date: 2026-06-07
---

# SDK TUI API

Terminal user interface actions that programmatically control the editor UI. All methods return `boolean`.

```ts
await client.tui.appendPrompt({ body: { text: "additional context" } });
await client.tui.openHelp();
await client.tui.openSessions();
await client.tui.openThemes();
await client.tui.openModels();
await client.tui.submitPrompt();
await client.tui.clearPrompt();
await client.tui.executeCommand({ body: { command: "workbench.action.terminal.new" } });
await client.tui.showToast({
  body: { message: "Operation completed", variant: "success" },
});
```

## Methods

| Method | Description |
|---|---|
| `tui.appendPrompt({ body })` | Append text to the current prompt input (`body.text`) |
| `tui.openHelp()` | Open the help panel |
| `tui.openSessions()` | Open the session selector |
| `tui.openThemes()` | Open the theme selector |
| `tui.openModels()` | Open the model selector |
| `tui.submitPrompt()` | Submit the current prompt |
| `tui.clearPrompt()` | Clear the prompt input |
| `tui.executeCommand({ body })` | Execute a VS Code-style command (`body.command`) |
| `tui.showToast({ body })` | Show a toast notification (`body.message`, `body.variant`, `body.title?`) |
