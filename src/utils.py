import os, requests, sys, re, psutil, subprocess
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

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
    integers = re.findall(r'\d+', input_string)
    if not integers:
        return None
    extracted_int = int(integers[0])
    return extracted_int

def retain_specific_classes(page_html, specified_classes):
    # Parse the HTML content
    soup = BeautifulSoup(page_html, 'html.parser')

    # Find all elements with specified classes
    elements_to_retain = soup.find_all(class_=specified_classes)

    print(elements_to_retain)
    
    # Remove all classes from the elements except the specified ones
    for element in elements_to_retain:
        classes_to_keep = set(element.get('class', [])) & set(specified_classes)
        element['class'] = classes_to_keep

    # Remove all other elements
    elements_to_remove = [element for element in soup.find_all() if element not in elements_to_retain]
    for element in elements_to_remove:
        element.decompose()

    # Convert the modified soup back to HTML string
    modified_html = soup.prettify()

    return modified_html

def compare_dates(date_str1, date_str2):
    # Parse the dates
    date1 = datetime.strptime(date_str1, "%A, %b %d, %Y")
    date2 = datetime.strptime(date_str2, "%m/%d/%Y")
    
    # Compare the dates
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

def download_image(url, filename, article_no):
    try:
        response = requests.get(url)
        with open(filename, "wb") as f:
            f.write(response.content)
        return f"Article {article_no}"
    except Exception as e:
        return f"Failed to download {filename}: {e}"

def download_images(image_urls, folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print("Download started...")
        # sys.stdout.write("\n")

    with ThreadPoolExecutor(max_workers=20) as executor:  
        for i, url in enumerate(image_urls, 1):
            filename = os.path.join(folder_path, f"article_{i}.jpg")
            executor.submit(download_image, url, filename, i)
        print(f"{len(image_urls)} articles downloaded")
    #     sys.stdout.write(f"{len(image_urls)} articles")
    # sys.stdout.write("\033[K")  
    # sys.stdout.write("\033[F")  
    # sys.stdout.write("\033[K")

def convert_datestr_to_var(selected_date):
    day, month, year = map(int, selected_date.split('/'))
    return day, month, year

def validate_date(date_str):
    # Define a regular expression pattern for the dd/mm/yyyy format
    date_pattern = r"\d{2}/\d{2}/\d{4}"
    
    # Check if the date string matches the pattern
    if not re.match(date_pattern, date_str):
        return False, "Invalid date format. Please use the format dd/mm/yyyy."
    else:
        try:
            # Parse the date string using the expected format
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