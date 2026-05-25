import customtkinter as ctk
from tkinter import filedialog
from services.crypto_service import CryptoService
from repository.file_repository import FileRepository
from db_info.db import get_connection

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CryptoManagerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.service = CryptoService()
        self.file_repo = FileRepository()

        self.title("Sistem de Gestiune Criptografică")
        self.geometry("900x600")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR (meniu Stanga) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Crypto\nManager", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        self.btn_import = ctk.CTkButton(self.sidebar_frame, text="1. Importă Fișier Nou", command=self.import_file)
        self.btn_import.grid(row=1, column=0, padx=20, pady=10)

        self.btn_encrypt = ctk.CTkButton(self.sidebar_frame, text="2. Criptează Fișier", command=lambda: self.open_crypto_window("ENCRYPT"))
        self.btn_encrypt.grid(row=2, column=0, padx=20, pady=10)

        self.btn_decrypt = ctk.CTkButton(self.sidebar_frame, text="3. Decriptează Fișier", command=lambda: self.open_crypto_window("DECRYPT"))
        self.btn_decrypt.grid(row=3, column=0, padx=20, pady=10)

        self.btn_keys = ctk.CTkButton(self.sidebar_frame, text="4. Generează Chei", command=self.open_keys_window)
        self.btn_keys.grid(row=4, column=0, padx=20, pady=10)

        self.btn_stats = ctk.CTkButton(self.sidebar_frame, text="Statistici Performanță", command=self.open_stats_window)
        self.btn_stats.grid(row=5, column=0, padx=20, pady=10)

        self.btn_refresh = ctk.CTkButton(self.sidebar_frame, text="Refresh", fg_color="#555555", hover_color="#333333", command=self.populate_file_explorer)
        self.btn_refresh.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # --- MAIN AREA (Taburi in loc de o simpla consola) ---
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.tabview.add("Explorator Fișiere")
        self.tabview.add("Consolă Loguri")

        # --- TAB: EXPLORATOR FISIERE ---
        self.tabview.tab("Explorator Fișiere").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Explorator Fișiere").grid_rowconfigure(0, weight=1)
        
        self.scrollable_files = ctk.CTkScrollableFrame(self.tabview.tab("Explorator Fișiere"), label_text="Fișiere in Sistem")
        self.scrollable_files.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # --- TAB: CONSOLA LOGURI ---
        self.tabview.tab("Consolă Loguri").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Consolă Loguri").grid_rowconfigure(0, weight=1)
        self.textbox_log = ctk.CTkTextbox(self.tabview.tab("Consolă Loguri"), font=ctk.CTkFont(family="Consolas", size=13))
        self.textbox_log.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.log_message("[SISTEM] Interfața grafică a fost inițializată cu succes.")
        
        # populam lista la pornire
        self.populate_file_explorer()

    # --- LOGICA PENTRU EXPLORATORUL VIZUAL ---
    def populate_file_explorer(self):
        """Goleste lista si o repopuleaza cu fisierele din DB sub forma de randuri UI."""
        # curatam frame-ul de widget-urile vechi
        for widget in self.scrollable_files.winfo_children():
            widget.destroy()
            
        files = self.file_repo.get_all()
        if not files:
            lbl = ctk.CTkLabel(self.scrollable_files, text="Niciun fișier importat. Folosește butonul din stânga.", text_color="gray")
            lbl.pack(pady=20)
            return

        for f in files:
            # Creare rand pentru fiecare fisier
            row_frame = ctk.CTkFrame(self.scrollable_files)
            row_frame.pack(fill="x", padx=5, pady=5)
            
            # Iconita text in functie de status
            status_color = "green" if f['status'] == "DECRYPTED" else ("red" if f['status'] == "ENCRYPTED" else "gray")
            
            name_lbl = ctk.CTkLabel(row_frame, text=f"📄 {f['original_name']}", font=ctk.CTkFont(weight="bold"))
            name_lbl.pack(side="left", padx=10, pady=10)
            
            status_lbl = ctk.CTkLabel(row_frame, text=f"[{f['status']}]", text_color=status_color)
            status_lbl.pack(side="left", padx=10, pady=10)
            
            # Butonul de detalii care face magia UX
            btn_details = ctk.CTkButton(row_frame, text="Vezi Detalii", width=100, 
                                        command=lambda f_id=f['id'], f_data=f: self.show_file_details(f_id, f_data))
            btn_details.pack(side="right", padx=10, pady=10)

    def show_file_details(self, file_id, file_data):
        """Deschide panoul cu informatii detaliate si ultima cheie folosita."""
        window = ctk.CTkToplevel(self)
        window.title(f"Detalii: {file_data['original_name']}")
        window.geometry("450x350")
        window.wait_visibility()
        window.grab_set()

        # Detalii Generale
        ctk.CTkLabel(window, text="Informații Fișier", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15,5))
        ctk.CTkLabel(window, text=f"Dimensiune: {file_data['size_bytes']} bytes").pack()
        ctk.CTkLabel(window, text=f"SHA-256: {file_data['checksum'][:25]}...").pack()
        
        # AICI ADUCEM DATELE DIN ISTORIC!
        history = self.service.get_file_history(file_id)
        
        frame_history = ctk.CTkFrame(window, fg_color="#333333")
        frame_history.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(frame_history, text="Istoric Criptare", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        if history:
            ctk.CTkLabel(frame_history, text=f"Ultima Cheie Folosită: {history['key_name']}", text_color="#F2A65A").pack()
            ctk.CTkLabel(frame_history, text=f"Tip Algoritm: {history['key_type']}").pack()
            ctk.CTkLabel(frame_history, text=f"Framework: {history['framework_name']}").pack()
            ctk.CTkLabel(frame_history, text=f"Data: {history['ended_at']}").pack(pady=(0,10))
        else:
            ctk.CTkLabel(frame_history, text="Acest fișier nu a fost criptat încă.", text_color="gray").pack(pady=10)

        ctk.CTkButton(window, text="Închide", command=window.destroy, fg_color="gray").pack(pady=10)


    
    def log_message(self, message):
        self.textbox_log.insert("end", message + "\n")
        self.textbox_log.see("end")

    def get_db_keys(self):
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, name, key_type FROM keys_storage WHERE is_active = TRUE")
        keys = cursor.fetchall()
        cursor.close()
        connection.close()
        return keys

    def import_file(self):
        filepath = filedialog.askopenfilename(title="Alege un fișier pentru import")
        if filepath:
            try:
                self.service.add_new_file(filepath)
                self.log_message(f"[SUCCES] Fișier importat: {filepath}")
                self.populate_file_explorer() # actualizare lista vizuala automata
                self.tabview.set("Explorator Fișiere") # sarim automat pe tabul cu fisiere
            except Exception as e:
                self.log_message(f"[EROARE] Import eșuat: {e}")

    def open_keys_window(self):
        window = ctk.CTkToplevel(self)
        window.title("Generare Chei")
        window.geometry("300x250")
        window.wait_visibility()
        window.grab_set() 

        ctk.CTkLabel(window, text="Nume Cheie:").pack(pady=(20, 5))
        entry_name = ctk.CTkEntry(window, placeholder_text="Ex: proiect_sva")
        entry_name.pack(pady=5)

        ctk.CTkLabel(window, text="Tip Algoritm:").pack(pady=(10, 5))
        combo_type = ctk.CTkComboBox(window, values=["AES", "RSA"])
        combo_type.pack(pady=5)

        def btn_generate():
            nume = entry_name.get()
            tip = combo_type.get()
            if nume:
                try:
                    self.service.generate_new_key(nume, tip)
                    self.log_message(f"[SUCCES] Cheia {tip} '{nume}' a fost generată.")
                    window.destroy()
                except Exception as e:
                    self.log_message(f"[EROARE] {e}")
            else:
                self.log_message("[AVERTISMENT] Introduceți un nume pentru cheie!")

        ctk.CTkButton(window, text="Generează", command=btn_generate).pack(pady=20)

    def open_crypto_window(self, op_type):
        window = ctk.CTkToplevel(self)
        window.title(f"Operațiune: {op_type}")
        window.geometry("400x350")
        window.wait_visibility()
        window.grab_set()

        files = self.file_repo.get_all()
        keys = self.get_db_keys()

        file_options = [f"{f['id']} - {f['original_name']} ({f['status']})" for f in files]
        key_options = [f"{k['id']} - {k['name']} ({k['key_type']})" for k in keys]
        fw_options = ["1 - OpenSSL (Cryptography)",
                      "2 - PyCryptodome (Alternativ)",
                      "3 - PyNaCl (Libsodium)"]

        if not file_options or not key_options:
            self.log_message("[EROARE] Nu ai fișiere sau chei în sistem.")
            window.destroy()
            return

        ctk.CTkLabel(window, text="Selectează Fișierul:").pack(pady=(15, 0))
        combo_file = ctk.CTkComboBox(window, values=file_options, width=300)
        combo_file.pack(pady=5)

        ctk.CTkLabel(window, text="Selectează Cheia:").pack(pady=(10, 0))
        combo_key = ctk.CTkComboBox(window, values=key_options, width=300)
        combo_key.pack(pady=5)

        ctk.CTkLabel(window, text="Selectează Framework (pt AES):").pack(pady=(10, 0))
        combo_fw = ctk.CTkComboBox(window, values=fw_options, width=300)
        combo_fw.pack(pady=5)

        def execute():
            try:
                f_id = int(combo_file.get().split(" - ")[0])
                k_id = int(combo_key.get().split(" - ")[0])
                fw_id = int(combo_fw.get().split(" - ")[0])
                
                self.service.execute_crypto_operation(op_type, f_id, k_id, fw_id)
                self.log_message(f"[SUCCES] {op_type} finalizat cu succes!")
                self.populate_file_explorer() 
                window.destroy()
            except Exception as e:
                self.log_message(f"[EROARE] {e}")

        ctk.CTkButton(window, text="Execută Operațiunea", command=execute, fg_color="#2FA572").pack(pady=20)

    def open_stats_window(self):
            stats_exist = self.service.get_performance_stats(1) or self.service.get_performance_stats(2)
            if not stats_exist:
                self.log_message("[AVERTISMENT] Nu există suficiente date pentru grafice.")
                return

            # 1. creare fereastra de baza
            window = ctk.CTkToplevel(self)
            window.title("Analiză Performanță Framework-uri")
            window.geometry("900x650") 
            window.wait_visibility()
            window.grab_set()

            # 2. adaugare frame-ul de control pentru butoanele AES / RSA
            control_frame = ctk.CTkFrame(window)
            control_frame.pack(fill="x", padx=20, pady=10)

            ctk.CTkLabel(control_frame, text="Selectează Algoritmul pentru Analiză:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=15, pady=10)

            # 3. container dedicat
            chart_container = ctk.CTkFrame(window, fg_color="transparent")
            chart_container.pack(fill="both", expand=True, padx=10, pady=10)

            def update_view(selected_algo):
                """functie interna apelata la fiecare schimbare de tab."""
                # mapare textul pe ID-ul din baza de date
                algo_id = 1 if selected_algo == "AES" else 2
                
                stats = self.service.get_performance_stats(algo_id)

                #golire 
                for widget in chart_container.winfo_children():
                    widget.destroy()

                if not stats:
                    ctk.CTkLabel(chart_container, text=f"Nu există date introduse în sistem pentru algoritmul {selected_algo}.", text_color="orange", font=ctk.CTkFont(size=14)).pack(pady=100)
                    return

                # Extragere date pentru axe 
                names = [s['name'] for s in stats]
                times = [float(s['avg_time']) for s in stats]
                mems = [float(s['avg_mem']) for s in stats]

                # Creare figura matplotlib 
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
                fig.patch.set_facecolor('#2B2B2B') # tema dark
                
                colors = ['#3a7ebf', '#1f538d', '#2fa572']

                # gf 1: Timp de exec (ms)
                ax1.set_facecolor('#2B2B2B')
                bars1 = ax1.bar(names, times, color=colors[:len(names)])
                ax1.set_title("Timp Mediu Execuție (ms)", color='white', pad=15)
                ax1.tick_params(colors='white')
                ax1.bar_label(bars1, fmt='%.1f ms', color='white', padding=3) # Afișează valoarea exactă deasupra barei

                # gf 2: Consum Memorie (KB)
                ax2.set_facecolor('#2B2B2B')
                bars2 = ax2.bar(names, mems, color=colors[:len(names)])
                ax2.set_title("Consum Mediu Memorie (KB)", color='white', pad=15)
                ax2.tick_params(colors='white')
                ax2.bar_label(bars2, fmt='%.1f KB', color='white', padding=3) # Afișează valoarea exactă deasupra barei

                plt.tight_layout()

                # integrare grafic în noul container, nu direct în window
                canvas = FigureCanvasTkAgg(fig, master=chart_container)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)
                
                plt.close(fig)

            # 4. adaugare butoane
            algo_selector = ctk.CTkSegmentedButton(control_frame, values=["AES", "RSA"], command=update_view)
            algo_selector.pack(side="right", padx=15, pady=10)
            
            #declansare stare implicita 
            algo_selector.set("AES")
            update_view("AES")

if __name__ == "__main__":
    app = CryptoManagerGUI()
    app.mainloop()