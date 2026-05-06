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
        
        # Follow up selection
        self.follow_up = None
        self.follow_up_options = [
            "Tomorrow",
            "2-3 days",
            "2-4 weeks",
            "1 month",
            "3 months",
            "1 year",
            "PRN",
            "Next well check"
        ]
        
        self.setup_ui()
        
    def load_templates(self):
        """Load templates from JSON file"""
        if self.templates_file.exists():
            with open(self.templates_file, 'r') as f:
                data = json.load(f)
                self.templates = data.get('templates', {})
                self.quick_buttons = data.get('quick_buttons', [])
                self.patterns = data.get('patterns', [])
                self.conditional_logic = data.get('conditional_logic', {})
                self.condition_map = self.conditional_logic.get('condition_map', {})
                self.condition_phrases = self.conditional_logic.get('phrases', {})
                self.conditional_logic = data.get('conditional_logic', {})
                self.condition_map = self.conditional_logic.get('condition_map', {})
                self.condition_phrases = self.conditional_logic.get('phrases', {})
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
            },
            "injury": {
                "title": "INJURY",
                "content": [
                    "- {injury_type} affecting {location}",
                    "- Mechanism: {mechanism}",
                    "- Pain control with {pain_med}",
                    "- Activity restrictions: {restrictions}",
                    "- Follow up in {timeframe} or sooner if worsening"
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
            {"label": "Obesity", "template": "obesity"},
            {"label": "Injury", "template": "injury"}
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
            },
            {
                "pattern": r"injury|hurt|fall|trauma|sprain",
                "template": "injury",
                "defaults": {"injury_type": "soft tissue injury", "location": "extremity", "mechanism": "playground accident", "pain_med": "ibuprofen", "restrictions": "as tolerated", "timeframe": "1 week"}
            }
        ]
        

        # Save default templates
        self.condition_map = {
            'wcc': ['well_child'], 'asthma_stable': ['illness'], 'asthma_exacerbation': ['illness'],
            'uri': ['illness'], 'adhd_stable': ['adhd', 'pcmh'], 'adhd_titration': ['adhd', 'pcmh'],
            'otitis_media': ['ear_infection', 'illness'], 'pharyngitis': ['illness', 'strep_test'],
            'obesity': ['obesity', 'weight', 'pcmh'], 'constipation': ['gi_symptoms'],
            'gerd': ['gi_symptoms'], 'eczema': ['skin_condition'], 'headache': ['illness'],
            'anxiety': ['mental_health'], 'depression': ['mental_health'], 'injury': ['injury']
        }
        self.condition_phrases = {
            'well_child': "All forms, labs, immunizations, and patient concerns reviewed and addressed appropriately. Screening questions, past medical history, past social history, medications, and growth chart reviewed. Age-appropriate anticipatory guidance reviewed and printed in AVS. Parent questions addressed.",
            'illness': "Recommended supportive care with OTC medications as needed. Return precautions given including increasing pain, worsening fever, dehydration, new symptoms, prolonged symptoms, worsening symptoms, and other concerns. Caregiver expressed understanding and agreement with treatment plan.",
            'injury': "Recommended supportive care with Tylenol, Motrin, rest, ice, compression, elevation, and gradual return to activity as appropriate. Return precautions given including increasing pain, swelling, or failure to improve.",
            'ear_infection': "Risk of untreated otitis media includes persistent pain and fever, hearing loss, and mastoiditis.",
            'strep_test': "Risk of untreated strep throat includes rheumatic fever and peritonsillar abscess. This problem is moderate risk due to pending lab results which may necessitate further pharmacologic management.",
            'dehydration_gi': "Patient is at risk for dehydration, which would warrant emergency room care or admission for IV fluids.",
            'breathing': "Patient is at risk for worsening respiratory distress and clinical deterioration, which would need emergency room care or hospital admission.",
            'pcmh': "PCMH Reminder"
        }
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
        main_frame.rowconfigure(3, weight=1)
        
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
        
        # Follow-Up Buttons Section
        followup_frame = ttk.LabelFrame(main_frame, text="Follow-Up", padding="10")
        followup_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        for idx, option in enumerate(self.follow_up_options):
            btn = ttk.Button(
                followup_frame,
                text=option,
                command=lambda fu=option: self.set_follow_up(fu)
            )
            btn.grid(row=0, column=idx, padx=3, pady=3, sticky=(tk.W, tk.E))
            followup_frame.columnconfigure(idx, weight=1)
        
        # Shorthand Input Section
        input_frame = ttk.LabelFrame(main_frame, text="Shorthand Input", padding="10")
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        self.input_text = scrolledtext.ScrolledText(
            input_frame, 
            height=4, 
            wrap=tk.WORD,
            font=('Arial', 11)
        )
        self.input_text.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Autocomplete Listbox
        self.autocomplete_list = tk.Listbox(input_frame, height=4, font=('Arial', 10))
        self.autocomplete_list.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        self.autocomplete_list.grid_remove()
        self.autocomplete_list.bind('<<ListboxSelect>>', self.insert_autocomplete)
        

        # Autocomplete Listbox
        self.autocomplete_list = tk.Listbox(input_frame, height=4, font=('Arial', 10))
        self.autocomplete_list.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        self.autocomplete_list.grid_remove()
        self.autocomplete_list.bind('<<ListboxSelect>>', self.insert_autocomplete)
        
        self.input_text.bind('<KeyRelease>', self.on_typing)

        for i in range(1, 9):
            self.root.bind(f'<Command-{i}>', lambda e, idx=i-1: self.set_follow_up(self.follow_up_options[idx]) if idx < len(self.follow_up_options) else None)
            self.root.bind(f'<Control-{i}>', lambda e, idx=i-1: self.set_follow_up(self.follow_up_options[idx]) if idx < len(self.follow_up_options) else None)


        for i in range(1, 9):
            self.root.bind(f'<Command-{i}>', lambda e, idx=i-1: self.set_follow_up(self.follow_up_options[idx]) if idx < len(self.follow_up_options) else None)
            self.root.bind(f'<Control-{i}>', lambda e, idx=i-1: self.set_follow_up(self.follow_up_options[idx]) if idx < len(self.follow_up_options) else None)

        
        # Control buttons for input
        input_controls = ttk.Frame(input_frame)
        input_controls.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(input_controls, text="Process Now", command=self.process_input).pack(side=tk.LEFT, padx=3)
        ttk.Button(input_controls, text="Clear Input", command=self.clear_input).pack(side=tk.LEFT, padx=3)
        
        # Output Section
        output_frame = ttk.LabelFrame(main_frame, text="Expanded Output (auto-copies after typing pause)", padding="10")
        output_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
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
        # Configure tags
        self.output_text.tag_configure('italic', font=('Arial', 11, 'italic'))
        self.output_text.tag_configure('bold', font=('Arial', 11, 'bold'))
        self.output_text.tag_configure('red', foreground='red')
        # Bind down arrow to jump to next placeholder
        self.output_text.bind('<Down>', self.jump_to_next_placeholder)
        
        # Output controls
        output_controls = ttk.Frame(output_frame)
        output_controls.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(output_controls, text="Copy Now", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=3)
        ttk.Button(output_controls, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=3)
        ttk.Button(output_controls, text="Edit Templates", command=self.open_template_editor).pack(side=tk.LEFT, padx=3)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=4, column=0, sticky=(tk.W, tk.E))
        

    def insert_autocomplete(self, event):
        if not self.autocomplete_list.curselection(): return
        selected = self.autocomplete_list.get(self.autocomplete_list.curselection())
        content = self.input_text.get("1.0", tk.END).strip()
        words = content.split()
        if words:
            new_content = " ".join(words[:-1] + [selected]) + " "
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", new_content)
        self.autocomplete_list.grid_remove()
        self.input_text.focus_set()


    def insert_autocomplete(self, event):
        if not self.autocomplete_list.curselection(): return
        selected = self.autocomplete_list.get(self.autocomplete_list.curselection())
        content = self.input_text.get("1.0", tk.END).strip()
        words = content.split()
        if words:
            new_content = " ".join(words[:-1] + [selected]) + " "
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", new_content)
        self.autocomplete_list.grid_remove()
        self.input_text.focus_set()

    def on_typing(self, event=None):
        """Handle typing events - reset auto-copy timer and show autocomplete"""
        if event and event.keysym in ('space', 'Return', 'BackSpace', 'Escape'):
            self.autocomplete_list.grid_remove()
        elif event and event.char and event.char.isalnum():
            text_content = self.input_text.get("1.0", "end-1c").strip()
            words = text_content.split()
            if words:
                last_word = words[-1].lower()
                suggestions = []
                for p in self.patterns:
                    display_pat = p['pattern'].replace('\\s+', ' ').replace('|', ' or ').replace('\\\\', '')
                    if last_word in display_pat.lower() or last_word in p['template'].lower():
                        suggestions.append(display_pat)
                
                if suggestions:
                    self.autocomplete_list.delete(0, "end")
                    for s in suggestions[:4]:
                        self.autocomplete_list.insert("end", s)
                    self.autocomplete_list.grid()
                else:
                    self.autocomplete_list.grid_remove()

        # check for double space trigger
        if event and event.keysym == 'space':
            text_before_cursor = self.input_text.get("1.0", "insert")
            if text_before_cursor.endswith("  "):
                self.process_input()
                self.copy_to_clipboard()
                self.status_label.config(text="✓ Auto-copied to clipboard")
                self.root.after(3000, lambda: self.status_label.config(text="Ready"))

        if self.typing_timer:
            self.root.after_cancel(self.typing_timer)
        self.typing_timer = self.root.after(self.auto_copy_delay, self.auto_process_and_copy)

    def auto_process_and_copy(self):
        """Process input and auto-copy after typing pause"""
        input_text = self.input_text.get("1.0", "end-1c").strip()
        if input_text:
            self.process_input()
            self.copy_to_clipboard()
            self.status_label.config(text="✓ Auto-copied to clipboard")
            self.root.after(3000, lambda: self.status_label.config(text="Ready"))

    def add_template(self, template_key):
        """Add a template to the note"""
        if template_key in self.templates:
            current = self.input_text.get("1.0", "end-1c").strip()
            if current:
                self.input_text.insert("end", f"\n.{template_key} ")
            else:
                self.input_text.insert("end", f".{template_key} ")
            self.process_input()
            self.copy_to_clipboard()
            self.status_label.config(text=f"Added: {template_key}")

    def process_input(self):
        """Process shorthand input and expand to full text"""
        input_text = self.input_text.get("1.0", "end-1c").strip()
        self.autocomplete_list.grid_remove()
        
        self.note_components = []
        
        if not input_text:
            self.render_output()
            return
            
        self._check_follow_up_shorthand(input_text)
        
        current_freetext = []
        
        for line in input_text.split('\\n'):
            line_stripped = line.strip()
            
            words = line_stripped.split()
            macro_found = False
            
            for i, word in enumerate(words):
                if word.startswith('.'):
                    macro_cand = word[1:]
                    for p in self.patterns:
                        # Find matching pattern or direct template key match
                        if re.search(p['pattern'], macro_cand, re.IGNORECASE) or macro_cand.lower() == p['template'].lower():
                            overrides = {}
                            for w in words[i+1:]:
                                if '=' in w and w.count('=') == 1:
                                    k, v = w.split('=', 1)
                                    overrides[k.lower()] = v.replace('_', ' ')
                            
                            if current_freetext:
                                self.note_components.append({"type": "freetext", "content": "\\n".join(current_freetext)})
                                current_freetext = []
                                
                            defaults = p.get('defaults', {}).copy()
                            defaults.update(overrides)
                            self.note_components.append({"type": "template", "key": p['template'], "defaults": defaults})
                            macro_found = True
                            break
                    if macro_found:
                        break
            
            if not macro_found:
                current_freetext.append(line)
                
        if current_freetext:
            freetext_content = "\\n".join(current_freetext).strip()
            if freetext_content:
                self.note_components.append({"type": "freetext", "content": freetext_content})
                
        self.render_output()

    def set_follow_up(self, follow_up):
        """Set the follow-up timeframe"""
        self.follow_up = follow_up
        self.render_output()
        self.copy_to_clipboard()
        self.status_label.config(text=f"Follow-up set: {follow_up}")
        
    def jump_to_next_placeholder(self, event=None):
        """Jump to and select the next {bracketed} placeholder"""
        # Get current cursor position
        current_pos = self.output_text.index(tk.INSERT)
        
        # Search for next { starting from current position
        content = self.output_text.get("1.0", tk.END)
        search_start = self.output_text.index(f"{current_pos} + 1 chars")
        
        # Find next opening brace
        start_idx = self.output_text.search("{", search_start, stopindex=tk.END, regexp=False)
        
        if not start_idx:
            # If not found from current position, search from beginning
            start_idx = self.output_text.search("{", "1.0", stopindex=current_pos, regexp=False)
        
        if start_idx:
            # Find closing brace after the opening one
            end_idx = self.output_text.search("}", f"{start_idx} + 1 chars", stopindex=tk.END, regexp=False)
            
            if end_idx:
                # Select the entire placeholder including braces
                self.output_text.tag_remove(tk.SEL, "1.0", tk.END)
                self.output_text.tag_add(tk.SEL, start_idx, f"{end_idx} + 1 chars")
                self.output_text.mark_set(tk.INSERT, end_idx)
                self.output_text.see(start_idx)
                return "break"  # Prevent default down arrow behavior
        
        return None  # Let default behavior occur if no placeholder found
        
    def _check_follow_up_shorthand(self, text):
        """Check for follow-up shorthand in text"""
        text_lower = text.lower()
        follow_up_patterns = {
            r'follow[\s-]?up:\s*tomorrow|fu:\s*tomorrow|followup\s+tomorrow': 'Tomorrow',
            r'follow[\s-]?up:\s*2-3\s*days|fu:\s*2-3\s*days|followup\s+2-3\s*days': '2-3 days',
            r'follow[\s-]?up:\s*2-4\s*weeks|fu:\s*2-4\s*weeks|followup\s+2-4\s*weeks': '2-4 weeks',
            r'follow[\s-]?up:\s*1\s*month|fu:\s*1\s*month|followup\s+1\s*month': '1 month',
            r'follow[\s-]?up:\s*3\s*months|fu:\s*3\s*months|followup\s+3\s*months': '3 months',
            r'follow[\s-]?up:\s*1\s*year|fu:\s*1\s*year|followup\s+1\s*year': '1 year',
            r'follow[\s-]?up:\s*prn|fu:\s*prn|followup\s+prn': 'PRN',
            r'follow[\s-]?up:\s*next\s*well\s*check|fu:\s*next\s*well\s*check|followup\s+next\s*well\s*check': 'Next well check'
        }
        for pattern, fu in follow_up_patterns.items():
            if re.search(pattern, text_lower):
                self.follow_up = fu
                return True
        return False
        

    def highlight_placeholders(self):
        """Find and color {placeholders} red"""
        start_idx = "1.0"
        while True:
            start_idx = self.output_text.search("{", start_idx, stopindex=tk.END)
            if not start_idx: break
            end_idx = self.output_text.search("}", start_idx, stopindex=tk.END)
            if not end_idx: break
            end_idx = f"{end_idx}+1c"
            self.output_text.tag_add("red", start_idx, end_idx)
            start_idx = end_idx


    def highlight_placeholders(self):
        """Find and color {placeholders} red"""
        start_idx = "1.0"
        while True:
            start_idx = self.output_text.search("{", start_idx, stopindex=tk.END)
            if not start_idx: break
            end_idx = self.output_text.search("}", start_idx, stopindex=tk.END)
            if not end_idx: break
            end_idx = f"{end_idx}+1c"
            self.output_text.tag_add("red", start_idx, end_idx)
            start_idx = end_idx

    def render_output(self):
        """Render the current note components to output with conditional phrases"""
        self.output_text.delete("1.0", tk.END)
        detected_conditions = set()
        
        for component in self.note_components:
            if isinstance(component, str) and component in self.templates:
                template = self.templates[component]
                self.output_text.insert(tk.END, template['title'] + "\n", 'bold')
                for line in template['content']:
                    tag = 'bold' if line.endswith(':') or 'Plan:' in line or 'Goal' in line else None
                    if tag:
                        self.output_text.insert(tk.END, line + "\n", tag)
                    else:
                        self.output_text.insert(tk.END, line + "\n")
                self.output_text.insert(tk.END, "\n")
                self._detect_conditions(component, detected_conditions)
            elif isinstance(component, dict) and component.get('type') == 'template':
                template_key = component['key']
                defaults = component.get('defaults', {})
                if template_key in self.templates:
                    template = self.templates[template_key]
                    self.output_text.insert(tk.END, template['title'] + "\n", 'bold')
                    for line in template['content']:
                        formatted_line = line
                        for k, v in defaults.items():
                            formatted_line = formatted_line.replace(f"{{{k}}}", v)
                        # Check inline defaults {key:default}
                        while "{" in formatted_line and ":" in formatted_line[formatted_line.find("{"):formatted_line.find("}")]:
                            start = formatted_line.find("{")
                            end = formatted_line.find("}")
                            if end > start:
                                inner = formatted_line[start+1:end]
                                if ":" in inner:
                                    k, default_val = inner.split(":", 1)
                                    val = defaults.get(k, default_val)
                                    formatted_line = formatted_line[:start] + val + formatted_line[end+1:]
                                else:
                                    break
                            else:
                                break
                        
                        tag = 'bold' if formatted_line.endswith(':') or 'Plan:' in formatted_line or 'Goal:' in formatted_line else None
                        if tag:
                            self.output_text.insert(tk.END, formatted_line + "\n", tag)
                        else:
                            self.output_text.insert(tk.END, formatted_line + "\n")
                    self.output_text.insert(tk.END, "\n")
                    self._detect_conditions(template_key, detected_conditions)
            elif isinstance(component, dict) and component.get('type') == 'freetext':
                content = component['content']
                self.output_text.insert(tk.END, content.upper() + "\n\n", 'bold')
                self._detect_conditions_in_text(content, detected_conditions)
        
        conditional_phrases = self._get_conditional_phrases(detected_conditions)
        if conditional_phrases:
            self.output_text.insert(tk.END, "\n")
            for phrase in conditional_phrases:
                self.output_text.insert(tk.END, phrase + "\n", 'italic')
        
        if self.follow_up:
            self.output_text.insert(tk.END, f"\nFollow-up: {self.follow_up}\n", 'italic')
            
        self.highlight_placeholders()


    def _detect_conditions(self, template_key, conditions):
        """Detect conditions based on template key"""
        if hasattr(self, 'condition_map') and template_key in self.condition_map:
            conditions.update(self.condition_map[template_key])
            
    def _detect_conditions_in_text(self, text, conditions):
        """Detect conditions in free text"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['well child', 'health maintenance', 'wcc', 'check up', 'physical']):
            conditions.add('well_child')
        if any(word in text_lower for word in ['fever', 'cough', 'cold', 'sick', 'illness', 'infection', 'virus', 'pain', 'ache', 'symptom']):
            conditions.add('illness')
        if any(word in text_lower for word in ['injury', 'hurt', 'fall', 'accident', 'trauma', 'sprain', 'fracture', 'wound']):
            conditions.add('injury')
        if any(word in text_lower for word in ['ear infection', 'ear pain', 'otitis', 'earache']):
            conditions.add('ear_infection')
        if any(word in text_lower for word in ['strep', 'throat culture', 'rapid strep']):
            conditions.add('strep_test')
            conditions.add('pcmh')
        if any(word in text_lower for word in ['dehydration', 'vomiting', 'diarrhea', 'decreased urination', 'not peeing', 'not drinking']):
            conditions.add('dehydration_gi')
        if any(word in text_lower for word in ['breathing', 'wheezing', 'short of breath', 'respiratory', 'coughing', 'tachypnea']):
            conditions.add('breathing')
        if 'adhd' in text_lower or 'attention' in text_lower:
            conditions.add('adhd')
            conditions.add('pcmh')
        if any(word in text_lower for word in ['weight', 'obese', 'obesity', 'overweight', 'bmi', 'diet']):
            conditions.add('weight')
            conditions.add('pcmh')
            
    def _get_conditional_phrases(self, conditions):
        """Get phrases based on detected conditions"""
        phrases = []
        if hasattr(self, 'condition_phrases'):
            for cond in conditions:
                if cond in self.condition_phrases:
                    phrases.append(self.condition_phrases[cond])
        return phrases

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
        self.follow_up = None
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
