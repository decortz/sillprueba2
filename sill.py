# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime
import json
from streamlit_gsheets import GSheetsConnection

# Nombres de las hojas en Google Sheets
SHEET_CLIENTES = "clientes"
SHEET_VEHICULOS = "vehiculos"
SHEET_LLANTAS = "llantas"
SHEET_SERVICIOS = "servicios"
SHEET_USUARIOS = "usuarios"
SHEET_MOVIMIENTOS = "movimientos"

# Configuración de la página con colores personalizados
st.set_page_config(page_title="Sistema Integrado de Llantas", layout="wide", initial_sidebar_state="expanded")

# CSS personalizado con colores corporativos
st.markdown("""
    <style>
    /* Botones principales */
    .stButton>button {
        background-color: #2A2D62;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #F2B705;
        color: #2A2D62;
        border: none;
    }
    
    /* Tabs - solo texto amarillo, fondo transparente */
    .stTabs [data-baseweb="tab-list"] button {
        background-color: transparent;
        color: #5c5c5c;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: transparent;
        color: #F2B705 !important;
        font-weight: bold;
    }
    
    .stTabs [data-baseweb="tab-list"] button:hover {
        background-color: transparent;
        color: #F2B705;
    }
    
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #F2B705 !important;
    }
    
    /* Radio buttons - FORZAR AMARILLO */
    div[data-baseweb="radio"] > div,
    div[data-baseweb="radio"] > div > div,
    [role="radio"] > div,
    [role="radio"] > div > div {
        border-color: #cccccc !important;
    }
    
    div[data-baseweb="radio"]:hover > div,
    [role="radio"]:hover > div {
        border-color: #F2B705 !important;
    }
    
    div[data-baseweb="radio"] > div > div,
    [role="radio"] > div > div,
    div[aria-checked="true"] > div > div,
    [aria-checked="true"] > div > div {
        background-color: transparent !important;
    }
    
    div[data-baseweb="radio"][aria-checked="true"] > div,
    [role="radio"][aria-checked="true"] > div,
    div[aria-checked="true"] > div {
        border-color: #F2B705 !important;
    }
    
    div[data-baseweb="radio"][aria-checked="true"] > div > div,
    [role="radio"][aria-checked="true"] > div > div,
    div[aria-checked="true"] > div > div {
        background-color: #F2B705 !important;
    }
    
    [class*="st-"][class*="emotion"] [data-baseweb="radio"][aria-checked="true"] > div > div {
        background-color: #F2B705 !important;
    }
    
    [class*="st-"][class*="emotion"] [data-baseweb="radio"][aria-checked="true"] > div {
        border-color: #F2B705 !important;
    }
    
    /* Checkboxes */
    .stCheckbox > label > div[data-testid="stCheckbox"] > div {
        border-color: #cccccc;
    }
    
    .stCheckbox > label > div[data-testid="stCheckbox"]:hover > div {
        border-color: #F2B705;
    }
    
    .stCheckbox > label > div[data-testid="stCheckbox"] > div[data-checked="true"] {
        background-color: #F2B705 !important;
        border-color: #F2B705 !important;
    }
    
    /* Text input focus */
    .stTextInput > div > div > input:focus {
        border-color: #F2B705 !important;
        box-shadow: 0 0 0 1px #F2B705 !important;
    }
    
    /* Number input focus */
    .stNumberInput > div > div > input:focus {
        border-color: #F2B705 !important;
        box-shadow: 0 0 0 1px #F2B705 !important;
    }
    
    /* Date input focus */
    .stDateInput > div > div > input:focus {
        border-color: #F2B705 !important;
        box-shadow: 0 0 0 1px #F2B705 !important;
    }
    
    /* Selectbox focus */
    .stSelectbox > div > div:focus-within {
        border-color: #F2B705 !important;
        box-shadow: 0 0 0 1px #F2B705 !important;
    }
    
    /* Multiselect */
    .stMultiSelect > div > div:focus-within {
        border-color: #F2B705 !important;
        box-shadow: 0 0 0 1px #F2B705 !important;
    }
    
    /* Links */
    a {
        color: #2A2D62 !important;
    }
    
    a:hover {
        color: #F2B705 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ============= CONEXIÓN A GOOGLE SHEETS =============
# URL del spreadsheet
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1H05kURh2Lbo6C1rvOW4RyBNM8fyPFrlHqoT-U0TkCqE"

@st.cache_resource
def get_gsheets_connection():
    """Obtiene la conexión a Google Sheets con Service Account"""
    return st.connection("gsheets", type=GSheetsConnection)

def leer_hoja(nombre_hoja):
    """Lee una hoja de Google Sheets y retorna un DataFrame"""
    try:
        conn = get_gsheets_connection()
        df = conn.read(
            spreadsheet=SPREADSHEET_URL,
            worksheet=nombre_hoja,
            ttl=300
        )
        if df is None or df.empty:
            return pd.DataFrame()
        # Eliminar filas completamente vacías
        df = df.dropna(how='all')
        # Convertir columnas NIT a string (evitar decimales como 1234567890.0)
        for col in ['nit', 'nit_cliente']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: str(int(x)) if pd.notna(x) and isinstance(x, (int, float)) else str(x) if pd.notna(x) else '')
        return df
    except Exception as e:
        st.error(f"Error leyendo {nombre_hoja}: {str(e)}")
        return pd.DataFrame()

def leer_hoja_fresco(nombre_hoja):
    """Lee una hoja de Google Sheets SIN caché - para verificaciones críticas"""
    try:
        conn = get_gsheets_connection()
        df = conn.read(
            spreadsheet=SPREADSHEET_URL,
            worksheet=nombre_hoja,
            ttl=0
        )
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.dropna(how='all')
        # Convertir columnas NIT a string (evitar decimales como 1234567890.0)
        for col in ['nit', 'nit_cliente']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: str(int(x)) if pd.notna(x) and isinstance(x, (int, float)) else str(x) if pd.notna(x) else '')
        return df
    except Exception as e:
        st.error(f"Error leyendo {nombre_hoja}: {str(e)}")
        return pd.DataFrame()

def escribir_hoja(nombre_hoja, df):
    """Escribe un DataFrame a una hoja de Google Sheets y retorna datos frescos"""
    try:
        conn = get_gsheets_connection()
        conn.update(
            spreadsheet=SPREADSHEET_URL,
            worksheet=nombre_hoja,
            data=df
        )
        # Leer datos frescos inmediatamente después de escribir
        df_fresco = conn.read(
            spreadsheet=SPREADSHEET_URL,
            worksheet=nombre_hoja,
            ttl=0
        )
        if df_fresco is not None:
            df_fresco = df_fresco.dropna(how='all')
            # Convertir columnas NIT a string (evitar decimales como 1234567890.0)
            for col in ['nit', 'nit_cliente']:
                if col in df_fresco.columns:
                    df_fresco[col] = df_fresco[col].apply(lambda x: str(int(x)) if pd.notna(x) and isinstance(x, (int, float)) else str(x) if pd.notna(x) else '')
        return df_fresco if df_fresco is not None else df
    except Exception as e:
        st.error(f"Error escribiendo en {nombre_hoja}: {str(e)}")
        return None

def filtrar_por_clientes(df, columna_nit, clientes_acceso):
    """Filtra un DataFrame por clientes accesibles de forma segura"""
    if df.empty or columna_nit not in df.columns:
        return pd.DataFrame()
    # Convertir ambos a string para comparación consistente
    clientes_acceso_str = [str(c).strip() for c in clientes_acceso]
    return df[df[columna_nit].astype(str).str.strip().isin(clientes_acceso_str)]

def existe_valor(df, columna, valor):
    """Verifica si un valor existe en una columna de forma segura"""
    if df.empty or columna not in df.columns:
        return False
    return str(valor) in df[columna].astype(str).values

def crear_movimiento(id_llanta, tipo, vida, placa_vehiculo='', posicion='', kilometraje=0,
                     nueva_disponibilidad='', marca_reencauche='', ref_reencauche='',
                     precio_reencauche=0, observaciones=''):
    """Crea un nuevo registro en la hoja de movimientos"""
    try:
        df_movimientos = leer_hoja(SHEET_MOVIMIENTOS)

        # Generar ID de movimiento
        if df_movimientos.empty or 'id_movimiento' not in df_movimientos.columns:
            nuevo_id = 1
        else:
            nuevo_id = int(df_movimientos['id_movimiento'].max()) + 1

        # Obtener usuario actual
        usuario_actual = st.session_state.get('usuario', 'sistema')

        nuevo_movimiento = pd.DataFrame([{
            'id_movimiento': nuevo_id,
            'id_llanta': id_llanta,
            'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'tipo': tipo,
            'vida': vida,
            'placa_vehiculo': placa_vehiculo,
            'posicion': posicion,
            'kilometraje': kilometraje,
            'nueva_disponibilidad': nueva_disponibilidad,
            'marca_reencauche': marca_reencauche,
            'ref_reencauche': ref_reencauche,
            'precio_reencauche': precio_reencauche,
            'usuario': usuario_actual,
            'observaciones': observaciones
        }])

        df_movimientos = pd.concat([df_movimientos, nuevo_movimiento], ignore_index=True)
        escribir_hoja(SHEET_MOVIMIENTOS, df_movimientos)
        return True
    except Exception as e:
        st.error(f"Error creando movimiento: {str(e)}")
        return False

# ============= FUNCIONES DE INICIALIZACIÓN =============
def inicializar_datos():
    """Inicializa los datos en Google Sheets si las hojas están vacías"""
    # Verificar si usuarios está vacío y crear usuarios por defecto
    df_usuarios = leer_hoja(SHEET_USUARIOS)
    if df_usuarios.empty:
        usuarios_default = pd.DataFrame([
            {'usuario': 'admin', 'password': 'admin123', 'nivel': 1, 'nombre': 'Administrador', 'clientes_asignados': ''},
            {'usuario': 'supervisor', 'password': 'super123', 'nivel': 2, 'nombre': 'Supervisor', 'clientes_asignados': ''},
            {'usuario': 'admin_cliente', 'password': 'cliente123', 'nivel': 4, 'nombre': 'Admin Cliente', 'clientes_asignados': ''},
            {'usuario': 'operario', 'password': 'oper123', 'nivel': 3, 'nombre': 'Operario', 'clientes_asignados': ''}
        ])
        escribir_hoja(SHEET_USUARIOS, usuarios_default)

# ============= FUNCIONES AUXILIARES =============
def calcular_costo_km_vida(id_llanta, vida, guardar=False):
    """
    Calcula el costo/km de una llanta en una vida específica
    Formula: precio_vida / km_recorridos_en_vida
    Si guardar=True, actualiza el CSV con el valor calculado
    Retorna None si no hay suficientes datos
    """
    try:
        df_llantas = leer_hoja(SHEET_LLANTAS)
        df_servicios = leer_hoja(SHEET_SERVICIOS)
        
        llanta = df_llantas[df_llantas['id_llanta'] == id_llanta]
        if llanta.empty:
            return None
        
        # Obtener el precio de la vida correspondiente
        precio_col = f'precio_vida{vida}'
        if precio_col not in llanta.columns or pd.isna(llanta.iloc[0][precio_col]):
            return None
        
        precio = float(llanta.iloc[0][precio_col])
        
        # Obtener servicios de esa vida específica
        servicios_vida = df_servicios[
            (df_servicios['id_llanta'] == id_llanta) & 
            (df_servicios['vida'] == vida)
        ]
        
        if servicios_vida.empty or len(servicios_vida) < 2:
            return None
        
        # Calcular kilómetros recorridos en esa vida
        km_inicial = servicios_vida['kilometraje'].min()
        km_final = servicios_vida['kilometraje'].max()
        km_recorridos = km_final - km_inicial
        
        if km_recorridos <= 0:
            return None
        
        # Calcular costo/km
        costo_km = precio / km_recorridos
        costo_km_redondeado = round(costo_km, 2)
        
        # Guardar en CSV si se solicita
        if guardar:
            costo_col = f'costo_km_vida{vida}'
            df_llantas.loc[df_llantas['id_llanta'] == id_llanta, costo_col] = costo_km_redondeado
            escribir_hoja(SHEET_LLANTAS, df_llantas)
        
        return costo_km_redondeado
    
    except Exception as e:
        return None

def calcular_costo_km_acumulado(id_llanta):
    """
    Calcula el costo/km acumulado de todas las vidas de una llanta
    Formula: suma(precios_vidas) / km_totales
    """
    try:
        df_llantas = leer_hoja(SHEET_LLANTAS)
        df_servicios = leer_hoja(SHEET_SERVICIOS)
        
        llanta = df_llantas[df_llantas['id_llanta'] == id_llanta]
        if llanta.empty:
            return None
        
        # Sumar todos los precios de vidas que se han usado
        vida_val = llanta.iloc[0].get('vida_actual', llanta.iloc[0].get('vida', 1))
        vida_actual = int(vida_val) if pd.notna(vida_val) else 1
        precio_total = 0
        
        for v in range(1, vida_actual + 2):  # +2 porque vida 0 = nueva (vida1)
            precio_col = f'precio_vida{v}'
            if precio_col in llanta.columns and pd.notna(llanta.iloc[0][precio_col]):
                precio_total += float(llanta.iloc[0][precio_col])
        
        # Obtener todos los servicios de la llanta
        servicios_llanta = df_servicios[df_servicios['id_llanta'] == id_llanta]
        
        if servicios_llanta.empty or len(servicios_llanta) < 2:
            return None
        
        # Calcular kilómetros totales recorridos
        km_inicial = servicios_llanta['kilometraje'].min()
        km_final = servicios_llanta['kilometraje'].max()
        km_totales = km_final - km_inicial
        
        if km_totales <= 0 or precio_total <= 0:
            return None
        
        # Calcular costo/km acumulado
        costo_km_acumulado = precio_total / km_totales
        return round(costo_km_acumulado, 2)
    
    except Exception as e:
        return None

def actualizar_costos_km_llanta(id_llanta):
    """
    Actualiza todos los costos/km de una llanta después de registrar un servicio
    Recalcula costo_km_vida1, costo_km_vida2, costo_km_vida3, costo_km_vida4
    """
    try:
        df_llantas = leer_hoja(SHEET_LLANTAS)
        
        llanta = df_llantas[df_llantas['id_llanta'] == id_llanta]
        if llanta.empty:
            return False
        
        vida_val = llanta.iloc[0].get('vida_actual', llanta.iloc[0].get('vida', 1))
        vida_actual = int(vida_val) if pd.notna(vida_val) else 1

        # Recalcular costos para cada vida que se ha usado
        for v in range(1, 5):  # Vidas 1, 2, 3, 4
            if v <= vida_actual + 1:  # +1 porque vida 0 = nueva (vida1)
                costo_km = calcular_costo_km_vida(id_llanta, v, guardar=False)
                costo_col = f'costo_km_vida{v}'
                
                if costo_km is not None:
                    df_llantas.loc[df_llantas['id_llanta'] == id_llanta, costo_col] = costo_km
                else:
                    # Si no hay suficientes datos, dejar en 0 o None
                    if costo_col in df_llantas.columns:
                        df_llantas.loc[df_llantas['id_llanta'] == id_llanta, costo_col] = None
        
        escribir_hoja(SHEET_LLANTAS, df_llantas)
        return True
    
    except Exception as e:
        return False

def tiene_acceso_cliente(nit_cliente):
    """Verifica si el usuario tiene acceso al cliente especificado"""
    nivel = st.session_state.get('nivel', 999)

    # Solo nivel 1 (Admin) tiene acceso a todos los clientes
    if nivel == 1:
        return True

    # Niveles 2, 3 y 4 solo acceden a clientes asignados
    if nivel in [2, 3, 4]:
        clientes_asignados = st.session_state.get('clientes_asignados', '')
        if clientes_asignados:
            lista_clientes = [c.strip() for c in clientes_asignados.split(',')]
            return str(nit_cliente) in lista_clientes
        return False

    return False

def obtener_clientes_accesibles():
    """Retorna lista de NITs de clientes a los que el usuario tiene acceso"""
    nivel = st.session_state.get('nivel', 999)

    # Solo nivel 1 (Admin) ve todos los clientes
    if nivel == 1:
        df_clientes = leer_hoja(SHEET_CLIENTES)
        return df_clientes['nit'].tolist() if not df_clientes.empty else []

    # Niveles 2, 3 y 4 solo ven clientes asignados
    if nivel in [2, 3, 4]:
        clientes_asignados = st.session_state.get('clientes_asignados', '')
        # Asegurar que sea string válido (puede ser NaN, None, float)
        if clientes_asignados and pd.notna(clientes_asignados) and isinstance(clientes_asignados, str):
            return [c.strip() for c in clientes_asignados.split(',') if c.strip()]
        return []

    return []

def generar_id_servicio(nit_cliente, frente):
    """Genera el ID de servicio con formato: 2 letras cliente + letra frente + consecutivo"""
    df_clientes = leer_hoja(SHEET_CLIENTES)
    df_servicios = leer_hoja(SHEET_SERVICIOS)

    nombre_cliente = df_clientes[df_clientes['nit'] == nit_cliente]['nombre_cliente'].values[0]

    nombre_limpio = nombre_cliente.replace(" ", "")
    prefijo_cliente = nombre_limpio[:2].upper()

    if frente and frente != "General":
        prefijo_frente = frente[0].upper()
    else:
        prefijo_frente = ""

    prefijo = prefijo_cliente + prefijo_frente

    # Verificar que df_servicios tiene la columna necesaria
    if df_servicios.empty or 'id_servicio' not in df_servicios.columns:
        consecutivo = 1
    else:
        servicios_prefijo = df_servicios[df_servicios['id_servicio'].str.startswith(prefijo, na=False)]

        if servicios_prefijo.empty:
            consecutivo = 1
        else:
            try:
                numeros = servicios_prefijo['id_servicio'].str.extract(r'(\d+)$')[0].astype(int)
                consecutivo = numeros.max() + 1
            except:
                consecutivo = 1

    id_servicio = f"{prefijo}{consecutivo:04d}"

    return id_servicio

# ============= SISTEMA DE AUTENTICACIÓN =============
def login():
    """Sistema de login con niveles de usuario"""
    st.title("🔐 Sistema Integrado de Llantas")
    st.subheader("Inicio de Sesión")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        
        if st.button("Iniciar Sesión", use_container_width=True):
            df_usuarios = leer_hoja(SHEET_USUARIOS)
            user_data = df_usuarios[(df_usuarios['usuario'] == usuario) & (df_usuarios['password'] == password)]
            
            if not user_data.empty:
                st.session_state['logged_in'] = True
                st.session_state['usuario'] = usuario
                st.session_state['nivel'] = int(user_data.iloc[0]['nivel'])
                st.session_state['nombre'] = user_data.iloc[0]['nombre']

                # Guardar clientes_asignados como string válido
                if 'clientes_asignados' in user_data.columns:
                    clientes_valor = user_data.iloc[0]['clientes_asignados']
                    # Convertir a string y manejar NaN/None/float
                    if pd.notna(clientes_valor) and clientes_valor:
                        st.session_state['clientes_asignados'] = str(clientes_valor)
                    else:
                        st.session_state['clientes_asignados'] = ''
                else:
                    st.session_state['clientes_asignados'] = ''

                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

def verificar_permiso(nivel_requerido):
    """Verifica si el usuario tiene el nivel necesario"""
    if st.session_state.get('nivel', 999) > nivel_requerido:
        st.error(f"⛔ No tienes permisos suficientes. Se requiere nivel {nivel_requerido} o superior.")
        return False
    return True

# ============= FUNCIÓN: SUBIR DATOS CSV =============
def subir_datos_csv():
    """Función para cargar datos desde archivos CSV usando append"""

    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("📤 Subir Datos desde CSV")

    if not verificar_permiso(1):  # Solo Administrador puede subir CSV
        return
    
    st.subheader("Selecciona qué datos deseas cargar")
    
    tipo_dato = st.selectbox(
        "Tipo de Datos",
        options=["Clientes", "Vehículos", "Llantas", "Servicios", "Movimientos"]
    )
    
    archivo = st.file_uploader(f"Subir archivo CSV de {tipo_dato}", type=['csv'])
    
    if archivo is not None:
        try:
            df_nuevo = pd.read_csv(archivo, encoding='utf-8')
            
            st.write("**Vista previa de los datos:**")
            st.dataframe(df_nuevo.head(), use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Confirmar y Agregar Datos", type="primary"):
                    if tipo_dato == "Clientes":
                        df_existente = leer_hoja(SHEET_CLIENTES)
                        df_combinado = pd.concat([df_existente, df_nuevo], ignore_index=True)
                        escribir_hoja(SHEET_CLIENTES, df_combinado)
                    elif tipo_dato == "Vehículos":
                        df_existente = leer_hoja(SHEET_VEHICULOS)
                        df_combinado = pd.concat([df_existente, df_nuevo], ignore_index=True)
                        escribir_hoja(SHEET_VEHICULOS, df_combinado)
                    elif tipo_dato == "Llantas":
                        df_existente = leer_hoja(SHEET_LLANTAS)
                        df_combinado = pd.concat([df_existente, df_nuevo], ignore_index=True)
                        escribir_hoja(SHEET_LLANTAS, df_combinado)
                    elif tipo_dato == "Servicios":
                        df_existente = leer_hoja(SHEET_SERVICIOS)
                        df_combinado = pd.concat([df_existente, df_nuevo], ignore_index=True)
                        escribir_hoja(SHEET_SERVICIOS, df_combinado)
                    elif tipo_dato == "Movimientos":
                        df_existente = leer_hoja(SHEET_MOVIMIENTOS)
                        df_combinado = pd.concat([df_existente, df_nuevo], ignore_index=True)
                        escribir_hoja(SHEET_MOVIMIENTOS, df_combinado)

                    st.success(f"✅ Datos de {tipo_dato} agregados exitosamente")
                    st.rerun()
            
            with col2:
                if st.button("❌ Cancelar"):
                    st.rerun()
                    
        except Exception as e:
            st.error(f"Error al leer el archivo: {str(e)}")
            st.info("Asegúrate de que el CSV tenga las columnas correctas y esté codificado en UTF-8")

# ============= FUNCIÓN: ELIMINAR Y CORREGIR DATOS =============
def eliminar_corregir_datos():
    """Función para eliminar o corregir datos"""
    
    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("✏️ Eliminar o Corregir Datos")
    
    if not verificar_permiso(2):
        return
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚛 Vehículos", "⚙️ Llantas", "🛠️ Servicios", "👤 Clientes", "📦 Movimientos"])
    
    with tab1:
        st.subheader("Gestión de Vehículos")
        df_vehiculos = leer_hoja(SHEET_VEHICULOS)
        
        if not df_vehiculos.empty:
            clientes_acceso = obtener_clientes_accesibles()
            df_vehiculos = filtrar_por_clientes(df_vehiculos, 'nit_cliente', clientes_acceso)
            
            if not df_vehiculos.empty:
                id_editar = st.selectbox("Seleccionar Vehículo",
                    df_vehiculos['id_vehiculo'].values,
                    format_func=lambda x: f"ID {x} - {df_vehiculos[df_vehiculos['id_vehiculo']==x]['placa_vehiculo'].values[0]}",
                    key="select_vehiculo_editar")
                
                vehiculo = df_vehiculos[df_vehiculos['id_vehiculo'] == id_editar].iloc[0]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    nueva_marca = st.text_input("Marca", value=vehiculo.get('marca', ''), key="edit_marca_vehiculo")
                    nuevo_estado = st.selectbox("Estado",
                        options=['no_asignado', 'activo', 'fuera_de_servicio'],
                        index=['no_asignado', 'activo', 'fuera_de_servicio'].index(vehiculo.get('estado', 'no_asignado')),
                        key="edit_estado_vehiculo")

                with col2:
                    nueva_linea = st.text_input("Línea", value=vehiculo.get('linea', ''), key="edit_linea_vehiculo")
                    nuevo_km_inicial = st.number_input("Kilometraje Inicial", value=float(vehiculo.get('kilometraje_inicial', 0)), key="edit_km_vehiculo")

                with col3:
                    nueva_tipologia = st.text_input("Tipología", value=vehiculo.get('tipologia', ''), key="edit_tipologia_vehiculo")
                    nuevo_calculo = st.selectbox("Cálculo KMs",
                        options=['odometro', 'promedio', 'tabla'],
                        index=['odometro', 'promedio', 'tabla'].index(vehiculo.get('calculo_kms', 'odometro')),
                        key="edit_calculo_vehiculo")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("💾 Guardar Cambios", key="guardar_vehiculo"):
                        df_todos = leer_hoja(SHEET_VEHICULOS)
                        df_todos.loc[df_todos['id_vehiculo'] == id_editar, 'marca'] = nueva_marca
                        df_todos.loc[df_todos['id_vehiculo'] == id_editar, 'linea'] = nueva_linea
                        df_todos.loc[df_todos['id_vehiculo'] == id_editar, 'tipologia'] = nueva_tipologia
                        df_todos.loc[df_todos['id_vehiculo'] == id_editar, 'estado'] = nuevo_estado
                        df_todos.loc[df_todos['id_vehiculo'] == id_editar, 'kilometraje_inicial'] = nuevo_km_inicial
                        df_todos.loc[df_todos['id_vehiculo'] == id_editar, 'calculo_kms'] = nuevo_calculo
                        escribir_hoja(SHEET_VEHICULOS, df_todos)
                        st.success("✅ Vehículo actualizado con éxito")
                        st.rerun()
                
                with col_btn2:
                    if st.button("🗑️ Eliminar Vehículo", key="eliminar_vehiculo"):
                        df_todos = leer_hoja(SHEET_VEHICULOS)
                        df_todos = df_todos[df_todos['id_vehiculo'] != id_editar]
                        escribir_hoja(SHEET_VEHICULOS, df_todos)
                        st.success("✅ Vehículo eliminado con éxito")
                        st.rerun()
            else:
                st.info("No tienes vehículos accesibles")
        else:
            st.info("No hay vehículos registrados")
    
    with tab2:
        st.subheader("Gestión de Llantas")
        df_llantas = leer_hoja(SHEET_LLANTAS)
        
        if not df_llantas.empty:
            clientes_acceso = obtener_clientes_accesibles()
            df_llantas = filtrar_por_clientes(df_llantas, 'nit_cliente', clientes_acceso)
            
            if not df_llantas.empty:
                id_editar = st.selectbox("Seleccionar Llanta", df_llantas['id_llanta'].values, key="select_llanta_editar")
                
                llanta = df_llantas[df_llantas['id_llanta'] == id_editar].iloc[0]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    nueva_marca = st.text_input("Marca", value=llanta.get('marca_llanta', ''), key="edit_marca_llanta")
                    nueva_referencia = st.text_input("Referencia", value=llanta.get('referencia', ''), key="edit_referencia_llanta")

                with col2:
                    nueva_dimension = st.text_input("Dimensión", value=llanta.get('dimension', ''), key="edit_dimension_llanta")
                    precio_v1 = st.number_input("Precio Vida 1", value=float(llanta.get('precio_vida1', 0)), key="edit_precio_v1_llanta")

                with col3:
                    precio_v2 = st.number_input("Precio Vida 2", value=float(llanta.get('precio_vida2', 0)), key="edit_precio_v2_llanta")
                    precio_v3 = st.number_input("Precio Vida 3", value=float(llanta.get('precio_vida3', 0)), key="edit_precio_v3_llanta")

                precio_v4 = st.number_input("Precio Vida 4", value=float(llanta.get('precio_vida4', 0)), key="edit_precio_v4_llanta")
                
                st.info("💡 Los costos/km se recalculan automáticamente al guardar cambios")
                
                if st.button("💾 Guardar Cambios", key="guardar_llanta"):
                    df_todos = leer_hoja(SHEET_LLANTAS)
                    df_todos.loc[df_todos['id_llanta'] == id_editar, 'marca_llanta'] = nueva_marca
                    df_todos.loc[df_todos['id_llanta'] == id_editar, 'referencia'] = nueva_referencia
                    df_todos.loc[df_todos['id_llanta'] == id_editar, 'dimension'] = nueva_dimension
                    df_todos.loc[df_todos['id_llanta'] == id_editar, 'precio_vida1'] = precio_v1
                    df_todos.loc[df_todos['id_llanta'] == id_editar, 'precio_vida2'] = precio_v2
                    df_todos.loc[df_todos['id_llanta'] == id_editar, 'precio_vida3'] = precio_v3
                    df_todos.loc[df_todos['id_llanta'] == id_editar, 'precio_vida4'] = precio_v4
                    escribir_hoja(SHEET_LLANTAS, df_todos)
                    
                    # Recalcular costos/km después de guardar
                    actualizar_costos_km_llanta(id_editar)
                    
                    st.success("✅ Llanta actualizada con éxito")
                    st.rerun()
                
                if st.button("🗑️ Eliminar Llanta", key="eliminar_llanta"):
                    df_todos = leer_hoja(SHEET_LLANTAS)
                    df_todos = df_todos[df_todos['id_llanta'] != id_editar]
                    escribir_hoja(SHEET_LLANTAS, df_todos)
                    st.success("✅ Llanta eliminada con éxito")
                    st.rerun()
            else:
                st.info("No tienes llantas accesibles")
        else:
            st.info("No hay llantas registradas")
    
    with tab3:
        st.subheader("Gestión de Servicios")
        df_servicios = leer_hoja(SHEET_SERVICIOS)

        if not df_servicios.empty:
            id_servicio_editar = st.selectbox("Seleccionar Servicio", df_servicios['id_servicio'].values, key="select_servicio_editar")

            servicio = df_servicios[df_servicios['id_servicio'] == id_servicio_editar].iloc[0]

            st.write("**Datos del Servicio:**")
            col1, col2, col3 = st.columns(3)

            with col1:
                # Fecha del servicio
                fecha_actual = servicio.get('fecha', '')
                try:
                    fecha_parsed = datetime.strptime(str(fecha_actual), "%d/%m/%Y").date() if fecha_actual else datetime.now().date()
                except:
                    fecha_parsed = datetime.now().date()
                nueva_fecha = st.date_input("Fecha", value=fecha_parsed, key="edit_fecha_servicio")

                # Kilometraje
                km_actual = int(servicio.get('kilometraje', 0)) if pd.notna(servicio.get('kilometraje')) else 0
                nuevo_km = st.number_input("Kilometraje", min_value=0, value=km_actual, key="edit_km_servicio")

            with col2:
                st.write("**Profundidades (mm)**")
                prof1_actual = float(servicio.get('profundidad_1', 10.0)) if pd.notna(servicio.get('profundidad_1')) else 10.0
                prof2_actual = float(servicio.get('profundidad_2', 10.0)) if pd.notna(servicio.get('profundidad_2')) else 10.0
                prof3_actual = float(servicio.get('profundidad_3', 10.0)) if pd.notna(servicio.get('profundidad_3')) else 10.0

                nueva_prof1 = st.number_input("Profundidad 1", min_value=0.0, max_value=30.0, value=prof1_actual, step=0.5, key="edit_prof1")
                nueva_prof2 = st.number_input("Profundidad 2", min_value=0.0, max_value=30.0, value=prof2_actual, step=0.5, key="edit_prof2")
                nueva_prof3 = st.number_input("Profundidad 3", min_value=0.0, max_value=30.0, value=prof3_actual, step=0.5, key="edit_prof3")

            with col3:
                st.write("**Servicios Realizados**")
                edit_rotacion = st.checkbox("Rotación", value=(servicio.get('rotacion', 'No') == 'Sí'), key="edit_rotacion")
                if edit_rotacion:
                    edit_pos_nueva = st.text_input("Nueva Posición", value=servicio.get('posicion_nueva', ''), key="edit_pos_nueva")
                else:
                    edit_pos_nueva = ""
                edit_balanceo = st.checkbox("Balanceo", value=(servicio.get('balanceo', 'No') == 'Sí'), key="edit_balanceo")
                edit_alineacion = st.checkbox("Alineación", value=(servicio.get('alineacion', 'No') == 'Sí'), key="edit_alineacion")
                edit_regrabacion = st.checkbox("Regrabación", value=(servicio.get('regrabacion', 'No') == 'Sí'), key="edit_regrabacion")
                edit_torqueo = st.checkbox("Torqueo", value=(servicio.get('torqueo', 'No') == 'Sí'), key="edit_torqueo")

            # Comentario FVU (campo adicional)
            comentario_actual = servicio.get('comentario_fvu', '') if pd.notna(servicio.get('comentario_fvu')) else ''
            nuevo_comentario = st.text_area("Comentario FVU", value=comentario_actual, key="edit_comentario_fvu")

            col_btn1, col_btn2 = st.columns(2)

            with col_btn1:
                if st.button("💾 Guardar Cambios", key="guardar_servicio", type="primary"):
                    if edit_rotacion and not edit_pos_nueva:
                        st.error("Si hay rotación, debes especificar la nueva posición")
                    else:
                        # Actualizar los campos editables
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'fecha'] = nueva_fecha.strftime("%d/%m/%Y")
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'kilometraje'] = nuevo_km
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'profundidad_1'] = nueva_prof1
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'profundidad_2'] = nueva_prof2
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'profundidad_3'] = nueva_prof3
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'rotacion'] = 'Sí' if edit_rotacion else 'No'
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'posicion_nueva'] = edit_pos_nueva if edit_rotacion else ''
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'balanceo'] = 'Sí' if edit_balanceo else 'No'
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'alineacion'] = 'Sí' if edit_alineacion else 'No'
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'regrabacion'] = 'Sí' if edit_regrabacion else 'No'
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'torqueo'] = 'Sí' if edit_torqueo else 'No'
                        df_servicios.loc[df_servicios['id_servicio'] == id_servicio_editar, 'comentario_fvu'] = nuevo_comentario

                        escribir_hoja(SHEET_SERVICIOS, df_servicios)

                        # Recalcular costos si cambió el kilometraje
                        id_llanta_servicio = servicio.get('id_llanta')
                        if id_llanta_servicio:
                            actualizar_costos_km_llanta(id_llanta_servicio)

                        st.success("✅ Servicio actualizado con éxito")
                        st.rerun()

            with col_btn2:
                if st.button("🗑️ Eliminar Servicio", key="eliminar_servicio"):
                    df_servicios = df_servicios[df_servicios['id_servicio'] != id_servicio_editar]
                    escribir_hoja(SHEET_SERVICIOS, df_servicios)
                    st.success("✅ Servicio eliminado con éxito")
                    st.rerun()

            # Mostrar información de referencia
            st.divider()
            st.caption(f"ID Llanta: {servicio.get('id_llanta', 'N/A')} | Placa: {servicio.get('placa_vehiculo', 'N/A')} | Posición original: {servicio.get('posicion', 'N/A')} | Vida: {servicio.get('vida', 'N/A')}")
        else:
            st.info("No hay servicios registrados")
    
    with tab4:
        st.subheader("Gestión de Clientes")
        
        if st.session_state.get('nivel') != 1:
            st.warning("⚠️ Solo el Administrador puede editar clientes")
            return
        
        df_clientes = leer_hoja(SHEET_CLIENTES)
        
        if not df_clientes.empty:
            nit_editar = st.selectbox("Seleccionar Cliente", df_clientes['nit'].values, key="select_cliente_editar")
            
            cliente = df_clientes[df_clientes['nit'] == nit_editar].iloc[0]
            
            nuevo_nombre = st.text_input("Nombre Cliente", value=cliente['nombre_cliente'], key="edit_nombre_cliente")
            
            if st.button("💾 Guardar Cambios", key="guardar_cliente"):
                df_clientes.loc[df_clientes['nit'] == nit_editar, 'nombre_cliente'] = nuevo_nombre
                escribir_hoja(SHEET_CLIENTES, df_clientes)
                st.success("✅ Cliente actualizado con éxito")
                st.rerun()
            
            if st.button("🗑️ Eliminar Cliente", key="eliminar_cliente"):
                df_clientes = df_clientes[df_clientes['nit'] != nit_editar]
                escribir_hoja(SHEET_CLIENTES, df_clientes)
                st.success("✅ Cliente eliminado con éxito")
                st.rerun()
        else:
            st.info("No hay clientes registrados")

    with tab5:
        st.subheader("Gestión de Movimientos")

        df_movimientos = leer_hoja(SHEET_MOVIMIENTOS)

        if not df_movimientos.empty:
            # Filtrar por clientes accesibles
            clientes_acceso = obtener_clientes_accesibles()
            if st.session_state.get('nivel') != 1:
                df_llantas_temp = leer_hoja(SHEET_LLANTAS)
                llantas_cliente = df_llantas_temp[df_llantas_temp['nit_cliente'].isin(clientes_acceso)]['id_llanta'].tolist()
                df_movimientos = df_movimientos[df_movimientos['id_llanta'].isin(llantas_cliente)]

            if not df_movimientos.empty:
                id_mov_editar = st.selectbox(
                    "Seleccionar Movimiento",
                    options=df_movimientos['id_movimiento'].values,
                    format_func=lambda x: f"ID {x} - Llanta {df_movimientos[df_movimientos['id_movimiento']==x]['id_llanta'].values[0]} - {df_movimientos[df_movimientos['id_movimiento']==x]['tipo'].values[0]} ({df_movimientos[df_movimientos['id_movimiento']==x]['fecha'].values[0]})",
                    key="select_movimiento_editar"
                )

                movimiento = df_movimientos[df_movimientos['id_movimiento'] == id_mov_editar].iloc[0]

                st.write("**Datos del Movimiento:**")
                col1, col2, col3 = st.columns(3)

                with col1:
                    # Tipo de movimiento
                    tipos_mov = ['montaje', 'desmontaje', 'aprobacion_reencauche', 'rotacion', 'otro']
                    tipo_actual = movimiento.get('tipo', 'otro')
                    tipo_idx = tipos_mov.index(tipo_actual) if tipo_actual in tipos_mov else 4
                    nuevo_tipo = st.selectbox("Tipo", options=tipos_mov, index=tipo_idx, key="edit_tipo_mov")

                    # Vida
                    vida_mov = int(movimiento.get('vida', 1)) if pd.notna(movimiento.get('vida')) else 1
                    vida_mov = max(1, vida_mov)  # Asegurar que sea al menos 1
                    # Limpiar session_state si tiene valor inválido
                    if 'edit_vida_mov' in st.session_state and st.session_state['edit_vida_mov'] < 1:
                        del st.session_state['edit_vida_mov']
                    nueva_vida = st.number_input("Vida", min_value=1, max_value=4, value=vida_mov, key="edit_vida_mov")

                with col2:
                    # Placa vehículo
                    placa_mov = movimiento.get('placa_vehiculo', '') if pd.notna(movimiento.get('placa_vehiculo')) else ''
                    nueva_placa = st.text_input("Placa Vehículo", value=placa_mov, key="edit_placa_mov")

                    # Posición
                    pos_mov = movimiento.get('posicion', '') if pd.notna(movimiento.get('posicion')) else ''
                    nueva_posicion = st.text_input("Posición", value=pos_mov, key="edit_pos_mov")

                with col3:
                    # Kilometraje
                    km_mov = int(movimiento.get('kilometraje', 0)) if pd.notna(movimiento.get('kilometraje')) else 0
                    nuevo_km = st.number_input("Kilometraje", min_value=0, value=km_mov, key="edit_km_mov")

                    # Nueva disponibilidad
                    disp_mov = movimiento.get('nueva_disponibilidad', '') if pd.notna(movimiento.get('nueva_disponibilidad')) else ''
                    nueva_disp = st.text_input("Nueva Disponibilidad", value=disp_mov, key="edit_disp_mov")

                # Datos de reencauche (si aplica)
                st.write("**Datos de Reencauche (si aplica):**")
                col4, col5, col6 = st.columns(3)

                with col4:
                    marca_reenc = movimiento.get('marca_reencauche', '') if pd.notna(movimiento.get('marca_reencauche')) else ''
                    nueva_marca_reenc = st.text_input("Marca Reencauche", value=marca_reenc, key="edit_marca_reenc")

                with col5:
                    ref_reenc = movimiento.get('ref_reencauche', '') if pd.notna(movimiento.get('ref_reencauche')) else ''
                    nueva_ref_reenc = st.text_input("Ref. Reencauche", value=ref_reenc, key="edit_ref_reenc")

                with col6:
                    precio_reenc = float(movimiento.get('precio_reencauche', 0)) if pd.notna(movimiento.get('precio_reencauche')) else 0
                    nuevo_precio_reenc = st.number_input("Precio Reencauche", min_value=0.0, value=precio_reenc, key="edit_precio_reenc")

                # Observaciones
                obs_mov = movimiento.get('observaciones', '') if pd.notna(movimiento.get('observaciones')) else ''
                nuevas_obs = st.text_area("Observaciones", value=obs_mov, key="edit_obs_mov")

                col_btn1, col_btn2 = st.columns(2)

                with col_btn1:
                    if st.button("💾 Guardar Cambios", key="guardar_movimiento", type="primary"):
                        df_mov_todos = leer_hoja(SHEET_MOVIMIENTOS)
                        df_mov_todos.loc[df_mov_todos['id_movimiento'] == id_mov_editar, 'tipo'] = nuevo_tipo
                        df_mov_todos.loc[df_mov_todos['id_movimiento'] == id_mov_editar, 'vida'] = nueva_vida
                        df_mov_todos.loc[df_mov_todos['id_movimiento'] == id_mov_editar, 'placa_vehiculo'] = nueva_placa
                        df_mov_todos.loc[df_mov_todos['id_movimiento'] == id_mov_editar, 'posicion'] = nueva_posicion
                        df_mov_todos.loc[df_mov_todos['id_movimiento'] == id_mov_editar, 'kilometraje'] = nuevo_km
                        df_mov_todos.loc[df_mov_todos['id_movimiento'] == id_mov_editar, 'nueva_disponibilidad'] = nueva_disp
                        df_mov_todos.loc[df_mov_todos['id_movimiento'] == id_mov_editar, 'marca_reencauche'] = nueva_marca_reenc
                        df_mov_todos.loc[df_mov_todos['id_movimiento'] == id_mov_editar, 'ref_reencauche'] = nueva_ref_reenc
                        df_mov_todos.loc[df_mov_todos['id_movimiento'] == id_mov_editar, 'precio_reencauche'] = nuevo_precio_reenc
                        df_mov_todos.loc[df_mov_todos['id_movimiento'] == id_mov_editar, 'observaciones'] = nuevas_obs
                        escribir_hoja(SHEET_MOVIMIENTOS, df_mov_todos)
                        st.success("✅ Movimiento actualizado con éxito")
                        st.rerun()

                with col_btn2:
                    if st.button("🗑️ Eliminar Movimiento", key="eliminar_movimiento"):
                        df_mov_todos = leer_hoja(SHEET_MOVIMIENTOS)
                        df_mov_todos = df_mov_todos[df_mov_todos['id_movimiento'] != id_mov_editar]
                        escribir_hoja(SHEET_MOVIMIENTOS, df_mov_todos)
                        st.success("✅ Movimiento eliminado con éxito")
                        st.rerun()

                # Mostrar información de referencia
                st.divider()
                st.caption(f"ID Llanta: {movimiento.get('id_llanta', 'N/A')} | Fecha: {movimiento.get('fecha', 'N/A')} | Usuario: {movimiento.get('usuario', 'N/A')}")
            else:
                st.info("No tienes movimientos accesibles")
        else:
            st.info("No hay movimientos registrados")

# ============= FUNCIÓN: LLANTAS DISPONIBLES =============
def ver_llantas_disponibles():
    """Función para ver todas las llantas y su disponibilidad"""
    
    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("🔍 Estado de Llantas")
    
    df_llantas = leer_hoja(SHEET_LLANTAS)
    
    if df_llantas.empty:
        st.info("No hay llantas registradas")
        return
    
    clientes_acceso = obtener_clientes_accesibles()
    df_llantas = filtrar_por_clientes(df_llantas, 'nit_cliente', clientes_acceso)
    
    if df_llantas.empty or 'disponibilidad' not in df_llantas.columns:
        st.info("No tienes llantas accesibles")
        return

    tab1, tab2, tab3 = st.tabs(["📋 Ver Todas", "✅ Aprobar Reencauches", "💰 Análisis de Costos"])

    with tab1:
        st.subheader("Inventario Completo de Llantas")

        col1, col2, col3 = st.columns(3)
        with col1:
            opciones_disp = list(df_llantas['disponibilidad'].unique())
            opciones_disp.insert(0, "Todas")
            filtro_disp = st.selectbox("Filtrar por Disponibilidad", options=opciones_disp)
        
        if filtro_disp == "Todas":
            df_filtrado = df_llantas
        else:
            df_filtrado = df_llantas[df_llantas['disponibilidad'] == filtro_disp]
        
        columnas_mostrar = ['id_llanta', 'marca_llanta', 'referencia', 'dimension', 'disponibilidad', 
                           'placa_vehiculo', 'pos_inicial', 'vida', 'precio_vida1', 'precio_vida2', 
                           'precio_vida3', 'precio_vida4', 'costo_km_vida1', 'costo_km_vida2', 
                           'costo_km_vida3', 'costo_km_vida4']
        
        columnas_disponibles = [col for col in columnas_mostrar if col in df_filtrado.columns]
        st.dataframe(df_filtrado[columnas_disponibles], use_container_width=True)
    
    with tab2:
        st.subheader("✅ Aprobar Reencauches")

        if not verificar_permiso(2):
            return

        llantas_reencauche = df_llantas[
            (df_llantas['disponibilidad'] == 'reencauche') &
            (df_llantas['estado_reencauche'] == 'condicionada_planta')
        ]

        if not llantas_reencauche.empty:
            st.info(f"📋 **{len(llantas_reencauche)} llantas** pendientes de aprobación de planta de reencauche")

            # Formulario de datos del reencauche
            st.write("### Datos del Reencauche")
            col_form1, col_form2, col_form3 = st.columns(3)

            with col_form1:
                marca_reencauche = st.text_input("🏭 Marca Reencauche", placeholder="Ej: Vipal, Bandag")
            with col_form2:
                referencia_reencauche = st.text_input("📋 Referencia", placeholder="Ej: VT120, BDR-AS")
            with col_form3:
                precio_reencauche = st.number_input("💰 Precio Reencauche", min_value=0.0, value=0.0, step=10000.0)

            st.divider()
            st.write("### Seleccionar Llantas a Aprobar")
            st.caption("Marca las llantas que deseas aprobar con los datos ingresados arriba")

            # Inicializar estado de selección si no existe
            if 'llantas_seleccionadas' not in st.session_state:
                st.session_state.llantas_seleccionadas = []

            # Mostrar tabla con checkboxes
            llantas_seleccionadas = []
            for idx, row in llantas_reencauche.iterrows():
                id_llanta = row['id_llanta']
                marca_original = row.get('marca_llanta', 'N/A')
                referencia_original = row.get('referencia', 'N/A')
                dimension = row.get('dimension', 'N/A')
                vida_val = row.get('vida_actual', row.get('vida', 1))
                vida_actual = int(vida_val) if pd.notna(vida_val) else 1
                vida_nueva = vida_actual + 1

                col_check, col_info, col_vida = st.columns([0.5, 3, 1])

                with col_check:
                    seleccionada = st.checkbox("", key=f"sel_{id_llanta}", label_visibility="collapsed")
                    if seleccionada:
                        llantas_seleccionadas.append(id_llanta)

                with col_info:
                    st.write(f"**ID {id_llanta}** - {marca_original} {referencia_original} ({dimension})")

                with col_vida:
                    st.write(f"Vida {vida_actual} → **{vida_nueva}**")

            st.divider()

            # Botón de aprobación múltiple
            col_btn1, col_btn2 = st.columns([1, 3])
            with col_btn1:
                aprobar_btn = st.button("✅ Aprobar Seleccionadas", type="primary", disabled=len(llantas_seleccionadas) == 0)

            with col_btn2:
                if len(llantas_seleccionadas) > 0:
                    st.write(f"Se aprobarán **{len(llantas_seleccionadas)}** llantas")

            if aprobar_btn:
                if not marca_reencauche:
                    st.error("⚠️ Debes ingresar la marca del reencauche")
                elif not referencia_reencauche:
                    st.error("⚠️ Debes ingresar la referencia del reencauche")
                elif precio_reencauche <= 0:
                    st.error("⚠️ Debes ingresar el precio del reencauche")
                elif len(llantas_seleccionadas) == 0:
                    st.error("⚠️ Debes seleccionar al menos una llanta")
                else:
                    df_todos = leer_hoja(SHEET_LLANTAS)
                    aprobadas = 0

                    for id_llanta in llantas_seleccionadas:
                        llanta_row = llantas_reencauche[llantas_reencauche['id_llanta'] == id_llanta].iloc[0]
                        # Usar vida_actual o vida según la columna disponible
                        vida_col = 'vida_actual' if 'vida_actual' in llanta_row.index else 'vida'
                        vida_actual = int(llanta_row[vida_col]) if pd.notna(llanta_row.get(vida_col)) else 1
                        vida_nueva = vida_actual + 1

                        # Guardar marca y referencia del reencauche
                        marca_ref_reencauche = f"{marca_reencauche} - {referencia_reencauche}"
                        if vida_nueva == 2:
                            df_todos.loc[df_todos['id_llanta'] == id_llanta, 'reencauche1'] = marca_ref_reencauche
                            df_todos.loc[df_todos['id_llanta'] == id_llanta, 'precio_vida2'] = precio_reencauche
                        elif vida_nueva == 3:
                            df_todos.loc[df_todos['id_llanta'] == id_llanta, 'reencauche2'] = marca_ref_reencauche
                            df_todos.loc[df_todos['id_llanta'] == id_llanta, 'precio_vida3'] = precio_reencauche
                        elif vida_nueva == 4:
                            df_todos.loc[df_todos['id_llanta'] == id_llanta, 'reencauche3'] = marca_ref_reencauche
                            df_todos.loc[df_todos['id_llanta'] == id_llanta, 'precio_vida4'] = precio_reencauche

                        df_todos.loc[df_todos['id_llanta'] == id_llanta, 'vida_actual'] = vida_nueva
                        df_todos.loc[df_todos['id_llanta'] == id_llanta, 'estado_reencauche'] = 'aprobado'
                        df_todos.loc[df_todos['id_llanta'] == id_llanta, 'disponibilidad'] = 'recambio'
                        df_todos.loc[df_todos['id_llanta'] == id_llanta, 'fecha_modificacion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        # Crear movimiento de aprobación de reencauche
                        crear_movimiento(
                            id_llanta=id_llanta,
                            tipo='aprobacion_reencauche',
                            vida=vida_nueva,
                            marca_reencauche=marca_reencauche,
                            ref_reencauche=referencia_reencauche,
                            precio_reencauche=precio_reencauche
                        )
                        aprobadas += 1

                    escribir_hoja(SHEET_LLANTAS, df_todos)
                    st.success(f"✅ {aprobadas} llantas aprobadas - Marca: {marca_reencauche}, Ref: {referencia_reencauche}, Precio: ${precio_reencauche:,.0f}")
                    st.rerun()
        else:
            st.info("✨ No hay llantas pendientes de aprobación de reencauche")
    
    with tab3:
        st.subheader("💰 Análisis de Costos por Kilómetro")
        
        # Seleccionar llanta para análisis
        id_llanta_analisis = st.selectbox(
            "Seleccionar Llanta",
            options=df_llantas['id_llanta'].values,
            format_func=lambda x: f"ID {x} - {df_llantas[df_llantas['id_llanta']==x]['marca_llanta'].values[0]}"
        )
        
        llanta_sel = df_llantas[df_llantas['id_llanta'] == id_llanta_analisis].iloc[0]
        vida_val = llanta_sel.get('vida_actual', llanta_sel.get('vida', 1))
        vida_actual = int(vida_val) if pd.notna(vida_val) else 1

        st.write(f"**Llanta ID {id_llanta_analisis}** - Vida Actual: {vida_actual}")
        
        # Botón para recalcular costos
        if st.button("🔄 Recalcular Costos/km", type="secondary"):
            if actualizar_costos_km_llanta(id_llanta_analisis):
                st.success("✅ Costos recalculados exitosamente")
                st.rerun()
            else:
                st.error("❌ Error al recalcular costos")
        
        st.divider()
        
        # Mostrar costos por vida (valores guardados en CSV)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Precio Vida 1", f"${llanta_sel.get('precio_vida1', 0):,.0f}")
            costo_v1 = llanta_sel.get('costo_km_vida1', None)
            if costo_v1 and not pd.isna(costo_v1):
                st.metric("Costo/km Vida 1", f"${float(costo_v1):,.2f}")
            else:
                st.info("Sin datos suficientes")
        
        with col2:
            st.metric("Precio Vida 2", f"${llanta_sel.get('precio_vida2', 0):,.0f}")
            costo_v2 = llanta_sel.get('costo_km_vida2', None)
            if costo_v2 and not pd.isna(costo_v2):
                st.metric("Costo/km Vida 2", f"${float(costo_v2):,.2f}")
            else:
                st.info("Sin datos suficientes")
        
        with col3:
            st.metric("Precio Vida 3", f"${llanta_sel.get('precio_vida3', 0):,.0f}")
            costo_v3 = llanta_sel.get('costo_km_vida3', None)
            if costo_v3 and not pd.isna(costo_v3):
                st.metric("Costo/km Vida 3", f"${float(costo_v3):,.2f}")
            else:
                st.info("Sin datos suficientes")
        
        with col4:
            st.metric("Precio Vida 4", f"${llanta_sel.get('precio_vida4', 0):,.0f}")
            costo_v4 = llanta_sel.get('costo_km_vida4', None)
            if costo_v4 and not pd.isna(costo_v4):
                st.metric("Costo/km Vida 4", f"${float(costo_v4):,.2f}")
            else:
                st.info("Sin datos suficientes")
        
        st.divider()
        
        # Costo acumulado
        costo_acumulado = calcular_costo_km_acumulado(id_llanta_analisis)
        if costo_acumulado:
            st.success(f"**Costo/km Acumulado Total:** ${costo_acumulado:,.2f}")
        else:
            st.info("No hay suficientes datos de servicios para calcular el costo/km acumulado")

# Continuará en la siguiente parte debido a límite de caracteres...

# ============= FUNCIÓN 1: GESTIÓN DE CLIENTES =============
def crear_cliente():
    """Función para crear clientes con frentes"""
    
    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("👤 Gestión de Clientes")

    if not verificar_permiso(1):  # Solo Administrador puede crear clientes
        return
    
    tab1, tab2 = st.tabs(["➕ Crear Cliente", "📋 Ver Clientes"])
    
    with tab1:
        st.subheader("Crear Nuevo Cliente")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nit = st.text_input("NIT (10 dígitos)", max_chars=10)
            nombre_cliente = st.text_input("Nombre del Cliente")
        
        with col2:
            num_frentes = st.number_input("Número de Frentes", min_value=0, max_value=20, value=1)
        
        frentes = []
        if num_frentes > 0:
            st.write("**Nombres de los Frentes:**")
            cols = st.columns(3)
            for i in range(num_frentes):
                with cols[i % 3]:
                    frente = st.text_input(f"Frente {i+1}", key=f"frente_{i}")
                    if frente:
                        frentes.append(frente)
        
        # Mostrar mensaje de éxito si viene de crear cliente
        if st.session_state.get('cliente_creado'):
            st.success("✅ ¡Cliente creado con éxito!")
            st.session_state['cliente_creado'] = False

        # Evitar doble click
        guardando = st.session_state.get('guardando_cliente', False)

        if st.button("💾 Guardar Cliente", type="primary", disabled=guardando):
            if len(nit) != 10 or not nit.isdigit():
                st.error("El NIT debe tener exactamente 10 dígitos numéricos")
            elif not nombre_cliente:
                st.error("Debes ingresar el nombre del cliente")
            elif num_frentes > 0 and len(frentes) != num_frentes:
                st.error("Debes ingresar todos los nombres de frentes")
            else:
                st.session_state['guardando_cliente'] = True
                # Leer datos frescos SIN caché para verificar duplicados
                df_clientes = leer_hoja_fresco(SHEET_CLIENTES)

                # Verificar si el NIT ya existe
                if existe_valor(df_clientes, 'nit', nit):
                    st.error("Este NIT ya está registrado")
                    st.session_state['guardando_cliente'] = False
                else:
                    nuevo_cliente = pd.DataFrame([{
                        'nit': nit,
                        'nombre_cliente': nombre_cliente,
                        'frentes': json.dumps(frentes) if frentes else json.dumps([]),
                        'fecha_creacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }])

                    df_clientes = pd.concat([df_clientes, nuevo_cliente], ignore_index=True)
                    escribir_hoja(SHEET_CLIENTES, df_clientes)
                    st.session_state['cliente_creado'] = True
                    st.session_state['guardando_cliente'] = False
                    st.rerun()
    
    with tab2:
        df_clientes = leer_hoja(SHEET_CLIENTES)
        
        if st.session_state.get('nivel') == 4:
            clientes_acceso = obtener_clientes_accesibles()
            df_clientes = filtrar_por_clientes(df_clientes, 'nit', clientes_acceso)
        
        if not df_clientes.empty:
            for idx, row in df_clientes.iterrows():
                with st.expander(f"🏢 {row.get('nombre_cliente', 'N/A')} - NIT: {row.get('nit', 'N/A')}"):
                    frentes = json.loads(row.get('frentes', '[]')) if row.get('frentes') else []
                    if frentes:
                        st.write(f"**Frentes:** {', '.join(frentes)}")
                    else:
                        st.write("**Sin frentes**")
                    st.write(f"**Fecha de Creación:** {row.get('fecha_creacion', 'N/A')}")
        else:
            st.info("No hay clientes registrados o no tienes acceso")

# ============= FUNCIÓN 2: GESTIÓN DE VEHÍCULOS =============
def crear_vehiculos():
    """Función para crear vehículos asociados a cliente y frente"""
    
    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("🚛 Gestión de Vehículos")
    
    if not verificar_permiso(2):
        return
    
    df_clientes = leer_hoja(SHEET_CLIENTES)
    
    clientes_acceso = obtener_clientes_accesibles()
    df_clientes = filtrar_por_clientes(df_clientes, 'nit', clientes_acceso)
    
    if df_clientes.empty:
        st.warning("⚠️ Primero debes crear un cliente o no tienes acceso")
        return
    
    tab1, tab2 = st.tabs(["➕ Registrar Vehículo", "📋 Ver Vehículos"])
    
    with tab1:
        st.subheader("Registrar Nuevo Vehículo")
        
        col1, col2, col3 = st.columns(3)

        with col1:
            # ID manual - sin restricciones
            id_vehiculo = st.number_input("ID Vehículo", min_value=1, value=1)

            cliente_seleccionado = st.selectbox(
                "Cliente",
                options=df_clientes['nit'].values if not df_clientes.empty and 'nit' in df_clientes.columns else [],
                format_func=lambda x: f"{df_clientes[df_clientes['nit']==x]['nombre_cliente'].values[0]} - {x}" if not df_clientes.empty else str(x)
            )
            marca = st.text_input("Marca (ej: Freightliner)")
        
        with col2:
            linea = st.text_input("Línea (ej: Cascadia)")
            tipologia = st.selectbox("Tipología", ["Camión", "Tractomula", "Volqueta", "Turbo", "Sencillo", "Otro"])
            placa_vehiculo = st.text_input("Placa del Vehículo").upper()
        
        with col3:
            frentes_cliente = json.loads(df_clientes[df_clientes['nit']==cliente_seleccionado]['frentes'].values[0])
            if frentes_cliente:
                frente = st.selectbox("Frente", options=frentes_cliente)
            else:
                frente = st.text_input("Frente (sin frentes definidos)", value="General")
            
            estado = st.selectbox("Estado", ["no_asignado", "activo", "fuera_de_servicio"])
            kilometraje_inicial = st.number_input("Kilometraje Inicial", min_value=0, value=0)
        
        calculo_kms = st.selectbox("Cálculo de Kilómetros", ["odometro", "promedio", "tabla"])
        
        if st.button("💾 Registrar Vehículo", type="primary"):
            if not placa_vehiculo or not marca or not linea:
                st.error("Debes completar todos los campos obligatorios")
            else:
                # Leer datos frescos SIN caché para verificar duplicados
                df_vehiculos = leer_hoja_fresco(SHEET_VEHICULOS)

                if existe_valor(df_vehiculos, 'placa_vehiculo', placa_vehiculo):
                    st.error("Esta placa ya está registrada")
                elif existe_valor(df_vehiculos, 'id_vehiculo', id_vehiculo):
                    st.error("Este ID de vehículo ya existe")
                else:
                    nuevo_vehiculo = pd.DataFrame([{
                        'id_vehiculo': id_vehiculo,  # Aquí usa la variable id_vehiculo del input
                        'nit_cliente': cliente_seleccionado,
                        'marca': marca,
                        'linea': linea,
                        'tipologia': tipologia,
                        'placa_vehiculo': placa_vehiculo,
                        'frente': frente,
                        'estado': estado,
                        'kilometraje_inicial': kilometraje_inicial,
                        'calculo_kms': calculo_kms,
                        'fecha_creacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }])
                    
                    df_vehiculos = pd.concat([df_vehiculos, nuevo_vehiculo], ignore_index=True)
                    escribir_hoja(SHEET_VEHICULOS, df_vehiculos)
                    st.success("✅ Dato creado con éxito")
                    st.balloons()
                    st.rerun()                
      
    with tab2:
        df_vehiculos = leer_hoja(SHEET_VEHICULOS)
        
        df_vehiculos = filtrar_por_clientes(df_vehiculos, 'nit_cliente', clientes_acceso)
        
        if not df_vehiculos.empty:
            df_display = df_vehiculos.merge(df_clientes[['nit', 'nombre_cliente']], left_on='nit_cliente', right_on='nit')
            columnas_mostrar = ['id_vehiculo', 'nombre_cliente', 'marca', 'linea', 'placa_vehiculo', 
                               'tipologia', 'frente', 'estado', 'kilometraje_inicial', 'calculo_kms']
            st.dataframe(df_display[[col for col in columnas_mostrar if col in df_display.columns]], use_container_width=True)
        else:
            st.info("No hay vehículos registrados o no tienes acceso")

# ============= FUNCIÓN 3: GESTIÓN DE LLANTAS =============
def crear_llantas():
    """Función para crear llantas y asociarlas a clientes"""
    
    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("⚙️ Gestión de Llantas")
    
    if not verificar_permiso(3):
        return
    
    df_clientes = leer_hoja(SHEET_CLIENTES)
    df_llantas = leer_hoja(SHEET_LLANTAS)
    
    clientes_acceso = obtener_clientes_accesibles()
    df_clientes = filtrar_por_clientes(df_clientes, 'nit', clientes_acceso)
    
    if df_clientes.empty:
        st.warning("⚠️ Primero debes crear un cliente o no tienes acceso")
        return
    
    tab1, tab2 = st.tabs(["➕ Registrar Llanta", "📋 Ver Llantas"])
    
    with tab1:
        st.subheader("Registrar Nueva Llanta")
        
        col1, col2 = st.columns(2)
        
        with col1:
            def format_cliente(x):
                try:
                    nombre = df_clientes[df_clientes['nit']==x]['nombre_cliente'].values
                    return nombre[0] if len(nombre) > 0 else f"NIT: {x}"
                except:
                    return f"NIT: {x}"
            
            cliente_seleccionado = st.selectbox(
                "Cliente",
                options=df_clientes['nit'].values,
                format_func=format_cliente,
                key="llanta_cliente"
            )
            marca_llanta = st.text_input("Marca de Llanta")
            referencia = st.text_input("Diseño (ej: XZA2)")

        with col2:
            dimension = st.text_input("Dimensión (ej: 295/80R22.5)")
            max_id = df_llantas['id_llanta'].max() if not df_llantas.empty and 'id_llanta' in df_llantas.columns else 0
            id_llanta = st.number_input("ID Llanta", min_value=1, value=int(max_id)+1 if pd.notna(max_id) else 1)
            precio_vida1 = st.number_input("Precio Vida 1 (Nueva)", min_value=0.0, value=1500000.0, step=10000.0)

        if st.button("💾 Registrar Llanta", type="primary"):
            if not dimension or not referencia or not marca_llanta:
                st.error("Debes completar todos los campos")
            else:
                # Leer datos frescos SIN caché para verificar duplicados
                df_llantas = leer_hoja_fresco(SHEET_LLANTAS)

                if existe_valor(df_llantas, 'id_llanta', id_llanta):
                    st.error("Este ID de llanta ya existe")
                else:
                    nueva_llanta = pd.DataFrame([{
                        'id_llanta': id_llanta,
                        'nit_cliente': str(cliente_seleccionado),
                        'marca_llanta': marca_llanta,
                        'referencia': referencia,
                        'dimension': dimension,
                        'vida_actual': 1,
                        'disponibilidad': 'llanta_nueva',
                        'placa_actual': '',
                        'posicion_actual': '',
                        'estado_reencauche': '',
                        'precio_vida1': precio_vida1,
                        'reencauche1': '',
                        'precio_vida2': 0,
                        'reencauche2': '',
                        'precio_vida3': 0,
                        'reencauche3': '',
                        'precio_vida4': 0,
                        'costo_km_vida1': 0,
                        'costo_km_vida2': 0,
                        'costo_km_vida3': 0,
                        'costo_km_vida4': 0,
                        'fecha_creacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'fecha_modificacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }])

                    df_llantas = pd.concat([df_llantas, nueva_llanta], ignore_index=True)
                    escribir_hoja(SHEET_LLANTAS, df_llantas)
                    st.success("✅ Dato creado con éxito")
                    st.balloons()
                    st.rerun()
    
    with tab2:
        df_llantas = leer_hoja(SHEET_LLANTAS)
        
        df_llantas = filtrar_por_clientes(df_llantas, 'nit_cliente', clientes_acceso)
        
        if not df_llantas.empty:
            df_display = df_llantas.merge(df_clientes[['nit', 'nombre_cliente']], left_on='nit_cliente', right_on='nit', how='left')
            df_display['nombre_cliente'].fillna('Cliente Inválido', inplace=True)
            columnas_mostrar = ['id_llanta', 'nombre_cliente', 'marca_llanta', 'referencia', 'dimension', 
                               'disponibilidad', 'placa_vehiculo', 'vida', 'precio_vida1', 'precio_vida2', 
                               'precio_vida3', 'precio_vida4', 'costo_km_vida1', 'costo_km_vida2',
                               'costo_km_vida3', 'costo_km_vida4']
            st.dataframe(df_display[[col for col in columnas_mostrar if col in df_display.columns]], use_container_width=True)
        else:
            st.info("No hay llantas registradas o no tienes acceso")

# Debido al límite de caracteres, las funciones restantes (montaje, servicios, desmontaje, reportes, gestión de usuarios y main) 
# permanecen igual que en el código original con ajustes menores para compatibilidad.
# Se incluyen las firmas principales:

def montaje_llantas():
    """Función para montar llantas en vehículos"""

    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("🔧 Montaje de Llantas")

    if not verificar_permiso(3):
        return

    df_llantas = leer_hoja(SHEET_LLANTAS)
    df_vehiculos = leer_hoja(SHEET_VEHICULOS)

    clientes_acceso = obtener_clientes_accesibles()
    df_llantas = filtrar_por_clientes(df_llantas, 'nit_cliente', clientes_acceso)
    df_vehiculos = filtrar_por_clientes(df_vehiculos, 'nit_cliente', clientes_acceso)

    if df_vehiculos.empty:
        st.warning("⚠️ No hay vehículos registrados para tus clientes")
        return

    # Verificar que el DataFrame tiene las columnas necesarias
    if df_llantas.empty or 'disponibilidad' not in df_llantas.columns or 'estado_reencauche' not in df_llantas.columns:
        st.warning("⚠️ No hay llantas registradas o no se pueden cargar los datos")
        return

    col1, col2 = st.columns(2)

    # PRIMERO: Seleccionar vehículo
    with col1:
        placa_vehiculo = st.selectbox(
            "1️⃣ Seleccionar Vehículo",
            options=df_vehiculos['placa_vehiculo'].values,
            format_func=lambda x: f"{x} - {df_vehiculos[df_vehiculos['placa_vehiculo']==x]['marca'].values[0] if 'marca' in df_vehiculos.columns else ''}"
        )

    # Obtener el nit_cliente y kilometraje del vehículo seleccionado
    vehiculo_seleccionado = df_vehiculos[df_vehiculos['placa_vehiculo'] == placa_vehiculo]
    nit_cliente_vehiculo = vehiculo_seleccionado['nit_cliente'].values[0] if not vehiculo_seleccionado.empty else None

    # Filtrar llantas disponibles SOLO del mismo cliente que el vehículo
    llantas_cliente = df_llantas[df_llantas['nit_cliente'] == nit_cliente_vehiculo]
    llantas_disponibles = llantas_cliente[
        (llantas_cliente['disponibilidad'].isin(['llanta_nueva', 'recambio'])) |
        ((llantas_cliente['disponibilidad'] == 'reencauche') & (llantas_cliente['estado_reencauche'] == 'aprobado'))
    ]

    # SEGUNDO: Seleccionar llanta (filtrada por cliente del vehículo)
    with col2:
        if llantas_disponibles.empty:
            st.warning(f"⚠️ No hay llantas disponibles para este cliente")
            id_llanta = None
        else:
            id_llanta = st.selectbox(
                "2️⃣ Seleccionar Llanta",
                options=llantas_disponibles['id_llanta'].values,
                format_func=lambda x: f"ID {x} - {llantas_disponibles[llantas_disponibles['id_llanta']==x]['marca_llanta'].values[0]} {llantas_disponibles[llantas_disponibles['id_llanta']==x]['dimension'].values[0]} (Vida {int(llantas_disponibles[llantas_disponibles['id_llanta']==x]['vida_actual'].values[0]) if 'vida_actual' in llantas_disponibles.columns and pd.notna(llantas_disponibles[llantas_disponibles['id_llanta']==x]['vida_actual'].values[0]) else 1})"
            )

    col3, col4 = st.columns(2)
    with col3:
        posicion = st.text_input("3️⃣ Posición (ej: DI, DD, TI1)")
    with col4:
        kilometraje = st.number_input("4️⃣ Kilometraje del Vehículo", min_value=0, value=0)

    if st.button("🔧 Montar Llanta", type="primary"):
        if id_llanta is None:
            st.error("No hay llantas disponibles para montar")
        elif not posicion:
            st.error("Debes especificar la posición")
        elif kilometraje <= 0:
            st.error("Debes ingresar el kilometraje actual del vehículo")
        else:
            df_llantas = leer_hoja(SHEET_LLANTAS)

            # Obtener vida actual de la llanta
            vida_actual = df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'vida_actual'].values[0] if 'vida_actual' in df_llantas.columns else 1
            vida_actual = int(vida_actual) if pd.notna(vida_actual) else 1

            # Actualizar datos en hoja llantas (nuevos nombres de columnas)
            df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'disponibilidad'] = 'al_piso'
            df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'placa_actual'] = placa_vehiculo
            df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'posicion_actual'] = posicion
            df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'estado_reencauche'] = ''
            df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'fecha_modificacion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            escribir_hoja(SHEET_LLANTAS, df_llantas)

            # Crear movimiento de montaje
            crear_movimiento(
                id_llanta=id_llanta,
                tipo='montaje',
                vida=vida_actual,
                placa_vehiculo=placa_vehiculo,
                posicion=posicion,
                kilometraje=kilometraje
            )

            st.success(f"✅ Llanta ID {id_llanta} montada en vehículo {placa_vehiculo} - Posición: {posicion} - Km: {kilometraje:,}")
            st.rerun()

    st.divider()
    st.subheader("📊 Llantas Montadas")
    llantas_montadas = df_llantas[df_llantas['disponibilidad'] == 'al_piso']
    if not llantas_montadas.empty:
        columnas_mostrar = [col for col in ['id_llanta', 'marca_llanta', 'dimension', 'placa_actual', 'posicion_actual', 'vida_actual'] if col in llantas_montadas.columns]
        st.dataframe(llantas_montadas[columnas_mostrar], use_container_width=True)

def registrar_servicios():
    """Función para registrar servicios de mantenimiento"""

    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("🛠️ Registro de Servicios")

    if not verificar_permiso(3):
        return

    df_llantas = leer_hoja(SHEET_LLANTAS)
    df_vehiculos = leer_hoja(SHEET_VEHICULOS)

    clientes_acceso = obtener_clientes_accesibles()
    df_llantas = filtrar_por_clientes(df_llantas, 'nit_cliente', clientes_acceso)

    # Verificar que el DataFrame tiene la columna necesaria
    if df_llantas.empty or 'disponibilidad' not in df_llantas.columns:
        st.warning("⚠️ No hay llantas registradas o no se pueden cargar los datos")
        return

    llantas_en_piso = df_llantas[df_llantas['disponibilidad'] == 'al_piso']

    if llantas_en_piso.empty:
        st.warning("⚠️ No hay llantas montadas para registrar servicios")
        return

    st.subheader("Formulario de Servicio")

    col1, col2, col3 = st.columns(3)

    # Determinar nombre de columna de placa (compatibilidad)
    placa_col = 'placa_actual' if 'placa_actual' in llantas_en_piso.columns else 'placa_vehiculo'
    pos_col = 'posicion_actual' if 'posicion_actual' in llantas_en_piso.columns else 'pos_final'

    with col1:
        id_llanta = st.selectbox(
            "ID Llanta",
            options=llantas_en_piso['id_llanta'].values,
            format_func=lambda x: f"ID {x} - Placa: {llantas_en_piso[llantas_en_piso['id_llanta']==x][placa_col].values[0] if placa_col in llantas_en_piso.columns else 'N/A'}"
        )

        fecha_servicio = st.date_input("Fecha del Servicio", datetime.now())
        kilometraje = st.number_input("Kilometraje", min_value=0, value=0)

    # Mostrar info de la llanta seleccionada
    llanta_sel = llantas_en_piso[llantas_en_piso['id_llanta'] == id_llanta].iloc[0]
    posicion_actual = llanta_sel.get('posicion_actual', llanta_sel.get('pos_final', ''))
    vida_actual = int(llanta_sel.get('vida_actual', llanta_sel.get('vida', 1))) if pd.notna(llanta_sel.get('vida_actual', llanta_sel.get('vida', 1))) else 1

    st.info(f"📍 Posición actual: **{posicion_actual}** | 🔄 Vida: **{vida_actual}**")

    with col2:
        st.write("**Profundidades (mm)**")
        profundidad_1 = st.number_input("Profundidad 1", min_value=0.0, max_value=30.0, value=10.0, step=0.5)
        profundidad_2 = st.number_input("Profundidad 2", min_value=0.0, max_value=30.0, value=10.0, step=0.5)
        profundidad_3 = st.number_input("Profundidad 3", min_value=0.0, max_value=30.0, value=10.0, step=0.5)

    with col3:
        st.write("**Servicios Realizados**")
        rotacion = st.checkbox("Rotación")
        if rotacion:
            nueva_posicion = st.text_input("Nueva Posición")
        else:
            nueva_posicion = ""

        balanceo = st.checkbox("Balanceo")
        alineacion = st.checkbox("Alineación")
        regrabacion = st.checkbox("Regrabación")
        torqueo = st.checkbox("Torqueo")

    if st.button("💾 Registrar Servicio", type="primary"):
        if rotacion and not nueva_posicion:
            st.error("Si hay rotación, debes especificar la nueva posición")
        else:
            df_servicios = leer_hoja(SHEET_SERVICIOS)
            df_llantas = leer_hoja(SHEET_LLANTAS)
            df_vehiculos = leer_hoja(SHEET_VEHICULOS)

            llanta_data = df_llantas[df_llantas['id_llanta'] == id_llanta].iloc[0]
            # Compatibilidad con nombres de columnas antiguos y nuevos
            placa = llanta_data.get('placa_actual', llanta_data.get('placa_vehiculo', ''))
            nit_cliente = llanta_data['nit_cliente']
            posicion = llanta_data.get('posicion_actual', llanta_data.get('pos_final', ''))
            vida = llanta_data.get('vida_actual', llanta_data.get('vida', 1))
            disponibilidad = llanta_data.get('disponibilidad', '')

            vehiculo_data = df_vehiculos[df_vehiculos['placa_vehiculo'] == placa].iloc[0]
            frente = vehiculo_data['frente']
            tipologia = vehiculo_data.get('tipologia', '')

            id_servicio = generar_id_servicio(nit_cliente, frente)

            # Posición final después del servicio
            posicion_nueva = nueva_posicion if rotacion and nueva_posicion else posicion

            # Si hay rotación, actualizar posicion_actual en llantas
            if rotacion and nueva_posicion:
                df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'posicion_actual'] = nueva_posicion
                escribir_hoja(SHEET_LLANTAS, df_llantas)

            nuevo_servicio = pd.DataFrame([{
                'id_servicio': id_servicio,
                'fecha': fecha_servicio.strftime("%d/%m/%Y"),
                'id_llanta': id_llanta,
                'placa_vehiculo': placa,
                'posicion': posicion,  # Posición al momento del servicio
                'vida': vida,
                'tipologia': tipologia,
                'disponibilidad': disponibilidad,
                'kilometraje': kilometraje,
                'rotacion': 'Sí' if rotacion else 'No',
                'posicion_nueva': posicion_nueva if rotacion else '',  # Nueva posición si hubo rotación
                'profundidad_1': profundidad_1,
                'profundidad_2': profundidad_2,
                'profundidad_3': profundidad_3,
                'balanceo': 'Sí' if balanceo else 'No',
                'alineacion': 'Sí' if alineacion else 'No',
                'regrabacion': 'Sí' if regrabacion else 'No',
                'torqueo': 'Sí' if torqueo else 'No',
                'comentario_fvu': '',
                'usuario_registro': st.session_state['usuario'],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            
            df_servicios = pd.concat([df_servicios, nuevo_servicio], ignore_index=True)
            escribir_hoja(SHEET_SERVICIOS, df_servicios)
            
            # ACTUALIZAR COSTOS/KM AUTOMÁTICAMENTE
            actualizar_costos_km_llanta(id_llanta)
            
            st.success(f"✅ Servicio {id_servicio} registrado exitosamente para llanta ID {id_llanta}")
            st.info("💡 Los costos/km se han actualizado automáticamente")
            
            st.session_state['servicio_completado'] = True
            st.session_state['id_llanta_servicio'] = id_llanta
            st.rerun()
    
    if st.session_state.get('servicio_completado', False):
        st.divider()
        st.subheader("¿Qué deseas hacer ahora?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("➕ Registrar Otro Servicio", use_container_width=True):
                st.session_state['servicio_completado'] = False
                st.rerun()
        
        with col2:
            if st.button("🔽 Realizar Desmontaje", use_container_width=True, type="primary"):
                st.session_state['servicio_completado'] = False
                st.session_state['ir_a_desmontaje'] = True
                st.rerun()
    
    st.divider()
    st.subheader("📋 Historial de Servicios")
    df_servicios = leer_hoja(SHEET_SERVICIOS)
    if not df_servicios.empty:
        servicios_recientes = df_servicios.sort_values('timestamp', ascending=False).head(10)
        columnas_mostrar = [col for col in ['id_servicio', 'fecha', 'id_llanta', 'placa_vehiculo', 'pos_inicial', 'vida', 'tipologia', 'kilometraje', 'profundidad_1', 'profundidad_2', 'profundidad_3'] if col in servicios_recientes.columns]
        st.dataframe(servicios_recientes[columnas_mostrar], use_container_width=True)

def desmontaje_llantas():
    """Función para desmontar llantas y cambiar disponibilidad"""

    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("🔽 Desmontaje de Llantas")

    if not verificar_permiso(2):
        return

    df_llantas = leer_hoja(SHEET_LLANTAS)

    clientes_acceso = obtener_clientes_accesibles()
    df_llantas = filtrar_por_clientes(df_llantas, 'nit_cliente', clientes_acceso)

    # Verificar que el DataFrame tiene la columna necesaria
    if df_llantas.empty or 'disponibilidad' not in df_llantas.columns:
        st.warning("⚠️ No hay llantas registradas o no se pueden cargar los datos")
        return

    llantas_montadas = df_llantas[df_llantas['disponibilidad'] == 'al_piso']

    if llantas_montadas.empty:
        st.warning("⚠️ No hay llantas montadas para desmontar")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Usar placa_actual en lugar de placa_vehiculo
        placa_col = 'placa_actual' if 'placa_actual' in llantas_montadas.columns else 'placa_vehiculo'
        id_llanta = st.selectbox(
            "Seleccionar Llanta a Desmontar",
            options=llantas_montadas['id_llanta'].values,
            format_func=lambda x: f"ID {x} - Placa: {llantas_montadas[llantas_montadas['id_llanta']==x][placa_col].values[0] if placa_col in llantas_montadas.columns else 'N/A'}"
        )

    with col2:
        nueva_disponibilidad = st.selectbox(
            "Nueva Disponibilidad",
            options=['recambio', 'reencauche', 'FVU']
        )

    # Obtener datos de la llanta seleccionada
    llanta_sel = llantas_montadas[llantas_montadas['id_llanta'] == id_llanta].iloc[0]
    posicion_actual = llanta_sel.get('posicion_actual', llanta_sel.get('pos_final', ''))
    placa_actual = llanta_sel.get('placa_actual', llanta_sel.get('placa_vehiculo', ''))
    vida_actual = int(llanta_sel.get('vida_actual', llanta_sel.get('vida', 1))) if pd.notna(llanta_sel.get('vida_actual', llanta_sel.get('vida', 1))) else 1

    st.info(f"📍 Posición actual: **{posicion_actual}** | 🚛 Placa: **{placa_actual}** | 🔄 Vida: **{vida_actual}**")

    col3, col4 = st.columns(2)
    with col3:
        kilometraje = st.number_input("Kilometraje actual del vehículo", min_value=0, value=0)

    razon_fvu = None
    if nueva_disponibilidad == 'FVU':
        with col4:
            razon_fvu = st.text_input("Razón de FVU (Fuera de Uso)")

    if st.button("🔽 Desmontar Llanta", type="primary"):
        if kilometraje <= 0:
            st.error("Debes ingresar el kilometraje actual del vehículo")
        elif nueva_disponibilidad == 'FVU' and not razon_fvu:
            st.error("Debes especificar la razón del desecho")
        else:
            df_llantas = leer_hoja(SHEET_LLANTAS)

            # Limpiar placa y posición actuales
            df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'placa_actual'] = ''
            df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'posicion_actual'] = ''
            df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'fecha_modificacion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            observaciones = ''
            if nueva_disponibilidad == 'reencauche':
                df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'disponibilidad'] = 'reencauche'
                df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'estado_reencauche'] = 'condicionada_planta'
                mensaje = f"✅ Llanta ID {id_llanta} desmontada. Estado: REENCAUCHE - Condicionada en planta"
            elif nueva_disponibilidad == 'FVU':
                df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'disponibilidad'] = 'FVU'
                df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'estado_reencauche'] = ''
                observaciones = f"FVU: {razon_fvu}"
                mensaje = f"✅ Llanta ID {id_llanta} desmontada. Estado: FVU (Fuera de Uso)"
            else:
                df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'disponibilidad'] = 'recambio'
                df_llantas.loc[df_llantas['id_llanta'] == id_llanta, 'estado_reencauche'] = ''
                mensaje = f"✅ Llanta ID {id_llanta} desmontada. Estado: RECAMBIO (Disponible)"

            escribir_hoja(SHEET_LLANTAS, df_llantas)

            # Crear movimiento de desmontaje
            crear_movimiento(
                id_llanta=id_llanta,
                tipo='desmontaje',
                vida=vida_actual,
                placa_vehiculo=placa_actual,
                posicion=posicion_actual,
                kilometraje=kilometraje,
                nueva_disponibilidad=nueva_disponibilidad,
                observaciones=observaciones
            )

            st.success(mensaje)
            st.rerun()

    st.divider()
    st.subheader("📋 Llantas pendientes de aprobación de reencauche")
    st.caption("Para aprobar reencauches con todos los datos, ve a **Estado de Llantas → Aprobar Reencauches**")

    llantas_reencauche = df_llantas[
        (df_llantas['disponibilidad'] == 'reencauche') &
        (df_llantas['estado_reencauche'] == 'condicionada_planta')
    ]

    if not llantas_reencauche.empty:
        columnas_mostrar = [col for col in ['id_llanta', 'marca_llanta', 'dimension', 'vida_actual'] if col in llantas_reencauche.columns]
        st.dataframe(llantas_reencauche[columnas_mostrar], use_container_width=True)
        st.info(f"📋 {len(llantas_reencauche)} llantas esperando aprobación de planta")
    else:
        st.info("✨ No hay llantas pendientes de aprobación")

def reportes():
    """Función para generar reportes y análisis"""
    
    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("📊 Reportes y Análisis")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Desgaste de Llantas", "🛠️ Servicios por Llanta", "🚛 Servicios por Vehículo", "📊 Estado de Flota", "📥 Exportar Datos"])
    
    with tab1:
        st.subheader("Análisis de Desgaste")
        
        df_servicios = leer_hoja(SHEET_SERVICIOS)
        
        if df_servicios.empty:
            st.info("No hay datos de servicios para analizar")
        else:
            col1, col2 = st.columns(2)
            with col1:
                filtro_llantas = st.multiselect(
                    "Filtrar Llantas",
                    options=['Todas'] + list(df_servicios['id_llanta'].unique()),
                    default=['Todas']
                )
            
            if 'Todas' in filtro_llantas:
                id_llanta_filtro = st.selectbox(
                    "Seleccionar Llanta para Análisis",
                    options=df_servicios['id_llanta'].unique()
                )
            else:
                id_llanta_filtro = st.selectbox(
                    "Seleccionar Llanta para Análisis",
                    options=filtro_llantas
                )
            
            servicios_llanta = df_servicios[df_servicios['id_llanta'] == id_llanta_filtro].sort_values('timestamp')
            
            if not servicios_llanta.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Total de Servicios", len(servicios_llanta))
                    st.metric("Profundidad Promedio Actual", 
                             f"{servicios_llanta.iloc[-1][['profundidad_1', 'profundidad_2', 'profundidad_3']].mean():.2f} mm")
                
                with col2:
                    if len(servicios_llanta) > 1:
                        primera_prof = servicios_llanta.iloc[0][['profundidad_1', 'profundidad_2', 'profundidad_3']].mean()
                        ultima_prof = servicios_llanta.iloc[-1][['profundidad_1', 'profundidad_2', 'profundidad_3']].mean()
                        desgaste = primera_prof - ultima_prof
                        st.metric("Desgaste Total", f"{desgaste:.2f} mm")
                        
                        fecha_inicio = pd.to_datetime(servicios_llanta.iloc[0]['timestamp'])
                        fecha_fin = pd.to_datetime(servicios_llanta.iloc[-1]['timestamp'])
                        dias_uso = (fecha_fin - fecha_inicio).days
                        
                        if dias_uso > 0:
                            st.metric("Desgaste Promedio Diario", f"{desgaste/dias_uso:.3f} mm/día")
                
                st.divider()
                st.write("**Historial de Profundidades**")
                columnas_reporte = [col for col in ['id_servicio', 'fecha', 'kilometraje', 'profundidad_1', 'profundidad_2', 'profundidad_3', 'pos_final', 'comentario_fvu'] if col in servicios_llanta.columns]
                st.dataframe(servicios_llanta[columnas_reporte], use_container_width=True)
    
    with tab2:
        st.subheader("Servicios por Llanta")
        
        df_servicios = leer_hoja(SHEET_SERVICIOS)
        
        if not df_servicios.empty:
            resumen = df_servicios.groupby('id_llanta').agg({
                'id_servicio': 'count',
                'rotacion': lambda x: (x == 'Sí').sum(),
                'balanceo': lambda x: (x == 'Sí').sum(),
                'alineacion': lambda x: (x == 'Sí').sum(),
                'regrabacion': lambda x: (x == 'Sí').sum(),
                'torqueo': lambda x: (x == 'Sí').sum()
            }).reset_index()
            
            resumen.columns = ['ID Llanta', 'Total Servicios', 'Rotaciones', 'Balanceos', 'Alineaciones', 'Regrabaciones', 'Torqueos']
            
            st.dataframe(resumen, use_container_width=True)
            
            st.divider()
            id_llanta_detalle = st.selectbox(
                "Ver Detalle de Llanta",
                options=df_servicios['id_llanta'].unique(),
                key="detalle_servicios"
            )
            
            servicios_detalle = df_servicios[df_servicios['id_llanta'] == id_llanta_detalle].sort_values('timestamp', ascending=False)
            st.dataframe(servicios_detalle, use_container_width=True)
        else:
            st.info("No hay servicios registrados")
    
    with tab3:
        st.subheader("Servicios por Vehículo")
        
        df_servicios = leer_hoja(SHEET_SERVICIOS)
        
        if not df_servicios.empty:
            col1, col2 = st.columns(2)
            with col1:
                filtro_vehiculos = st.multiselect(
                    "Filtrar Vehículos",
                    options=['Todos'] + list(df_servicios['placa_vehiculo'].unique()),
                    default=['Todos']
                )
            
            if 'Todos' in filtro_vehiculos:
                vehiculo_filtro = st.selectbox(
                    "Seleccionar Vehículo",
                    options=df_servicios['placa_vehiculo'].unique()
                )
            else:
                vehiculo_filtro = st.selectbox(
                    "Seleccionar Vehículo",
                    options=filtro_vehiculos
                )
            
            servicios_vehiculo = df_servicios[df_servicios['placa_vehiculo'] == vehiculo_filtro].sort_values('timestamp', ascending=False)
            
            if not servicios_vehiculo.empty:
                st.metric("Total de Servicios en este Vehículo", len(servicios_vehiculo))
                
                st.divider()
                st.write("**Historial de Servicios**")
                columnas_vehiculo = [col for col in ['id_servicio', 'fecha', 'id_llanta', 'pos_inicial', 'vida', 'tipologia', 'kilometraje', 'profundidad_1', 'profundidad_2', 'profundidad_3'] if col in servicios_vehiculo.columns]
                st.dataframe(servicios_vehiculo[columnas_vehiculo], use_container_width=True)
        else:
            st.info("No hay servicios registrados")
    
    with tab4:
        st.subheader("Estado General de la Flota")
        
        df_llantas = leer_hoja(SHEET_LLANTAS)
        df_vehiculos = leer_hoja(SHEET_VEHICULOS)
        
        clientes_acceso = obtener_clientes_accesibles()
        df_llantas = filtrar_por_clientes(df_llantas, 'nit_cliente', clientes_acceso)
        df_vehiculos = filtrar_por_clientes(df_vehiculos, 'nit_cliente', clientes_acceso)
        
        if not df_llantas.empty and 'disponibilidad' in df_llantas.columns:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Llantas", len(df_llantas))

            with col2:
                en_uso = len(df_llantas[df_llantas['disponibilidad'] == 'al_piso'])
                st.metric("Llantas en Uso", en_uso)
            
            with col3:
                disponibles = len(df_llantas[df_llantas['disponibilidad'].isin(['llanta_nueva', 'recambio'])])
                st.metric("Llantas Disponibles", disponibles)
            
            with col4:
                fvu = len(df_llantas[df_llantas['disponibilidad'] == 'FVU'])
                st.metric("Llantas FVU", fvu)
            
            st.divider()
            
            st.write("**Distribución por Estado**")
            estado_counts = df_llantas['disponibilidad'].value_counts()
            st.bar_chart(estado_counts)
            
            st.divider()
            
            st.write("**Llantas por Vehículo**")
            if not df_vehiculos.empty:
                vehiculos_con_llantas = df_llantas[df_llantas['placa_vehiculo'] != ''].groupby('placa_vehiculo').size().reset_index(name='cantidad_llantas')
                vehiculos_info = df_vehiculos.merge(vehiculos_con_llantas, on='placa_vehiculo', how='left')
                vehiculos_info['cantidad_llantas'].fillna(0, inplace=True)
                st.dataframe(vehiculos_info[['placa_vehiculo', 'marca', 'linea', 'tipologia', 'frente', 'estado', 'cantidad_llantas']], use_container_width=True)
        else:
            st.info("No hay llantas registradas o no tienes acceso")
    
    with tab5:
        st.subheader("Exportar Datos")

        st.write("Descarga los datos en formato CSV para análisis externo")

        # Obtener clientes accesibles para filtrar exportaciones
        clientes_acceso_export = obtener_clientes_accesibles()

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📥 Descargar Servicios", use_container_width=True):
                df_servicios = leer_hoja(SHEET_SERVICIOS)
                # Filtrar por cliente si no es admin
                if st.session_state.get('nivel') != 1:
                    df_llantas_temp = leer_hoja(SHEET_LLANTAS)
                    llantas_cliente = df_llantas_temp[df_llantas_temp['nit_cliente'].isin(clientes_acceso_export)]['id_llanta'].tolist()
                    df_servicios = df_servicios[df_servicios['id_llanta'].isin(llantas_cliente)]
                csv = df_servicios.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="💾 Servicios.csv",
                    data=csv,
                    file_name=f"servicios_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime='text/csv'
                )

            if st.button("📥 Descargar Llantas", use_container_width=True):
                df_llantas = leer_hoja(SHEET_LLANTAS)
                df_llantas = filtrar_por_clientes(df_llantas, 'nit_cliente', clientes_acceso_export)
                csv = df_llantas.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="💾 Llantas.csv",
                    data=csv,
                    file_name=f"llantas_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime='text/csv'
                )

        with col2:
            if st.button("📥 Descargar Vehículos", use_container_width=True):
                df_vehiculos = leer_hoja(SHEET_VEHICULOS)
                df_vehiculos = filtrar_por_clientes(df_vehiculos, 'nit_cliente', clientes_acceso_export)
                csv = df_vehiculos.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="💾 Vehiculos.csv",
                    data=csv,
                    file_name=f"vehiculos_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime='text/csv'
                )

            if st.button("📥 Descargar Clientes", use_container_width=True):
                df_clientes = leer_hoja(SHEET_CLIENTES)
                df_clientes = filtrar_por_clientes(df_clientes, 'nit', clientes_acceso_export)
                csv = df_clientes.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="💾 Clientes.csv",
                    data=csv,
                    file_name=f"clientes_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime='text/csv'
                )

        with col3:
            if st.button("📥 Descargar Movimientos", use_container_width=True):
                df_movimientos = leer_hoja(SHEET_MOVIMIENTOS)
                # Filtrar por cliente si no es admin
                if st.session_state.get('nivel') != 1:
                    df_llantas_temp = leer_hoja(SHEET_LLANTAS)
                    llantas_cliente = df_llantas_temp[df_llantas_temp['nit_cliente'].isin(clientes_acceso_export)]['id_llanta'].tolist()
                    df_movimientos = df_movimientos[df_movimientos['id_llanta'].isin(llantas_cliente)]
                csv = df_movimientos.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="💾 Movimientos.csv",
                    data=csv,
                    file_name=f"movimientos_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime='text/csv'
                )

# ============= FUNCIÓN: MI PERFIL =============
def mi_perfil():
    """Permite a cualquier usuario editar su propio perfil"""

    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("👤 Mi Perfil")

    usuario_actual = st.session_state.get('usuario', '')

    # Leer datos del usuario actual
    df_usuarios = leer_hoja(SHEET_USUARIOS)
    usuario_data = df_usuarios[df_usuarios['usuario'] == usuario_actual]

    if usuario_data.empty:
        st.error("Error al cargar datos del usuario")
        return

    usuario_data = usuario_data.iloc[0]

    st.subheader("Editar mis datos")

    col1, col2 = st.columns(2)

    with col1:
        nuevo_usuario = st.text_input("Nombre de Usuario", value=usuario_data.get('usuario', ''), key="mi_perfil_usuario")
        nuevo_nombre = st.text_input("Nombre Completo", value=usuario_data.get('nombre', ''), key="mi_perfil_nombre")

    with col2:
        nueva_password = st.text_input("Nueva Contraseña (dejar vacío para mantener)", type="password", key="mi_perfil_password")
        confirmar_password = st.text_input("Confirmar Contraseña", type="password", key="mi_perfil_confirmar")

    st.info(f"**Nivel de acceso:** {usuario_data.get('nivel', '')} - No modificable")

    if st.button("💾 Guardar Cambios", key="guardar_mi_perfil", type="primary"):
        if not nuevo_usuario:
            st.error("El nombre de usuario no puede estar vacío")
        elif not nuevo_nombre:
            st.error("El nombre completo no puede estar vacío")
        elif nueva_password and nueva_password != confirmar_password:
            st.error("Las contraseñas no coinciden")
        else:
            df_todos = leer_hoja(SHEET_USUARIOS)

            # Verificar que el nuevo nombre de usuario no exista (si cambió)
            if nuevo_usuario != usuario_actual:
                if existe_valor(df_todos, 'usuario', nuevo_usuario):
                    st.error("Este nombre de usuario ya existe")
                    st.stop()

            # Actualizar datos
            df_todos.loc[df_todos['usuario'] == usuario_actual, 'usuario'] = nuevo_usuario
            df_todos.loc[df_todos['usuario'] == nuevo_usuario, 'nombre'] = nuevo_nombre

            # Solo actualizar contraseña si se proporcionó una nueva
            if nueva_password:
                df_todos.loc[df_todos['usuario'] == nuevo_usuario, 'password'] = nueva_password

            escribir_hoja(SHEET_USUARIOS, df_todos)

            # Actualizar session_state con los nuevos datos
            st.session_state['usuario'] = nuevo_usuario
            st.session_state['nombre'] = nuevo_nombre

            st.success("✅ Perfil actualizado con éxito")
            st.rerun()

def gestion_usuarios():
    """Función para gestionar usuarios (solo nivel 1)"""
    
    st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/megallanta-logo.png", width=200)
    st.header("👥 Gestión de Usuarios")
    
    if not verificar_permiso(1):
        return
    
    tab1, tab2, tab3 = st.tabs(["➕ Crear Usuario", "📋 Ver Usuarios", "✏️ Editar/Eliminar"])

    with tab1:
        st.subheader("Crear Nuevo Usuario")

        col1, col2 = st.columns(2)

        with col1:
            nuevo_usuario = st.text_input("Nombre de Usuario", key="crear_nuevo_usuario")
            nuevo_nombre = st.text_input("Nombre Completo", key="crear_nombre_completo")

        with col2:
            nueva_password = st.text_input("Contraseña", type="password", key="crear_password")
            nuevo_nivel = st.selectbox("Nivel de Acceso",
                                      options=[1, 2, 3, 4],
                                      format_func=lambda x: f"Nivel {x} - {'Administrador' if x==1 else 'Supervisor' if x==2 else 'Operario' if x==3 else 'Admin Cliente'}",
                                      key="crear_nivel_acceso")

        clientes_seleccionados = ""
        if nuevo_nivel in [2, 3, 4]:
            nivel_nombre = 'Supervisor' if nuevo_nivel == 2 else 'Operario' if nuevo_nivel == 3 else 'Admin Cliente'
            st.write(f"**Asignar Clientes para {nivel_nombre}**")
            df_clientes = leer_hoja(SHEET_CLIENTES)
            if not df_clientes.empty:
                clientes_opciones = st.multiselect(
                    "Seleccionar Clientes",
                    options=df_clientes['nit'].values,
                    format_func=lambda x: f"{df_clientes[df_clientes['nit']==x]['nombre_cliente'].values[0]} - {x}",
                    key="crear_clientes_asignados"
                )
                clientes_seleccionados = ','.join([str(c) for c in clientes_opciones])

        if st.button("💾 Crear Usuario", type="primary"):
            if not nuevo_usuario or not nueva_password or not nuevo_nombre:
                st.error("Debes completar todos los campos")
            elif nuevo_nivel in [2, 3, 4] and not clientes_seleccionados:
                st.error(f"Debes asignar al menos un cliente para este nivel de usuario")
            else:
                # Leer datos frescos SIN caché para verificar duplicados
                df_usuarios = leer_hoja_fresco(SHEET_USUARIOS)

                if existe_valor(df_usuarios, 'usuario', nuevo_usuario):
                    st.error("Este nombre de usuario ya existe")
                else:
                    nuevo_user = pd.DataFrame([{
                        'usuario': nuevo_usuario,
                        'password': nueva_password,
                        'nivel': nuevo_nivel,
                        'nombre': nuevo_nombre,
                        'clientes_asignados': clientes_seleccionados
                    }])
                    
                    df_usuarios = pd.concat([df_usuarios, nuevo_user], ignore_index=True)
                    escribir_hoja(SHEET_USUARIOS, df_usuarios)
                    st.success("✅ Dato creado con éxito")
                    st.balloons()
                    st.rerun()
    
    with tab2:
        df_usuarios = leer_hoja(SHEET_USUARIOS)
        df_clientes = leer_hoja(SHEET_CLIENTES)
        
        for idx, row in df_usuarios.iterrows():
            with st.expander(f"👤 {row.get('nombre', 'N/A')} - Nivel {row.get('nivel', 'N/A')}"):
                st.write(f"**Usuario:** {row.get('usuario', 'N/A')}")
                nivel = row.get('nivel', 0)
                st.write(f"**Nivel:** {nivel} - {'Administrador' if nivel==1 else 'Supervisor' if nivel==2 else 'Operario' if nivel==3 else 'Admin Cliente'}")
                
                clientes_asignados = row.get('clientes_asignados', '')
                if nivel in [2, 3, 4] and clientes_asignados and pd.notna(clientes_asignados):
                    clientes_nits = str(clientes_asignados).split(',')
                    nombres_clientes = []
                    for nit in clientes_nits:
                        if nit and existe_valor(df_clientes, 'nit', nit):
                            cliente_row = df_clientes[df_clientes['nit'].astype(str) == str(nit)]
                            if not cliente_row.empty:
                                nombre = cliente_row['nombre_cliente'].values[0]
                                nombres_clientes.append(f"{nombre} ({nit})")
                    if nombres_clientes:
                        st.write(f"**Clientes Asignados:** {', '.join(nombres_clientes)}")
        
        st.info("""
        **Niveles de Usuario:**
        - **Nivel 1 (Administrador)**: Acceso total al sistema
        - **Nivel 2 (Supervisor)**: Vehículos, Llantas, Montaje, Servicios, Desmontaje, Reportes, Editar datos (solo clientes asignados)
        - **Nivel 3 (Operario)**: Llantas, Montaje, Servicios, Desmontaje, Reportes - Solo registrar, NO editar (solo clientes asignados)
        - **Nivel 4 (Admin Cliente)**: Vehículos, Llantas, Estado, Montaje, Servicios, Desmontaje, Reportes, Editar (solo clientes asignados, NO gestión de clientes)
        """)

    with tab3:
        st.subheader("Editar o Eliminar Usuario")

        df_usuarios = leer_hoja(SHEET_USUARIOS)
        df_clientes = leer_hoja(SHEET_CLIENTES)

        if not df_usuarios.empty:
            usuario_editar = st.selectbox(
                "Seleccionar Usuario",
                options=df_usuarios['usuario'].values,
                format_func=lambda x: f"{df_usuarios[df_usuarios['usuario']==x]['nombre'].values[0]} ({x}) - Nivel {df_usuarios[df_usuarios['usuario']==x]['nivel'].values[0]}",
                key="select_usuario_editar"
            )

            usuario_data = df_usuarios[df_usuarios['usuario'] == usuario_editar].iloc[0]

            # No permitir editar el propio usuario admin que está logueado
            if usuario_editar == st.session_state.get('usuario'):
                st.warning("⚠️ No puedes editar tu propio usuario mientras estás conectado")
            else:
                st.write("**Datos del Usuario:**")
                col1, col2 = st.columns(2)

                with col1:
                    edit_usuario = st.text_input("Nombre de Usuario", value=usuario_data.get('usuario', ''), key="edit_usuario_nombre")
                    edit_nombre = st.text_input("Nombre Completo", value=usuario_data.get('nombre', ''), key="edit_nombre_usuario")

                with col2:
                    edit_password = st.text_input("Nueva Contraseña (dejar vacío para mantener)", type="password", key="edit_password_usuario")
                    niveles = [1, 2, 3, 4]
                    nivel_actual = int(usuario_data.get('nivel', 3)) if pd.notna(usuario_data.get('nivel')) else 3
                    nivel_idx = niveles.index(nivel_actual) if nivel_actual in niveles else 2
                    edit_nivel = st.selectbox(
                        "Nivel de Acceso",
                        options=niveles,
                        index=nivel_idx,
                        format_func=lambda x: f"Nivel {x} - {'Administrador' if x==1 else 'Supervisor' if x==2 else 'Operario' if x==3 else 'Admin Cliente'}",
                        key="edit_nivel_usuario"
                    )

                # Asignar clientes si el nivel lo requiere
                edit_clientes = ""
                if edit_nivel in [2, 3, 4]:
                    nivel_nombre = 'Supervisor' if edit_nivel == 2 else 'Operario' if edit_nivel == 3 else 'Admin Cliente'
                    st.write(f"**Asignar Clientes para {nivel_nombre}**")
                    if not df_clientes.empty:
                        # Obtener clientes actuales asignados
                        clientes_actuales = []
                        clientes_asignados_str = usuario_data.get('clientes_asignados', '')
                        if clientes_asignados_str and pd.notna(clientes_asignados_str) and isinstance(clientes_asignados_str, str):
                            clientes_actuales = [c.strip() for c in clientes_asignados_str.split(',') if c.strip()]

                        clientes_opciones_edit = st.multiselect(
                            "Seleccionar Clientes",
                            options=df_clientes['nit'].values,
                            default=[c for c in clientes_actuales if c in df_clientes['nit'].values],
                            format_func=lambda x: f"{df_clientes[df_clientes['nit']==x]['nombre_cliente'].values[0]} - {x}",
                            key="edit_clientes_usuario"
                        )
                        edit_clientes = ','.join([str(c) for c in clientes_opciones_edit])

                col_btn1, col_btn2 = st.columns(2)

                with col_btn1:
                    if st.button("💾 Guardar Cambios", key="guardar_usuario", type="primary"):
                        if not edit_usuario:
                            st.error("El nombre de usuario no puede estar vacío")
                        elif not edit_nombre:
                            st.error("El nombre completo no puede estar vacío")
                        elif edit_nivel in [2, 3, 4] and not edit_clientes:
                            st.error("Debes asignar al menos un cliente para este nivel")
                        else:
                            df_todos = leer_hoja(SHEET_USUARIOS)

                            # Verificar que el nuevo nombre de usuario no exista (si cambió)
                            if edit_usuario != usuario_editar:
                                if existe_valor(df_todos, 'usuario', edit_usuario):
                                    st.error("Este nombre de usuario ya existe")
                                    st.stop()

                            # Actualizar todos los campos incluyendo el nombre de usuario
                            df_todos.loc[df_todos['usuario'] == usuario_editar, 'usuario'] = edit_usuario
                            df_todos.loc[df_todos['usuario'] == edit_usuario, 'nombre'] = edit_nombre
                            df_todos.loc[df_todos['usuario'] == edit_usuario, 'nivel'] = edit_nivel
                            df_todos.loc[df_todos['usuario'] == edit_usuario, 'clientes_asignados'] = edit_clientes

                            # Solo actualizar contraseña si se proporcionó una nueva
                            if edit_password:
                                df_todos.loc[df_todos['usuario'] == edit_usuario, 'password'] = edit_password

                            escribir_hoja(SHEET_USUARIOS, df_todos)
                            st.success("✅ Usuario actualizado con éxito")
                            st.rerun()

                with col_btn2:
                    if st.button("🗑️ Eliminar Usuario", key="eliminar_usuario"):
                        df_todos = leer_hoja(SHEET_USUARIOS)
                        df_todos = df_todos[df_todos['usuario'] != usuario_editar]
                        escribir_hoja(SHEET_USUARIOS, df_todos)
                        st.success("✅ Usuario eliminado con éxito")
                        st.rerun()
        else:
            st.info("No hay usuarios registrados")

def main():
    """Función principal del sistema"""
    
    inicializar_datos()
    
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if not st.session_state['logged_in']:
        login()
        return
    
    with st.sidebar:
        st.image("https://elchorroco.wordpress.com/wp-content/uploads/2025/10/logo-sill.jpg", use_container_width=True)
        
        st.markdown("""
            <div style="background-color: #272F59; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                <h2 style="color: white; text-align: center; margin: 0;">Sistema Integrado de Llantas</h2>
            </div>
        """, unsafe_allow_html=True)
        
        st.write(f"**Usuario:** {st.session_state['nombre']}")
        st.write(f"**Nivel:** {st.session_state['nivel']}")
        
        st.divider()
        
        st.subheader("¿Qué quieres hacer hoy?")

        nivel_usuario = st.session_state['nivel']

        # Menú base para todos los usuarios
        opciones_menu = {}

        # Nivel 1 (Admin): Acceso total
        if nivel_usuario == 1:
            opciones_menu = {
                "👤 Gestión de Clientes": "clientes",
                "🚛 Gestión de Vehículos": "vehiculos",
                "⚙️ Gestión de Llantas": "llantas",
                "🔍 Estado de Llantas": "estado_llantas",
                "🔧 Montaje de Llantas": "montaje",
                "🛠️ Registro de Servicios": "servicios",
                "🔽 Desmontaje de Llantas": "desmontaje",
                "📊 Reportes y Análisis": "reportes",
                "📤 Subir Datos CSV": "subir_csv",
                "✏️ Editar/Eliminar Datos": "editar_datos",
                "👥 Gestión de Usuarios": "usuarios",
                "🔑 Mi Perfil": "mi_perfil"
            }
        # Nivel 2 (Supervisor): Vehículos, Llantas, Montaje, Servicios, Desmontaje, Reportes, Editar
        elif nivel_usuario == 2:
            opciones_menu = {
                "🚛 Gestión de Vehículos": "vehiculos",
                "⚙️ Gestión de Llantas": "llantas",
                "🔍 Estado de Llantas": "estado_llantas",
                "🔧 Montaje de Llantas": "montaje",
                "🛠️ Registro de Servicios": "servicios",
                "🔽 Desmontaje de Llantas": "desmontaje",
                "📊 Reportes y Análisis": "reportes",
                "✏️ Editar/Eliminar Datos": "editar_datos",
                "🔑 Mi Perfil": "mi_perfil"
            }
        # Nivel 3 (Operario): Llantas, Montaje, Servicios, Desmontaje, Reportes (solo ver, no editar)
        elif nivel_usuario == 3:
            opciones_menu = {
                "⚙️ Gestión de Llantas": "llantas",
                "🔍 Estado de Llantas": "estado_llantas",
                "🔧 Montaje de Llantas": "montaje",
                "🛠️ Registro de Servicios": "servicios",
                "🔽 Desmontaje de Llantas": "desmontaje",
                "📊 Reportes y Análisis": "reportes",
                "🔑 Mi Perfil": "mi_perfil"
            }
        # Nivel 4 (Admin Cliente): Vehículos, Llantas, Estado, Montaje, Servicios, Desmontaje, Reportes, Editar (NO clientes)
        elif nivel_usuario == 4:
            opciones_menu = {
                "🚛 Gestión de Vehículos": "vehiculos",
                "⚙️ Gestión de Llantas": "llantas",
                "🔍 Estado de Llantas": "estado_llantas",
                "🔧 Montaje de Llantas": "montaje",
                "🛠️ Registro de Servicios": "servicios",
                "🔽 Desmontaje de Llantas": "desmontaje",
                "📊 Reportes y Análisis": "reportes",
                "✏️ Editar/Eliminar Datos": "editar_datos",
                "🔑 Mi Perfil": "mi_perfil"
            }

        opcion = st.radio("Menú Principal", list(opciones_menu.keys()), label_visibility="collapsed")
        
        st.divider()
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        
        st.divider()
        
        with st.expander("ℹ️ Información de Permisos"):
            if st.session_state['nivel'] == 1:
                st.success("✅ Acceso Total al Sistema")
            elif st.session_state['nivel'] == 2:
                st.info("✅ Vehículos, Llantas, Montaje, Servicios, Desmontaje, Reportes, Editar datos, Mi Perfil\n❌ Clientes, Subir CSV, Usuarios")
            elif st.session_state['nivel'] == 3:
                st.warning("✅ Llantas, Montaje, Servicios, Desmontaje, Reportes, Mi Perfil (solo registrar)\n❌ Vehículos, Clientes, Editar datos")
            elif st.session_state['nivel'] == 4:
                st.info("✅ Vehículos, Llantas, Estado, Montaje, Servicios, Desmontaje, Reportes, Editar, Mi Perfil (solo clientes asignados)\n❌ Gestión de Clientes, Subir CSV, Usuarios")
        
        st.divider()
        
        logo_url = "https://elchorro.com.co/wp-content/uploads/2025/04/ch-plano.png?w=106&h=106"
        col_logo, col_texto = st.columns([1, 3], vertical_alignment="center")
        with col_logo:
            st.image(logo_url, width=60)
        with col_texto:
            st.markdown("""
                <div style="font-size:10px; line-height:1.1;">
                    <span style="font-style:italic;">Este programa fue desarrollado por:</span><br>
                    <span style="font-weight:bold;">Daniel Cortázar Triana</span><br>
                    <span style="font-weight:bold;">El Chorro Producciones SAS</span>
                </div>
            """, unsafe_allow_html=True)
    
    if st.session_state.get('ir_a_desmontaje', False):
        st.session_state['ir_a_desmontaje'] = False
        opcion = "🔽 Desmontaje de Llantas"
    
    opcion_seleccionada = opciones_menu[opcion]
    
    if opcion_seleccionada == "clientes":
        crear_cliente()
    elif opcion_seleccionada == "vehiculos":
        crear_vehiculos()
    elif opcion_seleccionada == "llantas":
        crear_llantas()
    elif opcion_seleccionada == "estado_llantas":
        ver_llantas_disponibles()
    elif opcion_seleccionada == "montaje":
        montaje_llantas()
    elif opcion_seleccionada == "servicios":
        registrar_servicios()
    elif opcion_seleccionada == "desmontaje":
        desmontaje_llantas()
    elif opcion_seleccionada == "reportes":
        reportes()
    elif opcion_seleccionada == "subir_csv":
        subir_datos_csv()
    elif opcion_seleccionada == "editar_datos":
        eliminar_corregir_datos()
    elif opcion_seleccionada == "usuarios":
        gestion_usuarios()
    elif opcion_seleccionada == "mi_perfil":
        mi_perfil()

if __name__ == "__main__":
    main()
