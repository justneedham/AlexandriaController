#Copyright Alexandria Books All Rights Reserved

from WebDriver import WebDriver
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random, re, os, time, smtplib, caffeine
import mysql.connector
from mysql.connector import Error

class InstaBot(object):

    def __init__(self, peopleToFollow, postsToLike, peopleToUnfollow):
        self.driver = WebDriver()
        self.url = 'https://www.instagram.com/?hl=en'
        self.username = "alexandriatextbooks"
        self.password = "Al3xandr1a!!!"
        self.longPause = [4.0, 3.5, 3.0, 2.5, 2.0]
        self.shortPause = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8]
        self.peopleToFollow = peopleToFollow
        self.peopleToUnfollow = peopleToUnfollow
        self.postsToLike = postsToLike
        self.sucessfullyFollowed = 0
        self.sucessfullyLiked = 0
        self.successfullyUnfollowed = 0
        self.followError = 0
        self.likeError = 0
        self.privateAccountsFollowed = 0
        self.unfollowError = 0
        self.scrollError = 0
        self.errorLog = []

    def run(self):
        """Calls the required methods to run the bot"""
        self.set_up()

        self.follow_routine()
        self.pause(self.longPause)
        if self.peopleToUnfollow != 0:
            self.unfollow_routine()
            self.pause(self.longPause)
        self.like_routine()
        self.pause(self.longPause)

        self.tear_down()

    def set_up(self):
        """Read current notifications, followers and activity"""
        self.startTime = time.time()
        self.login()
        self.click_profile_btn()

        self.numberOfFollowers = self.get_number_of_followers(self.username)
        self.numberOfFollowing = self.get_number_of_following(self.username)
        self.followers = self.get_followers(self.username)

        self.compare_activity_data()

    def like_routine(self):
        """Scroll instagram feed to look at next post"""
        self.click_exit_btn()
        self.click_instagram_home_btn()
        postsToLike = self.postsToLike - self.sucessfullyLiked
        liked = 0
        while liked < postsToLike:
            try:
                try:
                    liked += 1
                    likeBtn = self.driver.get_element_by_xpath("//span[@class='_8scx2 coreSpriteHeartOpen']")
                    self.driver.click_button(likeBtn)
                    self.sucessfullyLiked += 1
                except:
                    try:
                        unlikeBtn = self.driver.get_element_by_xpath("//span[@class='_8scx2 coreSpriteHeartFull']")
                        self.driver.scroll_main_window('400')
                        self.likeError += 1
                    except:
                        self.driver.scroll_main_window('400')
                        self.pause(self.longPause)
            except:
                self.scrollError += 1

    def follow_routine(self):
        """Follows random people"""
        try:
            randomFollower = random.choice(self.followers)
            self.got_to_follower_page(randomFollower)
            randomFollowerFollowers = self.get_followers(randomFollower)
            followed = 0
            while followed < self.peopleToFollow:
                self.got_to_follower_page(random.choice(randomFollowerFollowers))
                self.pause(self.shortPause)
                try:
                    self.click_follow_btn()
                    self.sucessfullyFollowed += 1
                    followed += 1
                except:
                    self.followError += 1
                try:
                    self.click_post("1")
                    try:
                        self.click_like_btn()
                        self.click_exit_btn()
                        self.sucessfullyLiked += 1
                    except:
                        self.likeError += 1
                except:
                    self.privateAccountsFollowed += 1
            self.pause(self.longPause)
        except:
            self.errorLog.append("Follow Routine Error")
            self.follow_routine()

    def tear_down(self):
        """Analyze session performance"""
        self.endTime = time.time()
        self.elapsedTime = self.endTime - self.startTime
        print('-------------- Recent Activity --------------')
        print('Current Followers: {}'.format(self.numberOfFollowers))
        print('Current Following: {}'.format(self.numberOfFollowing))
        print('Followers Lost: {}'.format(self.followersLost))
        print('Followers Gained: {}'.format(self.followersGained))
        print('Followers Retained: {}'.format(self.followersRetained))
        print('Net Change: {}'.format(self.netChange))
        print('New Likes: {}'.format(self.newLikes))
        print('\n')
        print('------------- Session Statistics -----------')
        print('Posts liked: {}'.format(self.sucessfullyLiked))
        print('People followed: {}'.format(self.sucessfullyFollowed))
        print('Private accounts followed: {}'.format(self.privateAccountsFollowed))
        print('People unfollowed: {}'.format(self.successfullyUnfollowed))
        print('Like errors: {}'.format(self.likeError))
        print('Follow errors: {}'.format(self.followError))
        print('Unfollow errors: {}'.format(self.unfollowError))
        print('Script Time: {} seconds'.format(round(self.elapsedTime),2))
        print('Number of Errors: {}'.format(len(self.errorLog)))
        self.send_email()
        self.log_to_datawarehouse()
        self.driver.close()

    def unfollow_routine(self):
        """Go to a following page, like their last post and unfollow"""
        following = self.get_following(self.username)
        x = 0
        while x < self.peopleToUnfollow:
            x += 1
            self.got_to_follower_page(random.choice(following))
            try:
                self.click_post("1")
                try:
                    self.click_like_btn()
                    self.sucessfullyLiked += 1
                    self.click_exit_btn()
                except:
                    self.likeError += 1
            except:
                self.likeError += 1

            try:
                self.click_unfollow_btn()
                self.successfullyUnfollowed += 1

            except:
                self.unfollowError += 1

    def read_following(self):
        """Download the html of the following page and save it to a txt file"""
        content = self.driver.driver.page_source
        usernames = self.parse_username_links(content)
        return usernames

    def get_following(self, username):
        """Get usernames of all following"""
        self.click_profile_btn()
        numberOfFollowing = self.get_number_of_following(username)
        self.click_following_btn()
        self.scroll_following(numberOfFollowing)
        following = self.read_following()

        self.click_exit_btn()
        return following

    def click_following_btn(self):
        """Click on the following button"""
        followingBtn = self.driver.get_element_by_xpath("//a[@href='/alexandriatextbooks/following/']")
        self.driver.click_button(followingBtn)

    def get_last_followers(self):
        """Loads the last followers from lastFollowersData.txt and returns list"""
        lastFollowers = []
        with open('lastFollowersData.txt') as file:
            line = file.readline()
            line.strip()
            cleanLine = re.sub(r'\n', '', line)
            lastFollowers.append(cleanLine)
            while line:
                line = file.readline()
                line.strip()
                cleanLine = re.sub(r'\n', '', line)
                lastFollowers.append(cleanLine)
        lastFollowers.pop()
        return lastFollowers

    def compare_activity_data(self):
        """Reads the new activity data and compares it with the old and returns the likes"""
        self.click_activity_btn()
        currentActivityData = self.get_current_activity_data()
        lastActivityData = self.get_last_activity_data()

        currentFollowers = self.numberOfFollowers
        lastFollowers = len(self.get_last_followers())

        x = currentActivityData['new followers'] - lastActivityData['new followers']
        if x > 0:
            newFollowers = x
        else:
            newFollowers = 0

        self.followersRetained = currentFollowers - newFollowers
        self.followersGained = newFollowers
        self.followersLost = lastFollowers - (currentFollowers - newFollowers)
        self.netChange = currentFollowers - lastFollowers
        self.numberOfCurrentFollowers = currentFollowers
        self.newLikes = currentActivityData['likes'] - lastActivityData['likes']

        self.save_activity_data(currentActivityData['all'])
        self.save_follower_data(self.followers)
        self.driver.refresh()

    def get_last_activity_data(self):
        """Returns a dictionary"""
        ### Loads each line from 'lastActivityData.txt' ###
        rawLastActivityData = []
        with open('lastActivityData.txt') as file:
            line = file.readline()
            line.strip()
            result = line.split(' ')
            rawLastActivityData.append(result)
            while line:
                line = file.readline()
                line.strip()
                result = line.split(' ')
                rawLastActivityData.append(result)
        ### Cleans the \n and concatenates into clean activityData and pop off the last empty list ###
        rawLastActivityData.pop()
        cleanLastActivityData = []
        for line in rawLastActivityData:
            time = re.sub(r'\n', '', line[2])
            cleanLastActivityData.append([line[0], line[1], time])

        ### Extracts the number of new followers and likes from the clean last activity data ###
        likes = 0
        newFollowers = 0
        errors = 0
        for line in cleanLastActivityData:
            if line[1] == 'started':
                newFollowers += 1
            elif line[1] == 'liked':
                likes += 1
            else:
                errors += 1

        return {'likes': likes, 'new followers': newFollowers, 'errors': errors}

    def get_current_activity_data(self):
        """Returns a dictionary"""
        ### Collects raw HTML ###
        content = self.driver.driver.page_source

        ### Parse with beautiful soup ###
        soup = BeautifulSoup(content, 'html.parser')
        liTagsTxt = []
        for tag in soup.find_all('li'):
            liTagsTxt.append(tag.text)

        ### Cleans out the banned items and duplicates ###
        cleanList = []
        bannedItems = [
            "LanguageAfrikaansČeštinaDanskDeutschΕλληνικάEnglishEspañol (España)EspañolSuomiFrançaisBahasa IndonesiaItaliano日本語한국어Bahasa MelayuNorskNederlandsPolskiPortuguês (Brasil)Português (Portugal)РусскийSvenskaภาษาไทยFilipinoTürkçe中文(简体)中文(台灣)বাংলাગુજરાતીहिन्दीHrvatskiMagyarಕನ್ನಡമലയാളംमराठीनेपालीਪੰਜਾਬੀසිංහලSlovenčinaதமிழ்తెలుగుTiếng Việt中文(香港)БългарскиFrançais (Canada)RomânăСрпскиУкраїнська",
            "Directory",
            "Terms",
            "Privacy",
            "Jobs",
            "API",
            "Press",
            "Blog",
            "Support",
            "About us"
            ]
        for item in bannedItems:
            self.removeItem(item, liTagsTxt)

        ### Skips the first three items
        for item in liTagsTxt[3:]:
            cleanList.append(item)
        cleanCurrentActivityData = []
        for item in cleanList:
            result = item.split(' ')
            username = result[0]
            activity = result[1]
            timeList = result[3].split('.')[1]
            time = re.sub(r'Following|Follow', '', timeList)
            cleanCurrentActivityData.append([username, activity, time])

        likes = 0
        newFollowers = 0
        errors = 0

        ### Extracts the number of new followers and likes from the clean last activity data ###
        for line in cleanCurrentActivityData:
            if line[1] == 'started':
                newFollowers += 1
            elif line[1] == 'liked':
                likes += 1
            else:
                errors += 1

        return {'likes': likes, 'new followers': newFollowers, 'errors': errors, 'all': cleanCurrentActivityData}

    def save_activity_data(self, activityData):
        """Writes activity data to 'lastActivityData.txt'"""
        os.remove('lastActivityData.txt')
        currentActivity = open('lastActivityData.txt', 'w')
        numberOfLines = len(activityData)
        line = 0
        for data in activityData:
            line = line + 1
            if line < numberOfLines:
                currentActivity.write(data[0] + ' ' + data[1] + ' ' + data[2] + '\n')
            else:
                currentActivity.writelines(data[0] + ' ' + data[1] + ' ' + data[2])

    def save_follower_data(self, followers):
        """Writes all followers to 'lastFollowersData.txt'"""
        os.remove('lastFollowersData.txt')
        currentFollowersData = open('lastFollowersData.txt', 'w')
        numberOfLines = len(followers)
        line = 0
        for follower in followers:
            line = line + 1
            if line < numberOfLines:
                currentFollowersData.write(follower + '\n')
            else:
                currentFollowersData.write(follower)

    def get_followers(self, username):
        """Get usernames of all followers"""
        numberOfFollowers = self.get_number_of_followers(username)
        self.click_followers_btn(username)
        self.scroll_followers(numberOfFollowers)
        followers = self.read_followers()

        self.click_exit_btn()
        return followers

    def get_number_of_followers(self, username):
        """Returns the number of followers of a given username"""
        followersElement = self.driver.get_element_by_xpath("//a[@href='/"+username+"/followers/']")
        numberOfFollowers = re.sub(r'\D', "", followersElement.text)
        return int(numberOfFollowers)

    def get_number_of_following(self, username):
        """Returns the number of people a username is following"""
        followingElement = self.driver.get_element_by_xpath("//a[@href='/"+username+"/following/']")
        numberOfFollowing = re.sub(r'\D', "", followingElement.text)
        return int(numberOfFollowing)

    def login(self):
        """Go to Instagram and login"""
        self.driver.go_to(self.url)
        expandBtn = self.driver.get_element_by_xpath("//a[@href='javascript:;']")
        self.driver.click_button(expandBtn)
        self.pause(self.longPause)

        userNameTextBox = self.driver.get_element_by_xpath("//input[@name='username']")
        self.driver.enter_text(userNameTextBox, self.username)
        self.pause(self.longPause)

        passwordTextBox = self.driver.get_element_by_xpath("//input[@name='password']")
        self.driver.enter_text(passwordTextBox, self.password)
        self.pause(self.longPause)

        loginBtn = self.driver.get_element_by_xpath("//button[@class='_qv64e _gexxb _4tgw8 _njrw0']")
        self.driver.click_button(loginBtn)
        self.pause(self.longPause)

        self.click_exit_btn()

    def read_followers(self):
        """Download the html of the followers page and save to a txt file"""
        content = self.driver.driver.page_source
        usernames = self.parse_username_links(content)
        return usernames

    def parse_username_links(self, content):
        """Takes raw html and returns the username hrefs"""
        hrefs = []
        soup = BeautifulSoup(content, 'html.parser')
        for link in soup.find_all('a'):
            hrefs.append(link.get('href'))
        usernames = self.clean_usernames(hrefs)
        return usernames

    def clean_usernames(self, hrefs):
        """Filter list of username hrefs for duplicates and site links"""
        cleanUsernames = []
        bannedItems = ["http:blog.instagram.com",
                       "developer",
                       "legalprivacy",
                       "explorelocations",
                       "#",
                       "aboutus",
                       "alexandriatextbooks",
                       "/explore/locations/",
                       "/legal/privacy/",
                       "/developer/",
                       "http://blog.instagram.com/",
                       "/about/us/",
                       "/",
                       "/alexandriatextbooks/followers/",
                       "/alexandriatextbooks/saved/",
                       "/p/Bc8BXL5n8Wq/?taken-by=alexandriatextbooks",
                       ]
        # removes duplicate hrefs
        for duplicate in hrefs:
            if duplicate in hrefs:
                pos = hrefs.index(duplicate)
                del hrefs[pos]
        # removes unrelated hrefs
        for item in bannedItems:
            self.removeItem(item, hrefs)
        # skips the first dynamic href and cleans remaining
        for item in hrefs[1:]:
            cleanUsername = item.replace('/', '')
            cleanUsernames.append(cleanUsername)

        return cleanUsernames

    def format_activity_data(self, clean_list):
        """Takes a cleaned list and splits it into a list of lists"""
        results = []
        for item in clean_list:
            result = item.split(' ')
            username = result[0]
            activity = result[1]
            timeList = result[3].split('.')[1]
            time = re.sub(r'Following|Follow', '', timeList)
            results.append([username, activity, time])
        return results

    def check_exists(self, item, list):
        """Check to see if an item is contained in a list"""
        if item in list:
            return True

        elif item not in list:
            return False
        else:
            print('check_exists: Error')

    def show(self, list):
        """Shows the contents of a list"""
        for x in list:
            print(x)

        print('Total {}'.format(len(list)))

    def removeItem(self, item, list):
        """Removes a particular item from a list"""
        for x in list:
            if x == item:
                pos = list.index(item)
                del list[pos]

    def clean_saved_follower_data(self, list):
        """Takes a raw list of stored data and removes the '\n'"""
        cleanData = []
        try:
            list.pop()
        except:
            print('Error: No saved follower data')
        for data in list:
            username = re.sub(r'\n', '', data)
            cleanData.append(username)
        return cleanData

    #### Instabot Actions ####

    def pause(self, secondsList):
        """Wait a random amount of seconds"""
        self.driver.pause(random.choice(secondsList))

    def click_activity_btn(self):
        """Click on the activity button"""
        try:
            activityBtn = self.driver.get_element_by_xpath(
                "//a[@class='_ohbcb _gvoze coreSpriteDesktopNavActivity _3pzlm']")
            self.driver.click_button(activityBtn)
            self.pause(self.longPause)
        except:
            try:
                activityBtn = self.driver.get_element_by_xpath(
                    "//a[@class='_ohbcb _gvoze coreSpriteDesktopNavActivity']")
                self.driver.click_button(activityBtn)
                self.pause(self.longPause)
            except:
                self.errorLog.append('click_activity_btn')

    def got_to_follower_page(self, username):
        """Direct transfer to follow's instagram page"""
        try:
            self.driver.go_to("https://www.instagram.com/"+username+"/")
            self.pause(self.longPause)
        except:
            self.errorLog.append('got_to_follower_page')

    def click_followers_btn(self, username):
        """Click on the followers button of a given username"""
        try:
            followersBtn = self.driver.get_element_by_xpath("//a[@href='/"+username+"/followers/']")
            self.driver.click_button(followersBtn)
            self.pause(self.longPause)
        except:
            self.errorLog.append('click_followers_btn')

    def click_post(self, postNumber):
        """Click on a post"""
        post = self.driver.get_element_by_xpath("//div[@class='_6d3hm _mnav9']/div["+postNumber+"]/a")
        self.driver.click_button(post)
        self.pause(self.longPause)

    def click_exit_btn(self):
        """Click the exit btn"""
        try:
            exitBtn = self.driver.get_element_by_xpath("//button[@class='_dcj9f']")
            self.driver.click_button(exitBtn)
            self.pause(self.longPause)
        except:
            print("No pop up window present")

    def click_like_btn(self):
        """Click on the like button"""
        try:
            likeBtn = self.driver.get_element_by_xpath("//span[@class='_8scx2 coreSpriteHeartOpen']")
            self.driver.click_button(likeBtn)
            self.pause(self.shortPause)
        except:
            self.likeError += 1

    def click_follow_btn(self):
        """Click the follow button"""
        try:
            followBtn = self.driver.get_element_by_xpath("//button[@class='_qv64e _gexxb _r9b8f _njrw0']")
            self.driver.click_button(followBtn)
            self.pause(self.longPause)
        except:
            self.followError += 1

    def click_unfollow_btn(self):
        """Click the unfollow button"""

        unfollowBtn = self.driver.get_element_by_xpath("//button[@class='_qv64e _t78yp _r9b8f _njrw0']")
        self.driver.click_button(unfollowBtn)
        self.pause(self.longPause)

    def click_profile_btn(self):
        """Click on the profile button"""
        try:
            profileBtn = self.driver.get_element_by_xpath("//a[@href='/alexandriatextbooks/']")
            self.driver.click_button(profileBtn)
            self.pause(self.longPause)
        except:
            self.errorLog.append("Unable to click profile button")
            self.driver.driver.back()
            self.driver.refresh()
            self.click_profile_btn()

    def click_instagram_home_btn(self):
        """Click on the home button to view feed"""
        instaHomeBtn = self.driver.get_element_by_xpath("//a[@class='_giku3 _8scx2 coreSpriteDesktopNavLogoAndWordmark _rujh3']")
        self.driver.click_button(instaHomeBtn)
        self.pause(self.longPause)

    def scroll_followers(self, numberOfFollowers):
        """Scroll the followers window"""
        if numberOfFollowers > 500:
            timesToScroll = 50
        else:
            timesToScroll = (numberOfFollowers // 10)
        followersWindow = self.driver.get_element_by_xpath("//div[@class='_gs38e']")
        self.driver.scroll(followersWindow, timesToScroll)

    def scroll_following(self, numberOfFollowing):
        """Scroll the following window"""
        if numberOfFollowing > 500:
            timesToScroll = 50
        else:
            timesToScroll = (numberOfFollowing // 10)
        followingWindow = self.driver.get_element_by_xpath("//div[@class='_gs38e']")
        self.driver.scroll(followingWindow, timesToScroll)

    def click_username(self, username):
        """Click a username"""
        link = self.driver.get_element_by_xpath("//a[@href='/"+username+"/']")
        self.driver.click_button(link)
        self.driver.pause(5)

    def shut_down(self):
        """Safely closes browser"""
        self.driver.close()

    def send_email(self):
        """Sends email with session statistics"""
        s = smtplib.SMTP(host='smtp.gmail.com', port='587')
        s.starttls()
        s.login('alexandriatextbooksassistant@gmail.com', 'teXtbooks@l3x')

        msg = MIMEMultipart()
        msg['From'] = 'Instabot'
        msg['To'] = 'info@alexandriatextbooks.com'
        msg['Subject'] = 'Instabot'

        message = """
        Recent Activity
        
        Followers Retained: {}
        Followers Gained: {}
        Followers Lost: {}
        Net Change: {}
        Current: {}
        New Likes: {}
        
        Session Statistics
        Posts liked: {}
        People followed: {}
        Private accounts followed: {}
        People unfollowed: {}
        Like errors: {}
        Follow errors: {}
        Scroll errors: {}
        Unfollow errors: {}
        Script Time: {} seconds
        """.format(self.followersRetained, self.followersGained, self.followersLost,
                   self.netChange, self.numberOfCurrentFollowers, self.newLikes, self.sucessfullyLiked,
                   self.sucessfullyFollowed, self.privateAccountsFollowed,
                   self.successfullyUnfollowed,
                   self.likeError, self.followError, self.scrollError, self.unfollowError,
                   round(self.elapsedTime))

        msg.attach(MIMEText(message, 'plain'))
        s.send_message(msg)

    def log_to_datawarehouse(self):
        """Connects to the data warehouse and inserts session data"""
        connection = self.connect()
        cur = connection.cursor()
        cur.callproc('insert_instabot_data', [self.numberOfCurrentFollowers, self.numberOfFollowing,
                                              self.followersLost, self.followersRetained,
                                              self.followersGained, self.newLikes,
                                              self.sucessfullyLiked, self.sucessfullyFollowed,
                                              self.successfullyUnfollowed, self.likeError,
                                              self.followError, self.unfollowError,
                                              round(self.elapsedTime)])

        connection.commit()

    def connect(self):
        """Connects to the datawarehouse and inserts session data"""
        try:
            connection = mysql.connector.connect(
                host='35.197.44.156',
                database='alexandria_data_warehouse',
                user='Justin Needham',
                password='DeoJuvante',
            )
            if connection.is_connected():
                return connection
        except Error as e:
            self.errorLog.append(e)

def test_follow():
    """Follows two people"""
    bot = InstaBot(2, 2, 0)
    bot.set_up()
    bot.follow_routine()
    bot.driver.close()

def test_like():
    """Likes photos"""
    bot = InstaBot(0, 5, 0)
    bot.set_up()
    bot.like_routine()
    bot.driver.close()

def test_unfollow():
    """Unfollows"""
    bot = InstaBot(0, 2, 2)
    bot.set_up()
    bot.unfollow_routine()
    bot.driver.close()

try:
    bot = InstaBot(50, 275, 25)
    bot.run()
except:
    s = smtplib.SMTP(host='smtp.gmail.com', port='587')
    s.starttls()
    s.login('alexandriatextbooksassistant@gmail.com', 'teXtbooks@l3x')
    msg = MIMEMultipart()
    msg['FROM'] = 'Instabot'
    msg['To'] = 'info@alexandriatextbooks.com'
    msg['Subject'] = 'CRITICAL ERROR'

    message = """
    Instabot crashed and was unable to complete the script
    """
    msg.attach(MIMEText(message, 'plain'))
    s.send_message(msg)

