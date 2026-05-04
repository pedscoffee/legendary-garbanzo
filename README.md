# Pediatric Clinical Charting Tool

A standalone Python application for expanding clinical shorthand into formatted Assessment & Plan notes. Designed specifically for pediatric clinicians with fully customizable templates.

## Features

- **Quick Button Interface**: POS-style buttons for common conditions
- **Shorthand Input**: Type abbreviated notes that auto-expand
- **Auto-Copy**: Automatically copies to clipboard 1.5 seconds after you stop typing
- **100% Customizable**: All templates stored in easy-to-edit JSON file
- **Fast & Offline**: No AI calls, no internet required, instant expansion
- **Pediatrics Focused**: Pre-loaded with common pediatric templates

## Installation

### Requirements
- Python 3.7 or higher
- pip (Python package installer)

### Setup Steps

1. **Install Python** (if not already installed):
   - Windows: Download from python.org
   - Mac: `brew install python3` or download from python.org
   - Linux: Usually pre-installed, or `sudo apt install python3 python3-pip`

2. **Install Required Packages**:
   ```bash
   pip install pyperclip
   ```
   
   Note: `tkinter` is usually included with Python. If you get an error, install it:
   - Ubuntu/Debian: `sudo apt-get install python3-tk`
   - Mac: Should be included with Python
   - Windows: Should be included with Python

3. **Run the Application**:
   ```bash
   python peds_charting_tool.py
   ```

## How to Use

### Quick Start
1. Launch the app
2. Click a quick button (e.g., "Asthma Stable") OR type shorthand (e.g., "asthma stable")
3. The expanded text appears in the output box
4. Text is auto-copied to clipboard after 1.5 seconds of no typing
5. Paste into your EHR!

### Interface Overview

```
┌─────────────────────────────────────────────┐
│  QUICK BUTTONS (Click to add)              │
│  [Asthma Stable] [URI] [WCC] [ADHD]...     │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  SHORTHAND INPUT                            │
│  Type: "asthma stable" or "uri"             │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  EXPANDED OUTPUT                            │
│  (Auto-copies after 1.5s pause)             │
│                                             │
│  ASTHMA                                     │
│  - Well-controlled on current regimen       │
│  - Continue albuterol PRN...                │
└─────────────────────────────────────────────┘
```

### Workflow Examples

**Example 1: Quick Button**
1. Click "Asthma Stable"
2. Text appears and auto-copies
3. Edit any `{placeholders}` directly in the output before pasting

**Example 2: Shorthand Typing**
1. Type: "uri"
2. Wait 1.5 seconds (or click "Process Now")
3. Auto-expands to full URI template
4. Auto-copies to clipboard

**Example 3: Multiple Conditions**
1. Click "Asthma Stable"
2. Click "Eczema"
3. Both appear in output, separated by blank lines
4. Click "Copy Now" or wait for auto-copy

## Customization Guide

### Easy Way: Edit Templates Button
1. Click "Edit Templates" button in the app
2. JSON file opens in your default text editor
3. Make changes (see below)
4. Save and restart the app

### Manual Way: Edit JSON File
Open `peds_templates.json` in any text editor.

### Template Structure

```json
{
  "templates": {
    "template_key": {
      "title": "CONDITION NAME",
      "content": [
        "- First line of note",
        "- Second line with {placeholder}",
        "- Third line"
      ]
    }
  },
  "quick_buttons": [
    {"label": "Button Text", "template": "template_key"}
  ],
  "patterns": [
    {
      "pattern": "shorthand regex",
      "template": "template_key",
      "defaults": {"placeholder": "default value"}
    }
  ]
}
```

### Adding a New Template

**Step 1: Add to templates section**
```json
"newborn_jaundice": {
  "title": "NEONATAL JAUNDICE",
  "content": [
    "- Jaundice noted at {age}",
    "- Bilirubin: {bilirubin_level}",
    "- Feeding: {feeding_status}",
    "- {treatment}",
    "- Recheck bilirubin in {timeframe}"
  ]
}
```

**Step 2: Add quick button (optional)**
```json
{"label": "Jaundice", "template": "newborn_jaundice"}
```

**Step 3: Add pattern for shorthand (optional)**
```json
{
  "pattern": "jaundice|hyperbili",
  "template": "newborn_jaundice",
  "defaults": {
    "age": "day 3 of life",
    "treatment": "phototherapy initiated"
  }
}
```

### Modifying Existing Templates

