from selenium import webdriver
import time, sqlite3, sys, os, re, json
import sqlite3
import sys
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from tqdm import tqdm
from datetime import datetime
from utils import *
from database import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "data", "dbfiles",'ipp.db')
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
        bot.get(url)
        gen_prompt("Navigating to " + name, char="#")
        wait(2)
        
    def crawl_timeline(self, year: int, month: int, day: int):
        bot = self.bot
        error_count = 0
        i = 0
        
        while True:
            try:
                i += 1
                j = 2
                K_EXISTS = False
                wrt = "Post no: " + str(i) + " "
                print(wrt.center(70, "-"))
                
                anchor_scroll = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[3]/div/div"
                
                try:
                    anchor_scroll_element = bot.find_element_by_xpath(anchor_scroll)
                except:
                    j = 3
                
                post_box = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[3]/div[1]/div"
                anchor_scroll = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[3]/div/div"
                date_hover_element = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[2]/div/div[2]/div/div[2]/span/div/span[1]/span/a"
                date_hover_box = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[2]/div"
                img_box = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[3]/div/div[1]/a/div[1]/div/div/div/img"
                img_box_2 = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[3]/div[2]/div[1]/div/div/div"
                react_str = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[4]/div/div/div[1]/div/div[1]/div/div[1]/div/span/div/span[2]/span/span"
                comment_str = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[4]/div/div/div/div/div[1]/div/div[2]/div[2]/span/div/span/span"
                share_str = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[4]/div/div/div/div/div[1]/div/div[2]/div[3]/span/div/span/span"
                share_str_2 = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[4]/div/div/div[1]/div/div[1]/div/div[2]/div[2]/span/div/span/span"
                comment_str_2 = f"/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[{j}]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[13]/div/div/div[4]/div/div/div[1]/div/div[1]/div/div[2]/div[1]/span/div/span/span"
                
                anchor_scroll_element = bot.find_element_by_xpath(anchor_scroll)
                bot.execute_script("window.scrollBy(0, arguments[0].getBoundingClientRect().top - 150);", anchor_scroll_element)
                time.sleep(1)
                
                try:
                    hover = ActionChains(bot).move_to_element(bot.find_element_by_xpath(date_hover_element))
                    hover.perform()
                    time.sleep(1.5)
                    
                    date_hover_box_element = bot.find_element_by_xpath(date_hover_box)
                    post_date = date_hover_box_element.text
                    print(post_date)
                except:
                    print("No date found")

                post_date_obj = parse_facebook_date(post_date)

                comparison_date_obj = datetime(year, month, day)
                
                if not post_date_obj >= comparison_date_obj:
                    break
                
                try:
                    post_element = bot.find_element_by_xpath(post_box)
                    child_divs = post_element.find_elements_by_xpath('.//div')
                    if child_divs:
                        texts = []
                        see_more_button = None
                        for div in child_divs:
                            text = div.text.strip()
                            if text and text not in texts:
                                texts.append(text)
                            if div.get_attribute('role') == 'button' and text == 'See more':
                                see_more_button = div
                        if see_more_button:
                            see_more_button.click()
                            texts = []
                            see_more_button = None
                            for div in child_divs:
                                text = div.text.strip()
                                if text and text not in texts:
                                    texts.append(text)
                                print(texts[0])
                        else:
                            print(texts[0])
                    else:
                        print("No text found")
                except:
                    print("No text found")
                
                img_src = None
                try:
                    img_element = bot.find_element_by_xpath(img_box)
                    img_tag = img_element
                    img_src = img_tag.get_attribute('src')
                    img_alt = img_tag.get_attribute('alt')
                    print(f"Image found: src={img_src}\nalt={img_alt}")
                except Exception as e:
                    # print("An error occurred: ", str(e))
                    if img_src == None:
                        img_elements = bot.find_elements_by_xpath(img_box_2 + "//img")
                        for img_element in img_elements:
                            img_src = img_element.get_attribute('src')
                            img_alt = img_element.get_attribute('alt')
                            print(f"Image found: src={img_src}\nalt={img_alt}")
                    
                    print("No image found")
                    
                
                try:
                    # print(bot.find_element_by_xpath(react_str).text)
                    reacts = int_from_string(bot.find_element_by_xpath(react_str).text)
                    if (reacts != None):
                        print ("\nReacts: "+ str(reacts))
                        if reacts > 999:
                            K_EXISTS = True
                except Exception as e:
                    print("\nReacts: 0")
                
                if K_EXISTS:
                    # comment_str = comment_str_2
                    # share_str = share_str_2
                    pass
                try:
                    # print(bot.find_element_by_xpath(comment_str).text)
                    comments = int_from_string(bot.find_element_by_xpath(comment_str).text)
                    if (comments != None):
                        print ("Comments: "+ str(comments))
                except Exception as e:
                    print("Comments: 0")

                try:
                    # print(bot.find_element_by_xpath(share_str).text)
                    shares = int_from_string(bot.find_element_by_xpath(share_str).text)
                    if (shares != None):
                        print ("Shares: "+ str(shares))
                except Exception as e:
                    print("Shares: 0")
            
            except Exception as e:
                print("An error occurred: ", str(e))
                error_count += 1
                if error_count >= 10:
                    break
                pass
        gen_prompt("Crawl ended", char="#")
        print("\n"*2)
        gen_prompt("Summary")
        print(f"Number of new entries to the database: {i}")
        # print(f"Size of database: {len(memory_list)}")
        print("\n"*2)
              
with open("C:\\Users\\hamid\\OneDrive\\Documents\\credential.txt", 'r', encoding='utf-8') as f:
    password = f.read()

scraper = FacebookProfileScraper('hrk.sahil', password, browser_type=1)

# scraper.login()
scraper.crawl_timeline(year=2024, month=10, day=3)
# scraper.poke()

