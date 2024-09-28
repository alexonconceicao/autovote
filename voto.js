const { Builder, By, until } = require('selenium-webdriver');
const { Options } = require('selenium-webdriver/chrome');
const dotenv = require('dotenv');
const log = require('loglevel');
const process = require('process');

dotenv.config();

const LINK = process.env.LINK;
const PROXY_HOST = process.env.PROXY_HOST;
const USE_PROXY = process.env.USE_PROXY === 'true';
const PROXY_PORT = process.env.PROXY_PORT;
const PROXY_USERNAME = process.env.PROXY_USERNAME;
const PROXY_PASS = process.env.PROXY_PASS;
const INFO_TO_SEARCH = process.env.INFO_TO_SEARCH;
const RADIO_BUTTON = process.env.RADIO_BUTTON;
const VOTE_BUTTON = process.env.VOTE_BUTTON;

log.setLevel('info');

async function closeCookieBanner(driver) {
  try {
    const cookieBanner = await driver.wait(
      until.elementLocated(By.css('.styles__CookieContainer-sc-150pbzj-0')),
      30000
    );
    await driver.wait(until.elementIsVisible(cookieBanner), 30000);
    await cookieBanner.click();
    log.info('Banner de cookies fechado.');
  } catch {
    log.warn('Banner de cookies não encontrado.');
  }
}

async function closePopups(driver) {
  log.info('Fechando popups...');
  try {
    const notificationCancelButton = await driver.wait(
      until.elementLocated(
        By.xpath('//*[@id="onesignal-slidedown-cancel-button"]')
      ),
      30000
    );
    await driver.wait(until.elementIsVisible(notificationCancelButton), 30000);
    await notificationCancelButton.click();
    log.info('Popup de notificação fechado.');
  } catch {
    log.warn('Popup de notificação não encontrado.');
  }
}

async function clearCache(driver) {
  log.info('Limpando cache...');
  await driver.executeScript('window.localStorage.clear();');
  await driver.executeScript('window.sessionStorage.clear();');
  await driver.manage().deleteAllCookies();
  log.info('Cache limpo.');
}

async function getVotesForItem(driver) {
  try {
    const items = await driver.findElements(By.css('.pds-feedback-group'));

    for (let item of items) {
      const titleElement = await item.findElement(By.css('.pds-answer-text'));
      const title = await titleElement.getAttribute('title');

      if (title === INFO_TO_SEARCH) {
        const votesElement = await item.findElement(
          By.css('.pds-feedback-votes')
        );
        const votesText = await votesElement.getText();
        log.info(`Votos para ${INFO_TO_SEARCH}: ${votesText}`);
        return votesText;
      }
    }
    log.warn(`${INFO_TO_SEARCH} não encontrado.`);
  } catch (error) {
    log.error(`Erro ao buscar votos para ${INFO_TO_SEARCH}:`, error);
  }
}

async function voteMultipleTimes(siteUrl, nVotes) {
  log.info('Configurando driver...');
  const wait5 = 5000;
  const wait15 = 15000;
  const chromeOptions = new Options();

  if (USE_PROXY) {
    log.info('Configurando proxy...');
    chromeOptions.addArguments(
      `--proxy-server=http://${PROXY_USERNAME}:${PROXY_PASS}@${PROXY_HOST}:${PROXY_PORT}`
    );
  }

  const driver = new Builder()
    .forBrowser('chrome')
    .setChromeOptions(chromeOptions)
    .build();

  for (let i = 0; i < nVotes; i++) {
    log.info(`Votando ${i + 1} de ${nVotes}...`);
    await driver.get(siteUrl);
    await closePopups(driver);
    await closeCookieBanner(driver);

    try {
      const radioButton = await driver.wait(
        until.elementLocated(By.xpath(RADIO_BUTTON)),
        30000
      );
      await driver.wait(until.elementIsVisible(radioButton), 30000);
      await driver.executeScript(
        'arguments[0].scrollIntoView(true);',
        radioButton
      );
      await driver.sleep(wait5);
      await driver.executeScript('arguments[0].click();', radioButton);
      log.info('Botão de escolha clicado.');
    } catch (error) {
      log.error('O botão de escolha não é clicável:', error);
    }

    try {
      //   await driver.sleep(wait5);
      const voteButton = await driver.wait(
        until.elementLocated(By.xpath(VOTE_BUTTON)),
        30000
      );
      await driver.wait(until.elementIsVisible(voteButton), 30000);
      await voteButton.click();
      log.info('Botão de voto clicado.');
      await driver.sleep(wait5);
      await getVotesForItem(driver);
      await driver.sleep(wait5);
      await clearCache(driver);
      log.info('Página atualizada.');
    } catch (error) {
      log.error('O botão de voto não é clicável:', error);
    }
  }
  await driver.quit();
  log.info('Finalizado.');
}

const args = process.argv.slice(2);
const nVotes = args.includes('--votos')
  ? parseInt(args[args.indexOf('--votos') + 1])
  : 10;
voteMultipleTimes(LINK, nVotes);
