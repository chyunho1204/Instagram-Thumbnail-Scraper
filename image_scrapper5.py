import csv
import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
from Keys import IG_USERNAME, IG_PASSWORD

username = IG_USERNAME
password = IG_PASSWORD

url = "https://www.instagram.com"

def setup_driver():
    global chrome
    chrome = webdriver.Chrome()

def login(username, password):
    chrome.get(url)
    time.sleep(4)
    usern = chrome.find_element(By.NAME, "username")
    usern.send_keys(username)
    passw = chrome.find_element(By.NAME, "password")
    passw.send_keys(password)
    passw.send_keys(Keys.RETURN)
    time.sleep(6)

    try:
        not_now_btn = WebDriverWait(chrome, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "_acan"))
        )
        not_now_btn.click()
        time.sleep(2)
    except:
        pass

def save_to_csv(user, post_url, img_name, post_date):
    file_path = f"{user}_posts.csv"
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Post URL", "Image Name", "Post Date"])
        writer.writerow([post_url, img_name, post_date])

def save_first_image(user):
    chrome.get(f"https://www.instagram.com/{user}/")
    time.sleep(4)

    if not os.path.isdir(user):
        os.mkdir(user)

    seen_posts = set()
    count = 1
    last_height = chrome.execute_script("return document.body.scrollHeight")

    while True:
        try:
            posts = chrome.find_elements(By.CLASS_NAME, "x1lliihq")

            for post in posts:
                try:
                    html = post.get_attribute("outerHTML")
                    soup = bs(html, 'html.parser')
                    
                    post_date = ""
                    
                    post_tag = soup.find("a")
                    if post_tag is None:
                        continue
                    
                    img_tag = soup.find("img")
                    if not img_tag:
                        continue
                    
                    img_url = img_tag["src"]
                    post_url = "https://www.instagram.com" + post_tag["href"]
                    img_name = f"post_{count}.jpg"
                    
                    if img_url in seen_posts:
                        continue

                    response = requests.get(img_url)
                    with open(f"{user}/{img_name}", "wb") as f:
                        f.write(response.content)
                    
                    try:
                        chrome.execute_script("window.open('');")
                        chrome.switch_to.window(chrome.window_handles[-1])
                        chrome.get(post_url)
                        time.sleep(2)
                        post_html = chrome.page_source
                        post_soup = bs(post_html, 'html.parser')
                        time_elem = post_soup.find("time")
                        if time_elem and "datetime" in time_elem.attrs:
                            post_date = time_elem["datetime"]
                            post_date = post_date[:10]
                        chrome.close()
                        chrome.switch_to.window(chrome.window_handles[0])
                    except Exception as e:
                        print(f"Error retrieving post date for post {count}: {e}")
                        post_date = ""
                    
                    save_to_csv(user, post_url, img_name, post_date)
                    
                    seen_posts.add(img_url)
                    print(f"Saved {img_name} and logged its details.")
                    count += 1
                    
                except Exception as e:
                    print(f"Error saving post {count}: {e}")
                    continue

            chrome.execute_script("window.scrollTo(0, document.body.scrollHeight);") #scroll down
            time.sleep(3)
            new_height = chrome.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("Reached the end of the page.")
                break
            last_height = new_height

        except Exception as e:
            print(f"Error during scrolling: {e}")
            break

if __name__ == "__main__":
    setup_driver()
    login(username, password)
    companies = [] #desired companies
    for company in companies:
        save_first_image(company)  
    chrome.quit()
x
