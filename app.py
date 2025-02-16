import random
import string
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import pyperclip
import requests
from faker import Faker
import webbrowser
import folium
from geopy.geocoders import Nominatim
from threading import Thread
import time

# ==============================
#       PALETA DE COLORES
# ==============================
LIGHT_COLORS = {
    "bg_main": "#F4F4F4",
    "bg_panel": "#FFFFFF",
    "fg_text": "#000000",
    "button_bg": "#E0E0E0",
    "button_fg": "#000000",
    "entry_bg": "#FFFFFF",
    "entry_fg": "#000000",
    "highlight": "#CCCCCC",
}

DARK_COLORS = {
    "bg_main": "#2F2F2F",
    "bg_panel": "#3A3A3A",
    "fg_text": "#FFFFFF",
    "button_bg": "#555555",
    "button_fg": "#FFFFFF",
    "entry_bg": "#555555",
    "entry_fg": "#FFFFFF",
    "highlight": "#777777",
}

# ==============================
#   CLASE PARA FONDO GRADIENTE
# ==============================
class GradientFrame(tk.Canvas):
    """
    Un Canvas que dibuja un gradiente vertical entre color1 y color2.
    Se redibuja automáticamente al cambiar el tamaño.
    """
    def __init__(self, parent, color1, color2, **kwargs):
        super().__init__(parent, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.bind("<Configure>", self._draw_gradient)

    def _draw_gradient(self, event=None):
        """
        Dibuja líneas horizontales desde color1 hasta color2.
        """
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()

        # Convertir colores a RGB
        r1, g1, b1 = self.winfo_rgb(self.color1)
        r2, g2, b2 = self.winfo_rgb(self.color2)

        # Dibujar cada línea con una interpolación entre los colores
        for i in range(height):
            ratio = i / float(height)
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = f"#{r >> 8:02x}{g >> 8:02x}{b >> 8:02x}"
            self.create_line(0, i, width, i, tags=("gradient",), fill=color)
        self.lower("gradient")

# ========================================================
#        CLASE PRINCIPAL DE LA APLICACIÓN
# ========================================================
class ModernApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CUPDEV - ULTRA FUTURE 2040")
        self.root.geometry("1200x850")

        # Faker en español
        self.fake = Faker("es_ES")

        # Estado inicial: modo claro
        self.is_dark_mode = False
        self.colors = LIGHT_COLORS

        # CONFIGURACIÓN DE ESTILOS
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._configure_futuristic_style()

        # FONDO GRADIENTE
        self.gradient_frame = GradientFrame(self.root, "#0f0c29", "#302b63")
        self.gradient_frame.pack(fill="both", expand=True)

        # Contenedor principal encima del gradiente
        self.main_container = tk.Frame(self.root, bg=self.colors["bg_main"])
        self.main_container.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Creación de interfaz
        self.create_top_bar()
        self.create_main_layout()
        self.create_tabs()
        self.apply_colors()

        # Variable para animar label "SCANNING"
        self.scanning_label_on = False
        self.scanning_colors = ["#00FFFB", "#00FFA0", "#FA00FF", "#FFF700"]
        self.scanning_index = 0

    # ---------------------------
    #  ESTILO FUTURISTA (NEÓN)
    # ---------------------------
    def _configure_futuristic_style(self):
        """
        Ajusta un estilo 'futurista' (tipo neón) para widgets TTK.
        """
        self.style.configure("TFrame", background=LIGHT_COLORS["bg_panel"])
        self.style.configure(
            "Neon.TButton",
            font=("Consolas", 10, "bold"),
            foreground="#00FFFB",  # azul neón
            background="#111111",
            padding=8,
            borderwidth=2,
            relief="flat"
        )
        self.style.map("Neon.TButton",
            foreground=[("active", "#00FFC9")],
            background=[("active", "#222222")]
        )

        self.style.configure("TLabel",
            font=("Consolas", 10, "bold"),
            foreground=LIGHT_COLORS["fg_text"],
            background=LIGHT_COLORS["bg_panel"]
        )
        self.style.configure("TNotebook",
            background=LIGHT_COLORS["bg_panel"]
        )
        self.style.configure("TNotebook.Tab",
            font=("Consolas", 10, "bold"),
            padding=(10, 5),
            foreground=LIGHT_COLORS["fg_text"],
            background="#1E1E1E",
        )
        self.style.map("TNotebook.Tab",
            foreground=[("active", "#00FFFB")],
            background=[("active", "#333333")]
        )
        self.style.configure("TProgressbar",
            troughcolor="#444444",
            background="#00FFA0",
            thickness=6
        )
        self.style.configure("TEntry",
            foreground="#00FFFB",
            fieldbackground="#111111",
            insertcolor="#00FFFB",
            borderwidth=1
        )

    # -------------------------
    #   BARRA SUPERIOR
    # -------------------------
    def create_top_bar(self):
        """
        Crea la barra superior con el título y el botón para cambiar modo oscuro/claro.
        """
        self.top_bar = tk.Frame(self.main_container, height=60, bg="#111111")
        self.top_bar.pack(side=tk.TOP, fill=tk.X)

        # Etiqueta super futurista
        self.lbl_title = tk.Label(
            self.top_bar,
            text="CUPDEV 2040 - HYPER-TECH SYSTEM",
            font=("Consolas", 18, "bold"),
            bg="#111111",
            fg="#00FFFB"
        )
        self.lbl_title.pack(side=tk.LEFT, padx=20)

        # Botón Modo Oscuro/Claro
        self.btn_toggle_mode = ttk.Button(
            self.top_bar,
            text="Modo Oscuro",
            style="Neon.TButton",
            command=self.toggle_dark_mode
        )
        self.btn_toggle_mode.pack(side=tk.RIGHT, padx=20)

    # -------------------------
    #      LAYOUT PRINCIPAL
    # -------------------------
    def create_main_layout(self):
        """Crea el diseño principal con sidebar y área de pestañas"""
        self.content_frame = tk.Frame(self.main_container, bg=self.colors["bg_main"])
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # SIDEBAR
        self.sidebar_frame = tk.Frame(self.content_frame, width=220, bg=self.colors["bg_panel"])
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Contenedor de Notebook
        self.notebook_frame = tk.Frame(self.content_frame, bg=self.colors["bg_panel"])
        self.notebook_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Título / Logo en Sidebar
        self.label_logo = tk.Label(
            self.sidebar_frame,
            text="CUPDEV\nNEON-TECH",
            font=("Consolas", 16, "bold"),
            justify="center",
            bg=self.colors["bg_panel"],
            fg=self.colors["fg_text"]
        )
        self.label_logo.pack(pady=20)

        # Botones de la barra lateral
        self.btn_identity = ttk.Button(
            self.sidebar_frame,
            text="Identidades",
            style="Neon.TButton",
            command=lambda: self.notebook.select(self.tab_identity)
        )
        self.btn_identity.pack(pady=10, padx=10, fill=tk.X)

        self.btn_ip = ttk.Button(
            self.sidebar_frame,
            text="IP Lookup",
            style="Neon.TButton",
            command=lambda: self.notebook.select(self.tab_ip)
        )
        self.btn_ip.pack(pady=10, padx=10, fill=tk.X)

        self.btn_geo = ttk.Button(
            self.sidebar_frame,
            text="Geolocalización",
            style="Neon.TButton",
            command=lambda: self.notebook.select(self.tab_geo)
        )
        self.btn_geo.pack(pady=10, padx=10, fill=tk.X)

        self.btn_pass = ttk.Button(
            self.sidebar_frame,
            text="Contraseñas",
            style="Neon.TButton",
            command=lambda: self.notebook.select(self.tab_password)
        )
        self.btn_pass.pack(pady=10, padx=10, fill=tk.X)

    # -------------------------
    #       CREAR TABS
    # -------------------------
    def create_tabs(self):
        """Crea las pestañas principales"""
        self.notebook = ttk.Notebook(self.notebook_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Crear pestañas
        self.tab_identity = ttk.Frame(self.notebook)
        self.tab_ip = ttk.Frame(self.notebook)
        self.tab_geo = ttk.Frame(self.notebook)
        self.tab_password = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_identity, text="Identidades")
        self.notebook.add(self.tab_ip, text="IP Lookup")
        self.notebook.add(self.tab_geo, text="Geolocalización")
        self.notebook.add(self.tab_password, text="Generador de Contraseñas")

        # Configurar cada pestaña
        self.setup_tab_identity()
        self.setup_tab_ip()
        self.setup_tab_geo()
        self.setup_tab_password()

    # =========================================================
    #     PESTAÑA 1: IDENTIDADES (GENERADOR DE IDENTIDAD)
    # =========================================================
    def setup_tab_identity(self):
        """Configura la pestaña de Identidades"""
        # Marco superior
        self.identity_top_frame = tk.LabelFrame(
            self.tab_identity,
            text="Generador de Identidad Española",
            font=("Consolas", 11, "bold"),
            bg=self.colors["bg_panel"],
            fg=self.colors["fg_text"]
        )
        self.identity_top_frame.pack(padx=15, pady=15, fill=tk.X)

        self.lbl_identity_title = tk.Label(
            self.identity_top_frame,
            text="Crea una identidad ficticia con datos españoles:",
            bg=self.colors["bg_panel"],
            fg=self.colors["fg_text"],
            font=("Consolas", 10)
        )
        self.lbl_identity_title.pack(side=tk.LEFT, padx=10, pady=10)

        # Label SCANNING (parpadeante)
        self.lbl_scanning = tk.Label(
            self.identity_top_frame,
            text="",
            bg=self.colors["bg_panel"],
            fg="#00FFFB",
            font=("Consolas", 12, "bold")
        )
        self.lbl_scanning.pack(side=tk.RIGHT, padx=10, pady=10)

        self.btn_generate_identity = ttk.Button(
            self.identity_top_frame,
            text="Generar Identidad",
            style="Neon.TButton",
            command=self.on_generate_identity_click
        )
        self.btn_generate_identity.pack(side=tk.RIGHT, padx=10, pady=10)

        # Progreso (animación) para la generación
        self.progress_identity = ttk.Progressbar(
            self.identity_top_frame,
            mode="indeterminate",
            style="TProgressbar"
        )
        self.progress_identity.pack(side=tk.RIGHT, padx=(0,10), pady=10)

        # Texto donde se imprime la identidad
        self.identity_text_frame = tk.Frame(self.tab_identity, bg=self.colors["bg_main"])
        self.identity_text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        self.txt_identity = tk.Text(
            self.identity_text_frame,
            wrap="word",
            height=15,
            font=("Consolas", 10),
            bg=self.colors["entry_bg"],
            fg=self.colors["entry_fg"],
            insertbackground=self.colors["entry_fg"]
        )
        self.txt_identity.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scroll_identity = ttk.Scrollbar(
            self.identity_text_frame,
            command=self.txt_identity.yview
        )
        self.scroll_identity.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_identity.config(yscrollcommand=self.scroll_identity.set)

        # Botones de Copiar / Guardar
        bottom_frame = tk.Frame(self.tab_identity, bg=self.colors["bg_main"])
        bottom_frame.pack(pady=10)

        self.btn_identity_copy = ttk.Button(
            bottom_frame,
            text="Copiar Identidad",
            style="Neon.TButton",
            command=self.copiar_identidad
        )
        self.btn_identity_copy.grid(row=0, column=0, padx=10, pady=5)

        self.btn_identity_save = ttk.Button(
            bottom_frame,
            text="Guardar Identidad",
            style="Neon.TButton",
            command=self.guardar_identidad
        )
        self.btn_identity_save.grid(row=0, column=1, padx=10, pady=5)

    def on_generate_identity_click(self):
        """
        Inicia un hilo para simular un proceso que tarda (con barra de progreso animada).
        """
        self.txt_identity.delete("1.0", tk.END)
        self.progress_identity.start(10)  # velocidad de animación
        self.start_identity_scanning()
        thread = Thread(target=self.generar_identidad)
        thread.start()

    def start_identity_scanning(self):
        """Activa el parpadeo del label 'SCANNING'."""
        self.scanning_label_on = True
        self.lbl_scanning.config(text="SCANNING...")
        self.animate_identity_label()

    def stop_identity_scanning(self):
        """Detiene el parpadeo del label 'SCANNING'."""
        self.scanning_label_on = False
        self.lbl_scanning.config(text="")

    def animate_identity_label(self):
        """Hace parpadear el label de SCANNING con colores futuristas."""
        if not self.scanning_label_on:
            return
        color = self.scanning_colors[self.scanning_index % len(self.scanning_colors)]
        self.scanning_index += 1
        self.lbl_scanning.config(fg=color)
        self.lbl_scanning.after(300, self.animate_identity_label)

    def generar_identidad(self):
        """Genera una identidad falsa en español con datos variados."""
        time.sleep(1.5)  # Simula un retardo

        # Datos básicos
        nombre = self.fake.name()
        fecha_nacimiento = self.fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%d/%m/%Y")
        dni = self.generar_dni()
        estado_civil = random.choice(["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a"])
        hijos = random.randint(0, 3)
        telefono = self.fake.phone_number()
        # Email con dominio real
        email = self.generar_email_personalizado()

        # Dirección
        direccion, ciudad, provincia, cp = self.generar_direccion_consistente()

        # Vehículo y licencia
        licencia_conducir = self.generar_licencia_conducir()
        matricula = self.generar_matricula_vehiculo()

        # Datos bancarios
        try:
            iban = self.fake.iban(country_code='ES')
        except:
            iban = self.fake.iban()
        cc_number = self.fake.credit_card_number()
        cc_expire = self.fake.credit_card_expire()
        cc_cvv = self.fake.credit_card_security_code()

        # Password aleatoria (12 caracteres)
        password = self.generar_password(12)

        # Pequeña “biografía”
        bio = self.fake.text(max_nb_chars=200)

        identidad = (
            f"=== DATOS PERSONALES ===\n"
            f"Nombre: {nombre}\n"
            f"Fecha de Nacimiento: {fecha_nacimiento}\n"
            f"DNI: {dni}\n"
            f"Estado Civil: {estado_civil}\n"
            f"Hijos: {hijos}\n"
            f"Teléfono: {telefono}\n"
            f"Email: {email}\n"
            f"\n=== DIRECCIÓN ===\n"
            f"{direccion}\n"
            f"Ciudad: {ciudad}\n"
            f"Provincia: {provincia}\n"
            f"CP: {cp}\n"
            f"\n=== VEHÍCULO ===\n"
            f"Licencia de Conducir: {licencia_conducir}\n"
            f"Matrícula: {matricula}\n"
            f"\n=== DATOS BANCARIOS ===\n"
            f"IBAN: {iban}\n"
            f"Tarjeta de Crédito: {cc_number}\n"
            f"Expiración: {cc_expire}\n"
            f"CVV: {cc_cvv}\n"
            f"\n=== SEGURIDAD ===\n"
            f"Password: {password}\n"
            f"\n=== BIOGRAFÍA ===\n"
            f"{bio}\n"
        )

        time.sleep(1)
        self.txt_identity.insert("1.0", identidad)
        self.progress_identity.stop()
        self.stop_identity_scanning()

    def generar_email_personalizado(self):
        """Genera un email con un dominio real (gmail, hotmail, outlook, yahoo)."""
        username = self.fake.user_name()
        lista_dominios = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com"]
        dominio = random.choice(lista_dominios)
        return f"{username}@{dominio}"

    def generar_dni(self):
        """Genera un DNI español válido."""
        dni_num = ''.join(random.choices(string.digits, k=8))
        letras = "TRWAGMYFPDXBNJZSQVHLCKE"
        dni_letter = letras[int(dni_num) % 23]
        return f"{dni_num}{dni_letter}"

    def generar_licencia_conducir(self):
        """Genera un número random como licencia de conducir."""
        return f"D-{''.join(random.choices(string.digits, k=8))}"

    def generar_matricula_vehiculo(self):
        """
        Genera una matrícula española moderna: 4 dígitos + 3 letras (sin vocales).
        Ejemplo: 1234 BBB
        """
        digits = ''.join(random.choices(string.digits, k=4))
        letters_allowed = "BCDFGHJKLMNPQRSTVWXYZ"  # Sin vocales
        letters = ''.join(random.choices(letters_allowed, k=3))
        return f"{digits} {letters}"

    def generar_password(self, length=12):
        """Genera un password aleatorio."""
        chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
        return ''.join(random.choices(chars, k=length))

    def generar_direccion_consistente(self):
        """Genera una dirección ficticia realista."""
        ciudades = [
            ("Madrid", "Madrid"), ("Barcelona", "Barcelona"), ("Valencia", "Valencia"),
            ("Sevilla", "Sevilla"), ("Málaga", "Málaga"), ("Zaragoza", "Zaragoza"),
            ("Murcia", "Murcia"), ("Bilbao", "Vizcaya"), ("Alicante", "Alicante"),
            ("Granada", "Granada"), ("Córdoba", "Córdoba"), ("Vigo", "Pontevedra"),
            ("Gijón", "Asturias"), ("Hospitalet", "Barcelona")
        ]
        ciudad, provincia = random.choice(ciudades)
        calle = self.fake.street_name()
        numero = random.randint(1, 200)
        cp = self.fake.postcode()
        return f"Calle {calle}, {numero}", ciudad, provincia, cp

    def copiar_identidad(self):
        contenido = self.txt_identity.get("1.0", tk.END).strip()
        if contenido:
            pyperclip.copy(contenido)
            messagebox.showinfo("Copiado", "Identidad copiada al portapapeles.")

    def guardar_identidad(self):
        contenido = self.txt_identity.get("1.0", tk.END).strip()
        if contenido:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Texto", "*.txt")]
            )
            if filepath:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(contenido)
                messagebox.showinfo("Guardado", "Identidad guardada correctamente.")

    # ===================================
    #     PESTAÑA 2: IP LOOKUP
    # ===================================
    def setup_tab_ip(self):
        """Configura la pestaña de Búsqueda de IP"""
        self.ip_frame_top = tk.LabelFrame(
            self.tab_ip,
            text="Búsqueda de IP (Lookup)",
            font=("Consolas", 11, "bold"),
            bg=self.colors["bg_panel"],
            fg=self.colors["fg_text"]
        )
        self.ip_frame_top.pack(padx=15, pady=15, fill=tk.X)

        lbl_ip_intro = tk.Label(
            self.ip_frame_top,
            text="Introduce una dirección IP para obtener información geográfica, ISP, etc.",
            bg=self.colors["bg_panel"],
            fg=self.colors["fg_text"],
            font=("Consolas", 10)
        )
        lbl_ip_intro.pack(side=tk.TOP, padx=10, pady=10)

        self.ip_entry = ttk.Entry(self.ip_frame_top, width=30, style="TEntry")
        self.ip_entry.pack(side=tk.LEFT, padx=10, pady=10)

        self.btn_search_ip = ttk.Button(
            self.ip_frame_top,
            text="Buscar IP",
            style="Neon.TButton",
            command=self.on_ip_lookup_click
        )
        self.btn_search_ip.pack(side=tk.LEFT, padx=10, pady=10)

        # Barra de progreso para la búsqueda
        self.progress_ip_lookup = ttk.Progressbar(
            self.ip_frame_top,
            mode="indeterminate",
            style="TProgressbar"
        )
        self.progress_ip_lookup.pack(side=tk.LEFT, padx=(0,10), pady=10)

        # Cuadro de texto para mostrar resultado
        self.ip_text_frame = tk.Frame(self.tab_ip, bg=self.colors["bg_main"])
        self.ip_text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        self.txt_ip_result = tk.Text(
            self.ip_text_frame,
            wrap="word",
            height=15,
            font=("Consolas", 10),
            bg=self.colors["entry_bg"],
            fg=self.colors["entry_fg"],
            insertbackground=self.colors["entry_fg"]
        )
        self.txt_ip_result.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scroll_ip_result = ttk.Scrollbar(
            self.ip_text_frame,
            command=self.txt_ip_result.yview
        )
        self.scroll_ip_result.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_ip_result.config(yscrollcommand=self.scroll_ip_result.set)

        # Botones Copiar / Guardar
        bottom_frame = tk.Frame(self.tab_ip, bg=self.colors["bg_main"])
        bottom_frame.pack(pady=10)

        self.btn_ip_copy = ttk.Button(
            bottom_frame,
            text="Copiar Info",
            style="Neon.TButton",
            command=self.copiar_ip_info
        )
        self.btn_ip_copy.grid(row=0, column=0, padx=10, pady=5)

        self.btn_ip_save = ttk.Button(
            bottom_frame,
            text="Guardar Info",
            style="Neon.TButton",
            command=self.guardar_ip_info
        )
        self.btn_ip_save.grid(row=0, column=1, padx=10, pady=5)

    def on_ip_lookup_click(self):
        """Inicia la búsqueda de IP en un hilo separado (con animación)."""
        self.txt_ip_result.delete("1.0", tk.END)
        self.progress_ip_lookup.start(10)
        thread = Thread(target=self.ip_lookup)
        thread.start()

    def ip_lookup(self):
        """Consulta un API público para obtener información de la IP."""
        time.sleep(1)

        ip_address = self.ip_entry.get().strip()
        if not ip_address:
            # Si no se proporciona IP, usamos la IP pública del usuario
            try:
                ip_address = requests.get("https://api.ipify.org").text
            except:
                ip_address = "127.0.0.1"

        api_url = f"http://ip-api.com/json/{ip_address}?fields=66846719"
        resultado_texto = ""

        try:
            response = requests.get(api_url, timeout=5)
            data = response.json()
            if data["status"] == "success":
                resultado_texto += f"IP: {data.get('query', '')}\n"
                resultado_texto += f"País: {data.get('country', '')}\n"
                resultado_texto += f"Región: {data.get('regionName', '')}\n"
                resultado_texto += f"Ciudad: {data.get('city', '')}\n"
                resultado_texto += f"Latitud: {data.get('lat', '')}\n"
                resultado_texto += f"Longitud: {data.get('lon', '')}\n"
                resultado_texto += f"Proveedor (ISP): {data.get('isp', '')}\n"
                resultado_texto += f"Zona Horaria: {data.get('timezone', '')}\n"
                resultado_texto += f"Organización: {data.get('org', '')}\n"
            else:
                resultado_texto = f"No se encontró información para la IP: {ip_address}"
        except Exception as e:
            resultado_texto = f"Ocurrió un error al consultar la IP: {str(e)}"

        self.txt_ip_result.insert("1.0", resultado_texto)
        self.progress_ip_lookup.stop()

    def copiar_ip_info(self):
        contenido = self.txt_ip_result.get("1.0", tk.END).strip()
        if contenido:
            pyperclip.copy(contenido)
            messagebox.showinfo("Copiado", "Información de IP copiada al portapapeles.")

    def guardar_ip_info(self):
        contenido = self.txt_ip_result.get("1.0", tk.END).strip()
        if contenido:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Texto", "*.txt")]
            )
            if filepath:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(contenido)
                messagebox.showinfo("Guardado", "Información de IP guardada correctamente.")

    # ========================================
    #     PESTAÑA 3: GEOLOCALIZACIÓN
    # ========================================
    def setup_tab_geo(self):
        """Configura la pestaña de Geolocalización"""
        self.geo_frame_top = tk.LabelFrame(
            self.tab_geo,
            text="Geolocalización",
            font=("Consolas", 11, "bold"),
            bg=self.colors["bg_panel"],
            fg=self.colors["fg_text"]
        )
        self.geo_frame_top.pack(padx=15, pady=15, fill=tk.X)

        lbl_geo_intro = tk.Label(
            self.geo_frame_top,
            text="Introduce una dirección y genera un mapa con su ubicación aproximada:",
            bg=self.colors["bg_panel"],
            fg=self.colors["fg_text"],
            font=("Consolas", 10)
        )
        lbl_geo_intro.pack(side=tk.TOP, padx=10, pady=10)

        self.geo_entry = ttk.Entry(self.geo_frame_top, width=30, style="TEntry")
        self.geo_entry.pack(side=tk.LEFT, padx=10, pady=10)

        self.btn_search_geo = ttk.Button(
            self.geo_frame_top,
            text="Buscar Dirección",
            style="Neon.TButton",
            command=self.on_geo_lookup_click
        )
        self.btn_search_geo.pack(side=tk.LEFT, padx=10, pady=10)

        # Barra de progreso
        self.progress_geo = ttk.Progressbar(
            self.geo_frame_top,
            mode="indeterminate",
            style="TProgressbar"
        )
        self.progress_geo.pack(side=tk.LEFT, padx=(0,10), pady=10)

        # Cuadro de texto para mostrar resultado
        self.geo_text_frame = tk.Frame(self.tab_geo, bg=self.colors["bg_main"])
        self.geo_text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        self.txt_geo_result = tk.Text(
            self.geo_text_frame,
            wrap="word",
            height=15,
            font=("Consolas", 10),
            bg=self.colors["entry_bg"],
            fg=self.colors["entry_fg"],
            insertbackground=self.colors["entry_fg"]
        )
        self.txt_geo_result.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scroll_geo_result = ttk.Scrollbar(
            self.geo_text_frame,
            command=self.txt_geo_result.yview
        )
        self.scroll_geo_result.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_geo_result.config(yscrollcommand=self.scroll_geo_result.set)

    def on_geo_lookup_click(self):
        """Inicia la búsqueda de geolocalización en un hilo separado."""
        self.txt_geo_result.delete("1.0", tk.END)
        self.progress_geo.start(10)
        thread = Thread(target=self.geo_lookup)
        thread.start()

    def geo_lookup(self):
        """Realiza la geocodificación y genera un mapa HTML con folium."""
        time.sleep(1)
        direccion = self.geo_entry.get().strip()

        if not direccion:
            self.txt_geo_result.insert("1.0", "Por favor, introduce una dirección válida.")
            self.progress_geo.stop()
            return

        geolocator = Nominatim(user_agent="cupdev_geoloc")
        try:
            location = geolocator.geocode(direccion, timeout=10)
            if location:
                resultado = (
                    f"Dirección: {direccion}\n"
                    f"Coordenadas: ({location.latitude}, {location.longitude})\n"
                )
                self.txt_geo_result.insert("1.0", resultado)

                # Crear mapa con folium
                mapa = folium.Map(location=[location.latitude, location.longitude], zoom_start=14)
                folium.Marker(
                    [location.latitude, location.longitude],
                    popup=direccion,
                    tooltip="Ubicación"
                ).add_to(mapa)

                # Guardar mapa en un archivo temporal HTML
                mapa.save("mapa_geolocalizacion.html")
                # Abrir en el navegador
                webbrowser.open("mapa_geolocalizacion.html")
            else:
                self.txt_geo_result.insert("1.0", f"No se encontró la dirección: {direccion}")

        except Exception as e:
            self.txt_geo_result.insert("1.0", f"Ocurrió un error: {e}")

        self.progress_geo.stop()

    # ============================================
    #     PESTAÑA 4: GENERADOR DE CONTRASEÑAS
    # ============================================
    def setup_tab_password(self):
        """Configura la pestaña de Generador de Contraseñas."""
        self.pass_frame_top = tk.LabelFrame(
            self.tab_password,
            text="Generador de Contraseñas",
            font=("Consolas", 11, "bold"),
            bg=self.colors["bg_panel"],
            fg=self.colors["fg_text"]
        )
        self.pass_frame_top.pack(padx=15, pady=15, fill=tk.X)

        lbl_pass_intro = tk.Label(
            self.pass_frame_top,
            text="Configura y genera tu contraseña super-segura y ultramoderna:",
            bg=self.colors["bg_panel"],
            fg=self.colors["fg_text"],
            font=("Consolas", 10)
        )
        lbl_pass_intro.pack(side=tk.TOP, padx=10, pady=10)

        # Frame para las opciones de configuración
        config_frame = tk.Frame(self.pass_frame_top, bg=self.colors["bg_panel"])
        config_frame.pack(fill=tk.X, padx=10, pady=5)

        # Etiqueta para longitud
        lbl_length = tk.Label(config_frame, text="Longitud:", bg=self.colors["bg_panel"], fg=self.colors["fg_text"])
        lbl_length.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        # Spinbox para longitud de la contraseña
        self.pass_length = tk.IntVar(value=12)
        self.spin_length = ttk.Spinbox(
            config_frame,
            from_=4, to=64,
            textvariable=self.pass_length,
            width=5,
            style="TEntry"
        )
        self.spin_length.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Checkboxes para tipos de caracteres
        self.include_upper = tk.BooleanVar(value=True)
        self.include_lower = tk.BooleanVar(value=True)
        self.include_digits = tk.BooleanVar(value=True)
        self.include_symbols = tk.BooleanVar(value=True)

        chk_upper = ttk.Checkbutton(config_frame, text="Mayúsculas", variable=self.include_upper, style="TCheckbutton")
        chk_lower = ttk.Checkbutton(config_frame, text="Minúsculas", variable=self.include_lower, style="TCheckbutton")
        chk_digits = ttk.Checkbutton(config_frame, text="Dígitos", variable=self.include_digits, style="TCheckbutton")
        chk_symbols = ttk.Checkbutton(config_frame, text="Símbolos", variable=self.include_symbols, style="TCheckbutton")

        # Ajustamos la posición de los checkboxes
        chk_upper.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        chk_lower.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        chk_digits.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        chk_symbols.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Botón para generar
        self.btn_generate_pass = ttk.Button(
            self.pass_frame_top,
            text="Generar Contraseña",
            style="Neon.TButton",
            command=self.on_generate_pass_click
        )
        self.btn_generate_pass.pack(side=tk.LEFT, padx=15, pady=10)

        # Barra de progreso
        self.progress_pass = ttk.Progressbar(
            self.pass_frame_top,
            mode="indeterminate",
            style="TProgressbar"
        )
        self.progress_pass.pack(side=tk.LEFT, padx=(0,10), pady=10)

        # Área para mostrar la contraseña generada
        self.pass_result_frame = tk.Frame(self.tab_password, bg=self.colors["bg_main"])
        self.pass_result_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        self.txt_pass_result = tk.Text(
            self.pass_result_frame,
            wrap="word",
            height=5,
            font=("Consolas", 12, "bold"),
            bg=self.colors["entry_bg"],
            fg="#00FFFB",  # Color destacado
            insertbackground=self.colors["entry_fg"]
        )
        self.txt_pass_result.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scroll_pass_result = ttk.Scrollbar(
            self.pass_result_frame,
            command=self.txt_pass_result.yview
        )
        self.scroll_pass_result.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_pass_result.config(yscrollcommand=self.scroll_pass_result.set)

        # Botones Copiar / Guardar Contraseña
        bottom_frame = tk.Frame(self.tab_password, bg=self.colors["bg_main"])
        bottom_frame.pack(pady=10)

        self.btn_pass_copy = ttk.Button(
            bottom_frame,
            text="Copiar Contraseña",
            style="Neon.TButton",
            command=self.copiar_password
        )
        self.btn_pass_copy.grid(row=0, column=0, padx=10, pady=5)

        self.btn_pass_save = ttk.Button(
            bottom_frame,
            text="Guardar Contraseña",
            style="Neon.TButton",
            command=self.guardar_password
        )
        self.btn_pass_save.grid(row=0, column=1, padx=10, pady=5)

    def on_generate_pass_click(self):
        """Inicia la generación de contraseña con una pequeña animación."""
        self.txt_pass_result.delete("1.0", tk.END)
        self.progress_pass.start(10)
        thread = Thread(target=self.generar_password_personalizado)
        thread.start()

    def generar_password_personalizado(self):
        """Genera la contraseña basándose en las opciones de la pestaña."""
        time.sleep(1.0)  # Simulamos "procesamiento"

        length = self.pass_length.get()
        chars = ""

        if self.include_upper.get():
            chars += string.ascii_uppercase
        if self.include_lower.get():
            chars += string.ascii_lowercase
        if self.include_digits.get():
            chars += string.digits
        if self.include_symbols.get():
            chars += "!@#$%^&*()-_=+[]{};:,.<>?/\\|"

        if not chars:
            # Si no se marca ninguna opción, añadimos algo por defecto
            chars = string.ascii_letters + string.digits + "!@#$%^&*()"

        password = ''.join(random.choices(chars, k=length))
        self.txt_pass_result.insert("1.0", password)

        self.progress_pass.stop()

    def copiar_password(self):
        """Copia la contraseña generada al portapapeles."""
        contenido = self.txt_pass_result.get("1.0", tk.END).strip()
        if contenido:
            pyperclip.copy(contenido)
            messagebox.showinfo("Copiado", "Contraseña copiada al portapapeles.")

    def guardar_password(self):
        """Guarda la contraseña en un archivo de texto."""
        contenido = self.txt_pass_result.get("1.0", tk.END).strip()
        if contenido:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Texto", "*.txt")]
            )
            if filepath:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(contenido)
                messagebox.showinfo("Guardado", "Contraseña guardada correctamente.")

    # ===========================
    #     MODO OSCURO/CLARO
    # ===========================
    def toggle_dark_mode(self):
        """Alterna entre modo claro y modo oscuro."""
        self.is_dark_mode = not self.is_dark_mode
        self.colors = DARK_COLORS if self.is_dark_mode else LIGHT_COLORS
        self.apply_colors()

        new_text = "Modo Claro" if self.is_dark_mode else "Modo Oscuro"
        self.btn_toggle_mode.config(text=new_text)

        # Cambia también el gradiente de fondo
        if self.is_dark_mode:
            self.gradient_frame.color1 = "#232526"
            self.gradient_frame.color2 = "#414345"
        else:
            self.gradient_frame.color1 = "#0f0c29"
            self.gradient_frame.color2 = "#302b63"
        self.gradient_frame._draw_gradient()

    def apply_colors(self):
        """Aplica la paleta de colores a los widgets."""
        # Fondo principal
        self.main_container.configure(bg=self.colors["bg_main"])
        self.content_frame.configure(bg=self.colors["bg_main"])
        self.sidebar_frame.configure(bg=self.colors["bg_panel"])
        self.notebook_frame.configure(bg=self.colors["bg_panel"])

        # Sidebar
        self.label_logo.configure(bg=self.colors["bg_panel"], fg=self.colors["fg_text"])

        # Frames en las pestañas
        self.identity_top_frame.configure(bg=self.colors["bg_panel"], fg=self.colors["fg_text"])
        self.ip_frame_top.configure(bg=self.colors["bg_panel"], fg=self.colors["fg_text"])
        self.geo_frame_top.configure(bg=self.colors["bg_panel"], fg=self.colors["fg_text"])
        self.pass_frame_top.configure(bg=self.colors["bg_panel"], fg=self.colors["fg_text"])

        # Text widgets
        self.txt_identity.configure(bg=self.colors["entry_bg"], fg=self.colors["entry_fg"], insertbackground=self.colors["entry_fg"])
        self.txt_ip_result.configure(bg=self.colors["entry_bg"], fg=self.colors["entry_fg"], insertbackground=self.colors["entry_fg"])
        self.txt_geo_result.configure(bg=self.colors["entry_bg"], fg=self.colors["entry_fg"], insertbackground=self.colors["entry_fg"])
        self.txt_pass_result.configure(bg=self.colors["entry_bg"], insertbackground=self.colors["entry_fg"])

        # Ajustamos la top_bar (mantenemos el fondo oscuro por estilo)
        self.top_bar.configure(bg="#111111")
        self.lbl_title.configure(bg="#111111", fg="#00FFFB")

# ========================================================
#             EJECUCIÓN PRINCIPAL DE LA APP
# ========================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = ModernApp(root)
    root.mainloop()
