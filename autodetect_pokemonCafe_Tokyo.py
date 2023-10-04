import requests
from bs4 import BeautifulSoup
import smtplib
import schedule
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC


# Website URL to monitor
url = "https://reserve.pokemon-cafe.jp/reserve/step1"

# Define your email settings
sender_email = "xxxx@gmail.com"
receiver_email = "xxxxx@gmail.com"
# incase you want to send to another email
receiver_email2 = "xxxx@gmail.com"
# password of the sender email
password = "yyyyy"


# Function to check for available spots
def check_availability():
    try:
        # Use Selenium to automate form submission and retrieve the updated page
        service = Service(
            executable_path="/Users/toeyscn/Downloads/chromedriver-mac-x64/chromedriver"
        )
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(
            service=service, options=options
        )  # Specify the path to chromedriver
        driver.get(url)

        # Locate the form element and the select element by name
        form_element = driver.find_element(By.TAG_NAME, "form")
        select_element = form_element.find_element(By.NAME, "guest")

        # Modify this part to select the desired value
        select_element.send_keys(
            "2"
        )  # Replace with the desired option (e.g., "2 people")
        select_element.send_keys(
            Keys.RETURN
        )  # Simulate pressing Enter to submit the form

        # Wait for the page to load and elements to be ready
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".calendar-day-cell"))
        )

        # Check if the updated page indicates availability
        soup = BeautifulSoup(driver.page_source, "html.parser")
        # Find all calendar-day-cell elements
        calendar_cells = soup.find_all("li", class_="calendar-day-cell")

        # Check each calendar cell for availability
        available_slots = []
        for cell in calendar_cells:
            if "full" not in cell.text.lower():
                available_slots.append(cell.text.strip())

        if available_slots:
            send_email_notification(available_slots)
        else:
            print("No available slots found.")

    except StaleElementReferenceException:
        print("Stale Element Reference Exception. Retrying...")
        # Check if the updated page indicates availability
        soup = BeautifulSoup(driver.page_source, "html.parser")
        # Find all calendar-day-cell elements
        calendar_cells = soup.find_all("li", class_="calendar-day-cell")

        # Check each calendar cell for availability
        available_slots = []
        for cell in calendar_cells:
            if "full" not in cell.text.lower():
                available_slots.append(cell.text.strip())

        if available_slots:
            send_email_notification(available_slots)
        else:
            print("No available slots found.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        send_error_notification(str(e))

    finally:
        driver.quit()  # Always quit the driver to close the browser

    print("Finish Running")  # Print "Finish Running" when the function finishes


# Function to send an email notification for errors
def send_error_notification(error_message):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        subject = "Error on Pokemon Cafe Reservation Script"
        body = f"An error occurred: {error_message}"
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(sender_email, receiver_email, message)
        print("Error notification sent!")
        server.quit()
    except Exception as e:
        print(f"Error notification email error: {str(e)}")


# Function to send an email notification for available slots
def send_email_notification(available_slots):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        subject = "New spots available on Pokemon Cafe Reservation(TOKYO)!"
        body = f"New spots are available on the following dates in Tokyo:\n\n{', '.join(available_slots)}\n\nVisit the website to reserve now! https://reserve.pokemon-cafe.jp/reserve/step1"
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(sender_email, receiver_email, message)
        server.sendmail(sender_email, receiver_email2, message)
        print("Email notification sent!")
        server.quit()
    except Exception as e:
        print(f"Email notification error: {str(e)}")


# Schedule the script to run at regular intervals (e.g., every 30 minutes)
schedule.every(5).minutes.do(check_availability)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
