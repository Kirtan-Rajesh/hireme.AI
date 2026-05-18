from main import parse_company_domains, extract_company_name_from_title, is_generic_company_name

sample = '''📦 [CACHED] 📄 AI Evaluator - Generalist at Sama - Startup Jobs
Source: https://startup.jobs/ai-evaluator-generalist-sama-5685791
Experience in GenAI is an added advantage. Preferred Qualifications: Strong critical thinking, reasoning, and exceptional problem-solving skills. Excellent ... Missing: early- stage hiring Developer

---
📄 Principal Software Engineer @ Harness | Simplify Jobs
Source: https://simplify.jobs/p/7f39caed-202d-4868-8de9-72fe22fab7e8/Principal-Software-Engineer
Workday selected Harness f...
'''

print("Test extract_company_name_from_title:")
title1 = "AI Evaluator - Generalist at Sama - Startup Jobs"
title2 = "Principal Software Engineer @ Harness | Simplify Jobs"
domain1 = "startup.jobs"
domain2 = "simplify.jobs"

print(f"  {repr(title1)} from {domain1} => {repr(extract_company_name_from_title(title1, domain1))}")
print(f"  {repr(title2)} from {domain2} => {repr(extract_company_name_from_title(title2, domain2))}")

print("\nTest is_generic_company_name:")
print(f"  'Usa' => {is_generic_company_name('Usa')}")
print(f"  'Simplify' => {is_generic_company_name('Simplify')}")
print(f"  'Sama' => {is_generic_company_name('Sama')}")
print(f"  'Harness' => {is_generic_company_name('Harness')}")

print("\n" + "="*60)
result = parse_company_domains(sample, limit=10)
print(f'Found {len(result)} companies:')
for c in result:
    print(f"  - {c['company']} ({c['domain']}) from {c['source']}")
