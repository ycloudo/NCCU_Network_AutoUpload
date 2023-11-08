from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np


class Automation:
    def __init__(self, url, out_dir, upload_dir, hw):
        # load env parameters
        load_dotenv()
        # setting
        self.hw = hw
        self.hwUrl = url
        self.ids = []
        self.out_dir = out_dir
        self.upload_dir = upload_dir
        self.driver = webdriver.Chrome()

    def login(self):
        self.driver.get(self.hwUrl)
        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")

        username_input.send_keys(os.getenv("USERNAME"))
        password_input.send_keys(os.getenv("PASSWORD"))

        login_button = self.driver.find_element(By.XPATH, "//input[@type='submit']")
        login_button.click()

    def downloader(self):
        self.driver.get(self.hwUrl)
        links = self.driver.find_elements(By.XPATH, '//a[contains(text(), "grade")]')
        for link in links:
            # open the link
            link.click()
            # switch to new tab
            self.driver.switch_to.window(self.driver.window_handles[1])
            time.sleep(2)
            # record the student serial number
            serial_element = self.driver.find_element(By.NAME, "eid")
            eid = serial_element.get_attribute("value")
            self.ids.append(eid)
            # click the download button
            iframe = self.driver.find_element(By.XPATH, "//iframe[@id='pdfjs']")
            self.driver.switch_to.frame(iframe)
            download_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "download"))
            )
            download_button.click()
            # exit the iframe
            self.driver.switch_to.default_content()
            # close the tab
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

    def uploader(self):
        score_file = pd.read_csv(self.out_dir)
        self.driver.get(self.hwUrl)
        links = self.driver.find_elements(By.XPATH, '//a[contains(text(), "grade")]')
        for link in links:
            sys_log = ""
            # open the link
            link.click()
            # switch to new tab
            self.driver.switch_to.window(self.driver.window_handles[1])
            time.sleep(2)
            # get the student serial number
            serial_element = self.driver.find_element(By.NAME, "eid")
            eid = serial_element.get_attribute("value")
            sys_log += f"{eid} "

            # choose the according file
            path = self.upload_dir + f"{eid}.pdf"
            upload_input = self.driver.find_element(
                By.XPATH, "//input[@type='file' and @name='retToUpload']"
            )
            sys_log += f"{path} "
            upload_input.send_keys(path)

            # score
            dropdown = Select(self.driver.find_element(By.XPATH, "//select[@name='g']"))
            score = score_file[score_file["eid"] == int(eid)].iloc[0]["score"]
            dropdown.select_by_value(score)
            sys_log += f"{score}"
            time.sleep(1)

            # log
            self.logging(sys_log)

            # upload
            upload_btn = self.driver.find_element(
                By.XPATH, "//input[@type='submit' and @name='submit']"
            )
            upload_btn.click()
            time.sleep(5)

            # close the tab
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

    def close_browser(self):
        self.driver.quit()

    def export_csv(self):
        df = pd.DataFrame({"eid": self.ids, "score": np.empty(len(self.ids))})
        df.to_csv(self.out_dir)

    def logging(self, str):
        with open(f"./logs/{self.hw}.txt", "a") as f:
            f.write(str)
            f.write("\n")


sys_url = "http://hsiaom.nccu.edu.tw:8888/admin/nccuhwapp/entry/?hw__hid__exact=23-NET-T-HW03"


hw = "hw3"
output_dir = f"./homeworks/{hw}/network_{hw}.csv"
upload_dir = (
    "/Users/cloudo/Desktop/研究所/Lab/NetworkTA/NCCU_Network_AutoUpload/homeworks/hw3/files"
)
Auto = Automation(sys_url, output_dir, upload_dir, hw)
Auto.login()
Auto.downloader()
Auto.export_csv()
# Auto.uploader()
Auto.close_browser()