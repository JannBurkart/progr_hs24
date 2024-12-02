import customtkinter as ctk
from ifc_functions.ifc_loader import load_ifc
from ifc_functions.ifc_filter import filter_elements
from ifc_functions.ifc_exporter import export_ifc
class IFCSplitter:
    def __init__(self, root):
        # Setze CustomTkinter-Erscheinung und Theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self.root = root
        self.root.title("IFC Splitter")
        self.root.geometry("750x500")
        self.root.configure(bg="#1e1e1e")  # Hintergrund

        # Initialisiere IFC-Modell und gefilterte Elemente
        self.ifc_model = None
        self.selected_categories = []
        self.category_dropdowns = []

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
            container, text="IFC-Datei hochladen", command=load_ifc, fg_color="#4a4a4a", hover_color="#5a5a5a"
        )
        upload_button.pack(pady=10, padx=20)

        # Kategorie-Filter (Dropdowns und Plus)
        category_frame = ctk.CTkFrame(container, fg_color="#2e2e2e")
        category_frame.pack(pady=10, padx=20, fill="y")

        self.add_category_dropdown(category_frame)  # Initiales Dropdown

        # Filtern-Button
        filter_button = ctk.CTkButton(
            container, text="Filtern", command=filter_elements, fg_color="#4a4a4a", hover_color="#5a5a5a"
        )
        filter_button.pack(pady=10, padx=20)

        # Exportieren-Button
        export_button = ctk.CTkButton(
            container, text="Neues IFC exportieren", command=export_ifc, fg_color="#4a4a4a", hover_color="#5a5a5a"
        )
        export_button.pack(pady=10, padx=20)

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
            values=["Außenwände", "Innenwände", "Stützen", "Fenster", "Türen", "Geschossdecken", "Gelände"],
            fg_color="#4a4a4a",
            button_color="#5a5a5a",
        )
        # Zentriere das Dropdown im Parent
        dropdown.grid(row=len(self.category_dropdowns), column=0, padx=10, pady=5, sticky="nsew")
        self.category_dropdowns.append((dropdown, category_var))

        # Aktualisiere die Position des Plus-Buttons
        self.update_plus_button_position(parent)



    def update_plus_button_position(self, parent):
        """Positioniert den Plus-Button rechts neben dem letzten Dropdown-Menü."""
        if hasattr(self, "plus_button"):
            self.plus_button.destroy()  # Entferne den alten Button

        # Der Plus-Button wird immer rechts neben dem letzten Dropdown angezeigt
        self.plus_button = ctk.CTkButton(
            parent, text="+", width=30, command=lambda: self.add_category_dropdown(parent),
            fg_color="#4a4a4a", hover_color="#5a5a5a"
        )
        self.plus_button.grid(row=len(self.category_dropdowns)-1, column=1, padx=10, pady=5, sticky="nsew")
    


# Hauptprogramm
if __name__ == "__main__":
    app = ctk.CTk()
    splitter = IFCSplitter(app)
    app.mainloop()