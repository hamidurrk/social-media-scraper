import os, requests, sys, re, psutil, subprocess, time
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def check_internet_connection():
    try:
        response = requests.get("https://www.google.com", timeout=5)
        if response.status_code == 200:
            return True  
    except requests.RequestException:
        pass  
    return False  

def is_firefox_running():
    for proc in psutil.process_iter():
        if "firefox" in proc.name().lower():
            return True
    return False

def int_from_string(input_string):
    input_string = input_string.replace(',', '')  # remove commas
    match = re.search(r'(\d+(?:\.\d+)?)(K|M|B)?', input_string)
    if match:
        value = float(match.group(1))
        suffix = match.group(2)
        if suffix == 'K':
            value *= 1000
        elif suffix == 'M':
            value *= 1000000
        elif suffix == 'B':
            value *= 1000000000
        return int(value)
    else:
        integers = re.findall(r'\d+', input_string)
        if not integers:
            return None
        return int(integers[0])

def retain_specific_classes(page_html, specified_classes):
    soup = BeautifulSoup(page_html, 'html.parser')

    elements_to_retain = soup.find_all(class_=specified_classes)
    print(elements_to_retain)
    
    for element in elements_to_retain:
        classes_to_keep = set(element.get('class', [])) & set(specified_classes)
        element['class'] = classes_to_keep

    elements_to_remove = [element for element in soup.find_all() if element not in elements_to_retain]
    for element in elements_to_remove:
        element.decompose()

    modified_html = soup.prettify()
    return modified_html

def parse_facebook_date(date_str):
    date_format = "%A %d %B %Y at %H:%M"
    return datetime.strptime(date_str, date_format)

def custom_strftime(date_obj):
    # Custom date format without leading zeroes for the day of the month
    date_format = "%A %-d %B %Y at %H:%M"
    
    # For Windows compatibility, use an alternative approach
    if os.name == 'nt':
        date_format = date_format.replace('%-d', str(date_obj.day))
    
    return date_obj.strftime(date_format)

def create_facebook_date(date_obj):
    return custom_strftime(date_obj)

def compare_dates(date_str1, date_str2):
    date1 = datetime.strptime(date_str1, "%A, %b %d, %Y")
    date2 = datetime.strptime(date_str2, "%m/%d/%Y")
    return date1.date() == date2.date()

def load_info(file_path):
    scraped_dates = set()
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            for line in file:
                scraped_dates.add(line.strip())
    return scraped_dates

def save_info(scraped_dates, file_path):
    with open(file_path, "a") as file:
        for date in scraped_dates:
            file.write(date + "\n")
            
def clear_last_lines(x):
    for _ in range(x):
        sys.stdout.write("\033[F")  
        sys.stdout.write("\033[K")  
        
def gen_prompt(message, value=70, char="-"):
    wrt = " " + message + " "
    sys.stdout.write(f"{wrt.center(value, char)}")
    sys.stdout.flush()
    sys.stdout.write("\n")

def download_image(url, filename):
    try:
        response = requests.get(url)
        with open(filename, "wb") as f:
            f.write(response.content)
        # return f"Article {article_no}"
    except Exception as e:
        return f"Failed to download {filename}: {e}"

def download_images(image_urls, folder_path, tags):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print("Download started...")
        # sys.stdout.write("\n")

    with ThreadPoolExecutor(max_workers=20) as executor:  
        for url, tag in zip(image_urls, tags):
            filename = os.path.join(folder_path, tag)
            executor.submit(download_image, url, filename)
            
        # for i, url in enumerate(image_urls, 1):
        #     filename = os.path.join(folder_path, f"article_{i}.jpg")
        #     executor.submit(download_image, url, filename)
        # print(f"{len(image_urls)} articles downloaded")
    # sys.stdout.write(f"{len(image_urls)} articles")
    # sys.stdout.write("\033[K")  
    # sys.stdout.write("\033[F")  
    # sys.stdout.write("\033[K")

def convert_datestr_to_var(selected_date):
    day, month, year = map(int, selected_date.split('/'))
    return day, month, year

def validate_date(date_str):
    date_pattern = r"\d{2}/\d{2}/\d{4}"
    
    if not re.match(date_pattern, date_str):
        return False, "Invalid date format. Please use the format dd/mm/yyyy."
    else:
        try:
            datetime.strptime(date_str, "%d/%m/%Y")
            return True, None  # Date is valid
        except ValueError:
            return False, "Invalid date. Please enter a valid date."

def date_to_timestamp(input_date):
    min_combined_datetime = datetime.combine(input_date, datetime.min.time())
    max_combined_datetime = datetime.combine(input_date, datetime.max.time())

    min_timestamp = int(min_combined_datetime.timestamp() * 1000)  
    max_timestamp = int(max_combined_datetime.timestamp() * 1000)  
    return min_timestamp, max_timestamp

def run_firefox():
    bat_file_path = os.path.join(BASE_DIR, "start_firefox.bat")
    subprocess.run(bat_file_path, shell=True)
    if is_firefox_running():
        gen_prompt("Firefox is Running")
    else:
        print("Error: Firefox is not running")
        
def is_open(driver, url):
    current_url = driver.current_url
    
    if current_url == url:
        return True
    else:
        return False
    
def loading(i, total):
    progress = (i / total) * 100
    sys.stdout.write('\r')
    sys.stdout.write("Poke Progress: | %-50s | %0.2f%% (%d poked)" % ('█' * int(progress/2), progress, i))
    sys.stdout.flush()

def random_wait(t):
    min_time = t - 1
    max_time = t + 2
    if min_time < 0:
        min_time = 0.1
    time.sleep(random.uniform(min_time, max_time))

# def wait(duration):
#     num_iterations = 100
#     time_interval = (duration-1) / num_iterations

#     with tqdm(total=num_iterations, desc="Loading", unit="iteration", ncols=100) as pbar:
#         for _ in range(num_iterations):
#             time.sleep(time_interval)
#             pbar.update(1)
#     print("\n")
    
