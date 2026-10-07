# Selenium Web Automation

A Selenium + Pytest automation project I built to practice and demonstrate web application testing.

The project automates different workflows in the **Coddy Pro demo ERP application**, including creating customers and products, working with quotations and invoices, switching payment filters, and checking how the application handles invalid or incomplete input.

## What I worked on

I automated the following scenarios:

* Login and dashboard access
* Creating a new customer
* Creating a new product
* Filling out a quotation
* Filling out an invoice
* Switching between payment filters
* Testing login with an incorrect password
* Testing login with empty fields
* Checking required fields in customer and product forms
* Checking validation for incomplete quotation and invoice forms

The project currently contains **11 automated test cases**.

## Tools & Technologies

* Python
* Selenium WebDriver
* Pytest
* Google Chrome
* Page Object Model (POM)
* Git & GitHub

## Project Structure

```text
selenium-web-automation/
│
├── pages/
│   ├── login_page.py
│   └── module_page.py
│
├── tests/
│   ├── test_modules.py
│   └── test_negative.py
│
├── conftest.py
├── requirements.txt
├── .gitignore
└── README.md
```

### `pages/`

Contains the Page Object classes used to interact with the application.

### `tests/`

Contains the actual Pytest test cases.

`test_modules.py` contains the main workflow tests, while `test_negative.py` contains scenarios using incorrect, empty, or incomplete input.

### `conftest.py`

Contains the shared Selenium WebDriver fixture and login setup used by the tests.

## How the automation is organized

I used the **Page Object Model** so that the Selenium interaction logic is kept separate from the test cases.

The tests reuse a common browser fixture and use explicit waits where needed instead of relying only on fixed delays.

For some workflows, the test data is generated dynamically so that records such as customers and products can be created without repeatedly using the same values.

## Running the project

Clone the repository and move into the project directory:

```bash
git clone <repository-url>
cd selenium-web-automation
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### Login credentials

The demo application's login credentials are **not stored in this repository**.

Before running the tests, set them as environment variables:

```bash
export CODDY_USERNAME="your-demo-username"
export CODDY_PASSWORD="your-demo-password"
```

Then run the test suite:

```bash
pytest -v
```

To run only the main module tests:

```bash
pytest tests/test_modules.py -v
```

To run only the negative tests:

```bash
pytest tests/test_negative.py -v
```

To check that all tests are discovered correctly without actually running them:

```bash
pytest --collect-only -q
```

## What I learned from this project

While working on this project, I practiced turning manual test scenarios into automated tests and learned more about:

* Writing reusable Selenium code
* Using the Page Object Model
* Working with explicit waits
* Handling dynamic elements and dropdowns
* Creating positive and negative test scenarios
* Using Pytest fixtures and parameterization
* Managing test data
* Keeping test credentials out of source code
* Organizing an automation project for GitHub

## Current scope

This project focuses mainly on **functional UI automation and basic negative testing**.

It does not currently cover performance testing, security testing, mobile testing, or extensive cross-browser testing.

I plan to continue improving the project as I learn more about test automation and QA practices.
