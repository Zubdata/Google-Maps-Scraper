"""
This module contain the code for backend,
that will handle scraping process
"""

from time import sleep
from scraper.base import Base
from scraper.scroller import Scroller
import undetected_chromedriver as uc
from settings import DRIVER_EXECUTABLE_PATH
from scraper.communicator import Communicator


class Backend(Base):
    

    def __init__(self, searchquery, outputformat,  healdessmode):
        """
        params:

        search query: it is the value that user will enter in search query entry 
        outputformat: output format of file , selected by user
        outputpath: directory path where file will be stored after scraping
        headlessmode: it's value can be 0 and 1, 0 means unchecked box and 1 means checked

        """


        self.searchquery = searchquery  # search query that user will enter
        
        # it is a function used as api for transfering message form this backend to frontend

        self.headlessMode = healdessmode

        self.init_driver()
        self.scroller = Scroller(driver=self.driver)
        self.init_communicator()

    def init_communicator(self):
        Communicator.set_backend_object(self)


    def init_driver(self):
        options = uc.ChromeOptions()
        if self.headlessMode == 1:
                options.headless = True

        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)

        Communicator.show_message("Wait checking for driver...\nIf you don't have webdriver in your machine it will install it")

        try:
            if DRIVER_EXECUTABLE_PATH is not None:
                self.driver = uc.Chrome(
                    driver_executable_path=DRIVER_EXECUTABLE_PATH, options=options)

            else:
                self.driver = uc.Chrome(options=options)

        except NameError:
            self.driver = uc.Chrome(options=options)
        
        
        

        Communicator.show_message("Opening browser...")
        self.driver.maximize_window()
        self.driver.implicitly_wait(self.timeout)



    def mainscraping(self):

        try:
            querywithplus = "+".join(self.searchquery.split())

            """
            link of page variable contains the link of page of google maps that user wants to scrape.
            We have make it by inserting search query in it
            """

            link_of_page = f"https://www.google.com/maps/search/{querywithplus}/"

            # ==========================================

            self.openingurl(url=link_of_page)

            Communicator.show_message("Working start...")

            sleep(1)

            self.scroller.scroll()
            

        except Exception as e:
            """
            Handling all errors.If any error occurs like user has closed the self.driver and if 'no such window' error occurs
            """
            Communicator.show_message(f"Error occurred while scraping. Error: {str(e)}")


        finally:
            try:
                Communicator.show_message("Closing the driver")
                self.driver.close()
                self.driver.quit()
            except:  # if browser is always closed due to error
                pass

            Communicator.end_processing()
            Communicator.show_message("Now you can start another session")



