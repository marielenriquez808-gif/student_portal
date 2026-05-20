from django.db import migrations


DEPARTMENTS_AND_PROGRAMS = [
    {
        'name': 'Department of Computer Studies',
        'code': 'DCS',
        'programs': [
            ('BS Information Technology', 'BSIT'),
            ('BS Computer Science', 'BSCS'),
            ('BS Computer Engineering', 'BSCpE'),
        ],
    },
    {
        'name': 'Department of College of Criminal Justice Education',
        'code': 'DCCJE',
        'programs': [
            ('BS Criminology', 'BSCrim'),
        ],
    },
    {
        'name': 'Department of General Teacher Training',
        'code': 'DGTT',
        'programs': [
            ('Bachelor of Elementary Education', 'BEEd'),
            ('Bachelor of Secondary Education', 'BSEd'),
        ],
    },
    {
        'name': 'Department of Business and Management',
        'code': 'DBM',
        'programs': [
            ('BS Business Administration', 'BSBA'),
            ('BS Entrepreneurship', 'BSEntrep'),
        ],
    },
    {
        'name': 'Department of Industrial Technology',
        'code': 'DIT',
        'programs': [
            ('BS Industrial Technology', 'BSIT-Ind'),
        ],
    },
]


def seed_data(apps, schema_editor):
    Department = apps.get_model('accounts', 'Department')
    Program = apps.get_model('accounts', 'Program')
    for dept_data in DEPARTMENTS_AND_PROGRAMS:
        dept, _ = Department.objects.get_or_create(
            code=dept_data['code'],
            defaults={'name': dept_data['name']},
        )
        for prog_name, prog_code in dept_data['programs']:
            Program.objects.get_or_create(
                code=prog_code,
                department=dept,
                defaults={'name': prog_name},
            )


def unseed_data(apps, schema_editor):
    Department = apps.get_model('accounts', 'Department')
    codes = [d['code'] for d in DEPARTMENTS_AND_PROGRAMS]
    Department.objects.filter(code__in=codes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_data, unseed_data),
    ]
