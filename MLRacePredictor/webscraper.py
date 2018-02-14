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

def write_to_csv(data):
    keys = data.keys()
    if os.stat("data.csv").st_size == 0:
        with open('data.csv', 'wb') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerow(data)
    else:
        with open('data.csv', 'a') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writerow(data)

def write_visited_users():
    if os.stat("visited_users.csv").st_size == 0:
        with open('visited_users.csv','wb') as resultFile:
            wr = csv.writer(resultFile, dialect='excel')
            wr.writerow(visited_hrefs)
    else:
        with open('visited_users.csv','a') as resultFile:
            wr = csv.writer(resultFile, dialect='excel')
            wr.writerows(visited_hrefs)


def loop_over_connections(level):
    if (level < 12):
        next_level = level + 1
        connections = driver.find_elements_by_xpath("//div[@class='title']/a[@class='colored']")
        hrefs = [c.get_attribute("href") for c in connections]

        for href in hrefs:
            if href in visited_hrefs:
                continue
            visited_hrefs.append(href)
            user = href.split("profile/",1)[1]
            driver.get(href)
            driver.implicitly_wait(3)
            driver.switch_to_default_content()

            get_data(user, level)
            try:
                driver.find_element_by_xpath("//div[@class='connections-count']/a").click()
                driver.implicitly_wait(10)
                loop_over_connections(next_level) 
            except Exception as e:
                print e

def get_my_connections():
    driver.find_element_by_xpath("//span[contains(text(),'Connections')]").click()
    driver.implicitly_wait(10)

    loop_over_connections(0) 

def get_data(user, level):

    print "level: ", level
    print "getting data for: ", user

    try:
        marathon = driver.find_element_by_xpath("//span[text()='Marathon']/following-sibling::span").text
        marathonYear = driver.find_element_by_xpath("//span[text()='Marathon']/following-sibling::span/following-sibling::span").text
        print "marathon time: ", marathon

        fiveK = driver.find_element_by_xpath("//span[contains(text(), '5K')]/following-sibling::span").text
        fiveKYear = driver.find_element_by_xpath("//span[contains(text(), '5K')]/following-sibling::span/following-sibling::span").text

        distance = driver.find_element_by_xpath("//div[@class='tab-content']/div/div/div/div/span[contains(text(), 'Distance')]/preceding-sibling::div").text
        activities = driver.find_element_by_xpath("//div[@class='tab-content']/div/div/div/div/span[contains(text(), 'Activities')]/preceding-sibling::div").text
        time = driver.find_element_by_xpath("//div[@class='tab-content']/div/div/div/div/span[contains(text(), 'Time')]/preceding-sibling::div").text
        elevation = driver.find_element_by_xpath("//div[@class='tab-content']/div/div/div/div/span[contains(text(), 'Elev Gain')]/preceding-sibling::div").text

        user_data = OrderedDict()
        user_data['user'] = user
        user_data['5K'] = fiveK
        user_data['5KYear'] = fiveKYear
        user_data['marathon'] = marathon
        user_data['marathonYear'] = marathonYear
        user_data['distance'] = distance
        user_data['activities'] = activities
        user_data['time'] = time
        user_data['elevation'] = elevation
        user_data['level'] = level

        run_data.append(user_data)
        write_to_csv(user_data)

    except Exception as e:
        print e
      

def test_garmin_login():
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

    get_my_connections()

test_garmin_login()
write_visited_users()
    

