from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
from dotenv import load_dotenv
import os
import logging
import argparse

load_dotenv()

LINK = os.getenv("LINK")
PROXY_HOST = os.getenv("PROXY_HOST")
PROXY_PORT = os.getenv("PROXY_PORT")
PROXY_USERNAME = os.getenv("PROXY_USERNAME")
PROXY_PASS = os.getenv("PROXY_PASS")

logging.basicConfig(level=logging.INFO)


def fechar_popups(driver):
    logging.info("Fechando popups...")
    try:
        notification_cancel_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="onesignal-slidedown-cancel-button"]')
            )
        )
        if notification_cancel_button.is_displayed():
            notification_cancel_button.click()
            logging.info("Popup de notificação fechado.")
    except:
        logging.warning("Popup de notificação não encontrado.")

    try:
        specific_popup_close = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="ads-wrapper"]/div/button'))
        )
        if specific_popup_close.is_displayed():
            driver.execute_script(
                "arguments[0].scrollIntoView();", specific_popup_close
            )
            specific_popup_close.click()
            logging.info("Popup específico fechado.")
    except:
        logging.warning("Popup específico não encontrado.")


def limpar_cache(driver):
    logging.info("Limpando cache...")
    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")
    driver.delete_all_cookies()
    logging.info("Cache limpo.")


def delete_cache(driver):
    logging.info("Deletando cache do navegador...")
    driver.execute_script("window.open('')")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get("chrome://settings/clearBrowserData")
    sleep(3)
    actions = ActionChains(driver)
    actions.key_down(Keys.SHIFT).send_keys(Keys.TAB * 6).key_up(Keys.SHIFT)
    actions.perform()
    sleep(3)
    actions.send_keys(Keys.DOWN * 5 + Keys.TAB * 7 + Keys.ENTER)
    actions.perform()
    sleep(3)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    logging.info("Dados de navegação limpos.")


def obter_votos_atual(driver):
    try:

        votos_element = driver.find_element(
            By.XPATH, '//*[@id="pds-results"]/li[4]/label/span[2]/span[2]'
        )
        wait = WebDriverWait(driver, 30)
        votos_element = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="pds-results"]/li[4]/label/span[2]/span[2]')
            )
        )
        votos_atual = votos_element.text
        logging.info(f"Quantidade atual de votos: {votos_atual}")
        return votos_atual
    except Exception as e:
        logging.error("Não foi possível obter a quantidade de votos atuais: %s", e)
        return None


def votar_n_vezes(site_url, n_votos):

    logging.info("Configurando proxy...")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(
        "--proxy-server=http://%s:%s@%s:%s"
        % (PROXY_HOST, PROXY_PORT, PROXY_USERNAME, PROXY_PASS)
    )

    chrome_service = Service("chromedriver.exe")
    driver = webdriver.Chrome(options=chrome_options, service=chrome_service)

    for i in range(n_votos):
        logging.info(f"Votando {i + 1} de {n_votos}...")
        driver.get(site_url)

        fechar_popups(driver)

        try:
            radio_button = driver.find_element(By.ID, "PDI_answer64069335")
            wait = WebDriverWait(driver, 30)
            radio_button = wait.until(
                EC.element_to_be_clickable((By.ID, "PDI_answer64069335"))
            )
            driver.execute_script("arguments[0].click();", radio_button)
            logging.info("Botão de escolha clicado.")
        except Exception as e:
            logging.error("O botão de escolha HAPVIDA não é clicável: %s", e)

        try:
            wait = WebDriverWait(driver, 30)
            vote_button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="pd-vote-button14405457"]')
                )
            )
            driver.execute_script("arguments[0].click();", vote_button)
            logging.info("Botão de voto clicado.")

            sleep(15)

            obter_votos_atual(driver)

            sleep(5)

            limpar_cache(driver)
            delete_cache(driver)

            driver.refresh()
            logging.info("Página atualizada.")
        except Exception as e:
            logging.error("O botão de voto não é clicável: %s", e)

    driver.quit()
    logging.info("Finalizado.")


def main():
    parser = argparse.ArgumentParser(description="Votar em um site.")
    parser.add_argument(
        "--votos", type=int, default=10, help="Quantidade de votos (padrão: 10)"
    )
    args = parser.parse_args()

    n_votos = args.votos
    votar_n_vezes(LINK, n_votos)


if __name__ == "__main__":
    main()
