import ifcopenshell
from tkinter import filedialog, messagebox

def export_ifc(export_model):
    """Exportiert die gefilterten Elemente in eine neue IFC-Datei."""
    if not export_model.filtered_elements:
        messagebox.showwarning("Warnung", "Keine gefilterten Elemente zum Exportieren!")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".ifc", filetypes=[("IFC-Dateien", "*.ifc")])
    if file_path:
        try:
            # Neues IFC-Modell mit dem gleichen Schema wie das Original erstellen
            new_model = ifcopenshell.file(schema=export_model.ifc_model.schema)

            # Kopiere globale relevante Objekte
            for obj_type in ["IfcProject", "IfcSite", "IfcBuilding"]:
                for obj in export_model.ifc_model.by_type(obj_type):
                    new_model.add(obj)

            # Kopiere Bauteile und deren Relationen
            for elem in export_model.filtered_elements:
                new_model.add(elem)

                # Kopiere Relationen und andere Daten
                if hasattr(elem, "IsContainedInStructure"):
                    for rel in elem.IsContainedInStructure:
                        new_model.add(rel)

                if hasattr(elem, "Representation") and elem.Representation:
                    new_model.add(elem.Representation)

                if hasattr(elem, "HasAssociations"):
                    for assoc in elem.HasAssociations:
                        new_model.add(assoc)

            new_model.write(file_path)
            export_model.status_label.configure(text=f"Export erfolgreich: {file_path}", text_color="green")
        except Exception as e:
            export_model.status_label.configure(text=f"Fehler beim Export: {e}", text_color="red")