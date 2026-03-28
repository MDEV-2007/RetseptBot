import os
import sys
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.drugs.models import Drug

CATEGORIES = [
    'Antibiotic', 'Painkiller', 'Vitamin', 'Antiviral', 'Antifungal',
    'Antihistamine', 'Antidepressant', 'Antihypertensive', 'Diuretic',
    'Steroid', 'Vaccine', 'Antacid', 'Laxative', 'Sedative', 'Bronchodilator',
    'Anticoagulant', 'Antidiabetic', 'Antiepileptic', 'Immunosuppressant', 'Hormone',
]

PREFIXES = [
    'Amox', 'Cipro', 'Metr', 'Clar', 'Doxi', 'Azith', 'Ceph', 'Pen',
    'Ibup', 'Para', 'Aspir', 'Napr', 'Diclo', 'Keto', 'Tramad',
    'Ator', 'Simva', 'Rosuva', 'Losart', 'Amlodin', 'Ramip', 'Lisi',
    'Metf', 'Gliben', 'Insulin', 'Gliclaz', 'Sitagl', 'Empagl',
    'Omep', 'Panto', 'Ranitidin', 'Esomep', 'Lansop',
    'Cetiriz', 'Loratidin', 'Fexof', 'Diphen', 'Prometh',
    'Fluox', 'Sertral', 'Escital', 'Venlaflax', 'Dulox',
    'Diazep', 'Alpraz', 'Loraze', 'Midaz', 'Zolp',
    'Furos', 'Hydrochlo', 'Spiron', 'Torasem', 'Indap',
    'Prednis', 'Dexameth', 'Betameth', 'Hydrocort', 'Triamcin',
    'Acyclov', 'Valacycl', 'Oseltam', 'Ribavir', 'Tenofov',
    'Flucon', 'Itrakon', 'Vorikon', 'Caspof', 'Nystatin',
    'Morphin', 'Oxycod', 'Fentanyl', 'Codein', 'Buprenor',
    'Warfar', 'Heparin', 'Rivarox', 'Apixab', 'Dabigatr',
    'Salbutam', 'Ipratropi', 'Salmeter', 'Tiotropi', 'Formot',
    'Carbamaz', 'Valproat', 'Phenytoin', 'Levetir', 'Lamotrig',
    'Cyclospor', 'Tacrolim', 'Mycophen', 'Sirolim', 'Azathiopr',
    'Levothyr', 'Methimax', 'Propylth', 'Cabergol', 'Octreot',
]

SUFFIXES = [
    'icillin', 'oxacin', 'idazole', 'omycin', 'cycline', 'azole',
    'prazole', 'sartan', 'dipine', 'pril', 'statin', 'fibrate',
    'formin', 'gliptin', 'gliflozin', 'tidine', 'zine', 'pine',
    'olol', 'alol', 'afil', 'mab', 'nib', 'tide', 'tropin',
    'ine', 'ol', 'am', 'en', 'ate', 'ide', 'one', 'an',
]

DOSAGE_TEMPLATES = [
    '{dose}mg once daily',
    '{dose}mg twice daily (every 12 hours)',
    '{dose}mg three times daily (every 8 hours)',
    '{dose}mg every 6 hours as needed',
    '{dose}mcg inhaled twice daily',
    '{dose}mg orally with food',
    '{dose}mg IV infusion over 30 minutes',
    '{dose}units subcutaneously before meals',
    '{dose}mg at bedtime',
    '{dose}mg loading dose, then {half}mg daily',
]

SIDE_EFFECTS_POOL = [
    'nausea', 'vomiting', 'diarrhea', 'constipation', 'headache',
    'dizziness', 'fatigue', 'insomnia', 'dry mouth', 'rash',
    'itching', 'stomach pain', 'loss of appetite', 'weight gain',
    'weight loss', 'blurred vision', 'muscle pain', 'joint pain',
    'increased heart rate', 'low blood pressure', 'high blood pressure',
    'liver enzyme elevation', 'kidney dysfunction', 'anemia',
    'photosensitivity', 'hair loss', 'sweating', 'tremor',
    'anxiety', 'depression', 'confusion', 'shortness of breath',
    'swelling of ankles', 'hyperglycemia', 'hypoglycemia',
]

DESCRIPTION_TEMPLATES = [
    '{name} is a {category_lower} used to treat {condition}.',
    '{name} belongs to the {category_lower} class of medications.',
    '{name} is prescribed for the management of {condition}.',
    '{name} is a commonly used {category_lower} effective against {condition}.',
    '{name} is indicated for patients with {condition}.',
]

CONDITIONS = [
    'bacterial infections', 'viral infections', 'fungal infections',
    'high blood pressure', 'type 2 diabetes', 'high cholesterol',
    'pain and inflammation', 'acid reflux', 'allergic reactions',
    'depression and anxiety', 'epilepsy', 'heart failure',
    'asthma and COPD', 'blood clots', 'thyroid disorders',
    'autoimmune conditions', 'osteoporosis', 'migraines',
    'urinary tract infections', 'skin conditions',
]


def generate_drug_name(used_names):
    for _ in range(1000):
        prefix = random.choice(PREFIXES)
        suffix = random.choice(SUFFIXES)
        name = prefix + suffix
        # Capitalize nicely
        name = name[0].upper() + name[1:]
        if name not in used_names:
            used_names.add(name)
            return name
    # Fallback with number
    base = random.choice(PREFIXES) + random.choice(SUFFIXES)
    name = base[0].upper() + base[1:] + f'-{random.randint(10,99)}'
    used_names.add(name)
    return name


def generate_dosage():
    template = random.choice(DOSAGE_TEMPLATES)
    dose = random.choice([5, 10, 20, 25, 50, 100, 200, 250, 400, 500, 750, 1000])
    return template.format(dose=dose, half=dose // 2 or dose)


def generate_side_effects():
    effects = random.sample(SIDE_EFFECTS_POOL, random.randint(3, 7))
    return ', '.join(effects).capitalize() + '.'


def generate_description(name, category):
    template = random.choice(DESCRIPTION_TEMPLATES)
    condition = random.choice(CONDITIONS)
    return template.format(name=name, category_lower=category.lower(), condition=condition)


def run():
    existing = set(Drug.objects.values_list('name', flat=True))
    print(f'Existing drugs in DB: {len(existing)}')

    to_create = []
    used_names = set(existing)

    for _ in range(200):
        name = generate_drug_name(used_names)
        category = random.choice(CATEGORIES)
        generic = generate_drug_name(set(used_names))  # unique generic too
        used_names.add(generic)

        to_create.append(Drug(
            name=name,
            generic_name=generic if random.random() > 0.3 else '',
            description=generate_description(name, category),
            dosage_info=generate_dosage(),
            side_effects=generate_side_effects(),
            category=category,
            is_active=random.random() > 0.05,  # 95% active
        ))

    Drug.objects.bulk_create(to_create)
    print(f'Successfully inserted {len(to_create)} drugs.')
    print(f'Total drugs in DB: {Drug.objects.count()}')


if __name__ == '__main__':
    run()
