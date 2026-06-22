# Dashboard de Puntualidad de Vuelos — TPI Hito 4 y 5

Dashboard interactivo construido con **Streamlit** para analizar la puntualidad de
7.646 vuelos domésticos comerciales (1 de enero de 2024), con conexión híbrida
a PostgreSQL (pgAdmin 4) y respaldo automático en CSV.

## 📁 Estructura del proyecto

```
.
├── app.py                          # Interfaz del dashboard (Hito 4)
├── data_loader.py                  # ETL, conexión a la base y Feature Engineering
├── requirements.txt                # Dependencias para Streamlit Community Cloud
├── data/
│   └── flight_data_2024_act_.csv   # Plan de contingencia (Opción B del apunte)
└── Informe_de_Gestion_Hito5.docx   # Informe de gestión y propuestas (Hito 5)
```

## 🗄️ Cómo cargar los datos a tu base en PostgreSQL (pgAdmin 4)

Si querés que el dashboard se conecte a una base real en lugar del CSV:

1. En pgAdmin 4, creá una base nueva llamada `tpi_vuelos` (click derecho en
   **Databases** → **Create** → **Database...**). Cuidado al escribir el
   nombre: no debe quedar ningún espacio antes o después.
2. Definí tu contraseña real como variable de entorno (nunca se escribe
   directamente en el código, por seguridad):
   ```powershell
   $env:DB_PASSWORD="tu_clave_real"
   ```
3. Corré el script **una sola vez** desde la terminal (con el entorno
   virtual activado y la variable de entorno ya definida en esa misma
   sesión de terminal):
   ```bash
   python cargar_datos_a_postgres.py
   ```
   Esto crea la tabla `vuelos` dentro de `tpi_vuelos` y carga los 7.646
   registros. Podés verificarlo en pgAdmin 4: `tpi_vuelos` → `Schemas` →
   `public` → `Tables` → `vuelos` → click derecho → **View/Edit Data** →
   **All Rows**.
4. A partir de ahí, definí la misma variable `DB_PASSWORD` antes de correr
   `app.py` (ver sección siguiente), y el dashboard se va a conectar
   automáticamente a Postgres en lugar de usar el CSV (vas a ver "Fuente
   de datos activa: PostgreSQL (pgAdmin 4)" en el dashboard).

## 🚀 Cómo correrlo en local

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. (Opcional) Si querés conectar tu base real de pgAdmin 4, definí las
   variables de entorno antes de correr la app, **en la misma terminal y
   sesión** donde vas a ejecutar `streamlit run app.py` (si no las
   definís, la app usa el CSV de respaldo directamente):
   ```powershell
   $env:DB_HOST="127.0.0.1"
   $env:DB_PORT="5000"
   $env:DB_NAME="tpi_vuelos"
   $env:DB_USER="postgres"
   $env:DB_PASSWORD="tu_clave_real"
   $env:DB_TABLE="vuelos"
   ```
   (En Mac/Linux, reemplazar `$env:VAR="valor"` por `export VAR=valor`.)

3. Ejecutar:
   ```bash
   streamlit run app.py
   ```

Si la conexión a Postgres falla por cualquier motivo (base apagada, tabla
inexistente, credenciales incorrectas o no definidas), la app **cae
automáticamente** al CSV de respaldo en `data/flight_data_2024_act_.csv`,
sin romperse. Esto se indica de forma transparente en la parte superior
del dashboard ("Fuente de datos activa: ...").

## ☁️ Cómo desplegarlo en Streamlit Community Cloud

Como tu base de PostgreSQL corre en tu máquina local (`127.0.0.1`), la app
desplegada en la nube **no podrá conectarse a ella** (la nube no tiene
acceso a tu compu). Esto es esperado y está resuelto: la app cae
automáticamente al CSV de respaldo, así que el dashboard online siempre va
a funcionar — solo va a decir "Fuente de datos activa: CSV de respaldo"
en vez de PostgreSQL.

**Pasos:**

1. Creá un repositorio **público** en GitHub (ej. `tpi-dashboard-vuelos`).
2. Subí estos archivos al repositorio (manteniendo la misma estructura de
   carpetas):
   - `app.py`
   - `data_loader.py`
   - `requirements.txt`
   - `data/flight_data_2024_act_.csv`
   - (Opcional) `README.md`, `Informe_de_Gestion_Hito5.docx`
   - **NO subas** `cargar_datos_a_postgres.py` ni nada con tu contraseña real.
3. Ingresá a [share.streamlit.io](https://share.streamlit.io) e iniciá
   sesión vinculando tu cuenta de GitHub.
4. Click en **"New app"** → seleccioná tu repositorio, la rama (`main`) y
   `app.py` como archivo principal.
5. Click en **"Deploy!"** y esperá unos minutos mientras instala las
   dependencias de `requirements.txt`.
6. Vas a obtener una URL pública (algo como
   `https://tpi-dashboard-vuelos.streamlit.app`) para compartir en la
   presentación del TPI.

## 🧭 Filtros disponibles

- **Aerolínea** (multiselección)
- **Estado de origen** (multiselección)
- **Franja horaria de salida** (Madrugada / Mañana / Tarde / Noche)
- Checkbox para ver solo vuelos con retraso significativo (>15 min)

> Nota: la consigna original pide filtrar "por comisión, estado o fecha"
> (lenguaje del dominio educativo). Como este dataset es de vuelos y todos
> los registros corresponden a un único día, se adaptaron los filtros a
> **aerolínea**, **estado** y **franja horaria**, que son las dimensiones
> con variación real en los datos.

## 📊 Feature Engineering aplicado (Hito 2, reutilizado en el dashboard)

- `franja_horaria`: clasificación de la hora programada de salida en 4 bloques.
- `retraso_significativo`: booleano, `arr_delay > 15` minutos (estándar de la industria aérea).
- `llego_a_tiempo`: booleano complementario.
- `causa_principal_demora`: causa con mayor peso en minutos entre las 5 categorías disponibles.
- `arr_delay_outlier`: detección de outliers por método IQR (rango intercuartílico).

## 📄 Informe de Gestión (Hito 5)

Ver `Informe_de_Gestion_Hito5.docx`. Contiene:
- Diagnóstico general con evidencia gráfica (4 gráficos).
- Hallazgo 1: brecha crítica de puntualidad entre aerolíneas.
- Hallazgo 2: efecto cascada de demoras a lo largo del día.
- Dos propuestas de mejora operativa, justificadas con los datos.