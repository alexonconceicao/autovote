import os
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

load_dotenv()

LINK = os.getenv('LINK')
PROXY_HOST = os.getenv('PROXY_HOST')
USE_PROXY = os.getenv('USE_PROXY') == 'true'
PROXY_PORT = os.getenv('PROXY_PORT')
PROXY_USERNAME = os.getenv('PROXY_USERNAME')
PROXY_PASS = os.getenv('PROXY_PASS')
INFO_TO_SEARCH = os.getenv('INFO_TO_SEARCH')
RADIO_BUTTON = os.getenv('RADIO_BUTTON')
VOTE_BUTTON = os.getenv('VOTE_BUTTON')

logging.basicConfig(level=logging.INFO)

def close_cookie_banner(driver):
    try:
        cookie_banner = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.styles__CookieContainer-sc-150pbzj-0'))
        )
        cookie_banner.click()
        logging.info('Banner de cookies fechado.')
    except:
        logging.warning('Banner de cookies não encontrado.')

def close_popups(driver):
    logging.info('Fechando popups...')
    try:
        notification_cancel_button = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="onesignal-slidedown-cancel-button"]'))
        )
        notification_cancel_button.click()
        logging.info('Popup de notificação fechado.')
    except:
        logging.warning('Popup de notificação não encontrado.')

def clear_cache(driver):
    logging.info('Limpando cache...')
    driver.execute_script('window.localStorage.clear();')
    driver.execute_script('window.sessionStorage.clear();')
    driver.delete_all_cookies()
    logging.info('Cache limpo.')

def get_votes_for_item(driver):
    try:
        items = driver.find_elements(By.CSS_SELECTOR, '.pds-feedback-group')

        for item in items:
            title_element = item.find_element(By.CSS_SELECTOR, '.pds-answer-text')
            title = title_element.get_attribute('title')

            if title == INFO_TO_SEARCH:
                votes_element = item.find_element(By.CSS_SELECTOR, '.pds-feedback-votes')
                votes_text = votes_element.text
                logging.info(f'Votos para {INFO_TO_SEARCH}: {votes_text}')
                return votes_text
        logging.warning(f'{INFO_TO_SEARCH} não encontrado.')
    except Exception as error:
        logging.error(f'Erro ao buscar votos para {INFO_TO_SEARCH}: {error}')

def vote_multiple_times(site_url, n_votes):
    logging.info('Configurando driver...')
    wait5 = 5
    chrome_options = Options()

    if USE_PROXY:
        logging.info('Configurando proxy...')
        chrome_options.add_argument(f'--proxy-server=http://{PROXY_USERNAME}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}')

    service = Service('chromedriver.exe')
    service.start()

    driver = webdriver.Chrome(service=service, options=chrome_options)

    for i in range(n_votes):
        logging.info(f'Votando {i + 1} de {n_votes}...')
        driver.get(site_url)
        close_popups(driver)
        close_cookie_banner(driver)

        try:
            radio_button = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, RADIO_BUTTON))
            )
            driver.execute_script('arguments[0].scrollIntoView(true);', radio_button)
            time.sleep(wait5)
            driver.execute_script('arguments[0].click();', radio_button);
            logging.info('Botão de escolha clicado.')
        except Exception as error:
            logging.error('O botão de escolha não é clicável:', error)

        try:
            vote_button = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, VOTE_BUTTON))
            )
            vote_button.click()
            logging.info('Botão de voto clicado.')
            time.sleep(wait5)
            get_votes_for_item(driver)
            time.sleep(wait5)
            clear_cache(driver)
            logging.info('Página atualizada.')
        except Exception as error:
            logging.error('O botão de voto não é clicável:', error)

    driver.quit()
    service.stop()
    logging.info('Finalizado.')

if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    n_votes = 10
    if '--votos' in args:
        n_votes = int(args[args.index('--votos') + 1])
    vote_multiple_times(LINK, n_votes)
