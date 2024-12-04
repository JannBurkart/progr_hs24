# ifc_loader.py
#import ifcopenshell
#from tkinter import filedialog, messagebox

#def load_ifc(import_model):
 #       """Lädt eine IFC-Datei."""
  #      file_path = filedialog.askopenfilename(filetypes=[("IFC-Dateien", "*.ifc")])
   #     if file_path:
    #        try:
     #           import_model.ifc_model = ifcopenshell.open(file_path)
      #          import_model.status_label.configure(text=f"IFC-Datei geladen: {file_path}", text_color="green")
       #     except Exception as e:
        #        import_model.status_label.configure(text=f"Fehler: {e}", text_color="red")