from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from selenium.webdriver.support import expected_conditions as Ec
from selenium.common.exceptions import (
    WebDriverException
)
from .common import Common


class Base:
    timeout = 60

    def openingurl(self, url: str):
        """
        To avoid internet connection error while requesting"""

        while True:
            if Common.close_thread_is_set():
                self.driver.quit()
                return

            try:
                self.driver.get(url)
            except WebDriverException:
                sleep(5)
                continue
            else:
                break

    def findelementwithwait(self, by, value):
        """we will use this function to find an element"""

        element = WebDriverWait(self.driver, self.timeout).until(
            Ec.visibility_of_element_located((by, value))
        )
        return element