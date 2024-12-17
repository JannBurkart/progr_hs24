import customtkinter as ctk
from tkinter import filedialog, messagebox
import ifcopenshell
import time

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

        # Status-Anzeige
        self.status_label = ctk.CTkLabel(
            container, text="Status: Bereit", font=("Arial", 14), text_color="green"
        )
        self.status_label.pack(pady=20, padx=20)

        # Fortschrittsanzeige hinzufügen
        self.progress_bar = ctk.CTkProgressBar(container, orientation="horizontal", mode="determinate")
        self.progress_bar.pack(pady=10, padx=20, fill="x")
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()

    def show_progress(self, progress):
        """Aktualisiert den Fortschrittsbalken."""
        self.progress_bar.pack(pady=10, padx=20, fill="x")
        self.progress_bar.set(progress)
        self.root.update_idletasks()

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
        dropdown.grid(row=len(self.category_dropdowns), column=0, padx=10, pady=5, sticky="nsew")
        self.category_dropdowns.append((dropdown, category_var))
        self.update_plus_button_position(parent)

    def update_plus_button_position(self, parent):
        """Positioniert den Plus-Button rechts neben dem letzten Dropdown-Menü."""
        if hasattr(self, "plus_button"):
            self.plus_button.destroy()
        self.plus_button = ctk.CTkButton(
            parent, text="+", width=30, command=lambda: self.add_category_dropdown(parent),
            fg_color="#4a4a4a", hover_color="#5a5a5a"
        )
        self.plus_button.grid(row=len(self.category_dropdowns)-1, column=1, padx=10, pady=5, sticky="nsew")

    def load_ifc(self):
        """Lädt eine IFC-Datei mit Fortschrittsanzeige."""
        file_path = filedialog.askopenfilename(filetypes=[("IFC-Dateien", "*.ifc")])
        if file_path:
            try:
                self.show_progress(0)
                for i in range(1, 11):  # Simulierter Fortschritt
                    time.sleep(0.1)  # Kurze Verzögerung
                    self.show_progress(i / 10)
                self.ifc_model = ifcopenshell.open(file_path)
                self.status_label.configure(text=f"IFC-Datei geladen: {file_path}", text_color="green")
            except Exception as e:
                self.status_label.configure(text=f"Fehler: {e}", text_color="red")
            finally:
                self.progress_bar.pack_forget()

    def filter_elements(self):
        """Filtert Elemente basierend auf den ausgewählten Kategorien."""
        if not self.ifc_model:
            messagebox.showwarning("Warnung", "Bitte lade zuerst eine IFC-Datei!")
            return

        self.selected_categories = []
        self.filtered_elements = []

        total_steps = len(self.category_dropdowns)
        current_step = 0

        for dropdown, category_var in self.category_dropdowns:
            category = category_var.get()
            if category != "Kategorie wählen":
                self.selected_categories.append(category)
                self.filter_category(category)
                current_step += 1
                self.show_progress(current_step / total_steps)

        count = len(self.filtered_elements)
        self.status_label.configure(
            text=f"{count} Elemente in Kategorien {', '.join(self.selected_categories)} gefunden.",
            text_color="blue"
        )
        self.progress_bar.pack_forget()

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
                self.show_progress(0)
                time.sleep(0.2)  # Simulierter Exportbeginn
                self.status_label.configure(text=f"Export erfolgreich: {file_path}", text_color="green")
            finally:
                self.progress_bar.pack_forget()

# Ausführung
if __name__ == "__main__":
    app = ctk.CTk()
    splitter = IFCSearcher(app)
    app.mainloop()