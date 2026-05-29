import tkinter as tk
from tkinter import messagebox
import urllib.request
import json
import threading
import os
import time

class ChronosRetroTacho:
    def __init__(self, root):
        self.root = root
        self.root.title("SCS Chronos TachoSystem v1.3 - Retro Edition")
        self.root.geometry("620x340")
        self.root.configure(bg="#1A1A1A")
        self.root.resizable(False, False)

        # Dane konfiguracyjne i stan tachografu
        self.driver1_name = "JAN GŁOWACZ"
        self.driver2_name = "JULIA GŁOWACZ"
        self.current_driver = 1  # 1 lub 2
        self.active_mode = "ODPOCZYNEK"  # JAZDA, PRACA, ODPOCZYNEK
        
        # Liczniki czasu (w minutach gry z ETS2)
        self.drive_continuous = 0
        self.drive_daily = 0
        self.work_daily = 0
        self.rest_daily = 0
        self.extensions_used = 0
        
        # Dane z API
        self.speed_kmh = 0
        self.game_time_str = "--:--"
        self.truck_make = "Mercedes-Benz"
        self.truck_model = "Travego"
        
        # Nawigacja po ekranach (0-4)
        self.current_screen = 0 
        self.total_screens = 5
        
        self.telemetry_connected = False
        self.running = True
        self.last_game_minutes_total = -1

        # --- BUDOWA INTERFEJSU (STYL VDO SIEMENS) ---
        self.create_hardware_frame()
        
        # Start wątku pobierania danych z ETS2
        self.start_telemetry_loop()

    def create_hardware_frame(self):
        # Główna obudowa urządzenia
        outer_frame = tk.Frame(self.root, bg="#2B2B2B", bd=6, relief=tk.RAISED)
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # --- WYŚWIETLACZ LCD ---
        self.lcd_canvas = tk.Canvas(outer_frame, bg="#383D38", height=130, bd=4, relief=tk.SUNKEN, highlightthickness=0)
        self.lcd_canvas.pack(fill=tk.X, padx=15, pady=15)

        # Teksty na wyświetlaczu LCD
        self.lcd_line1 = self.lcd_canvas.create_text(
            20, 35, anchor="w", fill="#C8D0C8", 
            font=("Consolas", 14, "bold"), text="VDO  h   ----------  o■ --h--"
        )
        self.lcd_line2 = self.lcd_canvas.create_text(
            20, 75, anchor="w", fill="#C8D0C8", 
            font=("Consolas", 14, "bold"), text="CYKL: --h--   SUMA: --h--"
        )
        self.lcd_status = self.lcd_canvas.create_text(
            20, 110, anchor="w", fill="#A0A8A0", 
            font=("Consolas", 9), text="STATUS: BRAK POŁĄCZENIA Z ETS2"
        )

        # --- PANEL PRZYCISKÓW FIZYCZNYCH ---
        btn_frame = tk.Frame(outer_frame, bg="#2B2B2B")
        btn_frame.pack(fill=tk.X, padx=15, pady=5)

        btn_style = {
            "bg": "#3E3E3E", "fg": "#FFFFFF", 
            "activebackground": "#555555", "activeforeground": "#FFFFFF", 
            "font": ("Arial", 10, "bold"), "bd": 2, "relief": tk.RAISED
        }
        
        # Przyciski nawigacji menu
        tk.Button(btn_frame, text="↩", width=5, height=2, **btn_style, command=self.btn_back).grid(row=0, column=0, padx=3)
        tk.Button(btn_frame, text="▲", width=5, height=2, **btn_style, command=self.btn_up).grid(row=0, column=1, padx=3)
        tk.Button(btn_frame, text="▼", width=5, height=2, **btn_style, command=self.btn_down).grid(row=0, column=2, padx=3)
        tk.Button(btn_frame, text="OK", width=6, height=2, **btn_style, command=self.btn_ok).grid(row=0, column=3, padx=3)

        # Wybór kierowcy (Slot 1 i Slot 2)
        card_style = {"bg": "#1F3A52", "fg": "#FFFFFF", "activebackground": "#294F70", "font": ("Arial", 9, "bold"), "bd": 2, "relief": tk.RAISED}
        tk.Button(btn_frame, text="👤 [1]", width=8, height=2, **card_style, command=lambda: self.switch_driver(1)).grid(row=0, column=4, padx=20)
        tk.Button(btn_frame, text="👥 [2]", width=8, height=2, **card_style, command=lambda: self.switch_driver(2)).grid(row=0, column=5, padx=3)

        # Zapis i wydruk raportu
        tk.Button(btn_frame, text="WYDRUK (24h)", bg="#52411F", fg="#FFFFFF", font=("Arial", 9, "bold"), command=self.print_and_save_tacho).grid(row=0, column=6, padx=10)

    # --- STEROWANIE EKRANAMI (MENU) ---
    def btn_back(self):
        self.current_screen = 0
        self.update_lcd_display()

    def btn_up(self):
        self.current_screen = (self.current_screen + 1) % self.total_screens
        self.update_lcd_display()

    def btn_down(self):
        self.current_screen = (self.current_screen - 1) % self.total_screens
        self.update_lcd_display()
    
    def btn_ok(self):
        if self.extensions_used < 2:
            self.extensions_used += 1
            messagebox.showinfo("Chronos", f"Zgłoszono wydłużenie czasu jazdy do 10h ({self.extensions_used}/2)")
        else:
            messagebox.showwarning("Chronos", "Wykorzystano już limit przedłużeń w tym tygodniu!")

    def switch_driver(self, slot):
        self.current_driver = slot
        self.drive_continuous = 0
        self.update_lcd_display()
        messagebox.showinfo("Tachograf VDO", f"Przełączono na slot: Kierowca {slot}")

    # --- ZAPIS WYDRUKÓW DO PLIKU TEKSTOWEGO ---
    def print_and_save_tacho(self):
        current_name = self.driver1_name if self.current_driver == 1 else self.driver2_name
        status_conn = "ONLINE" if self.telemetry_connected else "OFFLINE"
        report = (
            f"=======================================\n"
            f"   WYDRUK OPERACYJNY CHRONOS RETRO 24H \n"
            f"=======================================\n"
            f"KIEROWCA:        {current_name}\n"
            f"AKTYWNOŚĆ:       {self.active_mode}\n"
            f"JAZDA CIĄGŁA:    {self.format_mins(self.drive_continuous)}\n"
            f"JAZDA DZIENNA:   {self.format_mins(self.drive_daily)}\n"
            f"INNA PRACA:      {self.format_mins(self.work_daily)}\n"
            f"ODPOCZYNEK:      {self.format_mins(self.rest_daily)}\n"
            f"PRZEDŁUŻENIA 10H: {self.extensions_used}/2\n"
            f"POJAZD:          {self.truck_make} {self.truck_model}\n"
            f"GODZINA ETS2:    {self.game_time_str}\n"
            f"MAGISTRALA API:  {status_conn}\n"
            f"=======================================\n\n"
        )
        
        try:
            with open("wydruk_tacho.txt", "a", encoding="utf-8") as f:
                f.write(report)
            print(report)
            messagebox.showinfo("Drukarka Tacho", "Raport został wydrukowany w konsoli oraz zapisany do pliku 'wydruk_tacho.txt'!")
        except Exception as e:
            messagebox.showerror("Błąd drukarki", f"Nie udało się zapisać wydruku: {e}")

    # --- WĄTEK TELEMETRII ---
    def start_telemetry_loop(self):
        def pull_data():
            url = "http://192.168.1.15:25555/api/ets2/telemetry"
            while self.running:
                try:
                    req = urllib.request.Request(url, headers={'Accept': 'application/json'})
                    with urllib.request.urlopen(req, timeout=0.4) as response:
                        data = json.loads(response.read().decode())
                        self.telemetry_connected = True
                        if self.running:
                            self.root.after(0, lambda d=data: self.process_telemetry_data(d))
                except Exception:
                    self.telemetry_connected = False
                    if self.running:
                        self.root.after(0, self.set_disconnected_ui)
                
                time.sleep(0.4)

        threading.Thread(target=pull_data, daemon=True).start()

    def set_disconnected_ui(self):
        status_text = f"EKRAN {self.current_screen + 1}/5 | MAGISTRALA: ROZŁĄCZONA"
        self.lcd_canvas.itemconfig(self.lcd_status, text=status_text)

        if self.current_screen == 0:
            self.lcd_canvas.itemconfig(self.lcd_line1, text="VDO  h   ----------  o■ --h--")
            self.lcd_canvas.itemconfig(self.lcd_line2, text="CYKL: --h--   SUMA: --h--")
        elif self.current_screen == 1:
            self.lcd_canvas.itemconfig(self.lcd_line1, text="AKTYWNOŚĆ: ----------")
            self.lcd_canvas.itemconfig(self.lcd_line2, text="⚒ PRACA: --h--  h ODP: --h--")
        elif self.current_screen == 2:
            self.lcd_canvas.itemconfig(self.lcd_line1, text="PRĘDKOŚĆ POJAZDU VDO")
            self.lcd_canvas.itemconfig(self.lcd_line2, text="V = --- km/h")
        elif self.current_screen == 3:
            self.lcd_canvas.itemconfig(self.lcd_line1, text="STAN:  ▶    ⚒    h ")
            self.lcd_canvas.itemconfig(self.lcd_line2, text="CZAS STANU: --h--")
        elif self.current_screen == 4:
            self.lcd_canvas.itemconfig(self.lcd_line1, text="PORT: 25555")
            self.lcd_canvas.itemconfig(self.lcd_line2, text="STATUS SYGNAŁU: BRAK ETS2")

    def process_telemetry_data(self, data):
        truck = data.get("truck", {})
        game = data.get("game", {})
        
        self.truck_make = truck.get("make", "Mercedes-Benz")
        self.truck_model = truck.get("model", "Travego")
        
        try:
            self.speed_kmh = int(abs(float(truck.get("speed", 0.0))))
        except (ValueError, TypeError):
            self.speed_kmh = 0

        engine_on = truck.get("engineOn", False)
        
        # --- PARSER CZASU GRY Z ISO STRING ---
        # Format w JSON: "0001-01-01T14:25:00Z" -> Wyciągamy godzinę i minutę gry
        iso_time_str = game.get("time", "")
        current_game_minutes = 0
        
        if "T" in iso_time_str and ":" in iso_time_str:
            try:
                time_part = iso_time_str.split("T")[1].replace("Z", "")
                hh, mm, ss = time_part.split(":")
                self.game_time_str = f"{hh}:{mm}"
                
                # Konwersja całego czasu gry na bezwzględne minuty (uwzględniając dni, jeśli się zmieniają)
                # Dla uproszczenia bierzemy pod uwagę aktualną godzinę i minutę doby gry
                current_game_minutes = int(hh) * 60 + int(mm)
            except Exception:
                self.game_time_str = "--:--"
        else:
            self.game_time_str = "--:--"

        # Wyznaczenie trybu pracy
        if self.speed_kmh > 1 and engine_on:
            self.active_mode = "JAZDA"
        elif engine_on:
            self.active_mode = "PRACA"
        else:
            self.active_mode = "ODPOCZYNEK"

        # --- DYNAMICZNE NALICZANIE DELTY CZASU ETS2 ---
        if self.last_game_minutes_total >= 0:
            # Obliczamy różnicę w minutach gry między klatkami telemetrii
            delta_game_mins = current_game_minutes - self.last_game_minutes_total
            
            # Korekta przejścia przez północ (np. zmiana z 23:59 na 00:00)
            if delta_game_mins < -1000:
                delta_game_mins += 1440 
            
            # Naliczamy czas tylko wtedy, kiedy gra nie jest zapauzowana i delta ma sens
            if 0 < delta_game_mins < 120 and not game.get("paused", False):
                if self.active_mode == "JAZDA":
                    self.drive_continuous += delta_game_mins
                    self.drive_daily += delta_game_mins
                    self.rest_daily = 0
                elif self.active_mode == "PRACA":
                    self.work_daily += delta_game_mins
                    self.rest_daily = 0
                elif self.active_mode == "ODPOCZYNEK":
                    self.drive_continuous = 0  # Reset cyklu ciągłego jazdy
                    self.rest_daily += delta_game_mins

        self.last_game_minutes_total = current_game_minutes
        self.update_lcd_display()

    # --- RENDEROWANIE EKRANÓW LCD ---
    def update_lcd_display(self):
        if not self.telemetry_connected:
            return

        current_name = self.driver1_name if self.current_driver == 1 else self.driver2_name
        mode_icons = {"JAZDA": "▶", "PRACA": "⚒", "ODPOCZYNEK": "h"}
        icon = mode_icons.get(self.active_mode, "h")

        status_text = f"EKRAN {self.current_screen + 1}/5 | LIMIT 10H: {self.extensions_used}/2 | TACHO: ONLINE"
        self.lcd_canvas.itemconfig(self.lcd_status, text=status_text)

        # WIDOK 1: Ekran Ogólny (Standard VDO z poprawną godziną)
        if self.current_screen == 0:
            line1_text = f"ETS2 {self.game_time_str}  {icon}  K{self.current_driver}:{current_name[:10]}"
            line2_text = f"CYKL: {self.format_mins(self.drive_continuous)}   SUMA: {self.format_mins(self.drive_daily)}"
            
        # WIDOK 2: Ekran Szczegółowy Czasów Pracy
        elif self.current_screen == 1:
            line1_text = f"AKT: {self.active_mode} ({icon}) | POZ: {self.truck_model[:7]}"
            line2_text = f"⚒ PRK: {self.format_mins(self.work_daily)}   h ODP: {self.format_mins(self.rest_daily)}"
            
        # WIDOK 3: Ekran Cyfrowego Prędkościomierza
        elif self.current_screen == 2:
            line1_text = f"POJAZD: {self.truck_make.upper()}"
            line2_text = f"PRĘDKOŚĆ: {self.speed_kmh} km/h"

        # WIDOK 4: Ekran Ikonowy z podświetlaniem obecnego stanu i licznikiem bieżącym
        elif self.current_screen == 3:
            i_jazda = "[▶]" if self.active_mode == "JAZDA" else " ▶ "
            i_praca = "[⚒]" if self.active_mode == "PRACA" else " ⚒ "
            i_odpoc = "[h]" if self.active_mode == "ODPOCZYNEK" else " h "
            
            if self.active_mode == "JAZDA":
                current_timer = self.drive_continuous
            elif self.active_mode == "PRACA":
                current_timer = self.work_daily
            else:
                current_timer = self.rest_daily

            line1_text = f"STAN:  {i_jazda}     {i_praca}     {i_odpoc}"
            line2_text = f"CZAS STANU: {self.format_mins(current_timer)}"

        # WIDOK 5: Ustawienia i status sieciowy magistrali
        elif self.current_screen == 4:
            line1_text = f"PORT: 25555"
            line2_text = f"MAGISTRALA: TELEMETRIA OK (v{data_plugin_ver if 'data_plugin_ver' in locals() else '9'})"

        self.lcd_canvas.itemconfig(self.lcd_line1, text=line1_text)
        self.lcd_canvas.itemconfig(self.lcd_line2, text=line2_text)

    def format_mins(self, total_mins):
        h = int(total_mins // 60)
        m = int(total_mins % 60)
        return f"{h:02d}h{m:02d}"

    def shutdown(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChronosRetroTacho(root)
    root.protocol("WM_DELETE_WINDOW", app.shutdown)
    root.mainloop()