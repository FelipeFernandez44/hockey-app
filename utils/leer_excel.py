import pandas as pd

def buscar_fixture_equipo(ruta_excel, equipo, anio=None, genero="ambos", categoria="todas"):
    try:
        df = pd.read_excel(ruta_excel, sheet_name="Fixtures")
        df.columns = df.columns.str.lower().str.strip()

        if 'fecha' in df.columns:
            df.rename(columns={'fecha': 'fecha_torneo'}, inplace=True)

        columnas_requeridas = ['año', 'equipo a', 'equipo b', 'goles a', 'goles b', 'torneo', 'zona', 'ronda', 'fecha_torneo', 'categoría']
        if not all(col in df.columns for col in columnas_requeridas):
            raise ValueError("Faltan columnas necesarias en Fixtures.")

        equipo = equipo.strip().upper()

        if genero == "damas":
            df = df[~df['torneo'].str.upper().str.contains("CABALLEROS")]
        elif genero == "caballeros":
            df = df[df['torneo'].str.upper().str.contains("CABALLEROS")]

        if anio:
            df = df[df['año'] == int(anio)]

        if categoria.lower() != "todas":
            df = df[df['categoría'].str.upper() == categoria.upper()]

        df_filtrado = df[
            (df['equipo a'].str.upper() == equipo) |
            (df['equipo b'].str.upper() == equipo)
        ].copy()

        df_filtrado['rol'] = df_filtrado.apply(
            lambda row: 'Local' if row['equipo a'].upper() == equipo else 'Visitante',
            axis=1
        )
        df_filtrado['rival'] = df_filtrado.apply(
            lambda row: row['equipo b'] if row['equipo a'].upper() == equipo else row['equipo a'],
            axis=1
        )
        df_filtrado['resultado'] = df_filtrado.apply(
            lambda row: f"{row['goles a']} - {row['goles b']}" if row['equipo a'].upper() == equipo else f"{row['goles b']} - {row['goles a']}",
            axis=1
        )

        df_filtrado = df_filtrado.sort_values(by='fecha_torneo', na_position='last')

        columnas_salida = ['fecha_torneo', 'torneo', 'categoría', 'zona', 'ronda', 'rol', 'rival', 'resultado']
        return df_filtrado[columnas_salida].to_dict(orient='records')

    except Exception as e:
        print(f"❌ Error Fixtures: {e}")
        return []

def buscar_posiciones_equipo(ruta_excel, equipo, anio, categoria):
    try:
        df = pd.read_excel(ruta_excel, sheet_name="Tablas de Posiciones")
        df.columns = df.columns.str.lower().str.strip()

        equipo = equipo.strip().upper()

        df = df[df['año'] == int(anio)]
        if categoria.lower() != "todas":
            df = df[df['categoría'].str.upper() == categoria.upper()]

        df = df[df['equipos'].str.upper() == equipo]

        return df.to_dict(orient='records')

    except Exception as e:
        print(f"❌ Error Posiciones: {e}")
        return []

def buscar_goleadoras_equipo(ruta_excel, equipo, anio, categoria, torneo=None, zona=None):
    try:
        df = pd.read_excel(ruta_excel, sheet_name="Goleadoras")
        df.columns = df.columns.str.lower().str.strip()

        df = df[df['año'] == int(anio)]

        if categoria.lower() != "todas":
            df = df[df['categoría'].str.upper() == categoria.upper()]

        df = df[df['club'].str.upper() == equipo.strip().upper()]

        # Log para depuración
        print(f"📌 Filtro Goleadoras - Torneo: {torneo}, Zona: {zona}")

        if torneo and 'torneo' in df.columns:
            df = df[df['torneo'].str.upper().str.contains(torneo.strip().upper(), na=False)]

        if zona and 'zona' in df.columns:
            df = df[df['zona'].str.upper().str.contains(zona.strip().upper(), na=False)]

        if df.empty:
            print("⚠️ No se encontraron goleadoras con estos filtros.")

        return df.to_dict(orient='records')

    except Exception as e:
        print(f"❌ Error Goleadoras: {e}")
        return []

def obtener_equipos_disponibles(ruta_excel):
    try:
        df = pd.read_excel(ruta_excel, sheet_name="Fixtures")
        df.columns = df.columns.str.lower().str.strip()
        equipos_a = df['equipo a'].dropna().str.strip().str.upper()
        equipos_b = df['equipo b'].dropna().str.strip().str.upper()
        todos = pd.concat([equipos_a, equipos_b]).unique()
        return sorted(todos)
    except Exception as e:
        print(f"⚠️ No se pudieron obtener los equipos: {e}")
        return []
