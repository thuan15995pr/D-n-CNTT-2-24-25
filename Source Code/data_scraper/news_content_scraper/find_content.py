import os
import random
import time
import pandas as pd

from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException, StaleElementReferenceException, NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/93.0.961.47 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
]


# In list: mark
# 0: Not scraped yet
# 1: Completed
# 2: Scraped but incomplete
# 3: No corresponding stock
# In stock: mark
# 0: Not completed
# 1: Completed
# 2: Premium content
# 3: Market insight content
def find_content(headline_url):
    # print("started find_content:", time.time())
    # text_url = "https://www.nasdaq.com/articles/" + title
    random_user_agent = random.choice(user_agents)
    headers = {'User-Agent': random_user_agent}
    options = Options()
    options.add_argument(f"user-agent={random_user_agent}")
    options.page_load_strategy = 'none'
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--headless")
    options.add_argument('--log-level=3')
    # Disable image loading
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option(
        'excludeSwitches', ['enable-logging'])
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.cache.disk.enable", False)
    profile.set_preference("browser.cache.memory.enable", False)
    profile.set_preference("browser.cache.offline.enable", False)
    profile.set_preference("network.http.use-cache", False)
    options.profile = profile

    driver = webdriver.Chrome(options=options)
    driver.delete_all_cookies()
    driver.execute_cdp_cmd("Network.setBlockedURLs", {
        "urls": ["*.flv*", "*.png", "*.jpg*", "*.jepg*", "*.gif*"]
    })
    driver.minimize_window()
    try:
        # Set implicit wait
        # driver.implicitly_wait(10)
        driver.get(headline_url)
        driver.execute_script(
            "var videoDiv = document.querySelector('.video__inline'); if (videoDiv) videoDiv.remove();")

        while True:
            time.sleep(0.1)
            # Check if content is loaded and load into body_content
            body_content = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'body__content')))
            date_content = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'jupiter22-c-author-byline__timestamp')))

            print("content Body OK")
            news_text = body_content.text
            date_text = date_content.text
            driver.close()
            return news_text, date_text, 1

    except TimeoutException:
        try:
            # Check if content is loaded and load into body_content
            body_content = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'body__content')))
            alter_time = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'timestamp__date')))
            print("Body OK")
            alter_time_text = alter_time.text
            news_text = body_content.text

            return news_text, alter_time_text, 1

        except TimeoutException:
            try:
                # Find <h1> tags in the page to check for special cases
                # h1_elements = driver.find_elements(By.TAG_NAME, 'h1')
                h1_elements = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, 'h1')))
                print("h1 OK")
                # Find <span> tags in the page to check for special cases
                # span_elements = driver.find_elements(By.CLASS_NAME, 'jupiter22-c-text-link__text')
                span_elements = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'jupiter22-c-text-link__text')))
                print("span OK")
                # Iterate through all found <h1> tags
                for h1 in h1_elements:
                    # Check if each <h1> tag's text is "Access Denied"
                    if h1.text == "Access Denied":
                        print("Warning, Access Denied, Please check your network")
                        driver.close()
                        return "0", "0", 0
                    if h1.text == "Nasdaq+ Exclusive":
                        print("Exclusive content or deleted")
                        driver.close()
                        return "2", "2", 2
                    if h1.text == "News & Insights":
                        print("Exclusive content or deleted")
                        driver.close()
                        return "2", "2", 2

                    # Exit loop after finding a match
                for span in span_elements:
                    if span.text == "MarketInsite":
                        print("Market Insight")
                        driver.close()
                        return "3", "3", 3
            except NoSuchElementException:
                print("No h1 or span found")
                # If no <h1> or <span> tags are found, do nothing
                pass
            print("Time out or wrong url")
            driver.close()
            return "0", "0", 0
    # except ElementClickInterceptedException:
    #     print("button missed")
    #     return 0
    except NoSuchWindowException:
        print("closed window manually")
        driver.close()
        return "0", "0", 0
    except StaleElementReferenceException:
        print("maybe too fast, elements weren't ready")
        driver.close()
        return "0", "0", 0


def title_to_content_new(stock_name):
    # print("started new:", new_time)
    stock_name = str(stock_name)
    title_file_path = "news_contents/" + stock_name + ".csv"
    print(title_file_path)
    if not os.path.isfile(title_file_path):
        # No file storing this stock, return 0
        print("No such file storing this stock:", stock_name)
        return 3
    else:
        try:
            df = pd.read_csv(title_file_path, encoding="utf-8", )
        except UnicodeDecodeError:
            df = pd.read_csv(title_file_path, encoding="ISO-8859-1")
        # print("Loaded df:", time.time())
        for index, row in df.iterrows():
            new_time = time.time()
            headline_url = row["Url"]
            Mark = row["Mark"]
            if Mark == 1 or Mark == 2 or Mark == 3:
                # print("Already downloaded, jump to next")
                continue
            print("now:", stock_name, " -- ", index + 1, r"/", len(df))
            print(headline_url)
            body_text, date_text, flag = find_content(headline_url)
            # print("finished one stock:", time.time())
            # If completed, flag is 1
            print("flag:", flag)
            df.at[index, 'Mark'] = flag
            df.at[index, 'Text'] = body_text
            df.at[index, 'Date'] = date_text

            df.to_csv("news_contents/" + stock_name + ".csv", index=False)
            print("used", str(time.time() - new_time)[:3], "s")
        # If all completed, return 1; if partially completed, return 2
        result = 1 if ((df["Mark"] == 1) | (df["Mark"] == 2) | (df["Mark"] == 3)).all() else 0
        if result == 1:
            print("stock:", stock_name, "finished")
            return 1
        else:
            return 2


def find_title(df, mode="N"):
    if mode == "N" or "R":
        for index, row in df.iterrows():
            stock_name = str(row["Stock_name"])
            if mode == "N":
                if row['Mark'] == 1:
                    # print(row["stock_name"], "has finished")
                    continue
                # print("Now:", stock_name)
                Mark = title_to_content_new(stock_name)
                df.at[index, 'Mark'] = Mark
                df.to_csv("lists/" + list_file_path, index=False)
        return df, 1
    else:
        print("!!! Typed wrong Mode !!!")
        return df, 0


if __name__ == "__main__":
    # Mode = input("Mode(N for new, R for review):")
    inits = input("from which lists:")
    for init in inits:
        list_file_path = 'list_' + init + '.csv'
        if not os.path.isfile("lists/" + list_file_path):
            print("!!! Wrong list_name !!!")
        else:
            list_df = pd.read_csv("lists/" + list_file_path, encoding="utf-8")
            while not list_df['Mark'].isin([1, 3]).all():
                print("need find")
                list_df, list_flag = find_title(list_df)
                if list_flag == 0:
                    break
            print("list_", init, "completed")

    # The parameter passed is the stock symbol
    # Current issue is that if interrupted, we can only start over
