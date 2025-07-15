from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

try:
    print("[BOT] Visiting login page...")

    driver.get("http://web:5000/login")  # не localhost!

    wait = WebDriverWait(driver, 10)
    username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    password_input = driver.find_element(By.NAME, "password")

    username_input.send_keys("admin")
    password_input.send_keys("admin123")

    driver.find_element(By.XPATH, "//input[@type='submit']").click()

    print("[BOT] Logged in. Visiting main page...")

    main_url = "http://web:5000/"
    print(f"[BOT] Main URL is: {main_url!r}")
    driver.get(main_url.strip())

    while True:
        time.sleep(5)
        print("[BOT] Refreshing comments page...")
        driver.refresh()

except Exception as e:
    print(f"[BOT ERROR] {e}")

finally:
    driver.quit()
