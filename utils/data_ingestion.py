import pytz
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import pandas as pd


def get_cer_df(url: str = None, delta_years: int = 1):
    """
    Gets a table from the web page of Banco Central de la República Argentina.
    :param url: url where data can be found
    :param delta_years: number of years of data from now (backforwards)
    """
    if url is None:
        url = "http://www.bcra.gov.ar/PublicacionesEstadisticas/Principales_variables_datos.asp?serie=3540&detalle=CER" \
              "%A0(Base%202.2.2002=1)"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    fecha_desde = driver.find_element(By.NAME, 'fecha_desde')
    fecha_desde.click()
    for i in range(3):
        fecha_desde.send_keys(Keys.LEFT)
    fecha_desde.send_keys(f"{str(pytz.datetime.datetime.today().date().day).zfill(2)}")
    driver.implicitly_wait(10)
    fecha_desde.send_keys(f"{str(pytz.datetime.datetime.today().date().month).zfill(2)}")
    driver.implicitly_wait(10)
    fecha_desde.send_keys(f"{str(pytz.datetime.datetime.today().date().year - delta_years).zfill(4)}")
    driver.implicitly_wait(10)
    fecha_hasta = driver.find_element(By.NAME, 'fecha_hasta')
    fecha_hasta.click()
    for i in range(3):
        fecha_hasta.send_keys(Keys.LEFT)
    fecha_hasta.send_keys(f"{str(pytz.datetime.datetime.today().date().day).zfill(2)}")
    driver.implicitly_wait(10)
    fecha_hasta.send_keys(f"{str(pytz.datetime.datetime.today().date().month).zfill(2)}")
    driver.implicitly_wait(10)
    fecha_hasta.send_keys(f"{str(pytz.datetime.datetime.today().date().year).zfill(4)}")
    driver.implicitly_wait(10)
    boton_buscar = driver.find_element(By.NAME, 'B1')
    driver.implicitly_wait(10)
    boton_buscar.click()
    table_raw = driver.find_elements(By.TAG_NAME, 'tbody')
    table_raw = [row.text for row in table_raw]
    df = pd.DataFrame(columns=['date', 'cer'])
    df['date'] = [
        pytz.timezone('America/Argentina/Mendoza').localize(pytz.datetime.datetime.strptime(row[0:10], "%d/%m/%Y"))
        for row in table_raw]
    df['cer'] = [float(row[11:].replace(',', '.')) for row in table_raw]

    df.set_index(keys=df['date'], inplace=True)
    df.drop(columns=['date'], inplace=True)

    return df
