import datetime
import sys
import time

from selenium.common.exceptions import (
    NoSuchElementException, NoSuchWindowException, WebDriverException, TimeoutException, UnexpectedAlertPresentException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

# sys.path.append(sys.path[0] + "/..")
from apps.seletask import SeleTask, new_windows_opened
from utils.telegram import get_tg


cookies = None

class Koinme(SeleTask):

    urls = {
        'home': 'http://koinme.com/',
        'login': 'http://koinme.com/sign-in',
        'offers': 'http://koinme.com/offers',
        'refer': 'http://koinme.com/refer-earn'
    }

    def __init__(self, config):
        super().__init__(config)
        # self.cookies = None

    def get_task_name(self):
        task_name = []
        task_name.append(self.task)
        task_name.append(self.extra.get('username'))
        _config = self.extra.get('config')
        if _config:
            task_name.append(_config)
        if self._config.get('prefs'):
            _proxy = self._config['prefs'].get('network.proxy.socks')
            if _proxy:
                task_name.append(_proxy)
            else:
                task_name.append('noproxy')
        else:
            task_name.append('noproxy')
        task_name = '-'.join(task_name)
        return task_name

    def run(self):
        self.koinme()

    def koinme(self, auto=False):
        offers_h, offer_h = None, None
        last_t = None
        _alert_exist = False
        wait = 240

        while True:
            try:
                if _alert_exist:
                    _alert_exist = False
                    self.s.close_alert()
                    continue

                if offers_h is None:
                    if offer_h is None:
                        if self.s.driver is None:
                            self.s.start()

                        offers_h = self.s.driver.window_handles[0]
                        # offers_h = self.s.get_new_window()
                    else:
                        self.s.driver.switch_to.window(self.s.driver.window_handles[0])
                        offers_h = self.s.get_new_window()
                    continue
                else:
                    # if not self.check_offers_url(offers_h):
                    #     continue
                    try:
                        self.s.driver.switch_to.window(offers_h)
                        if self.s.driver.current_url != self.urls['offers']:
                            self.visit_offers_page()

                        if offer_h is None:
                            try:
                                try:
                                    invalid_session = self.s.driver.find_element(By.ID, '#action-button-box')
                                    if invalid_session.text == 'Invalid session.':
                                        time.sleep(30 * 60)
                                        continue
                                except NoSuchElementException:
                                    pass
                                try:
                                    out_offer = self.s.driver.find_element(By.XPATH, '//h3[contains(., "out of offers")]')
                                    # Looks like we're all out of offers for the moments. Please check back later for more!
                                    self.logger.debug("Looks like we're all out of offers for the moments. Please check back later for more!")
                                    self.s.get(self.urls['refer'])
                                    time.sleep(30 * 60)
                                    continue
                                except NoSuchElementException:
                                    pass
                                try:
                                    no_offer = self.s.driver.find_element(By.XPATH, '//h3[contains(., "No offers")]')
                                    # No offers currently available at this time.
                                    self.logger.debug("No offers currently available at this time.")
                                    self.s.get(self.urls['refer'])
                                    time.sleep(30 * 60)
                                    continue
                                except NoSuchElementException:
                                    pass
                                _windows = self.s.driver.window_handles
                                offer = self.s.find_element((By.XPATH, '//a[@class="start-offer"]/img'))
                                # offer.click()
                                self.s.driver.execute_script("arguments[0].click();", offer)
                                # del offer
                                last_t = None
                                _new_open_windows = self.s.wait().until(new_windows_opened(_windows))
                                if _new_open_windows:
                                    offer_h = _new_open_windows[0]
                            except (NoSuchElementException, TimeoutException) as e:
                                time.sleep(10)
                            continue
                        else:
                            try:
                                self.s.driver.switch_to.window(offer_h)

                                if self.s.driver.current_url == self.urls['offers']:
                                    self.visit_offers_page()
                                    try:
                                        out_offer = self.s.driver.find_element(By.XPATH, '//h3[contains(., "out of offers")]')
                                        # Looks like we're all out of offers for the moments. Please check back later for more!
                                        self.logger.debug("Looks like we're all out of offers for the moments. Please check back later for more!")
                                        time.sleep(30 * 60)
                                        continue
                                    except NoSuchElementException:
                                        pass
                                    try:
                                        no_offer = self.s.driver.find_element(By.XPATH, '//h3[contains(., "No offers")]')
                                        # No offers currently available at this time.
                                        self.logger.debug("No offers currently available at this time.")
                                        time.sleep(30 * 60)
                                        continue
                                    except NoSuchElementException:
                                        pass
                                    try:
                                        offer = self.s.driver.find_element(By.XPATH, '//a[@class="start-offer"]/img')
                                        self.s.close_handles(self.s.driver.window_handles, exclude=[offers_h, offer_h])
                                        # offer.click()
                                        self.s.driver.execute_script("arguments[0].click();", offer)
                                        last_t = None
                                        self.logger.debug('wait 60 seconds')
                                        time.sleep(60)
                                        continue
                                    except NoSuchElementException:
                                        pass
                                else:
                                    if auto:
                                        self.logger.debug('wait %s seconds', wait)
                                        time.sleep(wait)
                                    else:
                                        try:
                                            self.s.driver.find_element(By.ID, 'clock')
                                        except (NoSuchElementException, ):
                                            self.s.driver.refresh()
                                            last_t = None
                                            time.sleep(10)
                                            continue
                                        try:
                                            more = self.s.driver.find_element(By.LINK_TEXT, 'Earn 1.00 More Koins')
                                            # more.click()
                                            self.s.driver.execute_script("arguments[0].click();", more)
                                            self.logger.debug('Get 1 koins, start next')
                                            last_t = datetime.datetime.now()
                                            self.logger.debug('wait %s seconds', wait)
                                            time.sleep(wait)
                                        except NoSuchElementException:
                                            if last_t is None:
                                                last_t = datetime.datetime.now()
                                                self.logger.debug('wait %s seconds', wait)
                                                time.sleep(wait)
                                            else:
                                                _duration = (datetime.datetime.now() - last_t).total_seconds()
                                                if _duration > 900:
                                                    self.s.driver.refresh()
                                                    last_t = None
                                                else:
                                                    self.logger.debug('wait 60 seconds')
                                                    time.sleep(60)
                            except NoSuchWindowException as e:
                                time.sleep(5)
                                offer_h = None
                                continue
                    except NoSuchWindowException as e:
                        time.sleep(5)
                        # offers_h = self.s.get_new_window()
                        offers_h = None
                        continue

            except KeyboardInterrupt:
                self.s.kill()
                offers_h, offer_h = None, None
                raise
            except (ConnectionRefusedError) as e:
                self.logger.exception(e)
                time.sleep(5)
                self.s.kill(profile_persist=True)
                offers_h, offer_h = None, None
                time.sleep(5)
            except UnexpectedAlertPresentException as e:
                _alert_exist = True
            except (TimeoutException, NoSuchWindowException, WebDriverException) as e:
                b = (
                    'Failed to decode response from marionette',
                    'Failed to write response to stream',
                    'Tried to run command without establishing a connection',
                )
                if e.msg in b:
                    self.logger.exception(e)
                    time.sleep(5)
                    self.s.kill(profile_persist=True)
                    offers_h, offer_h = None, None
                    time.sleep(5)
                else:
                    self.logger.exception(e)
                    time.sleep(5)
                    offers_h, offer_h = None, None
                    last_t = None
            except Exception as e:
                self.logger.exception(e)
                time.sleep(5)
                offers_h, offer_h = None, None
                last_t = None

    def visit_offers_page(self):
        self.s.get(self.urls['offers'])
        time.sleep(5)
        logged = False
        while not logged:
            if self.s.driver.current_url == self.urls['offers']:
                logged = True
            else:
                # self.s.driver.delete_all_cookies()
                if cookies:
                # if self.cookies:
                    for c in cookies:
                    # for c in self.cookies:
                        if c.get('domain') == '.koinme.com':
                            c['domain'] == 'koinme.com'
                        self.s.driver.add_cookie(c)
                self.s.get(self.urls['offers'])
                if self.s.driver.current_url == self.urls['offers']:
                    logged = True
                else:
                    self.login()
                    self.s.get(self.urls['offers'])
                    time.sleep(5)

    def login(self):
        try:
            tg = get_tg()
            if tg:
                tg.send_message('saythx', 'please solve login captcha')
            if self.s.driver.current_url != self.urls['login']:
                self.s.get(self.urls['login'])
            username = self.s.find_element((By.ID, 'loginform-username'))
            self.s.clear(username)
            username.send_keys(self.extra['username'])
            password = self.s.driver.find_element(By.ID, 'loginform-password')
            self.s.clear(password)
            password.send_keys(self.extra['password'])
            while True:
                _input = input('Login(Please enter "y" "yes" "ok" "n" "no" or "retry")?')
                if _input.isalpha():
                    if _input.lower() in ['y', 'yes', 'ok']:
                        self.logger.debug('Login success')
                        break
                    elif _input.lower() in ['n', 'no']:
                        self.logger.debug('Login failed')
                        raise WebDriverException('login failed')
                    elif _input.lower() in ['retry']:
                        self.logger.debug('Retry')
                        time.sleep(10)
                        raise WebDriverException('retry login koinme')
        except WebDriverException as e:
            if e.msg in ['retry login koinme']:
                self.s.get('about:blank')
                time.sleep(3)
                self.login()
            else:
                raise e
        cookies = self.s.driver.get_cookies()
        # self.cookies = self.s.driver.get_cookies()
        cookies = [c for c in cookies if 'koinme.com' in c.get('domain')]
        # self.cookies = [c for c in self.cookies if 'koinme.com' in c.get('domain')]

    def check_offers_url(self, offers_h):
        result = False
        try:
            self.s.driver.switch_to.window(offers_h)
            if self.s.driver.current_url != self.urls['offers']:
                self.visit_offers_page()
            result = True
        except NoSuchWindowException as e:
            time.sleep(5)
            offers_h = self.s.get_new_window()
            result = False
        except Exception as e:
            raise e

        return result
