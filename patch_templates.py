import json

with open('peds_templates.json', 'r') as f:
    data = json.load(f)

templates = data['templates']

# 1. ADHD
templates['adhd_comprehensive'] = {
    "title": "ADHD A&P",
    "content": [
        "- Patient has kept important appointments since last visit (referrals, diagnostic studies, etc): {appointments_kept:Yes}",
        "- Progress on goals since last visit: {progress:good progress}",
        "- Barrier: {barrier:No barriers}",
        "- Readiness to Change Score: {readiness_score:10}",
        "- Psychoeducational: Psychoeducational reassessment is not required at this time",
        "- Medication compliance: {compliance:good progress}",
        "- Referral made to Community Resource: {community_referral:No}",
        "- Self-Management logs explained and given to patient: {logs_explained:No}",
        "- Depression Screening: See chart",
        "",
        "Self Care Plan:",
        "Diet is not a direct cause of attention deficit disorder, but food can and does affect your child's mental state, which in turn seems to affect behavior. Monitoring and modifying what, when, and how much your child eats can help decrease the symptoms of ADD/ADHD. Eating small meals more often will be helpful. Children with ADD/ADHD are notorious for not eating regularly. They might not eat for hours and then binge on whatever is around. Prevent unhealthy eating habits by scheduling regular nutritious meals or snacks for your child no more than three hours apart. Get rid of the junk foods in your home. Put fatty and sugary foods off-limits when eating out. Turn off television shows riddled with junk-food ads. Give your child a daily vitamin-and-mineral supplement.",
        "",
        "Children with ADHD often have energy to burn. Organized sports and other physical activities can help them get their energy out in healthy ways and focus their attention on specific movements and skills. The benefits of physical activity are endless: it improves concentration, decreases depression and anxiety, and promotes brain growth. Most importantly for children with attention deficits, however, is the fact that exercise leads to better sleep, which in turn can also reduce the symptoms of ADHD. Find a sport that your child will enjoy and that suits his or her strengths. For example, sports such as softball that involve a lot of down time are not the best fit for children with attention problems. Individual or team sports like basketball and football require constant motion are better options."
    ]
}

# 2. Obesity
templates['obesity_comprehensive'] = {
    "title": "OBESITY ASSESSMENT",
    "content": [
        "- Problems associated with obesity: At risk for or currently experiencing comorbidities secondary to obesity",
        "- Patient has kept important appointments since last visit (referrals, diagnostic studies, etc): {appointments_kept:Yes}",
        "- Progress on goals since last visit: {progress:No}",
        "- Referral made to Community Resource: {community_referral:No}",
        "- Referred to Nutrition Education Class (BMI >95%): {nutrition_referral:No}",
        "- Referred to Nutrition Diabetic Education Class: {diabetic_referral:No}",
        "- Nutrition Class has been completed: {nutrition_completed:No}",
        "- Referred to Endocrinology: {endo_referral:No}",
        "- Depression screening completed: See chart",
        "- Self-Management logs explained and given to patient: {logs_explained:No}",
        "- Self-Management abilities: {management_abilities:Adequate}",
        "",
        "Self Care Plan:",
        "To reduce the amount of saturated fat in your diet, you should avoid all fried foods and most nuts. You must learn to plan ahead in order to have healthy snacks available and to avoid fast-food meals. Child should exercise at least 60 minutes every day. Sedentary activity such as watching TV or playing video games restricted to less than 2 hrs each day. Exercise may include walking, swimming, running or multi-media programs that require physical activity. The important factor is that overall movement is increased at a level within his/her physical limits. Barriers are identified and options for resolution discussed.",
        "",
        "Patient Goals:",
        "- Dietary Goal: Appropriate calorie intake, Reduction of saturated fat, Avoidance of dense foods (fast food or fruit juices), Increase of fiber-fruit and vegetables",
        "  - Barrier: {diet_barrier:none}",
        "- Exercise Goal: 60 minutes/day. Sedentary activity (TV, video games) restricted to < 2 hrs/day",
        "  - Barrier: {exercise_barrier:none}",
        "- Wt/BMI Goal: Attain/maintain goal weight/Ideal BMI (<85%)",
        "  - Barrier: {weight_barrier:none}",
        "",
        "Follow up next well check for abnormal labs/weight management"
    ]
}

