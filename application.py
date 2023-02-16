import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By



def fetch_image_urls(query: str, max_links_to_fetch: int, wd: webdriver, sleep_between_interactions: int = 1) -> 'list[str]':
    '''Return a list of URLs of query from duckduckgo.com'''

    def scroll_to_end(wd) -> None:
        '''Scroll the page to the end.'''
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

    # building the duckduckgo query
    search_url = 'https://duckduckgo.com/?q={q}&t=newext&atb=v313-1&iax=images&ia=images'

    # load the page
    wd.get(search_url.format(q=query))

    image_urls = set()
    Run = True
    while Run:
        
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail = wd.find_elements(By.CSS_SELECTOR, ".tile--img__img")
        print(f'Found {len(thumbnail)} results')

        # try to click every thumbnail such that we can get the real image behind it
        for image in thumbnail:
            try:
                image.click()
                print('Clicked on thumbnail')
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls
            actual_image = wd.find_element(By.CSS_SELECTOR, '.js-image-detail-link')
            link = actual_image.get_attribute('href')
            image_urls.add(link)
            print('Link Added Success')

            if len(image_urls) == max_links_to_fetch:
                Run = False
                break


    print(f"Found: {len(image_urls)} image links, done!")
    return image_urls


def persist_image(folder_path: str, url: str) -> None:
    '''Store a image URL to given Path'''

    try:
        image_content = requests.get(url).content

    except ConnectionError:
        print(f"ERROR - Could not download {url} - Invalid URL")

    try:
        file_name = url.split('/')[-1]
        path = os.path.join(folder_path, file_name)
        with open(path, 'wb') as f:
            f.write(image_content)
        print(f"SUCCESS - saved {url} - as {path}")

    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")


def search_and_download(query: str, driver_path: str, target_path='.\images', nimages=10) -> None:
    
    target_folder = os.path.join(target_path, '_'.join(query.lower().split(' ')))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
        print(f'Folder Created {target_path}')

    with webdriver.Firefox(firefox_binary=r'C:\Program Files\Mozilla Firefox\firefox.exe') as firefox:
        links = fetch_image_urls(search_term, nimages, wd=firefox, sleep_between_interactions=0.5)
        print('Retrieved all links successfully.')
        
    for link in links:
        persist_image(target_folder, link)



# How to execute this code
# Step 1 : pip install selenium, pillow, requests
# Step 2 : make sure you have firefox installed on your machine
# Step 3 : Check your firefox version (Type `about:support` in the address bar to check version)
# Step 4 : Download the gecko driver from here  "https://github.com/mozilla/geckodriver/releases" depending on your OS
# Step 5 : put it inside the same folder of this code


DRIVER_PATH = r'geckodriver.exe'

search_term = input('Search: ')

# num of images you can pass it from here  by default it's 10 if you are not passing
#number_images = 50
search_and_download(query = search_term, driver_path = DRIVER_PATH, nimages = 10)