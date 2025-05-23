import time

import pytest
from playwright.sync_api import sync_playwright
from faker import Faker
from sqlalchemy.testing.plugin.pytestplugin import pytest_addoption

faker = Faker(locale="es_ES")
accounts = []
for i in range(20):
    accounts.append([
        faker.first_name(),
        faker.last_name(),
        faker.phone_number(),
        faker.email(),
        faker.password(length=12, special_chars=True, upper_case=True, lower_case=True) + "@"
    ])


@pytest.fixture(scope="module")
def browser():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    yield page
    browser.close()
    playwright.stop()


@pytest.mark.parametrize("fn, ln, pn, em, ps", accounts)
def test_signup(browser, fn, ln, pn, em, ps):
    browser.goto("http://127.0.0.1:8000/auth/sign-up")
    first_name = browser.wait_for_selector('#first-name')
    last_name = browser.wait_for_selector('#last-name')
    phone_number = browser.wait_for_selector('#phone')
    email = browser.wait_for_selector('#email')
    password = browser.wait_for_selector('#password')
    confirm_password = browser.wait_for_selector('#confirm-password')

    first_name.type(fn)

    last_name.type(ln)

    phone_number.type(pn)

    email.type(em)

    password.type(ps)

    confirm_password.type(ps)

    browser.wait_for_selector('#submit-btn').click()

    assert browser.url == "http://127.0.0.1:8000/auth/sign-in"

@pytest.mark.parametrize("fn, ln, pn, em, ps", accounts)
def test_signin(browser, fn, ln, pn, em, ps):

    browser.goto("http://127.0.0.1:8000/auth/sign-in")
    email = browser.wait_for_selector('#email')
    password = browser.wait_for_selector('#password')

    email.type(em)
    password.type(ps)

    browser.wait_for_selector('body > div > form > button').click()

    assert browser.url == "http://127.0.0.1:8000/account/"

    logout_btn = browser.wait_for_selector('body > header > nav > a:nth-child(3)')
    logout_btn.click()

    assert browser.url == "http://127.0.0.1:8000/"