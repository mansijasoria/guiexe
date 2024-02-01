from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import sys
import time

class URLProcessor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setupHeadlessBrowser()

    def initUI(self):
        # Layout
        layout = QVBoxLayout()

        # URL Input
        self.urlInput = QLineEdit(self)
        self.urlInput.setPlaceholderText("Paste the URL here")
        self.urlInput.returnPressed.connect(self.processURL)

        # Output Label
        self.outputLabel = QLabel("Output will be shown here", self)

        # Adding widgets to the layout
        layout.addWidget(self.urlInput)
        layout.addWidget(self.outputLabel)

        # Setting the layout
        self.setLayout(layout)

        # Window Configurations
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('URL Processor')

    def setupHeadlessBrowser(self):
        # Selenium headless browser setup
        options = Options()
        options.headless = True
        service = Service("C:/Users/Mansi Jasoria/Desktop/IIT/chromedriver-win64/chromedriver-win64/chromedriver.exe") # Replace with your chromedriver path
        self.browser = webdriver.Chrome(service=service, options=options)

    def processURL(self):
        url = self.urlInput.text()
        self.browser.get(url)

        # Implement the specific data extraction logic here
        extracted_data = self.extractData(url)

        # Display the extracted data
        self.outputLabel.setText(str(extracted_data))

    def extractData(self, url):
        service = Service("C:/Users/Mansi Jasoria/Desktop/IIT/chromedriver-win64/chromedriver-win64/chromedriver.exe")
        driver = webdriver.Chrome(service=service)
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        videos = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.col-lg-12.col-md-16.pad-left.pad-right.u-padding-s-top')))
        video_list = []

        for video in videos:
            # XPath for the title element
            # title_script = 'return document.getElementById("screen-reader-main-title").textContent.trim();'
            # title_text = driver.execute_script(title_script)
            title_text = video.find_element(By.XPATH, '//*[@id="screen-reader-main-title"]/span').text

            # XPath for finding title
            title = video.find_element(By.XPATH, './/h2[@id="publication-title"]/a/span').text
            
            # New XPath for finding journal publication year
            journal_year_script = 'return document.evaluate("//*[@id=\'publication\']/div[2]/div/text()[2]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent.trim();'
            journal_year = driver.execute_script(journal_year_script)

            # XPath for finding authors
            author_buttons = video.find_elements(By.XPATH, '//*[@id="author-group"]/button')
                
            # Variable to store concatenated author names
            all_authors = ""

            for index, button in enumerate(author_buttons, start=1):
                # Click on the author button to open the overlay panel
                button.click()
                
                # Wait for the overlay panel to appear
                overlay_panel_xpath = f'//*[@id="author-group"]/button[{index}]/span/span[1]'
                overlay_panel = wait.until(EC.visibility_of_element_located((By.XPATH, overlay_panel_xpath)))
                
                # Extract the author name from the overlay panel
                author_name = overlay_panel.text

                # Concatenate author names
                all_authors += author_name + ", "
                
                # Close the overlay panel by clicking outside of it (you may need to adjust this depending on the actual page behavior)
                driver.find_element(By.CSS_SELECTOR, 'body').click()

            
            # New XPath for finding indexing agency
            indexing_agency_script = 'return document.getElementById("gh-wm-science-direct").textContent.trim();'
            indexing_agency = driver.execute_script(indexing_agency_script)

            # New XPath for finding DOI
            doi_element = video.find_element(By.XPATH, '//*[@id="article-identifier-links"]/a[1]/span')
            doi = doi_element.text if doi_element else "DOI not found"

            # New XPath for finding article type (adjust the XPath based on the actual structure)
            article_type_element = driver.find_element(By.XPATH, '/html/head/meta[12]')
            # Extract the content attribute of the meta tag
            article_type = article_type_element.get_attribute('content') if article_type_element else "Article type not found"

            # Click "Show More" button and extract the expanded content
            try:
                show_more_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="show-more-btn"]')))
                show_more_button.click()

                # Wait for the expanded content to load
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="banner"]/div[1]/p')))
                
                # Now locate and extract the text content
                element = driver.find_element(By.XPATH, '//*[@id="banner"]/div[1]/p')
                text_content = element.text if element else "Text not found"
                # print(text_content)
            except Exception as e:
                print(f"Error: {e}") 
            
            # XPath for finding text content
            text_content_script = 'return document.evaluate("//*[@id=\'banner\']/div[1]/p/text()[1]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent.trim();'
            text_content = driver.execute_script(text_content_script)

            
            # Remove trailing comma and space
            all_authors = all_authors.rstrip(', ')
            vid_item = {
                'title_text': title_text,
                'title': title,
                'journal_year': journal_year,
                'authors': all_authors,
                'indexing_agency': indexing_agency,
                'doi': doi,
                'article_type': article_type,
                'date_of_publication': text_content
            }
            
            video_list.append(vid_item)


        df = pd.DataFrame(video_list)
        pd.set_option("max_colwidth", None)  # Display full text in DataFrame
        df_transposed = df.set_index('title').transpose()
        print(df_transposed)        
        return df_transposed

    def closeEvent(self, event):
        # Close the browser when the application is closed
        self.browser.quit()
        event.accept()

def main():
    app = QApplication(sys.argv)
    ex = URLProcessor()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
