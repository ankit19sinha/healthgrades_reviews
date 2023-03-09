import time
import scrapy
import dateutil.parser
from selenium import webdriver
from selenium.webdriver.common.by import By
from healthgrades.items import HealthgradesItem

class HG_spider(scrapy.Spider):
    name = "hg_reviews"
    start_urls = ["https://www.healthgrades.com/family-practice-directory/ny-new-york/new-york"] + ["https://www.healthgrades.com/family-practice-directory/ny-new-york/new-york" + "_" + str(i) for i in range(2, 31)]

    def parse(self, response):
        links = ["https://www.healthgrades.com" + link for link in response.css('h3.card-name a::attr(href)').extract()]

        for url in links:
            yield scrapy.Request(url=url, callback=self.parse_details)

    
    def parse_details(self, response):
        # create a unique_id from the url
        unique_id = response.url.split("/")[-1]

        # get provider name and specialty
        provider_name = response.css("h1::text").get().replace("Dr.", "").split(",")[0].strip()
        provider_spec = response.css("h2::text").get()
        
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        options.add_argument('--headless')

        driver = webdriver.Chrome(options=options)
        driver.get(response.url)

        addresses = set()
        ph_numbers = set()

        # get all the unique listed locations
        try:
            locations = driver.find_elements(By.CLASS_NAME, 'office-location-content')
            for location in locations:
                addr = []
                for span in location.find_elements(By.CSS_SELECTOR, "span"):
                    addr.append(span.text.replace("New Patient?", "").replace(",", "").strip())
                
                addresses.add(" | ".join(addr))
        except:
            addresses.add("")


        # get all the unique listed phone numbers
        try:
            location = driver.find_elements(By.CLASS_NAME, 'office-location-content')
            for location in locations:
                tele = location.find_elements(By.CSS_SELECTOR, 'a[title^=Call]')[0].text
                tele = tele.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
                ph_numbers.add(tele)
        
        except:
            ph_numbers.add("")


        # click on "Show more reviews" to gather all the reviews posted
        more_button = driver.find_elements(By.CLASS_NAME, 'c-comment-list__show-more')
        
        if len(more_button) > 0:
            try:
                while(more_button[0].is_displayed()):
                    driver.execute_script("arguments[0].click();", more_button[0])
                    time.sleep(5)
            except:
                pass

        try:
            # get all comment divs
            comments = driver.find_elements(By.CLASS_NAME, 'l-single-comment-container')

            # iterate over each div and get the details
            if len(comments) > 0:
                for comment in comments:
                    item = HealthgradesItem()

                    # define provider level information
                    item["unique_id"] = unique_id
                    item["provider_name"] = provider_name
                    item["provider_spec"] = provider_spec
                    item["provider_addresses"] = list(addresses)
                    item["provider_ph_numbers"] = list(ph_numbers)
                    
                    # get rating and review 
                    item["rating"] = comment.find_element(By.CLASS_NAME, 's6RLV').get_attribute('aria-label').split(' ')[1]
                    item["review"] = comment.find_element(By.CLASS_NAME, 'c-single-comment__comment').text

                    # get commenter name and date
                    commenter_info = comment.find_element(By.CLASS_NAME, 'c-single-comment__commenter-info').text

                    # get commenter name if not anonymous
                    if ' – ' in commenter_info:
                        commenter_name, comment_date = commenter_info.split(' – ')
                        comment_date = dateutil.parser.parse(comment_date).strftime('%Y-%m-%d')

                        item["commenter_name"] = commenter_name
                        item["commenter_date"] = comment_date
                    else:
                        commenter_name = ""
                        comment_date = dateutil.parser.parse(commenter_info).strftime('%Y-%m-%d')

                        item["commenter_name"] = commenter_name
                        item["commenter_date"] = comment_date

                    yield item
            
            else:
                item = HealthgradesItem()
                item["unique_id"] = unique_id
                item["provider_name"] = provider_name
                item["provider_spec"] = provider_spec
                item["provider_addresses"] = list(addresses)
                item["provider_ph_numbers"] = list(ph_numbers)
                item["rating"] = ""
                item["review"] = ""
                item["commenter_name"] = ""
                item["commenter_date"] = ""

                yield item
        
        except:
            item = HealthgradesItem()
            item["unique_id"] = unique_id
            item["provider_name"] = provider_name
            item["provider_spec"] = provider_spec
            item["provider_addresses"] = list(addresses)
            item["provider_ph_numbers"] = list(ph_numbers)
            item["rating"] = ""
            item["review"] = ""
            item["commenter_name"] = ""
            item["commenter_date"] = ""

            yield item
