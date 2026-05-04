#!/usr/bin/env python3
"""
Pediatric Clinical Charting Tool
A standalone app for expanding clinical shorthand into formatted A&P notes
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import re
import pyperclip
from pathlib import Path
from typing import Dict, List, Tuple


class PedsChartingTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Pediatric Charting Tool")
        self.root.geometry("900x700")
        
        # Load templates
        self.templates_file = Path("peds_templates.json")
        self.load_templates()
        
        # Typing timer for auto-copy
        self.typing_timer = None
        self.auto_copy_delay = 1500  # 1.5 seconds
        
        # Current note components
        self.note_components = []
        
        self.setup_ui()
        
    def load_templates(self):
        """Load templates from JSON file"""
        if self.templates_file.exists():
            with open(self.templates_file, 'r') as f:
                data = json.load(f)
                self.templates = data.get('templates', {})
                self.quick_buttons = data.get('quick_buttons', [])
                self.patterns = data.get('patterns', [])
        else:
            # Create default templates
            self.create_default_templates()
            
    def create_default_templates(self):
        """Create default pediatric templates"""
        self.templates = {
            "asthma_stable": {
                "title": "ASTHMA",
                "content": [
                    "- Well-controlled on current regimen",
                    "- No recent exacerbations",
                    "- Continue {medication} as prescribed",
                    "- Patient/family educated on trigger avoidance",
                    "- Follow up in {timeframe}"
                ]
            },
            "asthma_exacerbation": {
                "title": "ASTHMA EXACERBATION",
                "content": [
                    "- Acute exacerbation with {symptoms}",
                    "- Increased albuterol use to {frequency}",
                    "- Started oral prednisone {dose} for {duration}",
                    "- Reviewed inhaler technique with family",
                    "- Close follow-up in {timeframe} or sooner if worsening"
                ]
            },
            "uri": {
                "title": "UPPER RESPIRATORY INFECTION",
                "content": [
                    "- Viral URI symptoms: {symptoms}",
                    "- No signs of bacterial superinfection",
                    "- Supportive care: hydration, rest, saline rinses",
                    "- Symptomatic relief with {medication} as needed",
                    "- Return if fever >3 days, worsening symptoms, or difficulty breathing"
                ]
            },
            "adhd_stable": {
                "title": "ADHD",
                "content": [
                    "- Symptoms well-controlled on {medication} {dose}",
                    "- No significant side effects reported",
                    "- School performance: {performance}",
                    "- Continue current medication",
                    "- Follow up in {timeframe} with Vanderbilt scales"
                ]
            },
            "adhd_titration": {
                "title": "ADHD - MEDICATION ADJUSTMENT",
                "content": [
                    "- Suboptimal symptom control on current dose",
                    "- Increasing {medication} from {old_dose} to {new_dose}",
                    "- Monitor for side effects: appetite, sleep, mood",
                    "- Teacher Vanderbilt to be completed",
                    "- Follow up in {timeframe} to assess response"
                ]
            },
            "wcc": {
                "title": "WELL CHILD CHECK",
                "content": [
                    "- Age-appropriate growth and development",
                    "- Height: {height_percentile}, Weight: {weight_percentile}",
                    "- Immunizations: {immunizations}",
                    "- Anticipatory guidance provided",
                    "- Next WCC at {next_visit}"
                ]
            },
            "gerd": {
                "title": "GASTROESOPHAGEAL REFLUX",
                "content": [
                    "- Reflux symptoms: {symptoms}",
                    "- {medication} {dose} {frequency}",
                    "- Dietary modifications discussed",
                    "- Positional changes recommended",
                    "- Follow up in {timeframe} to assess response"
                ]
            },
            "constipation": {
                "title": "CONSTIPATION",
                "content": [
                    "- Functional constipation",
                    "- Bowel movements: {frequency}",
                    "- Started {medication} {dose}",
                    "- Increase fiber and fluid intake",
                    "- Scheduled toilet sits after meals",
                    "- Follow up in {timeframe}"
                ]
            },
            "eczema": {
                "title": "ATOPIC DERMATITIS",
                "content": [
                    "- Eczema affecting {location}",
                    "- Severity: {severity}",
                    "- {medication} {frequency} to affected areas",
                    "- Daily moisturizer application",
                    "- Trigger avoidance discussed",
                    "- Follow up in {timeframe} or PRN for flares"
                ]
            },
            "obesity": {
                "title": "OBESITY",
                "content": [
                    "- BMI {bmi} ({percentile})",
                    "- Nutrition counseling provided",
                    "- Goal: {goal}",
                    "- Increase physical activity to {target}",
                    "- Limit screen time and sugary beverages",
                    "- Follow up in {timeframe} for weight check"
                ]
            }
        }
        
        self.quick_buttons = [
            {"label": "Asthma Stable", "template": "asthma_stable"},
            {"label": "Asthma Flare", "template": "asthma_exacerbation"},
            {"label": "URI", "template": "uri"},
            {"label": "ADHD Stable", "template": "adhd_stable"},
            {"label": "ADHD Adjust", "template": "adhd_titration"},
            {"label": "WCC", "template": "wcc"},
            {"label": "GERD", "template": "gerd"},
            {"label": "Constipation", "template": "constipation"},
            {"label": "Eczema", "template": "eczema"},
            {"label": "Obesity", "template": "obesity"}
        ]
        
        self.patterns = [
            {
                "pattern": r"asthma\s+stable",
                "template": "asthma_stable",
                "defaults": {"medication": "albuterol PRN", "timeframe": "3 months"}
            },
            {
                "pattern": r"asthma\s+flare",
                "template": "asthma_exacerbation",
                "defaults": {"symptoms": "wheezing, cough", "frequency": "q4h", "dose": "1mg/kg", "duration": "5 days", "timeframe": "1 week"}
            },
            {
                "pattern": r"uri",
                "template": "uri",
                "defaults": {"symptoms": "rhinorrhea, congestion, cough", "medication": "acetaminophen"}
            },
            {
                "pattern": r"adhd\s+stable",
                "template": "adhd_stable",
                "defaults": {"medication": "methylphenidate", "dose": "18mg daily", "performance": "improved", "timeframe": "3 months"}
            },
            {
                "pattern": r"wcc",
                "template": "wcc",
                "defaults": {"height_percentile": "50th", "weight_percentile": "50th", "immunizations": "up to date", "next_visit": "age-appropriate interval"}
            }
        ]
        
        # Save default templates
        self.save_templates()
        
    def save_templates(self):
        """Save templates to JSON file"""
        data = {
            "templates": self.templates,
            "quick_buttons": self.quick_buttons,
            "patterns": self.patterns
        }
        with open(self.templates_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Quick Buttons Section
        button_frame = ttk.LabelFrame(main_frame, text="Quick Add Buttons", padding="10")
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Create quick buttons in a grid
        for idx, button_config in enumerate(self.quick_buttons):
            row = idx // 5
            col = idx % 5
            btn = ttk.Button(
                button_frame, 
                text=button_config['label'],
                command=lambda t=button_config['template']: self.add_template(t)
            )
            btn.grid(row=row, column=col, padx=3, pady=3, sticky=(tk.W, tk.E))
            button_frame.columnconfigure(col, weight=1)
        
        # Shorthand Input Section
        input_frame = ttk.LabelFrame(main_frame, text="Shorthand Input", padding="10")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        self.input_text = scrolledtext.ScrolledText(
            input_frame, 
            height=4, 
            wrap=tk.WORD,
            font=('Arial', 11)
        )
        self.input_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.input_text.bind('<KeyRelease>', self.on_typing)
        
        # Control buttons for input
        input_controls = ttk.Frame(input_frame)
        input_controls.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(input_controls, text="Process Now", command=self.process_input).pack(side=tk.LEFT, padx=3)
        ttk.Button(input_controls, text="Clear Input", command=self.clear_input).pack(side=tk.LEFT, padx=3)
        
        # Output Section
        output_frame = ttk.LabelFrame(main_frame, text="Expanded Output (auto-copies after typing pause)", padding="10")
        output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame, 
            height=15, 
            wrap=tk.WORD,
            font=('Arial', 11),
            bg='#f0f0f0'
        )
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Output controls
        output_controls = ttk.Frame(output_frame)
        output_controls.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(output_controls, text="Copy Now", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=3)
        ttk.Button(output_controls, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=3)
        ttk.Button(output_controls, text="Edit Templates", command=self.open_template_editor).pack(side=tk.LEFT, padx=3)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
    def on_typing(self, event=None):
        """Handle typing events - reset auto-copy timer"""
        # Cancel existing timer
        if self.typing_timer:
            self.root.after_cancel(self.typing_timer)
        
        # Set new timer
        self.typing_timer = self.root.after(self.auto_copy_delay, self.auto_process_and_copy)
        
    def auto_process_and_copy(self):
        """Process input and auto-copy after typing pause"""
        input_text = self.input_text.get("1.0", tk.END).strip()
        if input_text:
            self.process_input()
            self.copy_to_clipboard()
            self.status_label.config(text="✓ Auto-copied to clipboard")
            # Reset status after 3 seconds
            self.root.after(3000, lambda: self.status_label.config(text="Ready"))
        
    def add_template(self, template_key):
        """Add a template to the note"""
        if template_key in self.templates:
            self.note_components.append(template_key)
            self.render_output()
            self.copy_to_clipboard()
            self.status_label.config(text=f"Added: {template_key}")
        
    def process_input(self):
        """Process shorthand input and expand to full text"""
        input_text = self.input_text.get("1.0", tk.END).strip().lower()
        
        if not input_text:
            return
        
        # Try to match patterns
        matched = False
        for pattern_config in self.patterns:
            pattern = pattern_config['pattern']
            if re.search(pattern, input_text, re.IGNORECASE):
                template_key = pattern_config['template']
                self.note_components.append(template_key)
                matched = True
                
        if matched:
            self.render_output()
            self.status_label.config(text="Input processed")
        else:
            # If no pattern matched, add as free text
            self.note_components.append({"type": "freetext", "content": input_text})
            self.render_output()
            self.status_label.config(text="Added as free text")
        
    def render_output(self):
        """Render the current note components to output"""
        self.output_text.delete("1.0", tk.END)
        
        output_parts = []
        
        for component in self.note_components:
            if isinstance(component, str) and component in self.templates:
                # It's a template key
                template = self.templates[component]
                output_parts.append(template['title'])
                for line in template['content']:
                    # Keep placeholders for easy manual editing
                    output_parts.append(line)
                output_parts.append("")  # Blank line between sections
            elif isinstance(component, dict) and component.get('type') == 'freetext':
                # It's free text
                output_parts.append(component['content'].upper())
                output_parts.append("")
        
        output = "\n".join(output_parts)
        self.output_text.insert("1.0", output)
        
    def copy_to_clipboard(self):
        """Copy output to clipboard"""
        output = self.output_text.get("1.0", tk.END).strip()
        if output:
            pyperclip.copy(output)
            self.status_label.config(text="✓ Copied to clipboard!")
        
    def clear_input(self):
        """Clear input field"""
        self.input_text.delete("1.0", tk.END)
        self.status_label.config(text="Input cleared")
        
    def clear_all(self):
        """Clear all fields and reset"""
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.note_components = []
        self.status_label.config(text="All cleared")
        
    def open_template_editor(self):
        """Open the templates JSON file for editing"""
        try:
            import subprocess
            import sys
            
            if sys.platform == 'win32':
                subprocess.run(['notepad', str(self.templates_file)])
            elif sys.platform == 'darwin':
                subprocess.run(['open', '-a', 'TextEdit', str(self.templates_file)])
            else:
                subprocess.run(['xdg-open', str(self.templates_file)])
                
            messagebox.showinfo(
                "Template Editor", 
                "After editing templates, click OK and restart the app to reload."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Could not open template editor: {str(e)}")


def main():
    root = tk.Tk()
    app = PedsChartingTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
