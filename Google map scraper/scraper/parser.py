from bs4 import BeautifulSoup
from selenium import webdriver
from .error_codes import ERROR_CODES
from .communicator import Communicator
from .datasaver import DataSaver
from .base import Base
from .common import Common

class Parser(Base):

    def __init__(self, driver) -> None:
        self.driver = driver
        self.finalData = []
        self.comparing_tool_tips = {
            "location": "Copy address",
            "phone": "Copy phone number",
            "website": "Open website",
            "booking": "Open booking link",
        }

    def init_data_saver(self):
        self.data_saver = DataSaver()
    
    def parse(self):
        """Our function to parse the html"""

        """This block will get element details sheet of a business. 
        Details sheet means that business details card when you click on a business in 
        serach results in google maps"""


        infoSheet = self.driver.execute_script(
            """return document.querySelector("[role='main']")""")
        try:
            # Initialize data points
            rating, totalReviews, address, websiteUrl, phone, hours, category, gmapsUrl, bookingLink, businessStatus = (
                None, None, None, None, None, None, None, None, None, None
            )

            html = infoSheet.get_attribute("outerHTML")
            soup = BeautifulSoup(html, "html.parser")

            # Extract rating
            try:
                rating = soup.find("span", class_="ceNzKf").get("aria-label")
                rating = rating.replace("stars", "").strip()
            except:
                rating = None

            # Extract total reviews
            try:
                totalReviews = list(soup.find("div", class_="F7nice").children)
                totalReviews = totalReviews[1].get_text(strip=True)
            except:
                totalReviews = None

            # Extract name
            try:
                name = soup.select_one(".tAiQdd h1.DUwDvf").text.strip()
            except:
                name = None

            # Extract address, website, phone, and appointment link
            allInfoBars = soup.find_all("button", class_="CsEnBe")
            for infoBar in allInfoBars:
                data_tooltip = infoBar.get("data-tooltip")
                text = infoBar.find('div', class_='rogA2c').text.strip()

                if data_tooltip == self.comparing_tool_tips["location"]:
                    address = text
               
                elif data_tooltip == self.comparing_tool_tips["phone"]:
                    phone = text.strip()
               
            # Extract website URL
            try:
                websiteTag = soup.find("a", {"aria-label": lambda x: x and "Website:" in x})
                if websiteTag:
                    websiteUrl = websiteTag.get("href")
            except:
                websiteUrl = None

            # Extract booking link
            try:
                bookingTag = soup.find("a", {"aria-label": lambda x: x and "Open booking link" in x})
                if bookingTag:
                    bookingLink = bookingTag.get("href")
            except:
                bookingLink = None

            # Extract hours of operation
            try:
                hours = soup.find("div", class_="t39EBf").get_text(strip=True)
            except:
                hours = None

            # Extract category
            try:
                category = soup.find("button", class_="DkEaL").text.strip()
            except:
                category = None

            # Extract Google Maps URL
            try:
                gmapsUrl = self.driver.current_url
            except:
                gmapsUrl = None


            # Extract business status
            try:
                businessStatus = soup.find("span", class_="ZDu9vd").findChildren("span", recursive=False)[0].get_text(strip=True)
            except:
                businessStatus = None

            data = {
                "Category": category,
                "Name": name,
                "Phone": phone,
                "Google Maps URL": gmapsUrl,
                "Website": websiteUrl,
                "Business Status": businessStatus,
                "Address": address,
                "Total Reviews": totalReviews,
                "Booking Links": bookingLink,
                "Rating": rating,
                "Hours": hours,
            }

            self.finalData.append(data)

        except Exception as e:
            Communicator.show_error_message(f"Error occurred while parsing a location. Error is: {str(e)}", ERROR_CODES['ERR_WHILE_PARSING_DETAILS'])

    def main(self, allResultsLinks):
        Communicator.show_message("Scrolling is done. Now going to scrape each location")
        try:
            for resultLink in allResultsLinks:
                if Common.close_thread_is_set():
                    self.driver.quit()
                    return

                self.openingurl(url=resultLink)
                self.parse()

        except Exception as e:
            Communicator.show_message(f"Error occurred while parsing the locations. Error: {str(e)}")
            
        finally:
            self.init_data_saver()
            self.data_saver.save(datalist=self.finalData)
