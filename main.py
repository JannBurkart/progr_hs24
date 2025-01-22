import customtkinter as ctk
from tkinter import filedialog, messagebox
import ifcopenshell
import pandas as pd


class IFCSearcher:
    def __init__(self, root):
        # Setze CustomTkinter-Erscheinung und dark Theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self.root = root
        self.root.title("IFC Searcher")
        self.root.geometry("750x500")
        self.root.configure(bg="#1e1e1e")  # <- Hintergrund

        # IFC-Modell und gefilterte Elemente
        self.ifc_model = None
        self.selected_categories = []
        self.category_dropdowns = []

        # Dashboard-Widgets erstellen
        self.create_widgets()

    def create_widgets(self):
        """Erstellt die Benutzeroberfläche."""
        # Header
        header_label = ctk.CTkLabel(
            self.root, text="IFC Searcher", font=("Arial", 24, "bold"), text_color="white"
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

        # Kategorie-Auswahl (Dropdowns und Plus)
        category_frame = ctk.CTkFrame(container, fg_color="#2e2e2e")
        category_frame.pack(pady=10, padx=20, fill="y")

        self.add_category_dropdown(category_frame)  # <- Initiales Dropdown

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

        # Excel-Export-Button
        excel_export_button = ctk.CTkButton(
            container, text="Als Excel exportieren", command=self.export_excel, fg_color="#4a4a4a", hover_color="#5a5a5a"
        )
        excel_export_button.pack(pady=10, padx=20)

        # Status-Anzeige
        self.status_label = ctk.CTkLabel(
            container, text="Status: Bereit", font=("Arial", 14), text_color="green"
        )
        self.status_label.pack(pady=20, padx=20)

    def add_category_dropdown(self, parent):
        """Fügt ein neues Dropdown-Menü unter den bisherigen hinzu und zentriert sie."""
        category_var = ctk.StringVar(value="Kategorie wählen")
        dropdown = ctk.CTkOptionMenu(
            parent,
            variable=category_var,
            values=["Aussenwände", "Innenwände", "Geschossdecken", "Dächer", "Stützen", "Fenster", "Türen", "Absturzsicherungen", "Treppen", "Gelände"],
            fg_color="#4a4a4a",
            button_color="#5a5a5a",
        )
        # Zentriere das Dropdown im Parent
        dropdown.grid(row=len(self.category_dropdowns), column=0, padx=10, pady=5, sticky="nsew")
        self.category_dropdowns.append((dropdown, category_var))

        # Aktualisiere die Position des Plus-Buttons immer rechts neben dem letzten Dropdown
        self.update_plus_button_position(parent)

    def update_plus_button_position(self, parent):
        """Positioniert den Plus-Button rechts neben dem letzten Dropdown-Menü."""
        if hasattr(self, "plus_button"):
            self.plus_button.destroy()  # <- Entferne den alten Button
        self.plus_button = ctk.CTkButton(
            parent, text="+", width=30, command=lambda: self.add_category_dropdown(parent),
            fg_color="#4a4a4a", hover_color="#5a5a5a"
        )
        self.plus_button.grid(row=len(self.category_dropdowns)-1, column=1, padx=10, pady=5, sticky="nsew")

    # Beginn der Funktionen
    # IFC hochladen
    def load_ifc(self):
        """Lädt eine IFC-Datei."""
        file_path = filedialog.askopenfilename(filetypes=[["IFC-Dateien", "*.ifc"]])
        if file_path:
            try:
                self.ifc_model = ifcopenshell.open(file_path)
                self.status_label.configure(text=f"IFC-Datei geladen: {file_path}", text_color="green")
            except Exception as e:
                self.status_label.configure(text=f"Fehler: {e}", text_color="red")

    # Elemente nach Kategorie filtern
    def filter_elements(self):
        """Filtert Elemente basierend auf den ausgewählten Kategorien."""
        if not self.ifc_model:
            messagebox.showwarning("Warnung", "Bitte lade zuerst eine IFC-Datei!")
            return

        self.selected_categories = []
        self.filtered_elements = []

        for dropdown, category_var in self.category_dropdowns:
            category = category_var.get()
            if category != "Kategorie wählen":
                self.selected_categories.append(category)
                self.filter_category(category)

        count = len(self.filtered_elements)
        self.status_label.configure(
            text=f"{count} Elemente in Kategorien {', '.join(self.selected_categories)} gefunden.",
            text_color="blue"
        )

    # Kategorien definieren
    def filter_category(self, category):
        """Filtert eine einzelne Kategorie."""
        if category == "Aussenwände":
            elements = self.ifc_model.by_type("IfcWall")
            self.filtered_elements.extend(self.filter_by_property(elements, "IsExternal", True))
        elif category == "Innenwände":
            elements = self.ifc_model.by_type("IfcWall")
            self.filtered_elements.extend(self.filter_by_property(elements, "IsExternal", False))
        elif category == "Geschossdecken":
            self.filtered_elements.extend(self.ifc_model.by_type("IfcSlab"))
        elif category == "Dächer":
            self.filtered_elements.extend(self.ifc_model.by_type("IfcRoof"))
        elif category == "Stützen":
            self.filtered_elements.extend(self.ifc_model.by_type("IfcColumn"))
        elif category == "Fenster":
            self.filtered_elements.extend(self.ifc_model.by_type("IfcWindow"))
        elif category == "Türen":
            self.filtered_elements.extend(self.ifc_model.by_type("IfcDoor"))
        elif category == "Absturzsicherungen":
            self.filtered_elements.extend(self.ifc_model.by_type("IfcRailing"))
        elif category == "Treppen":
            self.filtered_elements.extend(self.ifc_model.by_type("IfcStairFlight"))
        elif category == "Gelände":
            self.filtered_elements.extend(self.ifc_model.by_type("IfcGeographicElement"))

    # Bauteil-Infos werden mitgegeben
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

    # Neues IFC exportieren
    def export_ifc(self):
        """Exportiert die gefilterten Elemente in eine neue IFC-Datei."""
        if not self.filtered_elements:
            messagebox.showwarning("Warnung", "Keine gefilterten Elemente zum Exportieren!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".ifc", filetypes=[["IFC-Dateien", "*.ifc"]])
        if file_path:
            try:
                # Neues IFC-Modell mit dem gleichen Schema wie das Original erstellen
                new_model = ifcopenshell.file(schema=self.ifc_model.schema)

                # Kopiere global relevante Objekte
                for obj_type in ["IfcProject", "IfcSite", "IfcBuilding"]:
                    for obj in self.ifc_model.by_type(obj_type):
                        new_model.add(obj)

                # Kopiere Bauteile
                for element in self.filtered_elements:
                    new_model.add(element)

                # Speichere die neue IFC-Datei
                new_model.write(file_path)
                self.status_label.configure(
                    text=f"Gefilterte IFC-Datei exportiert: {file_path}", text_color="green"
                )
            except Exception as e:
                self.status_label.configure(text=f"Fehler: {e}", text_color="red")

    def get_quantities_dict(self, element):
        """Extrahiert Mengeninformationen aus einem IFC-Element."""
        quantities = {}
        for definition in element.IsDefinedBy:
            if definition.is_a("IfcRelDefinesByProperties"):
                property_set = definition.RelatingPropertyDefinition
                if property_set.is_a("IfcElementQuantity"):
                    for quantity in property_set.Quantities:
                        quantities[quantity.Name] = getattr(quantity, "NominalValue", getattr(quantity, "LengthValue", None))
        return quantities

    # Exportieren nach Excel
    def export_excel(self):
        """Exportiert die gefilterten Elemente und ihre Maße in eine Excel-Datei."""
        if not self.filtered_elements:
            messagebox.showwarning("Warnung", "Keine gefilterten Elemente zum Exportieren!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[["Excel-Dateien", "*.xlsx"]])
        if file_path:
            try:
                data = []
                for element in self.filtered_elements:
                    row = {
                        "GlobalId": element.GlobalId,
                        "Name": element.Name,
                        "Type": element.is_a(),
                    }
                    quantities = self.get_quantities_dict(element)
                    row.update(quantities)

                    # Füge geometrische Maße hinzu
                    if hasattr(element, "Representation") and element.Representation:
                        for representation in element.Representation.Representations:
                            if representation.is_a("IfcShapeRepresentation"):
                                for item in representation.Items:
                                    if item.is_a("IfcExtrudedAreaSolid"):
                                        row["Length"] = getattr(item, "Depth", "N/A")
                                        row["Width"] = getattr(item.Profile.ProfileWidth, "wrappedValue", "N/A") \
                                            if hasattr(item.Profile, "ProfileWidth") else "N/A"
                                        row["Height"] = getattr(item.Profile.ProfileHeight, "wrappedValue", "N/A") \
                                            if hasattr(item.Profile, "ProfileHeight") else "N/A"
                                    elif item.is_a("IfcBoundingBox"):
                                        row["X_Dimension"] = item.XDim
                                        row["Y_Dimension"] = item.YDim
                                        row["Z_Dimension"] = item.ZDim

                    data.append(row)

                # Speichere Daten in eine Excel-Datei
                df = pd.DataFrame(data)

                # Behalte nur ausgewählte Spalten
                gewünschte_spalten = ["GlobalId", "Name", "Type", "Length", "Width", "Height", "Wandlänge an der Innenseite", "Wandlänge an der Außenseite", "Unterkante zu Meereshöhe", "Unterkante zu Ursprungsgeschoss", "Unterkante zu Projektursprung"]
                df = df[[spalte for spalte in gewünschte_spalten if spalte in df.columns]]

                # Entferne Spalten, die nur leere Werte haben
                df = df.dropna(axis=1, how='all')

                df.to_excel(file_path, index=False)
                self.status_label.configure(
                    text=f"Excel-Datei exportiert: {file_path}", text_color="green"
                )
            except Exception as e:
                self.status_label.configure(text=f"Fehler: {e}", text_color="red")



if __name__ == "__main__":
    root = ctk.CTk()
    app = IFCSearcher(root)
    root.mainloop()