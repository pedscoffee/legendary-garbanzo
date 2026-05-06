import re

with open('peds_charting_tool.py', 'r') as f:
    content = f.read()

# Remove the old check_macro bindings
content = content.replace("        self.input_text.bind('<space>', self.check_macro)\n", "")
content = content.replace("        self.input_text.bind('<Return>', self.check_macro)\n", "")

# Remove check_macro function entirely
content = re.sub(r'    def check_macro\(self, event\):.*?    def insert_autocomplete', '    def insert_autocomplete', content, flags=re.DOTALL)

# Update on_typing to detect double space
new_on_typing = """    def on_typing(self, event=None):
        \"\"\"Handle typing events - reset auto-copy timer and show autocomplete\"\"\"
        if event and event.keysym in ('space', 'Return', 'BackSpace', 'Escape'):
            self.autocomplete_list.grid_remove()
        elif event and event.char and event.char.isalnum():
            text_content = self.input_text.get("1.0", "end-1c").strip()
            words = text_content.split()
            if words:
                last_word = words[-1].lower()
                suggestions = []
                for p in self.patterns:
                    display_pat = p['pattern'].replace('\\\\s+', ' ').replace('|', ' or ').replace('\\\\', '')
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
        self.typing_timer = self.root.after(self.auto_copy_delay, self.auto_process_and_copy)"""

content = re.sub(r'    def on_typing\(self, event=None\):.*?        self.typing_timer = self.root.after\(self.auto_copy_delay, self.auto_process_and_copy\)', new_on_typing, content, flags=re.DOTALL)

# Update process_input
new_process_input = """    def process_input(self):
        \"\"\"Process shorthand input and expand to full text\"\"\"
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
                
        self.render_output()"""

content = re.sub(r'    def process_input\(self\):.*?        self.status_label.config\(text="Added as free text"\)', new_process_input, content, flags=re.DOTALL)

# Update add_template
new_add_template = """    def add_template(self, template_key):
        \"\"\"Add a template to the note\"\"\"
        if template_key in self.templates:
            current = self.input_text.get("1.0", "end-1c").strip()
            if current:
                self.input_text.insert("end", f"\\n.{template_key} ")
            else:
                self.input_text.insert("end", f".{template_key} ")
            self.process_input()
            self.copy_to_clipboard()
            self.status_label.config(text=f"Added: {template_key}")"""

content = re.sub(r'    def add_template\(self, template_key\):.*?            self.status_label.config\(text=f"Added: \{template_key\}"\)', new_add_template, content, flags=re.DOTALL)

with open('peds_charting_tool.py', 'w') as f:
    f.write(content)
print("Updated!")
