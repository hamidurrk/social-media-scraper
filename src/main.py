from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time, sqlite3, sys, os, hashlib
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from utils import *
from database import *
import traceback

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "data", "dbfiles",'ipp.db')
IMAGE_DOWNLOAD_PATH = os.path.join(BASE_DIR, "data", "indiannationalcongress_img")
conn = sqlite3.connect(DATABASE_PATH)

class FacebookProfileScraper:
    def __init__(self, username, password, browser="CHROME", operating_system="WINDOWS"):
        self.username = username
        self.password = password
        gen_prompt("Facebook Profile Scraper (for research use only)")
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument("--devtools")
        if (browser == "FIREFOX"):
            self.bot = webdriver.Firefox(executable_path=GeckoDriverManager().install(), service_args = ['--marionette-port', '2828', '--connect-existing'], options=firefox_options)
        elif (browser.upper() == "CHROME"):
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
            chrome_install = ChromeDriverManager().install()
            print(chrome_install)
            if operating_system == "UBUNTU":
                self.bot = webdriver.Chrome(executable_path=chrome_install, options=chrome_options)
            elif operating_system == "WINDOWS":
                folder = os.path.dirname(chrome_install)
                chromedriver_path = os.path.join(folder, "chromedriver.exe")
                self.bot = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
        sys.stdout.flush()
        gen_prompt("FacebookProfileScraper initialized", char="#")
        print("\n")
    
    def highlight_element(self, element, color='yellow'):
        bot = self.bot
        original_style = element.__getattribute__('style')
        new_style = f"border: 2px solid {color}; background-color: yellow; {original_style}"
        bot.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, new_style)

    def login(self):
        bot = self.bot
        bot.get(f"https://www.facebook.com/")
        random_wait(1)
        gen_prompt("Navigated to Facebook", char="#")
        try:
            bot.find_element_by_xpath('//*[@id="email"]').send_keys(self.username)
            gen_prompt("Username Entered")
            bot.find_element_by_xpath('//*[@id="pass"]').send_keys(self.password)
            gen_prompt("Password Entered")
            random_wait(1)
            
            bot.find_element_by_xpath('//*[@id="pass"]').send_keys(Keys.RETURN)
            gen_prompt("Login Requested")
            
            print("\n"*4)
        except:
            pass
        
    def navigate_to_profile(self, name, url):
        bot = self.bot
        if not url == bot.current_url:
            bot.get(url)
        gen_prompt("Navigating to " + name, char="#")
    
    def hover_date_element(self, date_hover_element, date_hover_box, retries=1, timeout=0.5):
        bot = self.bot
        for attempt in range(retries):
            try:
                element = WebDriverWait(bot, 2).until(
                    EC.visibility_of_element_located((By.XPATH, date_hover_element))
                )
                
                hover = ActionChains(bot).move_to_element(element)
                hover.perform()
                
                random_wait(timeout)
                
                date_hover_box_element = WebDriverWait(bot, 2).until(
                    EC.visibility_of_element_located((By.XPATH, date_hover_box))
                )
                post_date = date_hover_box_element.text
                post_date_obj = parse_facebook_date(post_date)
                return post_date, post_date_obj
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                random_wait(timeout)
                print("Creating artificial date.")
                last_datetime_obj = parse_facebook_date(get_last_datetime("indiannationalcongress"))
                artificial_date_obj = last_datetime_obj - timedelta(minutes=7)
                artificial_date = create_facebook_date(artificial_date_obj)
                print(f"Artificial date: {artificial_date}")
                return artificial_date, artificial_date_obj
        return None, None
    
    def post_filter(self, filter_element, year: int, month: str, day: int):
        bot = self.bot
        bot.find_element_by_xpath(filter_element).click()
        random_wait(2)
        
        wait = WebDriverWait(bot, 5)
        
        year_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='combobox']//span[text()='Year']")))
        year_dropdown.click()
        random_wait(1)
        year_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@role='option']//span[text()='{year}']")))
        year_option.click()
        random_wait(1)
        
        month_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='combobox']//span[text()='Month']")))
        month_dropdown.click()
        random_wait(1)
        month_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@role='option']//span[text()='{month}']")))
        month_option.click()
        random_wait(1)
        
        day_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='combobox']//span[text()='Day']")))
        day_dropdown.click()
        random_wait(1)
        day_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@role='option']//span[text()='{day}']")))
        day_option.click()
        random_wait(1)
        
        done_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div[3]/div[2]/div/div[2]/div[1]")))
        done_button.click()
        random_wait(3)
    
    def get_likes(self, react_str):
        bot = self.bot
        reactions = {
            "All": 0,
            "Like": 0,
            "Love": 0,
            "Care": 0,
            "Haha": 0,
            "Wow": 0,
            "Sad": 0,
            "Angry": 0
        }
        react_str_element = bot.find_element_by_xpath(react_str)
        reactions["All"] = int_from_string(react_str_element.text)
        return reactions
    
    def get_reacts(self, react_str, react_pop_up, react_pop_up_close):
        bot = self.bot
        reactions = {
            "All": 0,
            "Like": 0,
            "Love": 0,
            "Care": 0,
            "Haha": 0,
            "Wow": 0,
            "Sad": 0,
            "Angry": 0
        }
        react_str_element = bot.find_element_by_xpath(react_str)
        
        try:
            print(react_str_element.text)
            react_str_element.click()
            WebDriverWait(bot, 10).until(
                EC.presence_of_element_located((By.XPATH, f"{react_pop_up}"))
            )
            random_wait(2)
            react_pop_up_element = bot.find_element_by_xpath(react_pop_up)
            child_elements = react_pop_up_element.find_elements_by_xpath('.//div')
        except Exception as e:
            print("React pop-up not found: ", str(e))
            print("Getting the total reacts from the main page")
            random_wait(3)
            wait = WebDriverWait(bot, 1)
            close_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Close' and @role='button']")))
            close_button.click()
            # bot.find_element_by_xpath(react_pop_up_close).click()
            random_wait(2)
            reactions["All"] = int_from_string(react_str_element.text)
            return reactions
        
        for child in child_elements:
            aria_label = child.get_attribute("aria-label")
            if not aria_label == None:
                match = re.match(r'Show ([\d,]+) (people|person) who reacted with (\w+)', aria_label)
                if match:
                    count = int(match.group(1).replace(',', ''))
                    reaction = match.group(3)
                    if reaction in reactions:
                        reactions[reaction] = count
                else:
                    reaction, count = aria_label.split(", ")
                    reactions[reaction] = int_from_string(count)
        if reactions["All"] != sum(reactions.values())-reactions["All"]:
            print("Reactions count mismatch")
            wait = WebDriverWait(bot, 1)
            try:
                react_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='tab' and @aria-haspopup='menu' and @tabindex='0']")))
                react_dropdown.click()
            except:
                pass
            random_wait(2)
            for i in range(1, 10):
                try:
                    label_div = f"/html/body/div[1]/div/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[1]/div/div[1]/div/div/div/div[2]/div[{i}]"
                    react_spans = f"/html/body/div[1]/div/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[1]/div/div[1]/div/div/div/div[2]/div[{i}]/div[1]/span"
                    label_element = bot.find_element_by_xpath(label_div).get_attribute("aria-label")
                    reacts = int_from_string(bot.find_element_by_xpath(react_spans).text)
                    if reacts != None:
                        if not label_element == None:
                            label = label_element.split(" ").pop()
                            reaction, count = label, reacts
                            if reaction in reactions and count != reactions[reaction]:
                                reactions[reaction] = count
                except:
                    break
            for i in range(1, 10):
                try:
                    label_div = f"/html/body/div[1]/div/div/div[1]/div/div[4]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div/div/div/div[1]/div/div[{i}]"
                    drop_react_spans = f"/html/body/div[1]/div/div/div[1]/div/div[4]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div/div/div/div[1]/div/div[{i}]/div[2]/div/div/span"
                    label_element = bot.find_element_by_xpath(label_div).get_attribute("aria-label")
                    reacts = int_from_string(bot.find_element_by_xpath(drop_react_spans).text)
                    if reacts != None:
                        if not label_element == None:
                            label = label_element.split(" ").pop()
                            reaction, count = label, reacts
                            if reaction in reactions and count != reactions[reaction]:
                                reactions[reaction] = count
                except:
                    break
        wait = WebDriverWait(bot, 5)
        # close_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Close' and @role='button']")))
        # close_button.click()
        bot.find_element_by_xpath(react_pop_up_close).click()
        return reactions

    def search_keyword_in_html(self, keyword, html):
        if keyword in html:
            word_index = html.index(keyword)
            word = html[word_index-5:word_index+len(keyword)]
            return word
        return False
        
    def get_html(self, element):
        bot = self.bot
        html = bot.execute_script("return arguments[0].innerHTML;", element)
        return html
    
    def perform_pagedown(self, n):
        bot = self.bot
        for i in range(n):
            ActionChains(bot).send_keys(Keys.PAGE_DOWN).perform()
            random_wait(0.5)
    
    def get_comments_shares_alt(self, comment_share_parent):
        bot = self.bot
        try:
            html = self.get_html(bot.find_element_by_xpath(comment_share_parent))
            comments = self.search_keyword_in_html("comments", html)
            comments = int_from_string(comments)
            shares = self.search_keyword_in_html("shares", html)
            shares = int_from_string(shares)
            return (comments, shares)
        except Exception as e:
            print("Error in get_comments_shares_alt: ", str(e))
            return None
    
    def crawl_timeline(self, start_date_obj = None, end_date_obj = None):
        bot = self.bot
        print(int((start_date_obj - end_date_obj).days), "days to crawl")
        filter_button = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]/div/div/div/div[2]/div/div/div"
        for n in range(int((start_date_obj - end_date_obj).days)):
            bot.refresh()
            random_wait(10)
            current_date_obj = start_date_obj - timedelta(n)
            print(current_date_obj.year, current_date_obj.strftime("%B"), current_date_obj.day)
                             
            self.post_filter(filter_button, current_date_obj.year, current_date_obj.strftime("%B"), current_date_obj.day)
            random_wait(8)
            
            i = 0
            close_button_exception = True
            reel_exception_count = 0
            while True:
                try:
                    i += 1
                    j = 3
                    error_count = 0
                    post_date = None
                    post_date_obj = None
                    
                    random_wait(8)

                    if i > 200:
                        bot.refresh()

                    wrt = "Post no: " + str(i) + " "
                    print(wrt.center(70, "-"))
                    
                    # anchor_scroll = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[3]/div/div"
                    # try:
                    #     anchor_scroll_element = bot.find_element_by_xpath(anchor_scroll)
                    # except:
                    #     # print({"error": "anchor_scroll_element not found"})
                    #     j = 3
                    # print(j, i)
                    post_box = f"/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[3]/div[1]/div"
                    anchor_scroll = f"/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[3]/div/div"
                    date_hover_element = f"/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[2]/div/div[2]/span/div/span[1]/span"
                    date_hover_box = f"/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[2]/div"
                    img_box = f"/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[3]/div/div[1]/a/div[1]/div/div/div/img"
                    img_box_2 = f"/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[3]/div[2]/div[1]/div/div/div"
                    react_str = f"/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[4]/div/div/div[1]/div/div[1]/div/div[1]/div/span/div/span[2]/span/span"
                    comment_share_parent = f"/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[4]/div/div/div[1]/div/div[1]"
                    comment_str = f"/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[4]/div/div/div/div/div[1]/div/div[2]/div[2]/span/div/span/span"
                    share_str = f"/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[4]/div/div/div/div/div[1]/div/div[2]/div[3]/span/div/span/span"
                    react_pop_up = "/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[1]/div/div[1]/div/div/div/div[2]"
                    react_pop_up_close = "/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[1]/div/div[2]/div"
                    try:
                        anchor_scroll_element = WebDriverWait(bot, 2).until(
                            EC.visibility_of_element_located((By.XPATH, anchor_scroll))
                        )
                        bot.execute_script("window.scrollBy(0, arguments[0].getBoundingClientRect().top - 150);", anchor_scroll_element)              
                        random_wait(5)
                    except:
                        self.perform_pagedown(1)
                        print("No anchor found. Probably a reel post.")
                        reel_exception_count += 1
                        if reel_exception_count >= 20:
                            bot.refresh()
                            i = 0
                        continue
                    
                    post_date, post_date_obj = self.hover_date_element(date_hover_element, date_hover_box)
                    
                    print("Post date: ", post_date)
                    
                    if post_date is None:
                        print("No date found")
                        continue
                    
                    print(post_date_obj.date(), current_date_obj.date())
                    if not post_date_obj.date() == current_date_obj.date():
                        if post_date_obj.date() > current_date_obj.date():
                            print(post_date_obj.date(), current_date_obj.date(), "future date")
                            continue
                        
                        if post_date_obj.date() < current_date_obj.date():
                            print(post_date_obj.date(), current_date_obj.date(), "current date exhausted")
                            wrt = "Continuing to next date"
                            print(wrt.center(70, "-"))
                            break
                    
                    if check_if_datetime_exists("indiannationalcongress", post_date):
                        print("Post already scraped: ", post_date)
                        continue
                    
                    try:
                        post_element = bot.find_element_by_xpath(post_box)
                        child_divs = post_element.find_elements_by_xpath('.//div')
                        if child_divs:
                            post_texts = []
                            see_more_button = None
                            for div in child_divs:
                                text = div.text.strip()
                                if text and text not in post_texts:
                                    post_texts.append(text)
                                if div.get_attribute('role') == 'button' and text == 'See more':
                                    see_more_button = div
                            if see_more_button:
                                see_more_button.click()
                                post_texts = []
                                see_more_button = None
                                for div in child_divs:
                                    text = div.text.strip()
                                    if text and text not in post_texts:
                                        post_texts.append(text)
                        else:
                            # print("No text found")
                            pass
                    except:
                        # print("No text found")
                        pass
                    
                    img_src_list = []
                    img_alt_list = []
                    try:
                        img_element = bot.find_element_by_xpath(img_box)
                        img_tag = img_element
                        img_src = img_tag.get_attribute('src')
                        img_alt = img_tag.get_attribute('alt')
                        if img_src is not None and img_alt is not None:
                            img_src_list.append(img_src)
                            img_alt_list.append(img_alt)
                    except Exception as e:
                        if img_src_list == []:
                            img_elements = bot.find_elements_by_xpath(img_box_2 + "//img")
                            for img_element in img_elements:
                                img_src = img_element.get_attribute('src')
                                img_alt = img_element.get_attribute('alt')
                                img_src_list.append(img_src)
                                img_alt_list.append(img_alt)
                        print("No image found")
                        pass
                    
                    img_tags = []
                    try:
                        for url in img_src_list:
                            hash_object = hashlib.sha256(url.encode())
                            time.sleep(0.5)
                            filename = hash_object.hexdigest() + ".jpg"
                            img_tags.append(filename)
                    except Exception as e:
                        print("An error occurred: ", str(e))
                        pass
                        
                    download_images(img_src_list, IMAGE_DOWNLOAD_PATH, img_tags)
                    
                    data = self.get_comments_shares_alt(comment_share_parent)
                    if data:
                        comments, shares = data[0], data[1]
                    else:
                        print("No comments or shares found using alt method")
                        comments = 0
                        shares = 0
                        try:
                            print(bot.find_element_by_xpath(comment_str).text)
                            comments = int_from_string(bot.find_element_by_xpath(comment_str).text)
                            if (comments != None):
                                pass
                        except Exception as e:
                            pass

                        try:
                            shares = int_from_string(bot.find_element_by_xpath(share_str).text)
                            if (shares != None):
                                pass
                        except Exception as e:
                            pass
                    if post_date_obj.date() < datetime(2016, 2, 22).date():
                        reactions = self.get_likes(react_str)
                    else:
                        reactions = self.get_reacts(react_str, react_pop_up, react_pop_up_close)
                                
                    print("\n"*2)
                    print("Date of post: ", post_date, 
                        "Post content: ", post_texts, 
                        "Image: ", img_src_list, 
                        "Image Summary: ", img_alt_list, 
                        "Image Tag: ",img_tags, 
                        "Comments: ", comments, 
                        "Shares: ", shares, 
                        "All Reacts: ", reactions["All"], 
                        "Like: ", reactions["Like"], 
                        "Love: ", reactions["Love"], 
                        "Care: ", reactions["Care"], 
                        "Haha: ", reactions["Haha"], 
                        "Wow: ", reactions["Wow"], 
                        "Sad: ", reactions["Sad"], 
                        "Angry: ", reactions["Angry"], 
                        sep="\n")
                    
                    data = {
                        'datetime': post_date,
                        'post_text': ', '.join(post_texts),
                        'img_link': ', '.join(img_src_list),  
                        'img_alt': ', '.join(img_alt_list),  
                        'img_tag': ', '.join(img_tags),  
                        'comments': comments,
                        'shares': shares,
                        'all_reacts': reactions["All"],
                        'like': reactions["Like"],
                        'love': reactions["Love"],
                        'care': reactions["Care"],
                        'haha': reactions["Haha"],
                        'sad': reactions["Sad"],
                        'angry': reactions["Angry"]
                    }
                    
                    insert_to_table("Indian National Congress",
                                    datetime=data['datetime'],
                                    post_text=data['post_text'],
                                    img_link=data['img_link'],
                                    img_alt=data['img_alt'],
                                    img_tag=data['img_tag'],
                                    comments=data['comments'],
                                    shares=data['shares'],
                                    all_reacts=data['all_reacts'],
                                    like=data['like'],
                                    love=data['love'],
                                    care=data['care'],
                                    haha=data['haha'],
                                    sad=data['sad'],
                                    angry=data['angry'])              
                except Exception as e:
                    print("An error occurred in the main loop:")
                    print("Exception type:", type(e).__name__)
                    print("Exception message:", str(e))
                    traceback.print_exc()
                    self.perform_pagedown(1)
                    error_count += 1
                    if error_count >= 10:
                        if close_button_exception:
                            try:
                                bot.find_element_by_xpath("/html/body/div[1]/div/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[1]/div/div").click()
                                i -= (error_count - 1)
                                error_count = 0
                            except:
                                close_button_exception = False
                        else:
                            bot.refresh()
                            random_wait(2)
                            current_date_obj = start_date_obj - timedelta(n)
                            print(current_date_obj.year, current_date_obj.strftime("%B"), current_date_obj.day)
                                            
                            self.post_filter(filter_button, current_date_obj.year, current_date_obj.strftime("%B"), current_date_obj.day)
                            random_wait(2)
                            
                            i = 0
                            error_count = 0
                    continue
        gen_prompt("Crawl ended", char="#")
        print("\n"*2)
        gen_prompt("Summary")
        print(f"Number of new entries to the database: {i}")
        print("\n"*2)
        
    def main(self, year, month, day):
        start_datetime_obj = parse_facebook_date(get_last_datetime("indiannationalcongress"))
        # start_datetime_obj = datetime(2017, 2, 20)
        end_datetime_obj = datetime(year, month, day) - timedelta(1)
        # name, url = fetch_new_profile("name"), fetch_new_profile("facebook")
        name, url = "Indian National Congress", "https://www.facebook.com/IndianNationalCongress"
        self.navigate_to_profile(name, url)
        self.crawl_timeline(start_date_obj=start_datetime_obj, end_date_obj=end_datetime_obj)

if __name__ == "__main__":
    scraper = FacebookProfileScraper('hrk.sahil', "password", operating_system="UBUNTU")         
    scraper.main(2010, 5, 30)
