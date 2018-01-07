# -*- coding:utf-8 -*-
"""
douban movies information download, parse
"""

import urllib.request
import urllib.error
from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36'
                         ' (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'}

movie_category = ['热门', '最新', '经典', '可播放', '豆瓣高分', '冷门佳片', '华语',
                  '欧美', '韩国', '日本', '动作', '喜剧', '爱情', '科幻', '悬疑',
                  '恐怖', '治愈']

movie_info_hot = []
movie_info_time = []
movie_info_comment = []
command_cache = []
movie_detail_info = []


class DoubanSpider(object):
    """
    download latest movie info from douban.com
    """
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.douban_url_base = 'https://movie.douban.com/'
        self.url_category = ''
        self.url_picture = ''
        self.url_movie_detail_info = []

    def cvt_cmd_to_ctgy_url(self, command):
        """
        url_category: https://movie.douban.com/explore
        could also be extended to others like reading books, music, etc.
        :param command:
        :return:
        """
        if '电影' in command:
            self.url_category = self.douban_url_base + 'explore'

    def browser_hotopen(self):
        """
        hotopen chrome before sender type in any words
        :return:
        """
        self.driver.get(self.douban_url_base)

    def browser_action_general_info(self, type_command):
        """
        chrome browser acts to crawl the general info to users (movie name, score)
        :param type_command:
        :return:
        """
        self.driver.get(self.url_category)
        sleep(1)
        for num in range(0, len(movie_category)):
            if type_command == movie_category[num]:
                self.driver.find_element_by_xpath('//*[@id="content"]/div/div[1]/div/div[2]/div[1]'
                                                  '/form/div[1]/div[1]/label[{}]'.format(num+1)).click()
        sleep(1)
        self.browser_crawl_general_info()
        return movie_info_hot + movie_info_time + movie_info_comment

    def browser_crawl_general_info(self):
        """
        crawl the general info from douban webstie
        :return:
        """
        # delete movie_info_xx for next search
        del movie_info_hot[:]
        del movie_info_time[:]
        del movie_info_comment[:]
        for num in range(1, 4):
            # click sequence
            self.driver.find_element_by_xpath('//*[@id="content"]/div/div[1]/div/div[2]/div'
                                              '[1]/form/div[3]/div[1]/label[{}]/input'.format(num)).click()
            sleep(1)
            for counter in range(1, 11):
                if num == 1:
                    movie_info_hot.append(self.get_movie_general_info(counter))
                elif num == 2:
                    movie_info_time.append(self.get_movie_general_info(counter))
                elif num == 3:
                    movie_info_comment.append(self.get_movie_general_info(counter))
                else:
                    pass
        self.clean_general_info()

    def get_movie_general_info(self, counter):
        """
        provide
        :param counter:
        :return:
        """
        each_movie_info = self.driver.find_element_by_xpath('//*[@id="content"]/div/div[1]'
                                                            '/div/div[4]/div/a[{}]/p'.format(counter)).text
        return each_movie_info

    @staticmethod
    def clean_general_info():
        """
        beautify the movie general info
        :return:
        """
        for num in range(0, len(movie_info_hot)):
            movie_info_hot[num] = movie_info_hot[num].replace(' ', ':  ')
            movie_info_time[num] = movie_info_time[num].replace(' ', ':  ')
            movie_info_comment[num] = movie_info_comment[num].replace(' ', ':  ')
            movie_info_hot[num] = str(num+1) + '.' + movie_info_hot[num] + '分'
            movie_info_time[num] = str(num+1) + '.' + movie_info_time[num] + '分'
            movie_info_comment[num] = str(num+1) + '.' + movie_info_comment[num] + '分'

    def browser_action_detail_info(self, counter, movie_name):
        """
        chrome browser acts to crawl the detail info for users
        :param counter:
        :param movie_name:
        :return:
        """
        movie_click_num = 0
        # click the type of movie
        for num in range(0, len(movie_category)):
            if command_cache[0] == movie_category[num]:
                self.driver.find_element_by_xpath('//*[@id="content"]/div/div[1]/div/div[2]/div[1]'
                                                  '/form/div[1]/div[1]/label[{}]'.format(num+1)).click()
        sleep(1)
        # click the sequence type
        self.driver.find_element_by_xpath('//*[@id="content"]/div/div[1]/div/div[2]/div'
                                          '[1]/form/div[3]/div[1]/label[{}]/input'.format(counter)).click()
        sleep(1)
        if counter == 1:
            for x in range(0, len(movie_info_hot)):
                if movie_name in movie_info_hot[x]:
                    movie_click_num = x + 1
        elif counter == 2:
            for x in range(0, len(movie_info_time)):
                if movie_name in movie_info_time[x]:
                    movie_click_num = x + 1
        else:
            for x in range(0, len(movie_info_comment)):
                if movie_name in movie_info_comment[x]:
                    movie_click_num = x + 1
        # click movie name for detail info
        movie_detail_url = self.driver.find_element_by_xpath('//*[@id="content"]/div/div[1]/div/div[4]/div/a[{}]'
                                                             .format(movie_click_num)).get_attribute('href')
        return movie_detail_url

    @staticmethod
    def parse_detail_info(html_result):
        """
        parse the html downloaded
        :param html_result:
        :return:
        """
        del movie_detail_info[:]

        movie_name = ''
        actor_name_list = '主演: '
        director_name = '导演: '
        movie_type = '类型: '
        movie_date = '上映日期: '
        movie_runtime = '片长: '
        soup = BeautifulSoup(html_result, 'lxml')

        movie_name = movie_name + soup.find('span', property='v:itemreviewed').string.strip()\
        + soup.find('span', class_='year').string.strip()
        director_name = director_name + soup.find('a', rel='v:directedBy').string.strip()
        for x in soup.find_all('a', rel='v:starring'):
            actor_name_list = actor_name_list + x.string.strip() + '/'
        for x in soup.find_all('span', property='v:genre'):
            movie_type = movie_type + x.string.strip() + '/'
        for x in soup.find_all('span', property='v:initialReleaseDate'):
            movie_date = movie_date + x.string.strip() + '/'
            movie_runtime = movie_runtime + soup.find('span', property='v:runtime').string.strip()

        movie_detail_info.append(movie_name)
        movie_detail_info.append(director_name)
        movie_detail_info.append(actor_name_list)
        movie_detail_info.append(movie_type)
        movie_detail_info.append(movie_date)
        movie_detail_info.append(movie_runtime)

    @staticmethod
    def download_detail_info_html(url_target):
        """
        download douban target html
        :param url_target:
        :return:
        """
        try:
            response = urllib.request.Request(url_target, headers=headers)
            result = urllib.request.urlopen(response)
            html = result.read().decode('utf-8')
            return html
        except urllib.error.HTTPError as e:
            if hasattr(e, 'code'):
                print(e.code)
        except urllib.error.URLError as e:
            if hasattr(e, 'reason'):
                print(e.reason)


if __name__ == '__main__':
    douban_crawl = DoubanSpider()
    douban_crawl.url_category = 'https://movie.douban.com/explore'


