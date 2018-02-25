# -*- coding] = utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re
import csv
import os
from collections import OrderedDict

run_data = []
visited_hrefs = []
driver = webdriver.Firefox()

def write_to_csv(data, file):
    keys = data.keys()
    if os.stat(file).st_size == 0:
        with open(file, 'wb') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerow(data)
    else:
        with open(file, 'a') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writerow(data)

def loop_over_connections(level):
    if (level < 15):
        next_level = level + 1
        connections = driver.find_elements_by_xpath("//div[@class='title']/a[@class='colored']")
        hrefs = [c.get_attribute("href") for c in connections]

        for href in hrefs:
            if href in visited_hrefs:
                continue
            visited_hrefs.append(href)
            user = href.split("profile/",1)[1]
            driver.get(href)
            driver.implicitly_wait(2)
            get_data(user, level)
            try:
                connections = driver.find_element_by_xpath("//div[@class='connections-count']/a")
                connection_number = int(connections.text.split()[0])
                if connection_number < 300:
                    connections.click()
                    driver.implicitly_wait(3)
                    loop_over_connections(next_level) 
            except Exception as e:
                print e
                test_garmin_login(visited_hrefs[-10])

def get_my_connections():
    connections = driver.find_element_by_xpath("//span[contains(text(),'Connections')]").click()
    driver.implicitly_wait(3)
    loop_over_connections(0)

def start_at_href(href):
    driver.get(href)
    driver.implicitly_wait(5)
    driver.find_element_by_xpath("//div[@class='connections-count']/a").click()
    driver.implicitly_wait(5)
    loop_over_connections(0) 

def get_data(user, level):

    user_data = OrderedDict()
    user_data['user'] = user
    user_data['level'] = level

    print "level: ", level
    print "getting data for: ", user

    # set to None
    marathon = None
    marathonYear = None
    half = None
    halfYear = None
    fiveK = None
    fiveKYear = None
    tenK = None
    tenKYear = None
    distance = None
    activities = None
    time = None
    elevation = None

    try:
        no_share = driver.find_element_by_xpath("//i[contains(@class,'icon-locked')]")
        user_data['share'] = False
        write_to_csv(user_data, 'visited_users.csv')
        return
    except:
        pass

    try:
        personal_records = driver.find_element_by_xpath("//div[contains(@class,'user-stats')]/div[1]/div/h3")
        if personal_records.text != 'Personal Records':
            return
    except:
        return

    try:
        marathon = driver.find_element_by_xpath("//span[text()='Marathon']/following-sibling::span").text
        marathonYear = driver.find_element_by_xpath("//span[text()='Marathon']/following-sibling::span/following-sibling::span").text
        print "marathon time: ", marathon
    except:
        pass
    
    try:
        half = driver.find_element_by_xpath("//span[text()='Half Marathon']/following-sibling::span").text
        halfYear = driver.find_element_by_xpath("//span[text()='Half Marathon']/following-sibling::span/following-sibling::span").text
        print "half time: ", half
    except:
        pass

    if marathon != None or half != None:
        try:
            fiveK = driver.find_element_by_xpath("//span[contains(text(), '5K')]/following-sibling::span").text
            fiveKYear = driver.find_element_by_xpath("//span[contains(text(), '5K')]/following-sibling::span/following-sibling::span").text
        except:
            pass

        try:    
            tenK = driver.find_element_by_xpath("//span[contains(text(), '10K')]/following-sibling::span").text
            tenKYear = driver.find_element_by_xpath("//span[contains(text(), '10K')]/following-sibling::span/following-sibling::span").text
        except:
            pass

        try:
            distance = driver.find_element_by_xpath("//div[@class='tab-content']/div/div/div/div/span[contains(text(), 'Distance')]/preceding-sibling::div").text
            activities = driver.find_element_by_xpath("//div[@class='tab-content']/div/div/div/div/span[contains(text(), 'Activities')]/preceding-sibling::div").text
            time = driver.find_element_by_xpath("//div[@class='tab-content']/div/div/div/div/span[contains(text(), 'Time')]/preceding-sibling::div").text
            elevation = driver.find_element_by_xpath("//div[@class='tab-content']/div/div/div/div/span[contains(text(), 'Elev Gain')]/preceding-sibling::div").text

        except Exception as e:
            print e

        user_data['5K'] = fiveK
        user_data['5KYear'] = fiveKYear
        user_data['10K'] = tenK
        user_data['10KYear'] = tenKYear
        user_data['half'] = half
        user_data['halfYear'] = halfYear
        user_data['marathon'] = marathon
        user_data['marathonYear'] = marathonYear
        user_data['distance'] = distance
        user_data['activities'] = activities
        user_data['time'] = time
        user_data['elevation'] = elevation
        

        run_data.append(user_data)
        write_to_csv(user_data, 'data.csv')

    else:
        user_data['share'] = True
        write_to_csv(user_data, 'visited_users.csv')
      

def test_garmin_login(start_href=None):
    driver.implicitly_wait(10)
    driver.get("https://connect.garmin.com/en-US/signin?service=https://connect.garmin.com/modern/activities")
    
    driver.switch_to_frame(driver.find_element_by_tag_name("iframe"))
    driver.find_element_by_id("username").clear()
    driver.find_element_by_id("username").send_keys("dbilenkin@gmail.com")
    driver.find_element_by_id("password").clear()
    driver.find_element_by_id("password").send_keys("as77db1A")
    driver.find_element_by_id("login-btn-signin").click()
    
    driver.implicitly_wait(10)
    driver.switch_to_default_content()

    if start_href == None:
        get_my_connections()
    else:
        start_at_href(start_href)

def load_visited_users():
    reader = csv.DictReader(open('visited_users.csv', 'rb'))
    for line in reader:
        visited_href = "https://connect.garmin.com/modern/profile/" + line["user"]
        visited_hrefs.append(visited_href)


load_visited_users()
test_garmin_login("https://connect.garmin.com/modern/profile/MONDRI81")
    

