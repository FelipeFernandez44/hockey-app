
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# Configurar opciones para que no abra ventana del navegador (opcional)
chrome_options = Options()
chrome_options.add_argument('--headless')  # Quitar esta línea si querés ver el navegador
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1920,1080')

# Reemplazá este path por el tuyo si hace falta
service = Service(executable_path="chromedriver.exe")  # Asegurate de tenerlo en tu carpeta de proyecto

driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    url = "https://ahba.com.ar/fixture.php?genero=2&categoria=1&nombre_torneo=105&subdivision=28&redireccion=1"
    driver.get(url)

    # Esperar a que se cargue el contenido por JavaScript
    time.sleep(5)  # Ajustar si tu conexión es lenta

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    filas = soup.find_all('tr', style=lambda x: x and 'font-size:14px' in x)

    partidos = []
    filtro_equipo = "EVERTON"

    for fila in filas:
        columnas = fila.find_all('td')
        if len(columnas) >= 6:
            fecha = columnas[1].get_text(strip=True)
            local = columnas[2].get_text(strip=True)
            visitante = columnas[4].get_text(strip=True)
            cancha = columnas[5].get_text(strip=True)

            if filtro_equipo in (local.upper(), visitante.upper()):
                partidos.append({
                    "fecha": fecha,
                    "local": local,
                    "visitante": visitante,
                    "cancha": cancha
                })

    print("📅 Partidos de Everton encontrados:")
    for p in partidos:
        print(f"{p['fecha']} - {p['local']} vs {p['visitante']} en {p['cancha']}")

finally:
    driver.quit()
