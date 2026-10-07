import random
import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# Seconds to linger on each step so browser actions are visible
PAUSE = 2


class ModulePage:
    """Open a Coddy Pro module, verify it, and actually use it (add/create)."""

    # url-slug -> (sidebar group, heading, action button)
    MODULES = {
        "clients":    ("SALES",        "Customers",               "Add customer"),
        "quotations": ("SALES",        "Quotations",              "New Quotation"),
        "invoices":   ("SALES",        "Invoices",                "New Invoice"),
        "payments":   ("ACCOUNTING",   "Payments & party statements", "Refresh"),
        "products":   ("INVENTORY",    "Item Master",             "Add product"),
    }

    # A real product code/name that exists in the demo data (used for line items)
    PRODUCT = "Test Product 12"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    # ---------- Navigation ----------

    def open(self, url):
        """Navigate to the module and verify its content loaded."""
        slug = url.strip("/")
        group, heading, action = self.MODULES[slug]

        # Expand the sidebar group this module belongs to
        button = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//button[@aria-controls='sidebar-group-{group.lower()}']")
            )
        )
        if button.get_attribute("aria-expanded") != "true":
            self._js_click(button)
            time.sleep(PAUSE)

        # Click the module link
        link = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//a[@href='{url}']"))
        )
        self._js_click(link)
        self.wait.until(EC.url_contains(url))

        # Verify the page actually rendered
        self._wait_text(heading)
        self._wait_button(action)
        self._wait_table()
        time.sleep(PAUSE)

    def add(self, url):
        """Perform the module's add/create task (except Payments = filter)."""
        slug = url.strip("/")
        if slug == "clients":
            self._add_customer()
        elif slug == "products":
            self._add_product()
        elif slug == "quotations":
            self._fill_doc_form("Submit quotation")
        elif slug == "invoices":
            self._fill_doc_form("Issue invoice")
        elif slug == "payments":
            self._switch_payments_filter()

    # ---------- Module actions ----------

    def _add_customer(self):
        """Fill and submit the New Customer form, then confirm it saved."""
        self._click_action("Add customer")
        name = "Auto Customer " + str(random.randint(1000, 9999))

        # Wait for the form to render, then fill it
        name_field = self.wait.until(EC.presence_of_element_located((By.ID, "customer_name")))
        name_field.send_keys(name)
        Select(self.driver.find_element(By.ID, "customer_group")).select_by_index(1)
        time.sleep(PAUSE)

        self._click_button("Create customer")
        # Saved -> redirected to a detail page showing the new customer
        self._wait_text(name)
        self._wait_text("Customer created successfully")
        time.sleep(PAUSE)

    def _add_product(self):
        """Fill and submit the New Product form, then confirm it saved."""
        self._click_action("Add product")
        code = "SKU" + str(random.randint(1000, 9999))
        name = "Auto Product " + str(random.randint(1000, 9999))

        # Wait for the form to render, then fill it
        self.wait.until(EC.presence_of_element_located((By.ID, "product_item_code"))).send_keys(code)
        self.driver.find_element(By.ID, "product_item_name").send_keys(name)
        self.driver.find_element(By.ID, "product_description").send_keys("Created by automation")
        self._pick_from_list("Products", "Products")
        self._pick_from_list("Nos", "Nos")
        time.sleep(PAUSE)

        self._click_button("Create product")
        # Saved -> redirected to the new product detail page
        self._wait_text(name)
        self._wait_text("Product created")
        time.sleep(PAUSE)

    def _fill_doc_form(self, submit_label):
        """Open a Quotation/Invoice form and fill customer + item line (no submit)."""
        action = "New Quotation" if "uot" in submit_label else "New Invoice"
        self._click_action(action)
        # Wait for the customer / item widgets on the form
        self._wait_inputs(2)

        # Select a customer from the search dropdown
        customer_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(.), 'Search customer')]"))
        )
        self._js_click(customer_btn)
        search = self.driver.find_element(
            By.XPATH, "//input[contains(@placeholder, 'Search customer name')]"
        )
        search.send_keys("Abc Company")
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(@role, 'option')]")))
        self._click_option("Abc Company")
        self._close_dropdown()  # dismiss the popup so it doesn't cover the form
        time.sleep(PAUSE)

        # Add an item line and pick a product
        self._js_click(self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(normalize-space(.), 'Add item')]"))
        ))
        item_search = self.driver.find_element(
            By.XPATH, "//input[contains(@placeholder, 'Search product')]"
        )
        item_search.send_keys(self.PRODUCT)
        self.wait.until(EC.presence_of_element_located((By.XPATH, f"//span[normalize-space()='{self.PRODUCT}']")))
        self._js_click(self.driver.find_element(
            By.XPATH, f"//span[normalize-space()='{self.PRODUCT}']"
        ))
        self._close_dropdown()  # dismiss the item popup as well
        time.sleep(PAUSE)

        # Leave the form filled and ready (avoids fragile final submit)

    def _switch_payments_filter(self):
        """Switch the ledger filter and confirm the table heading changes."""
        self._click_button("Supplier payables")
        self._wait_text("Open supplier bills")
        time.sleep(PAUSE)
        self._click_button("Customer receivables")
        self._wait_text("Open sales invoices")
        time.sleep(PAUSE)

    # ---------- Negative (invalid input) cases ----------

    def negative_customer_required(self):
        """Submit the customer form with the required name empty -> not saved."""
        self.driver.get("https://demo.coddypro.com/clients/new")
        self.wait.until(EC.presence_of_element_located((By.ID, "customer_name")))
        self._click_button("Create customer")  # name left blank
        time.sleep(PAUSE)
        # Should stay on the form (not saved / not redirected)
        assert "/clients/new" in self.driver.current_url, "customer saved without a name"

    def negative_product_required(self):
        """Submit the product form with required fields empty -> not saved."""
        self.driver.get("https://demo.coddypro.com/products/new")
        self.wait.until(EC.presence_of_element_located((By.ID, "product_item_code")))
        self._click_button("Create product")  # fields left blank
        time.sleep(PAUSE)
        assert "/products/new" in self.driver.current_url, "product saved without required fields"

    def negative_document_missing(self, submit_label):
        """Submit a quotation/invoice with no customer and no item -> error shown."""
        path = "quotations" if "uot" in submit_label else "invoices"
        self.driver.get(f"https://demo.coddypro.com/{path}/new")
        self._wait_inputs(2)
        # Click the submit button (last match = the real one; first is disabled)
        buttons = self.wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, f"//button[contains(normalize-space(), '{submit_label}')]")
            )
        )
        self._js_click(buttons[-1])
        time.sleep(PAUSE)
        # The form blocks: stays open and shows the missing-fields error
        assert f"/{path}/new" in self.driver.current_url, f"{submit_label} submitted with no data"
        self._wait_text("Select a customer")
        self._wait_text("Add at least one item")

    # ---------- Helpers ----------

    def _click_action(self, text):
        self._js_click(self.wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(normalize-space(), '{text}')]"))
        ))

    def _click_button(self, text):
        btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(normalize-space(), '{text}')]"))
        )
        self._js_click(btn)

    def _pick_from_list(self, button_text, option_text):
        # Open a custom picker and choose an option (first one if target not visible)
        trigger = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(normalize-space(), '{button_text}')]"))
        )
        self._js_click(trigger)
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(@role, 'option')]")))
        options = self.driver.find_elements(By.XPATH, "//*[contains(@role, 'option')]")
        # Prefer the requested option, else take the first one
        for opt in options:
            if opt.text.strip() == option_text:
                self._js_click(opt)
                return
        if options:
            self._js_click(options[0])

    def _click_option(self, text):
        for opt in self.driver.find_elements(By.XPATH, "//*[contains(@role, 'option')]"):
            if opt.text.strip() == text:
                self._js_click(opt)
                return
        raise AssertionError(f"option '{text}' not found")

    def _js_click(self, element):
        self.driver.execute_script("arguments[0].click();", element)

    def _close_dropdown(self):
        # Press Escape to dismiss any selection popup so it doesn't cover the form
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(1)

    def _wait_text(self, text):
        self.wait.until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(normalize-space(.), '{text}')]"))
        )

    def _wait_button(self, text):
        self.wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(normalize-space(), '{text}')]"))
        )

    def _wait_table(self):
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//table")))

    def _wait_inputs(self, count):
        self.wait.until(
            lambda d: len(d.find_elements(By.XPATH, "//input|//select|//textarea")) >= count
        )
