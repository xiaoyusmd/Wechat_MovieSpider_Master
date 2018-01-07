# -*- encoding:utf-8 -*-
"""
Wechat auto reply movies info in real-time mode by crawling douban website

(1)
    * sender could select the movie type according to popup movie type list
    * receiver will response with fist 10 movies listed in douban in three sequence mode(hot, time, commend)
(2)
    * sender could select the movie from the movies searched from above operation
    * receiver will response with the specific info of selected movies
"""
import itchat
import douban_crawl


@itchat.msg_register(itchat.content.TEXT, itchat.content.PICTURE)
def simple_reply(msg):
    global movie_info_all
    if u'电影' in msg['Text']:
        douban_object.browser_hotopen()
        douban_object.cvt_cmd_to_ctgy_url(msg['Text'])
        movie_category_option = ' '.join(douban_crawl.movie_category)
        itchat.send_msg('----请选择一种类型----\n' + movie_category_option, msg['FromUserName'])

    elif msg['Text'] in douban_crawl.movie_category:
            itchat.send_msg('正在查找' + msg['Text'] + '电影...', msg['FromUserName'])
            del douban_crawl.command_cache[:]
            douban_crawl.command_cache.append(msg['Text'])
            movie_info_all = douban_object.browser_action_general_info(msg['Text'])
            itchat.send_msg('----按热度排序----\n' + '\n' + '\n'.join(douban_crawl.movie_info_hot), msg['FromUserName'])
            itchat.send_msg('----按时间排序----\n' + '\n' + '\n'.join(douban_crawl.movie_info_time), msg['FromUserName'])
            itchat.send_msg('----按评论排序----\n' + '\n' + '\n'.join(douban_crawl.movie_info_comment), msg['FromUserName'])

    else:
        search_num = 0
        for x in movie_info_all:
            if msg['Text'] in x:
                itchat.send_msg('正在查找' + msg['Text'] + '...', msg['FromUserName'])
                loc = movie_info_all.index(x)
                if 0 <= loc < 10:
                    search_num = 1
                elif 10 <= loc < 20:
                    search_num = 2
                else:
                    search_num = 3
                break
        url_result = douban_object.browser_action_detail_info(search_num, msg['Text'])
        html_result = douban_object.download_detail_info_html(url_result)
        douban_object.parse_detail_info(html_result)
        itchat.send_msg('\n\n'.join(douban_crawl.movie_detail_info), msg['FromUserName'])


if __name__ == '__main__':
    itchat.auto_login(hotReload=True)
    douban_object = douban_crawl.DoubanSpider()
    movie_info_all = []
    itchat.run()


