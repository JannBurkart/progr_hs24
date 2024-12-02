import customtkinter as ctk
from tkinter import filedialog, messagebox
import ifcopenshell


class IFCSplitter:
    def __init__(self, root):
        # Setze CustomTkinter-Erscheinung und Theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self.root = root
        self.root.title("IFC Splitter")
        self.root.geometry("750x400")
        self.root.configure(bg="#1e1e1e")  # Hintergrund

        # Initialisiere IFC-Modell und gefilterte Elemente
        self.ifc_model = None
        self.filtered_elements = []

        # Dashboard-Widgets erstellen
        self.create_widgets()

    def create_widgets(self):
        """Erstellt die Benutzeroberfläche."""
        # Header
        header_label = ctk.CTkLabel(
            self.root, text="IFC Splitter", font=("Arial", 24, "bold"), text_color="white"
        )
        header_label.pack(pady=20)

        # Dashboard-Container
        container = ctk.CTkFrame(self.root, corner_radius=10, fg_color="#2e2e2e")  # Dashboard-Panel
        container.pack(pady=10, padx=20, fill="both", expand=True)

        # Hochladen-Button
        upload_button = ctk.CTkButton(
            container, text="IFC-Datei hochladen", command=self.load_ifc, fg_color="#4a4a4a", hover_color="#5a5a5a"
        )
        upload_button.pack(pady=10, padx=20)

        # Dropdown-Menü für Filter
        self.category_var = ctk.StringVar(value="Kategorie wählen")
        dropdown = ctk.CTkOptionMenu(
            container,
            variable=self.category_var,
            values=["Außenwände", "Innenwände", "Stützen", "Fenster", "Türen", "Geschossdecken", "Gelände"],
            fg_color="#4a4a4a",
            button_color="#5a5a5a",
        )
        dropdown.pack(pady=10, padx=20)

        # Filtern-Button
        filter_button = ctk.CTkButton(
            container, text="Filtern", command=self.filter_elements, fg_color="#4a4a4a", hover_color="#5a5a5a"
        )
        filter_button.pack(pady=10, padx=20)

        # Exportieren-Button
        export_button = ctk.CTkButton(
            container, text="Neues IFC exportieren", command=self.export_ifc, fg_color="#4a4a4a", hover_color="#5a5a5a"
        )
        export_button.pack(pady=10, padx=20)

        # Status-Anzeige
        self.status_label = ctk.CTkLabel(
            container, text="Status: Bereit", font=("Arial", 14), text_color="green"
        )
        self.status_label.pack(pady=20, padx=20)

    def load_ifc(self):
        """Lädt eine IFC-Datei."""
        file_path = filedialog.askopenfilename(filetypes=[("IFC-Dateien", "*.ifc")])
        if file_path:
            try:
                self.ifc_model = ifcopenshell.open(file_path)
                self.status_label.configure(text=f"IFC-Datei geladen: {file_path}", text_color="green")
            except Exception as e:
                self.status_label.configure(text=f"Fehler: {e}", text_color="red")

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
            self.filtered_elements = self.ifc_model.by_type("IfcColumn")
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
        self.status_label.configure(text=f"{count} Elemente in Kategorie '{category}' gefunden.", text_color="blue")

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

                # Kopiere globale relevante Objekte
                for obj_type in ["IfcProject", "IfcSite", "IfcBuilding"]:
                    for obj in self.ifc_model.by_type(obj_type):
                        new_model.add(obj)

                # Kopiere Bauteile und deren Relationen
                for elem in self.filtered_elements:
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
                self.status_label.configure(text=f"Export erfolgreich: {file_path}", text_color="green")
            except Exception as e:
                self.status_label.configure(text=f"Fehler beim Export: {e}", text_color="red")


# Hauptprogramm
if __name__ == "__main__":
    app = ctk.CTk()
    splitter = IFCSplitter(app)
    app.mainloop()