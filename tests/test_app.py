import time

import pytest
from playwright.sync_api import sync_playwright
from faker import Faker


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


# @pytest.mark.parametrize("fn, ln, pn, em, ps", accounts)
# def test_qrgenerate_and_delete(browser, fn, ln, pn, em, ps):
#     browser.goto("http://127.0.0.1:8000/auth/sign-in")
#     browser.wait_for_selector("#email").type(em)
#     browser.wait_for_selector("#password").type(ps)
#     browser.wait_for_selector('body > div > form > button').click()
#
#     assert browser.url == "http://127.0.0.1:8000/account/"
#
#     browser.goto("http://127.0.0.1:8000/qrcode/urlgen")
#     browser.wait_for_selector("input[name='url']").type("https://example.com")
#     browser.wait_for_selector("button[type='submit']").click()
#     browser.wait_for_url("**/qrcode/view/**", timeout=5000)
#     qr_url = browser.url
#     assert "/qrcode/view/" in qr_url
#     qr_id = qr_url.split("/")[-1]
#     print(f"Generated QR ID: {qr_id}")
#
#     # Go back to account page to verify it's listed
#     browser.goto("http://127.0.0.1:8000/account/")
#     browser.wait_for_selector(f"a[href='/qrcode/view/{qr_id}']")
#
#     # Now delete it
#     browser.goto(f"http://127.0.0.1:8000/qrcode/remove/{qr_id}")
#     assert browser.url == "http://127.0.0.1:8000/account/"
#
#     # Optional: make sure it's gone
#     page_content = browser.content()
#     assert f"/qrcode/view/{qr_id}" not in page_content
#
#     # Logout
#     browser.goto("http://127.0.0.1:8000/auth/logout")
#     assert browser.url == "http://127.0.0.1:8000/"