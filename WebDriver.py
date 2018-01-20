from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import time

class WebDriver(object):

    def __init__(self):
        self.driver = webdriver.Chrome('/Users/jarvis/PycharmProjects/OSTK/OSTKF/chromedriver')

    def get_identifier(self, nameString):
        identifiers = {'ID': By.ID, 'CLASS': By.CLASS_NAME}
        return identifiers[nameString]

    def wait(self):
        return WebDriverWait(self.driver, 5)

    def pause(self, seconds=2):
        time.sleep(seconds)

    def get_element(self, identifierString, itemString):
        identifier = self.get_identifier(identifierString)

        try:
            element = self.wait().until(EC.presence_of_element_located((identifier, itemString)))
            return element

        except TimeoutException:
            print(' Unable to find {} identified by {}'.format(itemString, identifierString))

    def get_element_by_xpath(self,xpath):

        try:
            time.sleep(2)
            element = self.driver.find_element_by_xpath(xpath)
            return element

        except TimeoutException:
            print('Unable to find {}'.format(xpath))

    def get_button(self, identifierString, itemString):
        identifier = self.get_identifier(identifierString)

        try:
            button = self.wait().until(EC.element_to_be_clickable((identifier, itemString)))
            return button

        except TimeoutException:
            print('Unable to find {} identified by {}'.format(itemString, identifierString))

    def click_button(self, button):
        button.click()

    def enter_text(self, textbox, inputText, criticalKeys=None):
        textbox.send_keys(inputText)

        if criticalKeys != None:
            for key in criticalKeys:
                self.enter_critical_key(textbox, key)

    def enter_critical_key(self, textbox, keyName):
        criticalKeys = {'RETURN': Keys.RETURN, 'DOWN': Keys.DOWN}
        criticalKey = None

        for key,value in criticalKeys.items():
            if keyName == key:
                criticalKey = value

        if criticalKey != None:
            textbox.send_keys(criticalKey)
        else:
            print('Error: Critical Key not in dictionary')

    def go_to(self, url):
        self.driver.get(url)

    def close(self):
        self.driver.close()

    def scroll(self, scrollWindow, iterations):
        x = 0
        while x < iterations:
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollWindow)
            self.pause()
            x += 1

    def scroll_main_window(self, pixels):
        self.driver.execute_script('window.scrollBy(0,'+pixels+')', '')




