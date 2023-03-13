import pathlib

from requests import Session
import requests as r
from bs4 import BeautifulSoup as bs
import  os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class Cloner():

    def __init__(self,base_url, home_folder):
        #list of urls
        self.urls = []
        #Root directory
        self.dir = home_folder
        #temp urls
        self.temp_urls = []
        self.inputs = {'username': "admin", 'password': 'pass'}
        self.url = base_url # base url
        app_url = self.url.split('/')[2] # get domain name url
        self.base_app_name = app_url.split('.')[0] # Get app name
        self.temp_app_name = self.base_app_name # Temp app name
        self.base_url = self.split(self.url, '/', 3)[0] # Get domain name url
        #list of images
        self.image_list = []
        #Javascript list
        self.javascript_list = []
        #css list
        self.css_list = []

    def split(self, strng, sep, pos):
        strng = strng.split(sep)
        return sep.join(strng[:pos]), sep.join(strng[pos:])

    def getUrls(self, temp_url):
        if self.temp_urls.__contains__(temp_url):
            pass
        else:
            with Session() as s:
                webpage = s.get(temp_url)
                webpage_content = bs(webpage.content, 'lxml')
                for link in webpage_content.find_all("a"):
                    try:
                        url = link['href']
                        if url.__contains__(self.base_app_name):
                            pass
                        elif url.__contains__('.com') or url.__contains__('//') or url.__contains__(
                                'jpeg') or url.__contains__(
                            'png') or url.__contains__('jpg') or url.__contains__('mp3') or url.__contains__(
                            '.pdf') or url.__contains__('mp4') or url.__contains__(':void(0)'):
                            pass
                        else:
                            if self.temp_urls.__contains__(url):
                                pass
                            else:
                                cur_url = ''
                                if url.__contains__('#'):
                                    cur_url = f'{self.base_url}/'
                                elif url.__contains__('mailto:'):
                                    cur_url = f'{self.base_url}/'
                                elif url.startswith('/'):
                                    cur_url = f'{self.base_url}{url}'
                                else:
                                    cur_url = f'{self.base_url}/{url}'

                                self.temp_urls.append(url)
                                if not self.urls.__contains__(cur_url):
                                        self.urls.append(cur_url)

                                self.getUrls(cur_url)
                    except :
                          pass

    def get_images(self, temp_url):
        with Session() as s:
            webpage = s.get(temp_url, headers={'User-Agent': 'Mozilla/5.0'})
            webpage_content = bs(webpage.content, 'lxml')
            # print(webpage_content)
            for link in webpage_content.find_all('img'):
                if self.image_list.__contains__(link['src']):
                    pass
                else:
                    self.image_list.append(link['src'])

            if len(self.image_list) == 0:
                print('empty')
    def save_file(self,home_folder,file_list):
        # self.get_images(self.url)

        for img in file_list:
            if img.startswith('//'):
                img_url = f'{img.replace("/", "", 1)}'
                img_url = f'http://{img_url.replace("/", "", 1)}'
            elif img.startswith('/'):
                img_url = f'{self.base_url}{img}'
            else:
                img_url = f'{self.base_url}/{img}'
            image = r.get(img_url)
            file_name = self.split(img_url, "/", -1)[1]
            # Leaf directory
            folder = f'{home_folder}/{self.split(img, "/", -1)[0]}'
            full_path = f'{folder}/{file_name}'
            dir = pathlib.Path(folder)
            unwanted = self.split(full_path, '?', 1)[1]
            wanted = self.split(full_path, '?', 1)[0]
        try:
            if os.path.exists(dir):

                if len(unwanted) > 0:
                    with open(wanted, 'wb') as file:
                        file.write(image.content)
                        file.flush()
                else:
                    with open(full_path, 'wb') as file:
                        file.write(image.content)
                        file.flush()
            else:
                dir.mkdir(parents=True)
                if len(unwanted) > 0:
                    with open(wanted, 'wb') as file:
                        file.write(image.content)
                        file.flush()
                else:
                    with open(full_path, 'wb') as file:
                        file.write(image.content)
                        file.flush()
        except:
               pass


    def get_javascripts(self,temp_url):
        with Session() as s:
            webpage = s.get(temp_url)
            webpage_content = bs(webpage.content, 'lxml')
            for js in webpage_content.find_all("script"):
                try:
                    if js['src'].__contains__('://'):
                        pass
                    else:
                        self.javascript_list.append(js['src'])
                except:
                    pass
    def get_css(self,temp_url):
        with Session() as s:
            webpage = s.get(temp_url)
            webpage_content = bs(webpage.content, 'lxml')
            for css in webpage_content.find_all("link"):
                try:
                    if css['href'].__contains__('://'):
                        pass
                    else:
                         self.css_list.append(css['href'])
                except:
                    pass

    def save_singlepage(self,home_folder,link):
        links = [link]
        self.save_html(home_folder,links)
    def save_html(self,home_folder,url_list):
        for url in url_list:
            req = r.get(url)
            status =  req.status_code
            domain = self.split(url, '/', 3)[0]
            query = self.split(url, '/', 3)[1]
            file_name = 'index.html'
            special_char_list = ['&', ' ', '-', '#' , '=', '$', '?']
            for char in special_char_list:
                if query.__contains__(char):
                    query = query.replace(char, '_')

            if len(query) > 1:
                file_name = f'{query}.html'
            else:
                file_name = 'index.html'
            folder = ''
            if query.__contains__('/'):
                folder = f'{home_folder}/{query}'
            else:
                folder = f'{home_folder}'
            full_path = f'{folder}/{file_name}'
            # print(f'Url -> {url}\nDomain -> {domain}\nQuery -> '
            #       f'{query}\nFolder->{folder} \n Full path -> {full_path}')
            dir = pathlib.Path(folder)
            if os.path.exists(dir):
                if status == 200:
                    with open(full_path, 'wb') as file:
                        file.write(req.content)
                        file.flush()
            else:
              if status == 200:
                dir.mkdir(parents=True)
                with open(full_path, 'wb') as file:
                        file.write(req.content)
                        file.flush()

    def webpage(self):
        print('Cloning css......')
        self.get_css(self.url)
        self.save_file(self.dir, self.css_list)
        print('Cloning javascript......')
        self.get_javascripts(self.url)
        self.save_file(self.dir, self.javascript_list)
        print('Cloning Images......')
        self.get_images(self.url)
        self.save_file(self.dir, self.image_list)
        print('Cloning Webpage......')
        self.save_singlepage(self.dir, self.url)
        print('cloned.......')
    def website(self):
        print('Cloning css......')
        self.get_css(self.url)
        self.save_file(self.dir, self.css_list)
        print('Cloning javascript......')
        self.get_javascripts(self.url)
        self.save_file(self.dir, self.javascript_list)
        print('Cloning Images......')
        self.get_images(self.url)
        self.save_file(self.dir, self.image_list)
        print('Cloning Webpage......')
        self.getUrls(self.url)
        self.save_html(self.dir, self.urls)
        print('cloned.......')
    def clone(self):
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_experimental_option('detach', True)
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
                # driver.implicitly_wait(10000)
                driver.get(f'{self.dir}/index.html');




url = 'https://instagram.com/'

dir  =  'C:\\Users\\Patrick\\PycharmProjects\\brutcrap\\BruteForce\\Attack\\main\\PyCloner'
clone = Cloner(url,dir)
clone.webpage()
clone.clone()
# clone.clone('C:\inetpub\wwwroot\cloner')
