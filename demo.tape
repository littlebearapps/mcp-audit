# VHS Demo Tape for token-audit v1.0.3
# TUI-only demo, ~15 seconds, 3-4s per view

Output docs/images/demo.gif

Set Shell bash
Set FontSize 14
Set Width 1000
Set Height 580
Set Padding 15
Set Theme "Catppuccin Mocha"
Set TypingSpeed 30ms
Set PlaybackSpeed 1.0
Set Framerate 60
Set CursorBlink false

# Setup environment silently and launch TUI directly
Hide
Type "cd /Users/nathanschram/claude-code-tools/lba/apps/devtools/token-audit/main"
Enter
Type "source .venv/bin/activate"
Enter
Type "export TOKEN_AUDIT_THEME=dark"
Enter
Type "token-audit ui"
Enter
Sleep 500ms
Show

# 1. Dashboard view (starts here) - 3.5s
Sleep 3500ms

# 2. Sessions view - 3.5s
Type "2"
Sleep 3500ms

# 3. Recommendations view - 3.5s
Type "3"
Sleep 3500ms

# 4. Analytics view - 3.5s
Type "5"
Sleep 3500ms

# 5. Back to Dashboard for clean loop - 1s
Type "1"
Sleep 1000ms

# Quit
Type "q"
