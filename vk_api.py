import json
from datetime import datetime
from os import getcwd
import os.path

import requests


class VK:
    def __init__(self, app_id=None, version=None):
        if app_id and version:
            self.app_id = app_id
            self.version = version
            self.api_key, self.user_id = self.get_api_key()
        else:
            print('You should provide your application id and API version to establish connection.',
                  'Read the guide to learn how to get them:',
                  'https://dev.vk.com/api/getting-started')

    def get_api_key(self):
        if os.path.exists(os.path.join(getcwd(), 'api_key.json')):
            with open('api_key.json', 'r') as file:
                data = json.load(file)
            api_key = data['api_key']
            user_id = data['user_id']
            return api_key, user_id
        else:
            scopes = 'groups+wall'
            print('To get an api key you mast follow the link:',
                  f'https://oauth.vk.com/authorize?client_id={self.app_id}&display=page&' +
                  f'redirect_uri=https://oauth.vk.com/blank.html&scope={scopes}&response_type=token&v={self.version}',
                  'After authorisation and redirection to https://oauth.vk.com/blank.html copy and past URL here.')
            raw = input()
            if 'access_token' in raw and 'user_id' in raw:
                parts = raw.split('#')[1].split('&')
                for part in parts:
                    if 'access_token' in part:
                        api_key = part.split('=')[1]
                    elif 'user_id' in part:
                        user_id = part.split('=')[1]
                with open('api_key.json', 'w') as file:
                    json.dump({'api_kei': api_key, 'user_id': user_id}, file)
                return api_key, user_id
            else:
                print('Error occurred while parsing URL, please try again.',
                      'Make sure you have "access_token" and "user_id" in URL.')

    def request_data(self, url, params):
        request = requests.get(url, params=params)
        if request.status_code == 200:
            response = request.content.decode()
            try:
                return json.loads(response)['response']
            except KeyError:
                print('Something went wrong. Server response:/n', json.loads(response))
        else:
            print('Something went wrong, request failed with status ', request.status_code)

    def get_groups(self, key_word, offset=0):
        url = 'https://api.vk.com/method/groups.search'
        params = {'access_token': self.api_key, 'q': key_word, 'v': self.version, 'owner_id': self.app_id,
                  'count': 500, 'offset': offset}
        return self.request_data(url, params)

    def get_posts(self, group_id, number=100, offset=0):
        url = 'https://api.vk.com/method/wall.get'
        params = {'access_token': self.api_key, 'v': self.version, 'owner_id': group_id,
                  'count': number, 'offset': offset}
        return self.request_data(url, params)

    def get_comms(self, group_id, post_id, number, offset=0):
        url = 'https://api.vk.com/method/wall.getComments'
        params = {'access_token': self.api_key, 'v': self.version, 'owner_id': group_id,
                  'count': number, 'offset': offset, 'post_id': post_id, 'extended': 1}
        return self.request_data(url, params)


def save_json(data):
    title = 'vk_data_from_' + datetime.now().strftime('%d.%m.%Y_%H:%M:%S')
    with open(f'{title}.json', 'w') as file:
        file.write(json.dumps(data))
    print(f'Data saved to file {title}.json.')

#if comms:
#    print('Comments total ', comms['count'])
#    items  = [item for item in comms['items']]
#    posters = []
#    for profile in comms['profiles']:
#        poster = {}
#        poster['first_name'] = profile['first_name']
#        poster['last_name'] = profile['last_name']
#        poster['comments'] = []
#        for item in items:
#            if item['from_id'] == profile['id']:
#                poster['comments'].append(item)
#                poster['comment_count'] = len(poster['comments'])
#        posters.append(poster)
#        print(profile)
#    posters.sort(key = lambda poster: poster ['comment_count'])
#    print('Here will be posters with their comments')
#    for poster in posters:
#        print(poster)
#else:
#    print('No comments')


if __name__ == '__main__':
    vk = VK('your_app_id', '5.131')

    data = vk.get_groups('renpy')
    groups_open = [item for item in data['items'] if item['is_closed'] == 0]
    save_json(groups_open)