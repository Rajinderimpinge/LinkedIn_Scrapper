import time
import os
import pandas as pd
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options
import pathlib
from selenium import webdriver
from bs4 import BeautifulSoup


class LinkedInScrapper:

    def __init__(self, *args, **kwargs):
        self.mail_id = kwargs.get("mail_id")
        self.mail_password = kwargs.get("mail_password")
        chromedriver_autoinstaller.install()
        self.BASE_URL = "https://www.linkedin.com/"

        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("window-size=1420,1080")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--enable-javascript")
        self.driver = webdriver.Chrome(options=self.options)

        self.df_columns = [
            "description",
            "website",
            "number_of_employee",
            "number_of_emp_on_linkedin",
            "headquarters",
            "specialties",
            "location",
        ]

        self.linked_in = list()

    def linkedIn_login(self):
        login_url = self.BASE_URL + "login"
        print("[%s]" % login_url)

        try:
            self.driver.get(login_url)
            time.sleep(10)
        except Exception as e:
            print(e)
            return False

        # enter email
        try:
            emailInput = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="username"]'))
            )
            emailInput.send_keys(self.mail_id)
            time.sleep(10)
        except Exception as e:
            print("Enter Email Failed :: ", e)
            return False

        # enter password
        try:
            passwordInput = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="password"]'))
            )
            passwordInput.send_keys(self.mail_password)
            time.sleep(10)
        except Exception as e:
            print("Enter Password failed :: ", e)
            return False

        # click on sign in button
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="organic-div"]/form/div[3]/button')
                )
            ).click()
            time.sleep(10)

        except Exception as e:
            print("Click Sign In failed :: ", e)
            return False
        # Js prompt
        # self.driver.execute_script("var a = prompt('Enter Company Name', '');document.body.setAttribute('data-id', a)")
        # get_prompt_data = self.driver.find_element(By.TAG_NAME, 'body').get_attribute('data-id')
        # print ("got prompt data [%s]" % get_prompt_data)
        return True

    def company_data(self, company_name):
        company_url = self.BASE_URL + f"company/{company_name}/about/"
        print("[%s]" % company_url)
        # open next tab code
        self.driver.execute_script(f"window.open('{company_url}','new window')")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        time.sleep(30)
        htmlIn = self.driver.page_source
        soup = BeautifulSoup(htmlIn, "html.parser")
        div_tag = soup.find_all("div", class_="mb6")

        for card in div_tag:
            in_data = self.get_linkedIn_data(card)
            self.linked_in.append(in_data)
        df = pd.DataFrame(self.linked_in, columns=self.df_columns)
        # self.driver.close()
        return df

    def get_linkedIn_data(self, card):
        description = (
            card.find(
                "p",
                class_="break-words white-space-pre-wrap mb5 text-body-small t-black--light",
            )
            .get_text()
            .strip()
        )
        website = (
            card.find("span", class_="link-without-visited-state").get_text().strip()
        )
        number_of_emp = (
            card.find("dd", class_="text-body-small t-black--light mb1")
            .get_text()
            .strip()
        )
        number_of_emp_on_linkedin = (
            card.find("dd", class_="text-body-small t-black--light mb4")
            .get_text()
            .strip()
        )
        headquarters = (
            card.find_all("dd", class_="mb4 text-body-small t-black--light")[2]
            .get_text()
            .strip()
        )
        specialties = (
            card.find_all("dd", class_="mb4 text-body-small t-black--light")[3]
            .get_text()
            .strip()
        )
        linkedIn_data = (
            description,
            website,
            number_of_emp,
            number_of_emp_on_linkedin,
            headquarters,
            specialties,
            headquarters,
        )
        return linkedIn_data


if __name__ == "__main__":
    mail_id = "johnabraham4mb@gmail.com"
    mail_password = "ghumarwin"
    # company_name = 'ford motor company'
    # company_name = "the walt disney company"

    obj = LinkedInScrapper(mail_id=mail_id, mail_password=mail_password)
    login_process = obj.linkedIn_login()
    if login_process:
        while True:
            company_name = input("Enter Company Name :: ")
            if company_name == "q":
                break
            company_name = company_name.replace(" ", "-")
            result = obj.company_data(company_name)
            print(result)
            # status = False
