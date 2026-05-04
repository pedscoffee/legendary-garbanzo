# QUICK START GUIDE
## Pediatric Charting Tool

### Installation (5 minutes)

**Windows:**
1. Double-click `setup.bat`
2. Double-click `run_app.bat` to start

**Mac/Linux:**
1. Open Terminal in this folder
2. Run: `bash setup.sh`
3. Run: `python3 peds_charting_tool.py`

### First Use

1. **Launch the app** (run_app.bat or python3 peds_charting_tool.py)
2. **Try a quick button**: Click "URI" 
3. **Watch the magic**: Expanded text appears and auto-copies
4. **Paste anywhere**: Ctrl+V (or Cmd+V on Mac)

### Daily Workflow

```
Type shorthand → Wait 1.5 seconds → Auto-copied!
        OR
Click buttons → Auto-copied!
        OR
Mix both → Edit in output → Copy Now
```

### Examples to Try

**Type these in the input box:**
- `asthma stable`
- `uri`
- `wcc`
- `adhd stable`

**Or click the buttons:**
- Asthma Stable
- URI
- WCC
- ADHD Stable

### Customize Your Templates

1. Click **"Edit Templates"** button in the app
2. File opens in text editor
3. Edit/add templates (see README.md for details)
4. Save and restart app

### Common Customizations

**Add a new condition:**
```json
"new_condition": {
  "title": "CONDITION NAME",
  "content": [
    "- First line",
    "- Second line with {placeholder}",
    "- Third line"
  ]
}
```

**Add a quick button:**
```json
{"label": "My Button", "template": "new_condition"}
```

### Tips

✓ Placeholders like `{medication}` are meant to be edited before pasting
✓ Click multiple buttons to combine conditions
✓ Auto-copy happens 1.5 seconds after you stop typing
✓ Keep templates generic - no patient info!

### Need Help?

See **README.md** for full documentation and advanced customization.

### Files Included

- `peds_charting_tool.py` - Main application
- `peds_templates.json` - Your templates (edit this!)
- `README.md` - Complete documentation
- `requirements.txt` - Python dependencies
- `setup.bat/sh` - Installation scripts
- `run_app.bat/sh` - Launch scripts

---

**You're all set!** Start by running the app and clicking a few buttons to see how it works.
