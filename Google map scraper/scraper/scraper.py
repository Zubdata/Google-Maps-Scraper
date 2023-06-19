"""
This module contain the code for backend,
that will handle scraping process
"""



from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from time import sleep
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as Ec
from selenium.common.exceptions import (
    NoSuchWindowException,
    WebDriverException,
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
    JavascriptException,
)
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import sys
import threading
import os
import undetected_chromedriver as uc
from datasaver import DataSaver


class Backend:
    closeThread=threading.Event()

    timeout = 60

    def __init__(self, searchquery, outputformat, messageshowingfunc, outputpath):
        """
        params:

        search query: it is the value that user will enter in search query entry 
        outputformat: output format of file , selected by user
        messageshowingfunc: function refernece to function of frontend class to 
        outputpath: directory path where file will be stored after scraping

        """


        self.searchquery = searchquery  # search query that user will enter
        self.messageshowing = messageshowingfunc  # it is a function used as api for transfering message form this backend to frontend

        """
        output path is location of folder where file will be stored after scraping.
        it will be asked When user will use this application for first time, after that 
        user can change this path by clicking on the button "Reset path" 
        """

        self.datasaver = DataSaver(
            selectedpath=outputpath,
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

        infoSheet = self.driver.execute_script("""return document.querySelector("[role='main']")""")
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

            name = soup.find("h1", class_="DUwDvf fontHeadlineLarge").text.strip()

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

        except:  #some resuts have no information , so we dont want them in our pretty cleaned list
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
            We will use these links to find our recuired data from information fields of the business card
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
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)

            self.messageshowing(
                custom=True,
                value="Wait checking for driver...\nIf you don't have webdriver in your machine it will install it",
            )

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

                        script="""
                        const xpathExpression = '//*[text()="You\\'ve reached the end of the list."]';
                        const result = document.evaluate(xpathExpression, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                        const element = result.singleNodeValue;
                        return element;

                        """
                        endAlertElement = self.driver.execute_script(script) # to know that we are at end of list or not

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


                allResultsListSoup = BeautifulSoup(scrollAbleElement.get_attribute('outerHTML'),'html.parser')


                allResultsAnchorTags=allResultsListSoup.find_all('a',class_='hfpxzc')

                """all the links of results"""
                allResultsLinks=[anchorTag.get('href') for anchorTag in allResultsAnchorTags] 


                for resultLink in allResultsLinks:
                    if  self.closeThread.is_set():
                        self.driver.quit()
                        return

                    self.openingurl(url=resultLink)
                    self.parsing()




            """
        Handling all errors.If any error occurs like user has closed the self.driver and if 'no such window' error occurs
            """
        except:
            try:
                self.messageshowing(interruptionerror=True)

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


