COMPATIBILITY_MAP = {
    'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
    'O+': ['O+', 'A+', 'B+', 'AB+'],
    'A-': ['A-', 'A+', 'AB-', 'AB+'],
    'A+': ['A+', 'AB+'],
    'B-': ['B-', 'B+', 'AB-', 'AB+'],
    'B+': ['B+', 'AB+'],
    'AB-': ['AB-', 'AB+'],
    'AB+': ['AB+'],
}


def compatible_recipient_types(donor_blood_type):
    """فصائل المرضى التي يمكن للمتبرع التبرع لها."""
    return COMPATIBILITY_MAP.get(donor_blood_type, [])


def compatible_donor_types(recipient_blood_type):
    """فصائل المتبرعين المؤهلين للتبرع لفصيلة مطلوبة."""
    return [
        donor_type
        for donor_type, recipients in COMPATIBILITY_MAP.items()
        if recipient_blood_type in recipients
    ]
