import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox, Button, Label, Frame
import ifcopenshell


class IFCSplitter:
    def __init__(self, root):
        self.root = root
        self.root.title("IFC Splitter")
        self.root.geometry("500x200")
        
        # Initialisiere IFC-Modell und gefilterte Elemente
        self.ifc_model = None
        self.filtered_elements = []

        # UI-Elemente
        self.create_widgets()

    def create_widgets(self):
        """Erstellt die Benutzeroberfläche."""
        # Oberes Frame für Datei und Filteroptionen
        frame_top = Frame(self.root, padding=10)
        frame_top.pack(fill=tk.X, pady=10)

        # IFC-Datei hochladen
        Button(frame_top, text="IFC-Datei hochladen", command=self.load_ifc).pack(side=tk.LEFT, padx=10)

        # Dropdown für Filter
        self.category_var = tk.StringVar()
        self.category_var.set("Kategorie wählen")
        Label(frame_top, text="Kategorie:").pack(side=tk.LEFT, padx=5)
        self.dropdown = Combobox(frame_top, textvariable=self.category_var, state="readonly", width=20)
        self.dropdown['values'] = ["Außenwände", "Innenwände", "Stützen", "Fenster", "Türen", "Geschossdecken", "Gelände"]
        self.dropdown.pack(side=tk.LEFT, padx=10)

        # Filter-Button
        Button(frame_top, text="Filtern", command=self.filter_elements).pack(side=tk.LEFT, padx=10)

        # Exportieren
        frame_bottom = Frame(self.root, padding=10)
        frame_bottom.pack(fill=tk.X, pady=10)

        Button(frame_bottom, text="Neues IFC exportieren", command=self.export_ifc).pack(side=tk.LEFT, padx=10)

        # Statusanzeige
        self.status_label = Label(self.root, text="Status: Bereit", foreground="green", anchor="w")
        self.status_label.pack(fill=tk.X, padx=10, pady=10)

    def load_ifc(self):
        """Lädt eine IFC-Datei."""
        file_path = filedialog.askopenfilename(filetypes=[("IFC-Dateien", "*.ifc")])
        if file_path:
            try:
                self.ifc_model = ifcopenshell.open(file_path)
                self.status_label.config(text=f"IFC-Datei geladen: {file_path}", foreground="green")
            except Exception as e:
                self.status_label.config(text=f"Fehler: {e}", foreground="red")

    def filter_elements(self):
        """Filtert Elemente basierend auf der ausgewählten Kategorie."""
        if not self.ifc_model:
            messagebox.showwarning("Warnung", "Bitte lade zuerst eine IFC-Datei!")
            return
        
        category = self.category_var.get()
        if category == "Kategorie wählen":
            messagebox.showwarning("Warnung", "Bitte wähle eine Kategorie aus!")
            return
        
        if category == "Außenwände":
            elements = self.ifc_model.by_type("IfcWall")
            self.filtered_elements = self.filter_by_property(elements, "IsExternal", True)
        elif category == "Innenwände":
            elements = self.ifc_model.by_type("IfcWall")
            self.filtered_elements = self.filter_by_property(elements, "IsExternal", False)
        elif category == "Stützen":
            elements = self.ifc_model.by_type("IfcColumn")
        elif category == "Fenster":
            self.filtered_elements = self.ifc_model.by_type("IfcWindow")
        elif category == "Türen":
            self.filtered_elements = self.ifc_model.by_type("IfcDoor")
        elif category == "Geschossdecken":
            self.filtered_elements = self.ifc_model.by_type("IfcSlab")
        elif category == "Gelände":
            self.filtered_elements = self.ifc_model.by_type("IfcGeographicElement")
        else:
            self.filtered_elements = []

        count = len(self.filtered_elements)
        self.status_label.config(text=f"{count} Elemente in Kategorie '{category}' gefunden.", foreground="blue")

    def filter_by_property(self, elements, property_name, expected_value):
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

    def export_ifc(self):
        """Exportiert die gefilterten Elemente in eine neue IFC-Datei."""
        if not self.filtered_elements:
            messagebox.showwarning("Warnung", "Keine gefilterten Elemente zum Exportieren!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".ifc", filetypes=[("IFC-Dateien", "*.ifc")])
        if file_path:
            try:
                # Neues IFC-Modell mit dem gleichen Schema wie das Original erstellen
                new_model = ifcopenshell.file(schema=self.ifc_model.schema)

                # Kopiere globale relevante Objekte wie IfcProject, IfcSite, IfcBuilding
                project = self.ifc_model.by_type("IfcProject")[0]
                new_model.add(project)

                for site in self.ifc_model.by_type("IfcSite"):
                    new_model.add(site)

                for building in self.ifc_model.by_type("IfcBuilding"):
                    new_model.add(building)

                # Kopiere Bauteile und deren Relationen
                for elem in self.filtered_elements:
                    new_model.add(elem)

                    # Kopiere Relationen, z. B. IfcRelContainedInSpatialStructure
                    if hasattr(elem, "IsContainedInStructure"):
                        for rel in elem.IsContainedInStructure:
                            new_model.add(rel)

                    # Kopiere geometrische und verwandte Daten
                    if hasattr(elem, "Representation") and elem.Representation:
                        new_model.add(elem.Representation)

                    # Kopiere zugehörige Assoziationen, Materialien etc.
                    if hasattr(elem, "HasAssociations"):
                        for association in elem.HasAssociations:
                            new_model.add(association)

                # Schreibe die neue Datei
                new_model.write(file_path)
                self.status_label.config(text=f"Export erfolgreich: {file_path}", foreground="green")
            except Exception as e:
                self.status_label.config(text=f"Fehler beim Export: {e}", foreground="red")


# Hauptprogramm
if __name__ == "__main__":
    root = tk.Tk()
    app = IFCSplitter(root)
    root.mainloop()