# 3. Strep
templates['strep_comprehensive'] = {
    "title": "STREP A&P",
    "content": [
        "- Patient has kept important appointments since last visit (referrals, diagnostic studies, etc): {appointments_kept:yes}",
        "- Progress on goals since last visit: {progress:New diagnosis/patient no prior goals set}",
        "- Strep Goal: Complete medication as prescribed",
        "  - Barrier: {barrier:No barrier identified}",
        "- Readiness to Change Score: {readiness_score:10}",
        "- Referral made to Community Resource: {community_referral:Assessed and not required at this time.}",
        "- Self-Management logs explained and given to patient: {logs_explained:None indicated at this time.}",
        "- Self-Management abilities: {management_abilities:Has adequate self-management skills}",
        "- Medication compliance: {compliance:good}",
        "",
        "Self Care Plan:",
        "Antibiotics treat a bacterial infection. Your child should feel better within 2 to 3 days after antibiotics are started. Give your child his antibiotics until they are gone, unless your child's healthcare provider says to stop them. Your child may return to school 24 hours after he starts antibiotic medicine.",
        "",
        "Acetaminophen (Tylenol) decreases pain and fever. Ask how much to give your child and how often to give it. Follow directions. Acetaminophen can cause liver damage if not taken correctly.",
        "",
        "NSAIDs, such as ibuprofen, help decrease swelling, pain, and fever. This medicine is available with or without a doctor's order. NSAIDs can cause stomach bleeding or kidney problems in certain people. Always read the medicine label and follow directions. Do not give these medicines to children under 6 months of age without direction from your child's healthcare provider.",
        "",
        "Give your child plenty of liquids. Liquids will help soothe your child's throat. Ask your child's healthcare provider how much liquid to give your child each day. Give your child warm or frozen liquids. Warm liquids include hot chocolate, sweetened tea, or soups. Frozen liquids include ice pops. Do not give your child acidic drinks such as orange juice, grapefruit juice, or lemonade. Acidic drinks can make your child's throat pain worse.",
        "",
        "Change your child's toothbrush after he/she has taken antibiotic for 72 hours."
    ]
}

# 4. 0-28 Days
templates['newborn_0_28'] = {
    "title": "0-28 DAYS OLD A&P",
    "content": [
        "- Patient has kept important appointments since last visit (referrals, diagnostic studies, etc): {appointments_kept:yes}",
        "- Progress on goals since last visit: {progress:New diagnosis/patient no prior goals set}",
        "- 0-28 Day Old Infant Goal: Normal Newborn Care",
        "  - Barrier: {barrier:none}",
        "- Readiness to Change Score: {readiness_score:10}",
        "- Referral made to Community Resource: {community_referral:Assessed and is not required at this time.}",
        "- Self-Management logs explained and given to patient: {logs_explained:None indicated at this time.}",
        "- Self-Management abilities: {management_abilities:Has adequate self-management skills}",
        "",
        "Self Care Plan:",
        "Emergency room with rectal temp > 100.4.",
        "Nothing to eat other than breastmilk or formula, and for bottle fed infants, make sure you mix powder formula with 1 scoop powder to 2 oz water. For the first two weeks, feed your baby at least every 3-4 hours during the day and night.",
        "Always lay your baby on his or her back to sleep. This position can help reduce your baby's risk for sudden infant death syndrome (SIDS)."
    ]
}

# 5. Eczema (updating existing or creating new, let's update existing to include the text)
if 'eczema' in templates:
    templates['eczema']['content'].extend([
        "",
        "Discussed supportive care including importance of frequent moisturization, appropriate use of topical steroids, wet wrap therapy, and return precautions."
    ])

# Add patterns and buttons
data['quick_buttons'].extend([
    {"label": "ADHD A&P", "template": "adhd_comprehensive"},
    {"label": "Obesity A&P", "template": "obesity_comprehensive"},
    {"label": "Strep A&P", "template": "strep_comprehensive"},
    {"label": "Newborn A&P", "template": "newborn_0_28"}
])

data['patterns'].extend([
    {
        "pattern": "adhd\\\\s+comp|adhd\\\\s+ap",
        "template": "adhd_comprehensive",
        "defaults": {}
    },
    {
        "pattern": "obesity\\\\s+comp|obesity\\\\s+ap",
        "template": "obesity_comprehensive",
        "defaults": {}
    },
    {
        "pattern": "strep\\\\s+comp|strep\\\\s+ap",
        "template": "strep_comprehensive",
        "defaults": {}
    },
    {
        "pattern": "newborn|0-28",
        "template": "newborn_0_28",
        "defaults": {}
    }
])

with open('peds_templates.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Updated peds_templates.json successfully.")
