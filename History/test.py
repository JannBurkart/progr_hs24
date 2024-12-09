import customtkinter as ctk

# Anwendung starten
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Custom Toggle Switch")
        self.geometry("300x200")

        # Label zur Anzeige des Toggle-Status
        self.status_label = ctk.CTkLabel(self, text="Toggle is OFF", font=("Arial", 16))
        self.status_label.pack(pady=20)

        # Toggle Switch hinzufügen
        self.toggle_switch = ctk.CTkCheckBox(
            self,
            text="Toggle",
            command=self.on_toggle,
            variable=ctk.BooleanVar(value=False),
            onvalue=True,
            offvalue=False,
            width=25,
            height=25,
            border_width=2,
            corner_radius=50,
            fg_color="gray",
            hover_color="lightgray",
            text_color="white",
            font=("Arial", 14)
        )
        self.toggle_switch.pack(pady=10)

    def on_toggle(self):
        """Callback für Toggle-Switch."""
        if self.toggle_switch.get():
            self.status_label.configure(text="Toggle is ON", text_color="lime")
        else:
            self.status_label.configure(text="Toggle is OFF", text_color="red")


# App ausführen
if __name__ == "__main__":
    app = App()
    app.mainloop()