import json

with open('peds_templates.json', 'r') as f:
    data = json.load(f)

data['conditional_logic'] = {
    "condition_map": {
        "wcc": ["well_child"],
        "asthma_stable": ["illness"],
        "asthma_exacerbation": ["illness"],
        "uri": ["illness"],
        "adhd_stable": ["adhd", "pcmh"],
        "adhd_titration": ["adhd", "pcmh"],
        "adhd_comprehensive": ["adhd", "pcmh"],
        "otitis_media": ["ear_infection", "illness"],
        "pharyngitis": ["illness", "strep_test"],
        "strep_comprehensive": ["illness", "strep_test"],
        "obesity": ["obesity", "weight", "pcmh"],
        "obesity_comprehensive": ["obesity", "weight", "pcmh"],
        "constipation": ["gi_symptoms"],
        "gerd": ["gi_symptoms"],
        "eczema": ["skin_condition"],
        "headache": ["illness"],
        "anxiety": ["mental_health"],
        "depression": ["mental_health"],
        "injury": ["injury"],
        "newborn_0_28": ["well_child"]
    },
    "phrases": {
        "well_child": "All forms, labs, immunizations, and patient concerns reviewed and addressed appropriately. Screening questions, past medical history, past social history, medications, and growth chart reviewed. Age-appropriate anticipatory guidance reviewed and printed in AVS. Parent questions addressed.",
        "illness": "Recommended supportive care with OTC medications as needed. Return precautions given including increasing pain, worsening fever, dehydration, new symptoms, prolonged symptoms, worsening symptoms, and other concerns. Caregiver expressed understanding and agreement with treatment plan.",
        "injury": "Recommended supportive care with Tylenol, Motrin, rest, ice, compression, elevation, and gradual return to activity as appropriate. Return precautions given including increasing pain, swelling, or failure to improve.",
        "ear_infection": "Risk of untreated otitis media includes persistent pain and fever, hearing loss, and mastoiditis.",
        "strep_test": "Risk of untreated strep throat includes rheumatic fever and peritonsillar abscess. This problem is moderate risk due to pending lab results which may necessitate further pharmacologic management.",
        "dehydration_gi": "Patient is at risk for dehydration, which would warrant emergency room care or admission for IV fluids.",
        "breathing": "Patient is at risk for worsening respiratory distress and clinical deterioration, which would need emergency room care or hospital admission.",
        "pcmh": "PCMH Reminder"
    }
}

with open('peds_templates.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Updated conditions in peds_templates.json")
