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

terms = ["Mehran Modiri",
         'Akbar Abdi',
         'Katayun riahi',
         'Taraneh alidoosti',
         'Angelina jolie',
         'ali daei',
         'Morgan freeman',
         'Keira nightly',
         'jane seymour',
         'Sacha baron cohen',
         ]

# Number of images to be downloaded
NUMBER_IMAGES = 100

# Starting a WebDriver
DRIVER_PATH = "./google_drive/chromedriver.exe"
service = webdriver.chrome.service.Service(executable_path=DRIVER_PATH)
wd = webdriver.Chrome(service=service)


# Searching for a particular phrase & get the image links
def search_and_download(search_term: str, number_of_required_images: int, wd: webdriver,
                        sleep_between_interactions: int = 2.5, target_path='./images'):
    target_folder = os.path.join(target_path, '_'.join(search_term.lower().split(' ')))
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

    # build the google query
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"
    # search_url = 'https://www.shutterstock.com/fr/search/{q}?tbm=isch&safe=off&q={q}&gs_l=img&oq={q}'
    # load the page
    wd.get(search_url.format(q=search_term))

    image_count = 0

    while image_count < number_of_required_images:
        wd.execute_script("window.scrollBy(0,10000)")
        try:
            wd.find_element(By.CSS_SELECTOR, '.mNsIhb').click()
        except:
            continue

        thumbnail_results = wd.find_elements(By.CSS_SELECTOR, 'img.YQ4gaf')

        ii = 0
        for img in thumbnail_results:
            if image_count < number_of_required_images:
                ii += 1
                print('Iteration in For loop : ' + str(ii))
                # extract image url
                img_url = img.get_attribute('src')
                image_download = persist_image(target_folder, img_url, '_'.join(search_term.lower().split(' ')) + '_' + str(image_count))
                if image_download == 1:
                    image_count += 1

    print(f'number of found images: {image_count} ')
    return 1


# Downloading the images
def persist_image(folder_path: str, url: str, file_name: str):
    try:
        image_content = requests.get(url).content
    # except Exception as e:
    except:
        # print(f"ERROR - Could not download {url} - {e}")
        print(f"ERROR - Could not download")
        return 0
    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        if max(image.size[0], image.size[1]) < 300:
            return 0
        # TODO: Check the size of the image
        file_path = os.path.join(folder_path, file_name + '.jpg')
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
        # print(f"SUCCESS - saved {url} - as {file_path}")
        text_file_path = os.path.join(folder_path, file_name + '.txt')
        open(text_file_path, 'a').close()
        print(f"SUCCESS - saved ")
        return 1
    # except Exception as e:
    except:
        # print(f"ERROR - Could not save {url} - {e}")
        print(f"ERROR - Could not save")
        return 0


# Execute the function to download the images
for search_term in terms:
    print('search for: ' + search_term)
    needed_pics_num = int(NUMBER_IMAGES / len(terms))
    print('needed num of pics : ' + str(needed_pics_num))
    search_and_download(
        search_term=search_term,
        number_of_required_images=needed_pics_num,
        wd=wd
    )
    res = []
wd.close()
