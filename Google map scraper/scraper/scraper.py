"""
This module contain the code for backend,
that will handle scraping process
"""

from bs4 import BeautifulSoup
from time import sleep
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as Ec
from selenium.common.exceptions import (
    WebDriverException,
    JavascriptException,
)
import sys
import threading
import undetected_chromedriver as uc
from .datasaver import DataSaver
from .settings import DRIVER_EXECUTABLE_PATH


class Backend:
    closeThread = threading.Event()

    timeout = 60

    def __init__(self, searchquery, outputformat, messageshowingfunc,  healdessmode):
        """
        params:

        search query: it is the value that user will enter in search query entry 
        outputformat: output format of file , selected by user
        messageshowingfunc: function refernece to function of frontend class to 
        outputpath: directory path where file will be stored after scraping
        headlessmode: it's value can be 0 and 1, 0 means unchecked box and 1 means checked

        """

        self.searchquery = searchquery  # search query that user will enter
        # it is a function used as api for transfering message form this backend to frontend
        self.messageshowing = messageshowingfunc

        self.headlessMode = healdessmode
        self.datasaver = DataSaver(
            outputformat=outputformat,
            messageshowfunc=messageshowingfunc,
        )

    def findelementwithwait(self, by, value):
        """we will use this function to find an element"""

        element = WebDriverWait(self.driver, self.timeout).until(
            Ec.visibility_of_element_located((by, value))
        )
        return element

    def openingurl(self, url: str):
        """
        To avoid internet connection error while requesting"""

        while True:
            if self.closeThread.is_set():
                self.driver.quit()
                return

            try:
                self.driver.get(url)
            except WebDriverException:
                sleep(5)
                continue
            else:
                break

    def parsing(self):
        """Our function to parse the html"""

        """This block will get element details sheet of a business. 
        Details sheet means that business details card when you click on a business in 
        serach results in google maps"""

        infoSheet = self.driver.execute_script(
            """return document.querySelector("[role='main']")""")
        try:
            """If that information sheet is founded in try block, this block will run and find the contact details"""
            rating, totalReviews, address, websiteUrl, phone = (
                None,
                None,
                None,
                None,
                None,
            )  # by default they will be none

            html = infoSheet.get_attribute("outerHTML")
            soup = BeautifulSoup(
                html, "html.parser"
            )  # soup of information  sheet of that place

            try:
                rating = soup.find("span", class_="ceNzKf").get("aria-label")

            except:  # if a business does not has rating
                rating = None

            try:
                totalReviews = list(soup.find("div", class_="F7nice").children)
                totalReviews = totalReviews[1].get_text(
                    strip=True
                )

            except:
                totalReviews = None

            name = soup.select_one(selector=".tAiQdd h1.DUwDvf").text.strip()

            allInfoBars = soup.find_all("div", class_="AeaXub")

            for infoBar in allInfoBars:
                link = infoBar.find("img").get("src")
                text = infoBar.text

                """Below three conditons are used to comapre fetched links to compare them with
                those links that we have write in start"""

                if link == self.comparingLinks["locationLink"]:
                    address = text.strip()

                elif link == self.comparingLinks["websiteLink"]:
                    try:
                        websiteUrl = infoBar.parent.get("href")
                    except:
                        websiteUrl = None

                elif link == self.comparingLinks["phoneLink"]:
                    phone = text.strip()

                else:
                    pass

            data = {
                "Name": name,
                "Phone": phone,
                "Address": address,
                "Website": websiteUrl,
                "Total Reviews": totalReviews,
                "Rating": rating,
            }

            self.finalData.append(data)

        except:  # some resuts have no information , so we dont want them in our pretty cleaned list
            pass

    def mainscraping(self):

        try:
            querywithplus = "+".join(self.searchquery.split())

            """
            link of page variable contains the link of page of google maps that user wants to scrape.
            We have make it by inserting search query in it
            """

            link_of_page = f"https://www.google.com/maps/search/{querywithplus}/"

            # ==========================================

            """ 
            We will use these links to find our required data from information fields of the business card
            To understand it , kindly see its use in parsing
            """
            self.comparingLinks = {
                "locationLink": """//www.gstatic.com/images/icons/material/system_gm/1x/place_gm_blue_24dp.png""",
                "phoneLink": """//www.gstatic.com/images/icons/material/system_gm/1x/phone_gm_blue_24dp.png""",
                "websiteLink": """//www.gstatic.com/images/icons/material/system_gm/1x/public_gm_blue_24dp.png""",
            }

            """
            In this empty list our records will be append, we will make pandas dataframe from it
            """
            self.finalData = []

            """Starting our browser"""

            options = uc.ChromeOptions()

            if self.headlessMode == 1:
                options.headless = True

            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)

            self.messageshowing(
                custom=True,
                value="Wait checking for driver...\nIf you don't have webdriver in your machine it will install it",
            )
            try:
                if DRIVER_EXECUTABLE_PATH is not None:
                    self.driver = uc.Chrome(
                        driver_executable_path=DRIVER_EXECUTABLE_PATH, options=options)

                else:
                    self.driver = uc.Chrome(options=options)

            except NameError:
                self.driver = uc.Chrome(options=options)

            self.driver.maximize_window()
            self.messageshowing(custom=True, value="Opening browser...")
            self.driver.implicitly_wait(self.timeout)

            # ====================================

            self.openingurl(url=link_of_page)

            self.messageshowing(custom=True, value="Working start...")

            sleep(1)
            scrollAbleElement = self.driver.execute_script(
                """return document.querySelector("[role='feed']")"""
            )

            """In case search results are not available"""
            if scrollAbleElement is None:
                self.messageshowing(noresultfound=True)

            else:
                last_height = 0

                while True:
                    if self.closeThread.is_set():
                        self.driver.quit()
                        return

                    """Scroll down to the bottom."""
                    self.driver.execute_script(
                        "arguments[0].scrollTo(0, arguments[0].scrollHeight);",
                        scrollAbleElement,
                    )
                    time.sleep(2)

                    # Wait to load the page.

                    # get new scroll height and compare with last scroll height.
                    new_height = self.driver.execute_script(
                        "return arguments[0].scrollHeight", scrollAbleElement
                    )
                    if new_height == last_height:
                        """checking if we have reached end of the list"""

                        script = f"""
                        const endingElement = document.querySelector(".PbZDve ");
                        return endingElement;
                        """
                        endAlertElement = self.driver.execute_script(
                            script)  # to know that we are at end of list or not

                        if endAlertElement is None:
                            """if it returns empty list its mean we are not at the end of list"""
                            try:  # sometimes google maps load results when a result is clicked
                                self.driver.execute_script(
                                    "array=document.getElementsByClassName('hfpxzc');array[array.length-1].click();"
                                )
                            except JavascriptException:
                                pass
                        else:

                            break
                    else:
                        last_height = new_height

                allResultsListSoup = BeautifulSoup(
                    scrollAbleElement.get_attribute('outerHTML'), 'html.parser')

                allResultsAnchorTags = allResultsListSoup.find_all(
                    'a', class_='hfpxzc')

                """all the links of results"""
                allResultsLinks = [anchorTag.get(
                    'href') for anchorTag in allResultsAnchorTags]

                for resultLink in allResultsLinks:
                    if self.closeThread.is_set():
                        self.driver.quit()
                        return

                    self.openingurl(url=resultLink)
                    self.parsing()

            """
        Handling all errors.If any error occurs like user has closed the self.driver and if 'no such window' error occurs
            """
        except Exception as e:
            import traceback
            traceback.print_exc()

            try:
                self.messageshowing(interruptionerror=True, exception=str(e))

                try:
                    self.driver.quit()
                except:  # if browser is always closed
                    pass

                try:
                    self.datasaver.save(self.finalData)
                except:
                    pass
            except RuntimeError:
                sys.exit()

        else:  # if not any error occured, will save the data smoothly
            self.driver.close()

            self.datasaver.save(self.finalData)
