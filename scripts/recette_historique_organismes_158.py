"""Restituer exactement l'état des autorités avant le lot A05f (1.57).

Utilisé uniquement par les recettes historiques : ne fait aucune mutation en place.
"""
from copy import deepcopy

def sans_a05f(current):
    d = deepcopy(current)
    rows = [a for a in d["authorities"] if a["id"] != "ORG-0756"]
    assert len(rows) == len(d["authorities"]) - 1, "ORG-0756 absente ou dupliquée"
    original = next(a for a in d["authorities"] if a["id"] == "ORG-0756")
    assert original["names"]["preferred"] == "Archéo Atlantica"
    assert original["usage"] == {
        "affiliations_linked": 1, "affiliations_validated": 1,
        "source_occurrences_linked": 1}
    d["authorities"] = rows
    assert d["totals"]["authorities"] == 935
    assert d["totals"]["organismes"] == 735
    assert d["totals"]["catalog_included"] == 683
    d["totals"]["authorities"] -= 1
    d["totals"]["organismes"] -= 1
    d["totals"]["catalog_included"] -= 1
    return d
