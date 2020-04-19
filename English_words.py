# -*- encoding: utf-8 -*- 
''' 
@File : English_words.py 
@Description: 主要功能：背单词，存储单词，检索单词，获取单词发音
@Contact : goaza123@sina.com
@Created info: Susie 2020-04-17 11:29
'''

# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import messagebox
from random import choice
import pandas as pd
import playsound
import tkinter.font as font
from Sql_connect import Connect
import urllib.request


class Functions():
    def __init__(self):
        self.count = 0  # 用于单词计数
        self.sql = Connect('English_words')  # 数据库连接
        self.url = 'http://dict.youdao.com/dictvoice?type=0&audio='  # 有道云单词发音API
        data = self.sql.load('word_list')
        self.word_list = list(set(data['单词']))  # 词库单词列表

    def Next_Random(self):
        '''
        从词库中随机抽取单词
        '''
        global text, word, counter, url, ans
        self.count += 1
        word = choice(self.word_list)  # 随机选择一个词
        text.configure(text=word)  # 在text控件中显示单词
        counter.configure(text='第' + str(self.count) + '个单词')  # 在counter控件中显示计数
        ans.config(text='')
        root.update_idletasks()
        try:  # 尝试播放单词发音
            self.Play_Sound()
        except:
            pass

    def Search_Word(self):
        '''
        在词库中检索单词并返回释义、发音
        '''
        global key, word
        word = key.get().lower()  # 从key控件中获取输入
        text.configure(text=word)  # 在text控件中显示单词
        try:  # 若词库中有该词，则显示释义并播放声音，否则 提示未收录
            self.Show_Answer()
            self.Play_Sound()
        except:
            ans.config(text='未收录')

    def Show_Answer(self):
        """
        显示单词释义
        """
        global word, ans
        l = self.sql.load('word_list where 单词 = \'' + word + '\'')  # 从词库中检索单词
        sstr = lambda s: s or "" #将空输入转换为空格
        # 单词有可能因为词性不同，在词库中出现多次，因此每次根据单词在词库中按照where语句进行茶盅，并显示多层释义
        if len(l) == 1:  # 若只有单层释义，直接拼接词性词义等信息
            c = l.iloc[0]
            s = c['词性'] + ' ' + c['词义']
            if c['补充信息'] is not None:
                s = s + '\n' + '\n'.join(c['补充信息'].split(';'))
        else:  # 否则，依次拼接词性词义等信息
            s = ''
            for k, c in l.iterrows():
                s = s + str(k + 1) + '. ' + sstr(c['词性']) + ' ' + sstr(c['词义'])
                if c['补充信息'] is not None:
                    s = s + '\n   ' + '\n   '.join(c['补充信息'].split(';'))
                s += '\n'
        ans.configure(text=s)
        root.update_idletasks()

    def Play_Sound(self):
        """
        播放单词发音
        """
        global word
        playsound.playsound(u'D:\\python\\py3\\interest\\English_words\\sound\\' + word + u'.mp3')

    def Add_Words(self):
        """
        向词库增加新单词
        """
        global e1, e2, e3, e4, text, word, counter, ans
        word = e1.get().lower()  # 为方便大小写输入，将词库中单词统一为小写字母
        gender = e2.get()
        meaning = e3.get()
        info = e4.get()
        if word is '':
            messagebox.showinfo("提示：", "请先输入内容！")
            return
        data = pd.DataFrame({'单词': [word], '词性': [gender], '词义': [meaning], '补充信息': [info]})
        if ' ' in word:  # 根据HTML访问规则，将词组中的空格符号进行替换
            urlword = word.replace(' ', '%20')
        else:
            urlword = word
        urllib.request.urlretrieve(self.url + urlword,
                                   r'D:\python\py3\interest\English_words\sound\%s.mp3' % word)  # 从接口获取发音并存在本地文件夹
        self.sql.upload(data, 'word_list', if_exists='append')
        e1.delete(0, END)  # 上传后自动情况输入框文本
        e2.delete(0, END)
        e3.delete(0, END)
        e4.delete(0, END)
        data = self.sql.load('word_list')
        self.word_list = list(set(data['单词']))
        return


