# Token Audit v1.0.3 TUI Demo
# Showcases: All 3 platforms (Claude Code, Codex CLI, Gemini CLI)
# Themes: Latte (light) first half, Mocha (dark) second half

Output docs/images/demo.gif
Set FontSize 14
Set Width 1200
Set Height 800
Set TypingSpeed 50ms
Set Theme "Catppuccin Latte"

# Launch TUI
Type "token-audit ui"
Enter
Sleep 2500ms

# Dashboard shows all platforms
Sleep 1500ms

# Sessions view - all platforms
Type "2"
Sleep 2000ms

# Cycle to Claude Code filter
Type "f"
Sleep 1500ms

# Cycle to Codex CLI filter
Type "f"
Sleep 1500ms

# Analytics view (showing Codex)
Type "5"
Sleep 2000ms

# Theme toggle to dark (Mocha)
Type "t"
Sleep 1000ms

# Cycle to Gemini CLI filter
Type "f"
Sleep 1500ms

# Smell Trends view (Gemini)
Type "6"
Sleep 2000ms

# Cycle back to All platforms
Type "f"
Sleep 1000ms

# Recommendations view (all platforms)
Type "3"
Sleep 2000ms

# Export modal
Type "e"
Sleep 1500ms
Escape
Sleep 500ms

# Return to dashboard for clean loop
Type "1"
Sleep 1500ms