Simply edit the content array:
```json
"asthma_stable": {
  "title": "ASTHMA",
  "content": [
    "- Well-controlled on current regimen",
    "- Peak flow: {peak_flow}",  ← Add this line
    "- Continue {medication} as prescribed"
  ]
}
```

### Placeholder Best Practices

- Use `{descriptive_name}` for values you'll fill in manually
- Common placeholders: `{medication}`, `{dose}`, `{timeframe}`, `{symptoms}`
- You can edit placeholders directly in the output before pasting

### Pattern Matching

Patterns use regular expressions. Common patterns:
- `"asthma"` - matches the word "asthma"
- `"asthma\\s+stable"` - matches "asthma stable" (\\s+ means one or more spaces)
- `"ear\\s+infection|otitis"` - matches "ear infection" OR "otitis"
- Case-insensitive by default

## Tips & Tricks

### Speed Tips
1. **Learn keyboard shortcuts**: Type shorthand faster than clicking
2. **Chain multiple conditions**: Click multiple buttons before pasting
3. **Use the auto-copy**: Just wait 1.5s instead of clicking "Copy Now"

### Customization Tips
1. **Start small**: Add 2-3 templates at a time
2. **Copy existing templates**: Duplicate and modify similar conditions
3. **Keep it simple**: Don't overthink placeholders - you can edit output before pasting
4. **Use meaningful keys**: Name template keys clearly (e.g., `adhd_titration` not `adhd2`)

### Clinical Workflow
1. **Morning prep**: Open the app at start of day
2. **During visit**: Click buttons or type shorthand as you go
3. **Copy-paste**: Drop expanded text into EHR
4. **Refine**: Edit placeholders in EHR as needed
5. **Evening review**: Add any new templates you wished you had

## Pre-loaded Templates

### Current Templates
- Asthma (stable and exacerbation)
- URI
- ADHD (stable and medication adjustment)
- Well Child Check
- GERD
- Constipation
- Eczema/Atopic Dermatitis
- Obesity
- Acute Otitis Media
- Pharyngitis
- Headache
- Anxiety
- Depression

### Expanding Your Library

Consider adding templates for:
- **Common diagnoses**: Your top 10 most frequent conditions
- **Chronic disease follow-up**: Diabetes, seizures, etc.
- **Medication refills**: Standard refill notes
- **Referrals**: Common referral templates
- **Procedures**: Documentation for I&D, laceration repair, etc.
- **Negative visits**: "Normal exam, reassurance provided"

## Troubleshooting

### App won't start
- Check Python is installed: `python --version`
- Install pyperclip: `pip install pyperclip`
- Check for typos in peds_templates.json (use a JSON validator)

### Templates not appearing
- Restart the app after editing JSON
- Check JSON syntax (commas, brackets, quotes)
- Look for error messages in terminal

### Auto-copy not working
- Make sure you have pyperclip installed
- On Linux, you may need: `sudo apt-get install xclip` or `xsel`
- You can always click "Copy Now" manually

### Button not showing
- Check that template key in quick_buttons matches template key in templates
- Restart app after adding buttons

## Advanced Customization

### Changing Auto-Copy Delay
In the code, find this line:
```python
self.auto_copy_delay = 1500  # milliseconds
```
Change to 2000 for 2 seconds, etc.

### Adding More Buttons Per Row
In the code, find:
```python
row = idx // 5  # 5 buttons per row
col = idx % 5
```
Change 5 to your preferred number.

### Changing Window Size
In the code:
```python
self.root.geometry("900x700")  # width x height
```

## Privacy & Security

- **100% Local**: No internet connection required
- **No logging**: Nothing is saved except your templates
- **HIPAA consideration**: No PHI in templates - use placeholders instead
- **Keep it generic**: Templates should be condition-based, not patient-specific

## Support & Contributions

This is a standalone tool - feel free to:
- Modify the code for your needs
- Share templates with colleagues
- Create specialty-specific versions
- Adapt for other medical specialties

## License

Free to use and modify for clinical practice.

## Quick Reference Card

### Common Shortcuts
- **Type → Wait → Auto-copy**: Main workflow
- **Click button → Auto-copy**: Fastest for common conditions
- **Edit Templates button**: Quick access to customization
- **Clear All**: Reset and start fresh

### Template Formula
```
Template Key → Button Label → Pattern → Expanded Text
```

### JSON Editing Checklist
- [ ] Commas after each item (except last in section)
- [ ] Matching quotes and brackets
- [ ] Valid template keys referenced in buttons/patterns
- [ ] Saved file before restarting app

---

**Happy Charting!** 🏥📝
