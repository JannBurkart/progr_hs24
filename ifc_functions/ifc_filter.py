from tkinter import messagebox

def filter_elements(selected_elem):
    """Filtert Elemente basierend auf den ausgewählten Kategorien."""
    if not selected_elem.ifc_model:
        messagebox.showwarning("Warnung", "Bitte lade zuerst eine IFC-Datei!")
        return

    selected_elem.selected_categories = []
    selected_elem.filtered_elements = []

    for dropdown, category_var in selected_elem.category_dropdowns:
        category = category_var.get()
        if category != "Kategorie wählen":
            selected_elem.selected_categories.append(category)
            selected_elem.filter_category(category)

    count = len(selected_elem.filtered_elements)
    selected_elem.status_label.configure(
        text=f"{count} Elemente in Kategorien {', '.join(selected_elem.selected_categories)} gefunden.",
        text_color="blue"
    )



def filter_category(selected_cat, category):
    """Filtert eine einzelne Kategorie."""
    if category == "Außenwände":
        elements = selected_cat.ifc_model.by_type("IfcWall")
        selected_cat.filtered_elements.extend(selected_cat.filter_by_property(elements, "IsExternal", True))
    elif category == "Innenwände":
        elements = selected_cat.ifc_model.by_type("IfcWall")
        selected_cat.filtered_elements.extend(selected_cat.filter_by_property(elements, "IsExternal", False))
    elif category == "Stützen":
        selected_cat.filtered_elements.extend(selected_cat.ifc_model.by_type("IfcColumn"))
    elif category == "Fenster":
        selected_cat.filtered_elements.extend(selected_cat.ifc_model.by_type("IfcWindow"))
    elif category == "Türen":
        selected_cat.filtered_elements.extend(selected_cat.ifc_model.by_type("IfcDoor"))
    elif category == "Geschossdecken":
        selected_cat.filtered_elements.extend(selected_cat.ifc_model.by_type("IfcSlab"))
    elif category == "Gelände":
        selected_cat.filtered_elements.extend(selected_cat.ifc_model.by_type("IfcGeographicElement"))



def filter_by_property(elements, property_name, expected_value):
    """Filtert Elemente basierend auf einer bestimmten Eigenschaft."""
    filtered = []
    for element in elements:
        for definition in element.IsDefinedBy:
            if definition.is_a("IfcRelDefinesByProperties"):
                property_set = definition.RelatingPropertyDefinition
                if property_set.is_a("IfcPropertySet"):
                    for prop in property_set.HasProperties:
                        if prop.Name == property_name and getattr(prop.NominalValue, "wrappedValue", None) == expected_value:
                            filtered.append(element)
    return filtered