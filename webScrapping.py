from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

# Lista de valores de departamentos
departamentos = ["16", "15", "04", "20", "00", "02", "05", "01", "13", "18", "21", "22", "17", "09", "14", "11", "03", "12", "06", "07", "10", "08", "19"]
print(len(departamentos))

# Función para seleccionar el departamento y obtener la tabla
def obtener_tabla_por_departamento(departamento):
    print("Obteniendo datos para el departamento", departamento)
    # Configura el driver de Chrome
    driver = webdriver.Chrome()  # Asegúrate de que chromedriver esté en tu PATH

    # Abre la página web
    url = 'https://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/'
    driver.get(url)
    # Selecciona "DIVERSIFICADO" en el dropdown de niveles
    select_nivel = Select(WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "_ctl0_ContentPlaceHolder1_cmbNivel"))
    ))
    select_nivel.select_by_value("46")

    data = []
    # Espera a que el dropdown de departamentos esté presente
    select_departamento = Select(WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "_ctl0_ContentPlaceHolder1_cmbDepartamento"))
    ))

    # Selecciona el departamento
    select_departamento.select_by_value(departamento)
    
    # Encuentra y clickea el botón de consulta
    boton_consultar = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "_ctl0_ContentPlaceHolder1_IbtnConsultar"))
    )
    boton_consultar.click()

    # Espera a que la tabla esté presente
    tabla = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "TableResumen"))
    )

    # Obtén el contenido de la tabla
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tabla_html = soup.find('table', {'id': 'TableResumen'})

    # Extrae los datos de la tabla
    rows = tabla_html.find_all('tr')
    for row in rows[2:]:
        cols = row.find_all('td')
        if cols:
            cols = [col.text.strip() for col in cols]
            data.append(cols)

    driver.quit()

    return data

# Itera sobre los departamentos y obtiene la tabla para cada uno
dataDepartamento = {}
columnas = ["", "CODIGO", "DISTRITO", "DEPARTAMENTO", "MUNICIPIO", "ESTABLECIMIENTO", "DIRECCION", "TELEFONO", "SUPERVISOR", "DIRECTOR", "NIVEL", "SECTOR", "AREA", "STATUS", "MODALIDAD", "JORNADA", "PLAN", "DEPARTAMENTAL"]
dfs = []
for departamento in departamentos:
    dataDepartamento[departamento] = obtener_tabla_por_departamento(departamento)
    key = departamento
    value = dataDepartamento[key]

    print("Departamento: ", key)
    # Crea el DataFrame
    df = pd.DataFrame(value, columns=columnas)

    # Elimina la columna vacía (la primera columna)
    df = df.drop(columns=[""])

    # Format the data with all columns are strings
    df = df.astype(str)

    # Eliminar columnas con solo NaN
    df = df.dropna(axis=1, how='all')

    # Guardar el DataFrame en la lista
    dfs.append(df)

# Concatenar todos los DataFrames en uno solo
df = pd.concat(dfs)

# Guardar el DataFrame en un archivo CSV
df.to_csv("establecimientos.csv", index=False)
