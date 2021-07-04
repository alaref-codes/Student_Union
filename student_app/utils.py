import requests
from bs4 import BeautifulSoup
import pickle
import os
from urllib.parse import urlparse, unquote
from urllib.parse import parse_qs
import pandas as pd
import json
import codecs
import re
from datetime import datetime
from pprint import pprint as pp


class FacebookPostsScraper:

    def __init__(self, email, password, post_url_text='Full Story'):
        self.email = email
        self.password = password
        self.headers = {  # This is the important part: Nokia C3 User Agent
            'User-Agent': 'NokiaC3-00/5.0 (07.20) Profile/MIDP-2.1 Configuration/CLDC-1.1 Mozilla/5.0 AppleWebKit/420+ (KHTML, like Gecko) Safari/420+'
        }
        self.session = requests.session()  # Create the session for the next requests
        self.cookies_path = 'session_facebook.cki'  # Give a name to store the session in a cookie file.
        self.post_url_text = post_url_text

        if self.new_session():
            self.login()

        self.posts = []  # Store the scraped posts

    def new_session(self):
        if not os.path.exists(self.cookies_path):
            return True

        f = open(self.cookies_path, 'rb')
        cookies = pickle.load(f)
        self.session.cookies = cookies
        return False

    def make_request(self, url, method='GET', data=None, is_soup=True):
        if len(url) == 0:
            raise Exception(f'Empty Url')

        if method == 'GET':
            resp = self.session.get(url, headers=self.headers)
        elif method == 'POST':
            resp = self.session.post(url, headers=self.headers, data=data)
        else:
            raise Exception(f'Method [{method}] Not Supported')

        if resp.status_code != 200:
            raise Exception(f'Error [{resp.status_code}] > {url}')

        if is_soup:
            return BeautifulSoup(resp.text, 'lxml')
        return resp

    def login(self):
        url_home = "https://m.facebook.com/"
        soup = self.make_request(url_home)
        if soup is None:
            raise Exception("Couldn't load the Login Page")

        lsd = soup.find("input", {"name": "lsd"}).get("value")
        jazoest = soup.find("input", {"name": "jazoest"}).get("value")
        m_ts = soup.find("input", {"name": "m_ts"}).get("value")
        li = soup.find("input", {"name": "li"}).get("value")
        try_number = soup.find("input", {"name": "try_number"}).get("value")
        unrecognized_tries = soup.find("input", {"name": "unrecognized_tries"}).get("value")

        url_login = "https://m.facebook.com/login/device-based/regular/login/?refsrc=https%3A%2F%2Fm.facebook.com%2F&lwv=100&refid=8"
        payload = {
            "lsd": lsd,
            "jazoest": jazoest,
            "m_ts": m_ts,
            "li": li,
            "try_number": try_number,
            "unrecognized_tries": unrecognized_tries,
            "email": self.email,
            "pass": self.password,
            "login": "Iniciar sesión",
            "prefill_contact_point": "",
            "prefill_source": "",
            "prefill_type": "",
            "first_prefill_source": "",
            "first_prefill_type": "",
            "had_cp_prefilled": "false",
            "had_password_prefilled": "false",
            "is_smart_lock": "false",
            "_fb_noscript": "true"
        }
        soup = self.make_request(url_login, method='POST', data=payload, is_soup=True)
        if soup is None:
            raise Exception(f"The login request couldn't be made: {url_login}")

        redirect = soup.select_one('a')
        if not redirect:
            raise Exception("Please log in desktop/mobile Facebook and change your password")

        url_redirect = redirect.get('href', '')
        resp = self.make_request(url_redirect)
        if resp is None:
            raise Exception(f"The login request couldn't be made: {url_redirect}")

        cookies = self.session.cookies
        f = open(self.cookies_path, 'wb')
        pickle.dump(cookies, f)

        return {'code': 200}

    # Scrap a list of profiles
    def get_posts_from_list(self, profiles):
        data = []
        n = len(profiles)

        for idx in range(n):
            profile = profiles[idx]
            print(f'{idx + 1}/{n}. {profile}')

            posts = self.get_posts_from_profile(profile)
            data.append(posts)

        return data

    # This is the extraction point!
    def get_posts_from_profile(self, url_profile):
        # Prepare the Url to point to the posts feed
        if "www." in url_profile: url_profile = url_profile.replace('www.', 'm.')
        if 'v=timeline' not in url_profile:
            if '?' in url_profile:
                url_profile = f'{url_profile}&v=timeline'
            else:
                url_profile = f'{url_profile}?v=timeline'

        is_group = '/groups/' in url_profile

        soup = self.make_request(url_profile)
        if soup is None:
            print(f"Couldn't load the Page: {url_profile}")
            return []

        css_profile = '.storyStream > div'  # Select the posts from a user profile
        css_page = '#recent > div > div > div'  # Select the posts from a Facebook page
        css_group = '#m_group_stories_container > div > div'  # Select the posts from a Facebook group
        raw_data = soup.select(f'{css_profile} , {css_page} , {css_group}')  # Now join and scrape it
        posts = []
        for item in raw_data:  # Now, for every post...
            description = item.select('p')  # Get list of all p tag, they compose the description
            images = item.select('a > img')  # Get list of all images
            _external_links = item.select('p a')  # Get list of any link in the description, this are external links
            post_url = item.find('a', text=self.post_url_text)  # Get the url to point this post.

            if len(description) > 0:
                description = '\n'.join([d.get_text() for d in description])
            else:
                description = ''

            # Get all the images links
            images = [image.get('src', '') for image in images[1:]]         

            # for image in images:
            #     images = image.get('src', '')

            # Clean the post link
            if post_url is not None:
                post_url = post_url.get('href', '')
                if len(post_url) > 0:
                    post_url = f'https://www.facebook.com{post_url}'
                    p_url = urlparse(post_url)
                    qs = parse_qs(p_url.query)
                    if not is_group:
                        post_url = f'{p_url.scheme}://{p_url.hostname}{p_url.path}?story_fbid={qs["story_fbid"][0]}&id={qs["id"][0]}'
                    else:
                        post_url = f'{p_url.scheme}://{p_url.hostname}{p_url.path}/permalink/{qs["id"][0]}/'
            else:
                post_url = ''

            external_links = []
            for link in _external_links:
                link = link.get('href', '')
                try:
                    a = link.index("u=") + 2
                    z = link.index("&h=")
                    link = unquote(link[a:z])
                    link = link.split("?fbclid=")[0]
                    external_links.append(link)
                except ValueError as e:
                    continue
            post = {'description': description, 'images': images,
                    'post_url': post_url, 'external_links': external_links}
            posts.append(post)
            self.posts.append(post)
        return posts

    def posts_to_json(self, filename):
        if filename[:-5] != '.json':
            filename = f'{filename}.json'

        with codecs.open(filename , 'w' , 'utf-8') as f:
            f.write('[')
            for index,entry in enumerate(self.posts):
                f.write(json.dumps(entry,ensure_ascii=False))
                if index < len(self.posts) - 1:
                    f.write(',\n')
                else:
                    f.write('\n')
            f.write(']')

def main():
    # Enter your Facebook email and password
    email = os.environ.get('EMAIL1')
    password = os.environ.get('FACEBOOK')

    # Instantiate an object
    fps = FacebookPostsScraper(email, password, post_url_text='Full Story')

    # Example with single profile
    single_profile = 'https://www.facebook.com/E.T.studentunion'
    data = fps.get_posts_from_profile(single_profile)

    fps.posts_to_json('my_posts')  # You can export the posts as JSON document
    
if __name__ == '__main__':
    main()
