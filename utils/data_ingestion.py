from time import sleep

import pytz

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager

import datetime as dt
import pandas as pd
import warnings


def validate_date(string):
    try:
        dt.datetime.strptime(string, '%d/%m/%Y')
        return True
    except ValueError:
        warnings.warn("Incorrect data format, should be DD/MM/YYYY")
        return False


def get_cer_df(url: str = None, delta_years: int = 1):
    """
    Gets a table from the web page of Banco Central de la República Argentina.
    :param url: url where data can be found
    :param delta_years: number of years of data from now (backforwards)
    """
    if url is None:
        url = "http://www.bcra.gov.ar/PublicacionesEstadisticas/Principales_variables_datos.asp?serie=3540&detalle=CER" \
              "%A0(Base%202.2.2002=1)"
    firefoxoptions = Options()
    firefoxoptions.add_argument("--headless")
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(
        options=firefoxoptions,
        service=service,
    )
    driver.get(url)
    fecha_desde = driver.find_element(By.NAME, 'fecha_desde')
    fecha_desde.click()
    fecha_desde.send_keys(str((pytz.datetime.datetime.today().date() - dt.timedelta(days=delta_years*370)).isoformat()))
    fecha_hasta = driver.find_element(By.NAME, 'fecha_hasta')
    fecha_hasta.click()
    fecha_hasta.send_keys(str(pytz.datetime.datetime.today().date().isoformat()))
    boton_buscar = driver.find_element(By.NAME, 'B1')
    boton_buscar.click()
    driver.implicitly_wait(10)
    table_raw = driver.find_elements(By.TAG_NAME, 'tbody')
    table_raw = [row.text for row in table_raw if validate_date(row.text[0:10])]
    df = pd.DataFrame(columns=['date', 'cer'])
    df['date'] = [
        pytz.timezone('America/Argentina/Mendoza').localize(pytz.datetime.datetime.strptime(row[0:10], "%d/%m/%Y"))
        for row in table_raw]
    df['cer'] = [float(row[11:].replace(',', '.')) for row in table_raw]

    driver.quit()

    df.set_index(keys=df['date'], inplace=True)
    df.drop(columns=['date'], inplace=True)

    return df


def get_dolar_blue_df(url: str = None, delta_years: int = 10):
    """
    Gets a table from the web page of https://www.ambito.com/contenidos/dolar-informal-historico.html.
    :param url: url where data can be found
    :param delta_years: number of years of data from now (backforwards)
    """
    if url is None:
        url = "https://www.ambito.com/contenidos/dolar-informal-historico.html"
    firefoxoptions = Options()
    firefoxoptions.add_argument("--headless")
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(
        options=firefoxoptions,
        service=service,
    )
    driver.get(url)
    df = None
    for i in range(2):
        fecha_desde = driver.find_element(By.CSS_SELECTOR, "input[class='datepicker desde form-control']")
        wait = WebDriverWait(driver, 2)
        wait.until(lambda d: fecha_desde.is_displayed())
        fecha_desde.click()
        fecha_desde.clear()
        for i in range(10):
            fecha_desde.send_keys(Keys.BACK_SPACE)
        driver.implicitly_wait(1)
        fecha_keys = (pytz.datetime.datetime.today().date() - dt.timedelta(days=delta_years*370)).strftime('%d-%m-%Y')
        fecha_desde.send_keys(fecha_keys)
        driver.implicitly_wait(1)
        fecha_desde.send_keys(Keys.ENTER)
        driver.implicitly_wait(1)
        fecha_hasta = driver.find_element(By.CSS_SELECTOR, "input[class='datepicker hasta form-control']")
        wait = WebDriverWait(driver, 2)
        wait.until(lambda d: fecha_hasta.is_displayed())
        fecha_hasta.click()
        fecha_hasta.clear()
        for i in range(10):
            fecha_hasta.send_keys(Keys.BACK_SPACE)
        fecha_keys = pytz.datetime.datetime.today().date().strftime('%d-%m-%Y')
        fecha_hasta.send_keys(fecha_keys)
        fecha_desde.send_keys(Keys.ENTER)
        boton_buscar = driver.find_element(By.CSS_SELECTOR, "button[class='boton']")
        wait = WebDriverWait(driver, 2)
        wait.until(lambda d: boton_buscar.is_displayed())
        boton_buscar.click()
        # sleep(1)
        # driver.implicitly_wait(10)
        table_raw = driver.find_elements(By.TAG_NAME, 'tbody')
        table_raw = table_raw[0].text.split('\n')
        # print(table_raw)
        df = pd.DataFrame(columns=['date', 'compra', 'venta'])
        df['date'] = [
            pytz.timezone('America/Argentina/Mendoza').localize(pytz.datetime.datetime.strptime(row[0:10], "%d-%m-%Y"))
            for row in table_raw]
        df['compra'] = [float(row.split(' ')[1].replace(',', '.')) for row in table_raw]
        df['venta'] = [float(row.split(' ')[2].replace(',', '.')) for row in table_raw]
        driver.implicitly_wait(1)
    driver.quit()

    df.set_index(keys=df['date'], inplace=True)
    df.drop(columns=['date'], inplace=True)

    return df

