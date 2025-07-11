import os
import random
import time

import chardet
import pandas as pd

from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException, StaleElementReferenceException, \
    ElementClickInterceptedException, NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/93.0.961.47 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
]


def find_headlines(stock_name, desired_page, list_df):
    # 'aapl'
    file_name = "headlines/" + str(stock_name) + ".csv"
    headlines_url = "https://www.nasdaq.com/market-activity/stocks/" + stock_name + "/news-headlines"
    # Location to store headlines
    random_user_agent = random.choice(user_agents)
    options = Options()
    options.add_argument(f"user-agent={random_user_agent}")
    options.add_argument('--ignore-ssl-error')
    options.add_argument('--ignore-certificate-errors')
    # options.add_argument("--headless")
    round_counter = 0

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Network.setBlockedURLs", {
        "urls": ["*.flv*", "*.png", "*.jpg*", "*.jepg*", "*.gif*"]
    })
    driver.minimize_window()
    now_retry = 0
    max_retries = 3
    headlines = []
    while True:
        if now_retry == max_retries:
            return desired_page
        try:
            driver.get(headlines_url)
            # driver.minimize_window()
            # Set implicit wait
            driver.implicitly_wait(5)

            attempts = 0

            while attempts < 2:
                try:
                    # Set flag to check if access is successful, here checking for logo loading
                    flag_loaded = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'nsdq-logo--default'))
                    )
                    print("Loaded Logo")
                    break
                except NoSuchElementException:
                    attempts += 1
                    print(attempts, "times meet NoSuchElementException, Maybe meet Special Page")
            current_page = 0
            while True:
                headlines = []
                round_counter += 1
                next_pages = WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'pagination__page')))
                exist_next = len(next_pages) > 1
                if desired_page == 9999:
                    print("This stock has been done")
                    break
                if current_page < desired_page:
                    next_page = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, 'pagination__next')))
                    driver.execute_script("arguments[0].click();", next_page)
                    current_page += 1
                    if next_page.get_attribute("disabled") == "true":
                        print("Last page reached.")
                        break
                    continue
                else:
                    # If connection keeps breaking, increase this value, 2s is more stable
                    time.sleep(2)

                # Load headlines
                headlines = WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'quote-news-headlines__item')))

                active_page_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'pagination__page--active')))
                current_page = int(active_page_element.text)

                for headline in headlines:
                    # Get headline date and content
                    # headline_date = headline.find_element(By.XPATH, './/a/span')
                    headline_date = WebDriverWait(headline, 20).until(
                        EC.presence_of_element_located((By.XPATH, './/a/span')))

                    # headline_content = headline.find_element(By.XPATH, './/a/p')
                    headline_content = WebDriverWait(headline, 20).until(
                        EC.presence_of_element_located((By.XPATH, './/a/p')))

                    # headline_url = headline.find_element(By.XPATH, './/a').get_attribute('href')
                    headline_url = WebDriverWait(headline, 20).until(
                        EC.presence_of_element_located((By.XPATH, './/a'))).get_attribute('href')

                    headline_content_cleaned = headline_content.text.replace(u"\u2018", "'").replace(u"\u2019", "'")

                    data = {
                        'Date': [headline_date.text],
                        'Headline': [headline_content_cleaned],
                        'URL': [headline_url]
                    }

                    # Create a DataFrame
                    df = pd.DataFrame(data)
                    # Check if file exists and is not empty
                    file_exists = os.path.isfile(file_name) and os.path.getsize(file_name) > 0
                    # Then decide whether to write column names based on whether the file already exists
                    df.to_csv(file_name, mode='a', index=False, header=not file_exists, encoding='utf-8-sig')
                    list_df.to_csv("lists/" + list_file_path, index=False)
                # Next page button
                next_page = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'pagination__next')))
                # next_page = next_pages[0]
                # Only one page
                if not exist_next:
                    print("Only one page")
                    desired_page = 9999
                    break
                if next_page.get_attribute("disabled") == "true":
                    print("Last page reached.")
                    desired_page = 9999
                    break
                print("current_page:", current_page)
                desired_page = current_page

                # Click the next page button
                driver.execute_script("arguments[0].click();", next_page)
            return desired_page
        except TimeoutException:
            try:
                # Look for <h1> tags in the page to check for special cases
                h2_elements = driver.find_elements(By.CLASS_NAME, 'alert__heading')
                # Exit loop after finding a match
                for h2 in h2_elements:
                    if h2.text.find("trading") != -1:
                        print("time out, finding alerts")
                        print("Alert found")
                        driver.close()
                        desired_page = 9999
                        return desired_page
            except NoSuchElementException:
                print("No Alert")
                # If no <h1> or <span> tags are found, do nothing
                pass
            print("Time out or wrong url")
            driver.close()
            return desired_page
        except ElementClickInterceptedException:
            print("button missed, desired_page:", desired_page)
            return desired_page
        except NoSuchWindowException:
            print("closed window manually, desired_page:", desired_page)
            return desired_page
        except StaleElementReferenceException:
            now_retry += 1
            print("maybe too fast, elements weren't ready, desired_page:", desired_page)
            try:
                WebDriverWait(driver, 20).until(
                    EC.staleness_of(headlines[0])
                )
            except Exception:
                pass
            continue
            # return desired_page


def start_find(list_df):
    for index, row in list_df.iloc[start_row_index:].iterrows():
        print("start: ", row["Stock_name"], "from:", row["Desired_page"])
        if row["Desired_page"] == 9999:
            print("This stock Has been done")
            continue
        # print("index: ", index)
        Desired_page = find_headlines(row['Stock_name'], row['Desired_page'], list_df)
        list_df.at[index, 'Desired_page'] = Desired_page
        print("now desired_page: ", list_df.loc[row.name, 'Desired_page'])
        list_df.to_csv("lists/" + list_file_path, index=False)
        print(list_df)
    return list_df


if __name__ == "__main__":
    # find_headlines("aapl")
    inits = input("from which list:")
    start_row_index = 0
    for init in inits:
        list_file_path = 'list_' + init + '.csv'
        if not os.path.isfile("lists/" + list_file_path):
            print("!!! Wrong list_name !!!")
        else:
            list_df = pd.read_csv("lists/" + list_file_path, encoding="utf-8")
            while not list_df['Desired_page'].isin([9999]).all():
                print("need find")
                list_df = start_find(list_df)
            print("list_", init, "completed")

    # The input parameter is the stock symbol
