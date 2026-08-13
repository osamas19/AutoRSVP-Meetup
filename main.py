from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep

class Autorsvp():
	def __init__(self,email,password):

		self.browser = webdriver.Firefox()
		self.wait = WebDriverWait(self.browser, 20)

		self.email = email
		self.password = password

	def login_with_email(self):

		self.browser.get("https://www.meetup.com/login/")

		email_box = self.wait.until(EC.presence_of_element_located((By.ID,"email")))
		email_box.send_keys(self.email)

		password_box = self.browser.find_element(By.ID,"current-password")
		password_box.send_keys(self.password)

		login_button = self.browser.find_element(By.NAME,"submitButton")
		login_button.click()

		# Wait until we've left the login page (or the login form disappears)
		self.wait.until(lambda d: "/login" not in d.current_url)



	def rsvp_meeting(self,link):
		self.browser.get("https://www.meetup.com" + link)
		self.wait.until(EC.presence_of_element_located((By.TAG_NAME,"body")))

		#If Already RSVP'ed

		if self.__check_already_going():
			return

		#Click RSVP Button
		attend_button = self.wait.until(
			EC.element_to_be_clickable((By.XPATH,"//button[contains(., 'Attend')]"))
		)
		attend_button.click()

		sleep(10)



	#Check if Already RSVPed
	def __check_already_going(self):
		text = "You're going to this event!"
		if text in self.browser.page_source:
			print("Already RSVP")
			return True
		else:
			return False


	def closeBrowser(self):
		self.browser.close()



#Fetchs links of events from group name
def fetch_events_by_group(group):

	group_link = f"https://www.meetup.com/{group}/events/"

	response = requests.get(group_link)

	if response.status_code != 200:
		print("Something Went Wrong! Please check Group Url")
		return []
	
	html_res = BeautifulSoup(response.text,"html.parser")
	events = html_res.select(".eventCard--link")
	events_links = [event.get("href") for event in events]

	return events_links



if __name__ == "__main__":


	print("\n================ Auto RSVP Meetup.com ================\n")
	
	email = input("Enter your email: ")
	password = input("Enter your password: ")
	groups = []

	no_groups = int(input("\nEnter the number(count) of groups you want to AutoRSVP: "))
	
	print("\nEnter the groups name in each line\n")

	for i in range(no_groups):
		usrinpt =  input("Enter group -> ")
		groups.append(usrinpt)


	print("\n ====== Auto RSVPing (Meetup.com) =======")

	waitTime = 60  #60 Minutes


	#Storing Visited Links to Increase Performance
	visitedLinks = set()

	while True:
		# Run this every 1 hour
		
		# Setup Browser
		rsvper = Autorsvp(email,password)


		# Login
		rsvper.login_with_email()

		# Get Groups Details

		for grp in groups:
				
			print(grp)

			eventLinks = fetch_events_by_group(grp)

			for link in eventLinks:
				print(link)

				if link in visitedLinks:
					continue

				visitedLinks.add(link)

				rsvper.rsvp_meeting(link)

				sleep(6)
			
			print()

		rsvper.closeBrowser()
		sleep(waitTime*60)

