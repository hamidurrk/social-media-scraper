from selenium import webdriver
import time, sqlite3, sys, os, hashlib
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
from utils import *
from database import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "data", "dbfiles",'ipp.db')
IMAGE_DOWNLOAD_PATH = os.path.join(BASE_DIR, "data", "img")
conn = sqlite3.connect(DATABASE_PATH)

class FacebookProfileScraper:
    def __init__(self, username, password, browser_type=0):
        self.username = username
        self.password = password
        gen_prompt("Facebook Profile Scraper (for research use only)")
        firefox_options = webdriver.FirefoxOptions()
        # firefox_options.add_argument("--headless") 
        firefox_options.add_argument("--devtools")
        if (browser_type):
            self.bot = webdriver.Firefox(executable_path=GeckoDriverManager().install(), service_args = ['--marionette-port', '2828', '--connect-existing'], options=firefox_options)
        else:
            self.bot = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        # self.bot.set_window_position(0, 0) 
        # self.bot.set_window_size(960, 1043)
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
        time.sleep(1)
        gen_prompt("Navigated to Facebook", char="#")
        try:
            bot.find_element_by_xpath('//*[@id="email"]').send_keys(self.username)
            gen_prompt("Username Entered")
            bot.find_element_by_xpath('//*[@id="pass"]').send_keys(self.password)
            gen_prompt("Password Entered")
            time.sleep(1)
            
            bot.find_element_by_xpath('//*[@id="pass"]').send_keys(Keys.RETURN)
            gen_prompt("Login Requested")
            wait(5)
            
            print("\n"*4)
        except:
            pass
        
    def navigate_to_profile(self, name, url):
        bot = self.bot
        if not url == bot.current_url:
            bot.get(url)
        gen_prompt("Navigating to " + name, char="#")
        wait(2)
    
    def get_last_datetime(self, table_name):
        c = conn.cursor()
        c.execute(f"SELECT datetime FROM {table_name} ORDER BY id DESC LIMIT 1")
        return c.fetchall()[0][0]
    
    def crawl_timeline(self, start_date_obj = None, end_date_obj = None):
        bot = self.bot
        error_count = 0
        i = 0
        prev = 0
        
        while True:
            try:
                i += 1
                j = 2
                K_EXISTS = False
                wrt = "Post no: " + str(i) + " "
                print(wrt.center(70, "-"))
                
                anchor_scroll = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[3]/div/div"
                                #   /html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]  /div[1]  /div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[3]/div/div
                try:
                    anchor_scroll_element = bot.find_element_by_xpath(anchor_scroll)
                except:
                    print({"error": "anchor_scroll_element not found"})
                    for _ in range(5):
                        ActionChains(bot).send_keys(Keys.PAGE_DOWN).perform()
                        time.sleep(2)
                    j = 3
                
                post_box = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[3]/div[1]/div"
                anchor_scroll = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[3]/div/div"
                date_hover_element = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[2]/div/div[2]/span/div/span[1]/span/a"
                date_hover_text_element = '//*[@id="SvgT125"]'           
                date_hover_box = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[2]/div"
                img_box = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[3]/div/div[1]/a/div[1]/div/div/div/img"
                img_box_2 = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[3]/div[2]/div[1]/div/div/div"
                react_str = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[4]/div/div/div[1]/div/div[1]/div/div[1]/div/span/div/span[2]/span/span"
                comment_str = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[4]/div/div/div/div/div[1]/div/div[2]/div[2]/span/div/span/span"
                share_str = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[4]/div/div/div/div/div[1]/div/div[2]/div[3]/span/div/span/span"
                share_str_2 = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[4]/div/div/div[1]/div/div[1]/div/div[2]/div[2]/span/div/span/span"
                comment_str_2 = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[4]/div/div/div[1]/div/div[1]/div/div[2]/div[1]/span/div/span/span"
                react_pop_up = "/html/body/div[1]/div/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[1]/div/div[1]/div/div/div/div[2]"
                react_pop_up_close = "/html/body/div[1]/div/div/div[1]/div/div[4]/div/div/div[1]/div/div[2]/div/div/div/div/div/div/div[1]/div/div[2]/div"
                
                # anchor_scroll_element = bot.find_element_by_xpath(anchor_scroll)
                anchor_scroll_element = WebDriverWait(bot, 5).until(
                    EC.visibility_of_element_located((By.XPATH, anchor_scroll))
                )
                bot.execute_script("window.scrollBy(0, arguments[0].getBoundingClientRect().top - 150);", anchor_scroll_element)
                
                if i < prev:
                    time.sleep(2)
                    continue
                
                time.sleep(2)
                
                try:
                    # date_hover_element_text = bot.find_element_by_xpath(date_hover_element).text
                    # print(date_hover_element_text)
                    hover = ActionChains(bot).move_to_element(bot.find_element_by_xpath(date_hover_element))
                    hover.perform()
                    time.sleep(2)
                    
                    date_hover_box_element = bot.find_element_by_xpath(date_hover_box)
                    post_date = date_hover_box_element.text
                    post_date_obj = parse_facebook_date(post_date)
                except:
                    print("Date invalid. Maybe not hoverable.")
                    pass
                
                
                # if post_date_obj > start_date_obj:
                #     print("Post already scraped: ", post_date_obj)
                #     continue
                # if not post_date_obj >= end_date_obj:
                #     break
                
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
                
                # try:
                #     reacts = int_from_string(bot.find_element_by_xpath(react_str).text)
                #     if (reacts != None):
                #         print ("\nReacts: "+ str(reacts))
                #         if reacts > 999:
                #             K_EXISTS = True
                # except Exception as e:
                #     print("\nReacts: 0")
                #     pass
                comments = 0
                shares = 0
                try:
                    comments = int_from_string(bot.find_element_by_xpath(comment_str).text)
                    if (comments != None):
                        # print ("Comments: "+ str(comments))
                        pass
                except Exception as e:
                    # print("Comments: 0")
                    pass

                try:
                    shares = int_from_string(bot.find_element_by_xpath(share_str).text)
                    if (shares != None):
                        # print ("Shares: "+ str(shares))
                        pass
                except Exception as e:
                    # print("Shares: 0")
                    pass
                
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
                
                try:
                    bot.find_element_by_xpath(react_str).click()
                    WebDriverWait(bot, 10).until(
                        EC.presence_of_element_located((By.XPATH, f"{react_pop_up}"))
                    )
                    time.sleep(1)
                    react_pop_up_element = bot.find_element_by_xpath(react_pop_up)
                    
                    child_elements = react_pop_up_element.find_elements_by_xpath('.//div')
                    
                    for child in child_elements:
                        aria_label = child.get_attribute("aria-label")
                        if not aria_label == None:
                            reaction, count = aria_label.split(", ")
                            reactions[reaction] = int_from_string(count)
                    bot.find_element_by_xpath(react_pop_up_close).click()
                except Exception as e:
                    print("An error occurred: ", str(e))
                
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
                
                insert_to_table("Bharatiya Janata Party (BJP)",
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
                
                wait(1)
            
            except Exception as e:
                print("An error occurred in the main loop: ", str(e))
                error_count += 1
                if error_count >= 10:
                    break
                continue
        gen_prompt("Crawl ended", char="#")
        print("\n"*2)
        gen_prompt("Summary")
        print(f"Number of new entries to the database: {i}")
        print("\n"*2)
        
    def main(self, year, month, day):
        # start_datetime_obj = parse_facebook_date(self.get_last_datetime("bharatiyajanatapartybjp"))
        # end_datetime_obj = datetime(year, month, day)
        name, url = fetch_new_profile("name"), fetch_new_profile("facebook")
        self.navigate_to_profile(name, url)
        # self.crawl_timeline(start_date_obj=start_datetime_obj, end_date_obj=end_datetime_obj)
        self.crawl_timeline()
              
with open("C:\\Users\\hamid\\OneDrive\\Documents\\credential.txt", 'r', encoding='utf-8') as f:     # importing password from local machine
    password = f.read()

if __name__ == "__main__":
    scraper = FacebookProfileScraper('hrk.sahil', password, browser_type=1)         # username of the facebook profile
    scraper.main(2010, 5, 30)
