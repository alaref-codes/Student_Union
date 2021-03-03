from .FacebookPostsScraper import FacebookPostsScraper as Fps
from pprint import pprint as pp
import json


def main():
    # Enter your Facebook email and password
    email = 'alarefabushaala@gmail.com'
    password = "%%%areef%%%"

    # Instantiate an object
    fps = Fps(email, password, post_url_text='Full Story')

    # Example with single profile
    single_profile = 'https://www.facebook.com/E.T.studentunion'
    data = fps.get_posts_from_profile(single_profile)

    fps.posts_to_json('my_posts')  # You can export the posts as JSON document
if __name__ == '__main__':
    main()