class Running_process():
    def __init__(self, func):
        self.func = func

    def eventhandler(self, event):
        """
        :param event:键盘事件
        :return: 响应键盘事件
        """
        if event.keysym == 'Up':
            self.func.Add_Words()
            e1.focus_set()
        elif event.keysym == 'Down':
            self.func.Next_Random()
        elif event.keysym == 'Return':
            self.func.Search_Word()
        elif event.keysym == 'space':
            self.func.Show_Answer()


def main():
    '''
    word: 当前检索单词
    root: TK窗体
    counter: 计数器显示控件
    text: 单词文本显示控件
    ans: 单词释义显示控件
    key： 单词检索输入控件
    e1, e2, e3, e4: 新单词输入控件
    :return: 窗体构建与功能实现
    '''
    global e1, e2, e3, e4, ans, count, text, counter, key, root
    # ======窗体基本设置=========================================
    root = Tk()
    root.iconbitmap('rainbow.ico')
    root.title('彩虹单词本')
    root.geometry("850x350")
    root.resizable(0, 0)
    # ======调用类==============================================
    func = Functions()
    proc = Running_process(func)
    # ======背单词模块===========================================
    counter = Label(root, fg='red', anchor='se', font=('Arial', 13))
    text = Label(root, text='开始背单词吧', font=('Arial', 15, 'bold'), width=20,
                 height=10, wraplength=280)
    ans = Label(root, text='', font=('Arial', 13), width=30, wraplength=280,
                justify='left', height=10, anchor=W)
    Button(root, text="Next", bg='#43A102', fg='white', font=font.Font(family='Helvetica', size=10, weight="bold"),
           width=15, command=func.Next_Random).grid(row=7, column=0)
    Button(root, text="Answer", bg='#A2B700', fg='white', font=font.Font(family='Helvetica', size=10, weight="bold"),
           width=15, command=func.Show_Answer).grid(row=7, column=1)
    counter.grid(row=1, column=0)
    text.grid(row=3, column=0, rowspan=4)
    ans.grid(row=3, column=1, rowspan=4, sticky=W, columnspan=2)
    Button(root, text="Sound", bg='#EED205', fg='white', font=font.Font(family='Helvetica', size=10, weight="bold"),
           width=15, command=func.Play_Sound).grid(row=7, column=2)
    # =======搜索单词模块========================================
    Label(root, text="搜索单词：", anchor=E).grid(row=0, column=0)
    key = Entry(root)
    Button(root, text="Search", bg='#FF8C05', fg='white', font=font.Font(family='Helvetica', size=10, weight="bold"),
           width=15, command=func.Search_Word).grid(row=0, column=2)
    key.grid(row=0, column=1)
    # =======上传单词模块========================================
    Label(root, text="请输入单词：").grid(row=3, column=3)
    Label(root, text="请输入词性：").grid(row=4, column=3)
    Label(root, text="请输入词义：").grid(row=5, column=3)
    Label(root, text="请输入补充信息：").grid(row=6, column=3)

    e1 = Entry(root)
    e2 = Entry(root)
    e3 = Entry(root)
    e4 = Entry(root)
    upload = Button(root, bg='#FDD283', fg='white', font=font.Font(family='Helvetica', size=10, weight="bold"),
                    text="Upload", width=15, command=func.Add_Words).grid(row=7, column=3, columnspan=2)

    e1.grid(row=3, column=4)
    e2.grid(row=4, column=4)
    e3.grid(row=5, column=4)
    e4.grid(row=6, column=4)

    # ========键盘响应模块========================================
    btn = Button(root, text='button')
    btn.bind_all('<KeyPress>', proc.eventhandler)
    # =============================================================
    root.mainloop()  # 进入消息循环


if __name__ == '__main__':
    main()
