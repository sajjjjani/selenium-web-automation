import pytest

from pages.module_page import ModulePage


# 5 module tests. Each opens the module, verifies its content, then
# actually performs the module's add/create task.
MODULES = [
    "/clients",       # creates a new customer
    "/quotations",    # fills a new quotation (customer + item)
    "/invoices",      # fills a new invoice (customer + item)
    "/payments",      # switches the receivables/payables filter
    "/products",      # creates a new product
]


@pytest.mark.parametrize("url", MODULES)
def test_module(driver, url):
    page = ModulePage(driver)
    page.open(url)  # navigate + verify heading, button, table
    page.add(url)   # perform the module's add/create task
