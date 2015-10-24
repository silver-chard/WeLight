#!/usr/bin/python
#coding=utf-8

import os
import xml.etree.ElementTree as Etree
import time
import hashlib


# 判断是否有get传递过来
def have_get():
    return os.environ.has_key('QUERY_STRING')


# 判断是否有post传递过来
def have_post():
    return os.environ.get('REQUEST_METHOD') == "POST"


# 初始化数据
# 主要是 获取 get信息 post信息 并且将信息装入字典返回
def init():
    xml_str = ''

    if have_get():
        get_str = os.environ.get('QUERY_STRING')
        get_tuple = get_str.split('&')

    if have_post():
        data = raw_input()
        while not data == "":
            if data == "<br>":
                xml_str += '\n'
            else:
                xml_str = xml_str + data
            try:
                data = raw_input()
            except:
                data = ''
        fh = open("recive", "w")
        fh.write(xml_str)
        fh.close()
    get_dict = {}
    post_dict = {}

    if have_get():
        i = 0
        while i < len(get_tuple):
            temp = get_tuple[i].split('=')
            get_dict[temp[0]] = temp[1]
            i += 1

    if have_post():
        try:
            xml_tree = Etree.fromstring(xml_str)
            for child in xml_tree:
                post_dict[child.tag] = child.text
        except:
            print "error theres no xml info"
    tree_dic = {'get': None, 'post': None}
    if have_get():
        tree_dic['get'] = get_dict
    if have_post():
        tree_dic['post'] = post_dict

    return tree_dic


# 检查post信息中的数据是否正确
def check(rdict, token):
    ch_list = [rdict.get('get').get('timestamp'), rdict.get('get').get('nonce'), token]
    ch_list.sort()
    ch_str = ch_list[0] + ch_list[1] + ch_list[2]
    return hashlib.sha1(ch_str).hexdigest() == rdict.get('get').get('signature')


# 开灯操作
def open_light():
    flag = "open"
    light_file = open("light_flag.html", "w")
    light_file.write(flag)
    light_file.close()


# 关灯操作
def shut_light():
    flag = "shut"
    light_file = open("light_flag.html", "w")
    light_file.write(flag)
    light_file.close()


# 分析字符串是否包含需要的值并且调用相关的函数去给树莓派传递信息
def analyze_str(r_str):
    flag = -1
    if r_str.find('开灯') != -1:
        open_light()
        flag = 1
    if r_str.find('关灯') != -1:
        shut_light()
        flag = 0
    return flag


# 发送信息函数 负责返回信息给用户 调用分析字符串
# todo：待解决 返回给微信的xml信息理论上正确 却无法引发微信回复给用户消息
# todo: 可能与回复的信息并不是xml而是单纯的字符串有关？ 待验证
def sendmsg(rdict):
    # 如果post有数据
    reply_str = u''
    if rdict.get('post') is not None:
        reply_str = "<xml><ToUserName><![CDATA[%s]]></ToUserName>" % rdict.get('post').get('ToUserName')
        reply_str += "<FromUserName><![CDATA[%s]]></FromUserName>" % rdict.get('post').get('FromUserName')
        reply_str += "<CreateTime>%d</CreateTime>" % int(time.time() + 1)
        # 编辑xml文件字符串
        r_str = u''

        if rdict.get('post').get('MsgType') == "voice":  # 如果收到的是voice类型
            if rdict.get('post').has_key('Recognition'):  # 是否有语音转文字结果
                r_str = rdict.get('post').get('Recognition')
                flag = analyze_str(r_str)
                if flag == 1:
                    r_str = "灯已开"
                elif flag == 0:
                    r_str = "灯已关"
                elif flag == -1:
                    r_str += " 是什么玩意？！"
            elif rdict.get('post').get('Recognition') is None:  # 如果没有语音识别结果
                r_str = "Sorry 我没听清 O_O?"

        if rdict.get('post').get('MsgType') == "text":  # 如果是文本类型的
            r_str=rdict.get("post").get("Content")
            flag = 0
            flag = analyze_str(r_str)
            if flag == 1:
                r_str = "灯已开".encode('utf-8')
            elif flag == 0:
                r_str = "灯已关".encode('utf-8')
            elif flag == -1:
                r_str += " 是什么玩意？！"

        reply_str += '<MsgType><![CDATA[text]]></MsgType>'
        reply_str += "<Content><![CDATA[%s]]></Content></xml>" % r_str

        reply_str +="\n"
    else:
        reply_str += "didnt get post at all"

    return reply_str


# 主函数
def main():
    token = u'silverWeChat'
    back = ''
    # 写入头
    if have_post() is False:
        back = u"Content-type:text/html\n\n"
    elif have_post() is True:
        back = u"Content-type:text/xml\n\n"

    # 获得腾讯发过来的提交信息
    rdict = init()

    # 检查token正确与否 正确的话 加入echostr
    if rdict.get('get') is not None and check(rdict, token) is True and rdict.get('get').has_key('echostr'):
        back += rdict.get('get').get('echostr').decode('unicode_escape')
        back += "\n"

    # 写入sent文件
    fh = open("sent", "w")
    fh.write(back)
    fh.close()
    back=back
    # 编写回执信息
    if have_post() is True:
        back += sendmsg(rdict)
        back += "\n"

    # 写入sent文件
    fh = open("sent", "w")
    fh.write(back)
    fh.close()

    print back.encode('utf-8')


# 执行开端

light = open("light_flag.html", "w")
light.write("nothing")
light.close()
main()
