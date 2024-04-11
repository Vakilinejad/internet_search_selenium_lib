# Import the libraries
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import os
import time
import io
import requests
from PIL import Image
import hashlib
import numpy as np
import tqdm
from selenium.common.exceptions import NoSuchElementException

URL = []
# terms, like 'Car damage'
# terms = ['car headlight damage',
#                 'car headlight broken',
#                 'car backlight damage',
#                 'car backlight broken',
#                 'car damage deformed',
#                 'car damage dent',
#                 'car damage missing part',
#                 'car damage scratch',
#                 'car defect scratch',
#                 'car dent',
#                 'car fault rust',
#                 'car front glass damage',
#                 'car missing part',
#                 'car rust',
#                 'car scratch',
#                 'car side glass damage',
#                 'car varnish defect',
#                 'car rust damage',
#                 'car scratch damage',
#                 'car damage scratch',
#                 'car defect dent',
#  ]
terms = ["a group of people",
         'a boy and a girl talking',
         'classmates',
         ]

# Number of images to be downloaded
NUMBER_IMAGES = 200

# Starting a WebDriver
DRIVER_PATH = "./google_drive/chromedriver.exe"
service = webdriver.chrome.service.Service(executable_path=DRIVER_PATH)
# wd = webdriver.Chrome(executable_path=DRIVER_PATH)
# wd.set_page_load_timeout(100)
# options = Options()
# # service = Service(executable_path=DRIVER_PATH)
# wd = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)
#
# # Set timeouts
# wd.set_page_load_timeout(30)
# wd.set_script_timeout(30)

wd = webdriver.Chrome(service=service)

# Searching for a particular phrase & get the image links
def fetch_image_urls(query: str, max_links_to_fetch: int, wd: webdriver, sleep_between_interactions: int = 2.5):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

    # build the google query
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"
    # search_url = 'https://www.shutterstock.com/fr/search/{q}?tbm=isch&safe=off&q={q}&gs_l=img&oq={q}'
    # load the page
    wd.get(search_url.format(q=query))

    images = set()
    # image_urls = []
    image_count = 0
    results_start = 0

    while image_count < NUMBER_IMAGES:
        # scroll_to_end(wd)
        wd.execute_script("window.scrollBy(0,10000)")
        try:
            # wd.find_element_by_css_selector('a[data-hveid="CAEQAA"]')
            # wd.find_element_by_link_text('Images').click()

            # wd.find_element_by_css_selector('.mNsIhb').click()
            wd.find_element(By.CSS_SELECTOR, '.mNsIhb').click()
        except:
            continue

        # get all image thumbnail results
        # thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        thumbnail_results = wd.find_elements(By.CSS_SELECTOR, 'img.YQ4gaf')
        # thumbnail_results = wd.find_elements_by_css_selector('img.YQ4gaf')
        # thumbnail_results = wd.find_elements_by_css_selector("img")
        ii=0
        for img in thumbnail_results:
            ii+=1
            print('Iteration in For loop : ' + str(ii))
            # extract image url
            img_url = img.get_attribute('src')
            # print(img_url)
            images.add(img_url)

        image_count = len(images)
        print('number of found images: ' + str(image_count))
        # if len(images) < NUMBER_IMAGES:
        #     try:
        #         wd.find_element_by_xpath('//a/span[text()="Suivant"]').click()
        #     except NoSuchElementException:
        #         break

    return images


# Downloading the images
def persist_image(folder_path: str, url: str):
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        file_path = os.path.join(folder_path, hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
        print(f"SUCCESS - saved {url} - as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")

# Define a function to get the URL and download the image
def search_and_download(search_term: str, driver_path: str, target_path='./images', number_images=5):
    target_folder = os.path.join(target_path, '_'.join(search_term.lower().split(' ')))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # with webdriver.Chrome(executable_path=driver_path) as wd:
    with webdriver.Chrome(service=service) as wd:
        res = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=1.5)
        print(res)
        print(f"Found: {len(res)} search results. Extracting links from {0}:{len(res)}")

    # import datetime
    # now = datetime.datetime.now().strftime("ulrs_%Y%m%d%H%M%S")
    # url_file = now + ".txt"
    # with open(url_file, "w") as f:
    #     f.write(str(res))

    if res is not None:
        # non_repeated_url = res[URL[np.searchsorted(URL, res)] != res]
        # non_repeated_url = res[~np.in1d(res, URL)]
        # non_repeated_url = filter(lambda i: i not in URL, res)
        for elem in res:
            persist_image(target_folder, elem)
    else:
        print(f"Failed to return links for term: {search_term}")

    # URL.append(non_repeated_url)
    # non_repeated_url=[]

# Execute the function to download the images
for search_term in terms:
    print('search for: ' + search_term)
    needed_pics_num = int(NUMBER_IMAGES/len(terms))
    print('needed num of pics : '+str(needed_pics_num))
    search_and_download(
        search_term=search_term,
        driver_path=DRIVER_PATH,
        # number_images=NUMBER_IMAGES
        number_images=needed_pics_num
    )
    res = []
wd.close()

# Download with requests

# search_url = 'https://www.carizy.com/voiture-occasion?q=&hPP=21&idx=CarAlgoliaIndex_prod&p=0&searchtext=&is_v=1'
# response = requests.get('https://api.github.com')
#
# if response.status_code == 200:
#     print('Allowed to access!')
# elif response.status_code == 404:
#     print('Not Found.')
# elif response.status_code == 403:
#     print('Forbidden to access!')