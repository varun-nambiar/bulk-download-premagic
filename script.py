import os
import threading
import multiprocessing
from math import ceil
from random import random
import json
import requests
import hmac
import hashlib
import base64
from tqdm import tqdm

# json file with same name
json_file_name = "assets"

folder = f"downloads/{json_file_name}"

# cores = 2
cores = multiprocessing.cpu_count()

if not os.path.exists(folder):
  os.makedirs(folder)

def generateKey(path):
  secret_key = 'Pr3m@g1c'
  # Compute HMAC-SHA1 hash
  hmac_sha1 = hmac.new(secret_key.encode('utf-8'), path.encode('utf-8'), hashlib.sha1).digest()
  # Encode the hash as Base64
  base64_encoded = base64.b64encode(hmac_sha1).decode('utf-8').replace("+","-").replace("/","_")
  return f"https://images.premagic.com/{base64_encoded}/{path}"


def process(index, total, start, end, files, progress_bar):
  # function to print cube of given num
  # @todo - fix total when not all cores are used.
  print(f"{index}/{total}) Processing items {start} to {end}")
  # sleep(random())
  
  for i in range(start, end + 1):
    download_name = files[i]['image_name'].split(".")[0]

    # skip if already exists
    if os.path.exists(f"{folder}/{download_name}.jpg"):
       continue

    dynamic_image_url = files[i]['dynamic_image_url'].split("https://asts.premagic.com/")[1]

    path = f"fit-in/4000x0/filters:quality(100):sharpen(0):attachment({download_name}.jpg):format(jpg)/{dynamic_image_url}"
    url = generateKey(path)

    response = requests.get(url)
    with open(f"{folder}/{download_name}.jpg", "wb") as file:
      file.write(response.content)

    progress_bar.update(1)

  print(f"{index}/{total} Done")


with open(f'{json_file_name}.json', 'r') as file:
  data = json.load(file)


files = list(data['files'].values())
count = len(files)
# count = 500

print(f"Total files: {count}")

perCore = ceil(count/cores)
threads = []
index = 1
progress_bar = tqdm(total=count, desc="Processing")
for start in range(0, count, perCore):
     end = start + perCore - 1
     if end > count - 1:
          end = count - 1

     threads.append(threading.Thread(target=process, args=(index, cores, start, end, files, progress_bar)))
     index = index+1

for thread in threads:
  thread.start()

for thread in threads:
  thread.join()

print("Completed")