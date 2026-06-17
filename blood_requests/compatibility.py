"""Blood-type compatibility rules for the donation matching system."""

# Maps each donor blood type to the recipient types it can supply.
COMPATIBILITY_MAP = {
    'O-':  ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
    'O+':  ['O+', 'A+', 'B+', 'AB+'],
    'A-':  ['A-', 'A+', 'AB-', 'AB+'],
    'A+':  ['A+', 'AB+'],
    'B-':  ['B-', 'B+', 'AB-', 'AB+'],
    'B+':  ['B+', 'AB+'],
    'AB-': ['AB-', 'AB+'],
    'AB+': ['AB+'],
}


def compatible_recipient_types(donor_blood_type: str) -> list[str]:
    """
    Return the list of recipient blood types that *donor_blood_type* can supply.

    Used when filtering BloodRequests to show only the ones a given donor
    can actually help with. Returns an empty list for unknown blood types.
    """
    return COMPATIBILITY_MAP.get(donor_blood_type, [])


def compatible_donor_types(recipient_blood_type: str) -> list[str]:
    """
    Return the list of donor blood types that can donate to *recipient_blood_type*.

    Used when a new BloodRequest is created to find which donors to notify.
    """
    return [
        donor for donor, recipients in COMPATIBILITY_MAP.items()
        if recipient_blood_type in recipients
    ]
