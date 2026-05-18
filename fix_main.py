from pathlib import Path

p = Path('main.py')
t = p.read_text(encoding='utf-8')

# Find and replace the line with the problematic emoji
lines = t.split('\n')
new_lines = []
changed = False
for i, line in enumerate(lines):
    if 'if stripped.startswith' in line and '📄' in line and len(line) > 50:
        # This is the problematic cached result line
        new_lines.append('        if "📄" in stripped:')
        changed = True
    else:
        new_lines.append(line)

new_text = '\n'.join(new_lines)
if changed:
    p.write_text(new_text, encoding='utf-8')
    print("✅ REPLACED problematic line")
else:
    print("⚠️ Could not find the exact problematic line to replace")

