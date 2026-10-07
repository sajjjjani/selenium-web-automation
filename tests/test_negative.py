import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.login_page import LoginPage
from pages.module_page import ModulePage

from conftest import URL, USERNAME, create_driver


# Negative tests show invalid input is correctly rejected.
# Login negative uses its own fresh (logged-out) browser so it can test login failure.


def test_login_wrong_password():
    driver = create_driver()
    try:
        driver.get(URL)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(USERNAME)
        driver.find_element(By.ID, "password").send_keys("WrongPassword")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)  # let the page react, so it's visible for recording
        # Wrong password -> should NOT reach the dashboard
        assert "/dashboard" not in driver.current_url, "dashboard reached with wrong password"
    finally:
        driver.quit()


def test_login_empty_fields():
    driver = create_driver()
    try:
        driver.get(URL)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.ID, "username")))
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()  # nothing filled
        time.sleep(2)
        assert "/dashboard" not in driver.current_url, "dashboard reached with empty fields"
    finally:
        driver.quit()


@pytest.mark.parametrize("submit_label", ["Submit quotation", "Issue invoice"])
def test_document_missing_fields(driver, submit_label):
    ModulePage(driver).negative_document_missing(submit_label)


def test_customer_missing_name(driver):
    ModulePage(driver).negative_customer_required()


def test_product_missing_fields(driver):
    ModulePage(driver).negative_product_required()
