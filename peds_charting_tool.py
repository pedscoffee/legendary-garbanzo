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
        self.input_text.bind('<KeyRelease>', self.on_typing)
        
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
        # Configure italic tag
        self.output_text.tag_configure('italic', font=('Arial', 11, 'italic'))
        
        # Output controls
        output_controls = ttk.Frame(output_frame)
        output_controls.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(output_controls, text="Copy Now", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=3)
        ttk.Button(output_controls, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=3)
        ttk.Button(output_controls, text="Edit Templates", command=self.open_template_editor).pack(side=tk.LEFT, padx=3)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=4, column=0, sticky=(tk.W, tk.E))
        
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
        input_text = self.input_text.get("1.0", tk.END).strip()
        
        if not input_text:
            return
        
        # Check for follow-up shorthand first
        self._check_follow_up_shorthand(input_text)
        
        input_text_lower = input_text.lower()
        
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
            self.note_components.append({"type": "freetext", "content": input_text_lower})
            self.render_output()
            self.status_label.config(text="Added as free text")
        
    def set_follow_up(self, follow_up):
        """Set the follow-up timeframe"""
        self.follow_up = follow_up
        self.render_output()
        self.copy_to_clipboard()
        self.status_label.config(text=f"Follow-up set: {follow_up}")
        
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
        
    def render_output(self):
        """Render the current note components to output with conditional phrases"""
        self.output_text.delete("1.0", tk.END)
        
        detected_conditions = set()
        
        # Build content line by line with proper formatting
        for component in self.note_components:
            if isinstance(component, str) and component in self.templates:
                # It's a template key
                template = self.templates[component]
                self.output_text.insert(tk.END, template['title'] + "\n")
                for line in template['content']:
                    self.output_text.insert(tk.END, line + "\n")
                self.output_text.insert(tk.END, "\n")
                # Detect conditions for phrases
                self._detect_conditions(component, detected_conditions)
            elif isinstance(component, dict) and component.get('type') == 'freetext':
                # It's free text
                content = component['content']
                self.output_text.insert(tk.END, content.upper() + "\n\n")
                # Check free text for conditions
                self._detect_conditions_in_text(content, detected_conditions)
        
        # Add conditional phrases in actual italics
        conditional_phrases = self._get_conditional_phrases(detected_conditions)
        if conditional_phrases:
            self.output_text.insert(tk.END, "\n")
            for phrase in conditional_phrases:
                self.output_text.insert(tk.END, phrase + "\n", 'italic')
        
        # Add follow-up if set (in italics)
        if self.follow_up:
            self.output_text.insert(tk.END, f"\nFollow-up: {self.follow_up}\n", 'italic')
        
    def _detect_conditions(self, template_key, conditions):
        """Detect conditions based on template key"""
        condition_map = {
            'wcc': ['well_child'],
            'asthma_stable': ['illness'],
            'asthma_exacerbation': ['illness'],
            'uri': ['illness'],
            'adhd_stable': ['adhd', 'pcmh'],
            'adhd_titration': ['adhd', 'pcmh'],
            'otitis_media': ['ear_infection', 'illness'],
            'pharyngitis': ['illness', 'strep_test'],
            'obesity': ['obesity', 'weight', 'pcmh'],
            'constipation': ['gi_symptoms'],
            'gerd': ['gi_symptoms'],
            'eczema': ['skin_condition'],
            'headache': ['illness'],
            'anxiety': ['mental_health'],
            'depression': ['mental_health'],
            'injury': ['injury']
        }
        if template_key in condition_map:
            conditions.update(condition_map[template_key])
            
    def _detect_conditions_in_text(self, text, conditions):
        """Detect conditions in free text"""
        text_lower = text.lower()
        # Well child / health maintenance
        if any(word in text_lower for word in ['well child', 'health maintenance', 'wcc', 'check up', 'physical']):
            conditions.add('well_child')
        # Illness
        if any(word in text_lower for word in ['fever', 'cough', 'cold', 'sick', 'illness', 'infection', 'virus', 'pain', 'ache', 'symptom']):
            conditions.add('illness')
        # Injury
        if any(word in text_lower for word in ['injury', 'hurt', 'fall', 'accident', 'trauma', 'sprain', 'fracture', 'wound']):
            conditions.add('injury')
        # Ear infection
        if any(word in text_lower for word in ['ear infection', 'ear pain', 'otitis', 'earache']):
            conditions.add('ear_infection')
        # Strep test
        if any(word in text_lower for word in ['strep', 'throat culture', 'rapid strep']):
            conditions.add('strep_test')
            conditions.add('pcmh')
        # Dehydration/GI
        if any(word in text_lower for word in ['dehydration', 'vomiting', 'diarrhea', 'decreased urination', 'not peeing', 'not drinking']):
            conditions.add('dehydration_gi')
        # Breathing
        if any(word in text_lower for word in ['breathing', 'wheezing', 'short of breath', 'respiratory', 'coughing', 'tachypnea']):
            conditions.add('breathing')
        # ADHD
        if 'adhd' in text_lower or 'attention' in text_lower:
            conditions.add('adhd')
            conditions.add('pcmh')
        # Weight/Obesity
        if any(word in text_lower for word in ['weight', 'obese', 'obesity', 'overweight', 'bmi', 'diet']):
            conditions.add('weight')
            conditions.add('pcmh')
            
    def _get_conditional_phrases(self, conditions):
        """Get phrases based on detected conditions"""
        phrases = []
        
        if 'well_child' in conditions:
            phrases.append("All forms, labs, immunizations, and patient concerns reviewed and addressed appropriately. Screening questions, past medical history, past social history, medications, and growth chart reviewed. Age-appropriate anticipatory guidance reviewed and printed in AVS. Parent questions addressed.")
            
        if 'illness' in conditions:
            phrases.append("Recommended supportive care with OTC medications as needed. Return precautions given including increasing pain, worsening fever, dehydration, new symptoms, prolonged symptoms, worsening symptoms, and other concerns. Caregiver expressed understanding and agreement with treatment plan.")
            
        if 'injury' in conditions:
            phrases.append("Recommended supportive care with Tylenol, Motrin, rest, ice, compression, elevation, and gradual return to activity as appropriate. Return precautions given including increasing pain, swelling, or failure to improve.")
            
        if 'ear_infection' in conditions:
            phrases.append("Risk of untreated otitis media includes persistent pain and fever, hearing loss, and mastoiditis.")
            
        if 'strep_test' in conditions:
            phrases.append("Risk of untreated strep throat includes rheumatic fever and peritonsillar abscess. This problem is moderate risk due to pending lab results which may necessitate further pharmacologic management.")
            
        if 'dehydration_gi' in conditions:
            phrases.append("Patient is at risk for dehydration, which would warrant emergency room care or admission for IV fluids.")
            
        if 'breathing' in conditions:
            phrases.append("Patient is at risk for worsening respiratory distress and clinical deterioration, which would need emergency room care or hospital admission.")
            
        if 'pcmh' in conditions:
            phrases.append("PCMH Reminder")
            
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
