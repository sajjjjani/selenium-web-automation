import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.login_page import LoginPage


URL = "https://demo.coddypro.com"

USERNAME = os.getenv("CODDY_USERNAME")
PASSWORD = os.getenv("CODDY_PASSWORD")


def create_driver():
    """Return a clean Chrome browser with autofill/suggestion popups disabled."""
    options = Options()

    options.add_argument("--disable-autofill")
    options.add_experimental_option(
        "prefs",
        {
            "autofill.profile_enabled": False,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        },
    )

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver


@pytest.fixture(scope="session")
def driver():
    if not USERNAME or not PASSWORD:
        pytest.fail(
            "CODDY_USERNAME and CODDY_PASSWORD environment variables must be set."
        )

    driver = create_driver()
    driver.get(URL)

    LoginPage(driver).login(USERNAME, PASSWORD)

    WebDriverWait(driver, 15).until(EC.url_contains("/dashboard"))
    time.sleep(3)

    yield driver

    driver.quit()