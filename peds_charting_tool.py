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
        
        # Current note components (stores objects with state)
        self.note_components = []
        # Mapping for interaction: {tag_name: {"comp_idx": i, "line_idx": j, "raw": "[[...]]"}}
        self.active_placeholders = {}
        
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
            },
            "return_precautions": {
                "title": "RETURN PRECAUTIONS",
                "content": [
                    "- Return precautions include [[*worsening fever|*worsening pain|*shortness of breath|worsening cough|chest pain|severe headache|neck stiffness|confusion|altered mental status|seizure|difficulty breathing|fast breathing|wheezing|cyanosis|dehydration|decreased urination|dry mouth|no tears|sunken eyes|lethargy|irritability|vomiting|persistent vomiting|blood in vomit|diarrhea|bloody diarrhea|severe abdominal pain|bloody stool|rash|worsening rash|spreading rash|petechiae|bruising|abnormal movements|stiffness|weakness|numbness|tingling|itching|hives|swelling|angioedema|failure to improve|prolonged symptoms|symptoms lasting >3 days|symptoms lasting >1 week|new symptoms|new rash|new pain|new swelling|not drinking|not eating|not responding to treatment|medication side effects|allergic reaction|anaphylaxis|behavioral changes|suicidal ideation|self-harm thoughts|hearing loss|vision changes]]"
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
            {"label": "Injury", "template": "injury"},
            {"label": "Return Precautions", "template": "return_precautions"}
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
            },
            {
                "pattern": r"\b(return precautions|rp)\b",
                "template": "return_precautions"
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
        # Configure hidden tag for unselected options
        self.output_text.tag_configure('hidden', elide=True)
        # Bind down arrow to jump to next placeholder
        self.output_text.bind('<Down>', self.jump_to_next_placeholder)
        # Also bind double-click for easier access
        self.output_text.bind('<Double-1>', self.jump_to_next_placeholder)
        
        # Configure placeholder tag (subtle highlight)
        self.output_text.tag_configure('placeholder_ui', background='#e8f0fe')
        
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
            template = self.templates[template_key]
            # Create a deep copy of the content lines for this instance
            component = {
                "type": "template",
                "key": template_key,
                "title": template['title'],
                "content": list(template['content']) 
            }
            self.note_components.append(component)
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
        
        remaining_text = input_text
        found_any = False
        
        # Try to match patterns and extract them from text
        for pattern_config in self.patterns:
            pattern = pattern_config['pattern']
            # Use a more robust check for patterns
            if re.search(pattern, remaining_text, re.IGNORECASE):
                template_key = pattern_config['template']
                self.note_components.append(template_key)
                # Remove the matched pattern from the remaining text to avoid duplicate adding
                remaining_text = re.sub(pattern, "", remaining_text, flags=re.IGNORECASE).strip()
                found_any = True
                
        # If there's remaining text that isn't just a shorthand, add it as free text
        if remaining_text:
            # Clean up extra whitespace/punctuation left over
            clean_text = re.sub(r"^\s*[:.,;-]\s*", "", remaining_text).strip()
            if clean_text:
                self.note_components.append({"type": "freetext", "content": clean_text})
                found_any = True

        if found_any:
            self.render_output()
            self.status_label.config(text="Input processed")
            self.input_text.delete("1.0", tk.END) 
        
    def set_follow_up(self, follow_up):
        """Set the follow-up timeframe"""
        self.follow_up = follow_up
        self.render_output()
        self.copy_to_clipboard()
        self.status_label.config(text=f"Follow-up set: {follow_up}")
        
    def jump_to_next_placeholder(self, event=None):
        """Jump to and select the next placeholder tag"""
        current_pos = self.output_text.index(tk.INSERT)
        
        # 1. Check if we are already ON a placeholder
        current_tags = self.output_text.tag_names(current_pos)
        for tag in current_tags:
            if tag in self.active_placeholders:
                data = self.active_placeholders[tag]
                # Get the current tag range to extract content
                ranges = self.output_text.tag_ranges(tag)
                if ranges:
                    content = data["raw"] # Use the raw stored content
                    self.show_multi_select_dialog(tag, data, content)
                    return "break"

        # 2. Search for the next placeholder tag
        # Find all tags in the widget
        all_tags = self.output_text.tag_names()
        placeholder_tags = [t for t in all_tags if t in self.active_placeholders]
        
        next_tag = None
        next_pos = None
        
        for tag in placeholder_tags:
            ranges = self.output_text.tag_ranges(tag)
            if ranges:
                tag_start = ranges[0]
                if self.output_text.compare(tag_start, ">", current_pos):
                    if next_pos is None or self.output_text.compare(tag_start, "<", next_pos):
                        next_pos = tag_start
                        next_tag = tag
        
        if next_tag:
            data = self.active_placeholders[next_tag]
            self.output_text.mark_set(tk.INSERT, next_pos)
            self.output_text.see(next_pos)
            self.show_multi_select_dialog(next_tag, data, data["raw"])
            return "break"
        
        return None
        
    def show_multi_select_dialog(self, tag_id, tag_data, content):
        """Show a dialog to select options from a multi-select placeholder"""
        # Extract options from [[option1|option2|...]]
        inner = content[2:-2]
        options = [opt.strip() for opt in inner.split('|')]
        
        selected_options = []
        display_options = []
        for opt in options:
            if opt.startswith('*'):
                clean_opt = opt[1:].strip()
                # Clean up existing separators if present
                clean_opt = re.sub(r' (and|,) ?$', '', clean_opt).strip()
                selected_options.append(clean_opt)
                display_options.append(clean_opt)
            else:
                display_options.append(opt)
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Options")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.geometry("450x550")
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (550 // 2)
        dialog.geometry(f"450x550+{x}+{y}")
        
        ttk.Label(dialog, text="Select options:", font=('Arial', 11, 'bold')).pack(pady=10)
        
        container = ttk.Frame(dialog)
        container.pack(fill=tk.BOTH, expand=True, padx=10)
        
        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        checkboxes = {}
        for opt in display_options:
            var = tk.BooleanVar(value=opt in selected_options)
            checkboxes[opt] = var
            ttk.Checkbutton(scroll_frame, text=opt, variable=var).pack(anchor=tk.W, padx=20, pady=2)
        
        def on_ok():
            canvas.unbind_all("<MouseWheel>")
            selected_indices = [i for i, opt in enumerate(display_options) if checkboxes[opt].get()]
            num_selected = len(selected_indices)
            
            new_options = []
            for i, opt in enumerate(display_options):
                if checkboxes[opt].get():
                    current_rank = selected_indices.index(i)
                    suffix = ""
                    if num_selected > 1:
                        if current_rank == num_selected - 2: suffix = " and "
                        elif current_rank < num_selected - 2: suffix = ", "
                    new_options.append(f"*{opt}{suffix}")
                else:
                    new_options.append(opt)
            
            replacement = "[[" + "|".join(new_options) + "]]"
            
            # Update the source data
            comp_idx = tag_data["comp_idx"]
            line_idx = tag_data["line_idx"]
            self.note_components[comp_idx]["content"][line_idx] = replacement
            
            dialog.destroy()
            self.render_output()
            self.copy_to_clipboard()
        
        def on_cancel():
            canvas.unbind_all("<MouseWheel>")
            dialog.destroy()
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="OK", command=on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)
        
        
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
        """Render the current note components to output with tag-based placeholders"""
        self.output_text.delete("1.0", tk.END)
        self.active_placeholders = {}
        detected_conditions = set()
        
        tag_counter = 0
        
        for i, component in enumerate(self.note_components):
            if component["type"] == "template":
                self.output_text.insert(tk.END, component['title'] + "\n")
                for j, line in enumerate(component['content']):
                    # Check for placeholders in this line
                    remaining = line
                    while "[[" in remaining:
                        start = remaining.find("[[")
                        end = remaining.find("]]", start)
                        if end == -1: break
                        
                        # Insert text before placeholder
                        self.output_text.insert(tk.END, remaining[:start])
                        
                        # Process placeholder content
                        raw_placeholder = remaining[start:end+2]
                        inner = raw_placeholder[2:-2]
                        options = inner.split('|')
                        selected_parts = []
                        for opt in options:
                            if opt.strip().startswith('*'):
                                selected_parts.append(opt.strip()[1:])
                        
                        display_text = "".join(selected_parts)
                        if not display_text:
                            display_text = "[Click to Select]"
                            
                        # Create unique tag
                        tag_name = f"p_{tag_counter}"
                        tag_counter += 1
                        self.active_placeholders[tag_name] = {
                            "comp_idx": i,
                            "line_idx": j,
                            "raw": raw_placeholder
                        }
                        
                        # Insert display text with tags
                        self.output_text.insert(tk.END, display_text, (tag_name, 'placeholder_ui'))
                        
                        remaining = remaining[end+2:]
                    
                    self.output_text.insert(tk.END, remaining + "\n")
                self.output_text.insert(tk.END, "\n")
                self._detect_conditions(component['key'], detected_conditions)
            elif component["type"] == "freetext":
                content = component['content']
                self.output_text.insert(tk.END, content.upper() + "\n\n")
                self._detect_conditions_in_text(content, detected_conditions)
        
        # Add conditional phrases
        conditional_phrases = self._get_conditional_phrases(detected_conditions)
        if conditional_phrases:
            self.output_text.insert(tk.END, "\n")
            for phrase in conditional_phrases:
                self.output_text.insert(tk.END, phrase + "\n", 'italic')
        
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
            'injury': ['injury'],
            'return_precautions': ['illness']
        }
        if template_key in condition_map:
            conditions.update(condition_map[template_key])
            
    def _detect_conditions_in_text(self, text, conditions):
        """Detect conditions in free text"""
        text_lower = text.lower()
        # Well child / health maintenance
        if any(word in text_lower for word in ['well child', 'health maintenance', 'wcc', 'check up', 'physical']):
            conditions.add('well_child')
        # Illness / Return Precautions
        if any(word in text_lower for word in ['fever', 'cough', 'cold', 'sick', 'illness', 'infection', 'virus', 'pain', 'ache', 'symptom', 'return precautions', 'rp']):
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
        """Copy output to clipboard, skipping hidden text"""
        # Get all text but filter out 'hidden' tags
        full_text = ""
        
        # Iterate through segments of the text
        idx = "1.0"
        while self.output_text.compare(idx, "<", tk.END):
            # Get next range of tags
            next_range = self.output_text.tag_nextrange("hidden", idx)
            if not next_range:
                # No more hidden text
                full_text += self.output_text.get(idx, tk.END)
                break
            
            # Add text before hidden range
            full_text += self.output_text.get(idx, next_range[0])
            # Skip hidden range
            idx = next_range[1]
            
        # Clean up double commas or trailing commas that might result from hiding
        full_text = re.sub(r',\s*,', ',', full_text)
        full_text = re.sub(r',\s*\]\]', ']]', full_text) # (shouldn't happen with [[ hidden)
        
        output = full_text.strip()
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
