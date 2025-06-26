def calculate_derived_leads(lead1, lead2):
    lead3 = lead2 - lead1
    avr = - (lead1 + lead2) / 2
    avl = (lead1 - lead3) / 2
    avf = (lead2 + lead3) / 2
    return lead3, avr, avl, avf