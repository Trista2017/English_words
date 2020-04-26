# -*- encoding: utf-8 -*- 
''' 
@File : English_words.py 
@Description: 主要功能：背单词，存储单词，检索单词，获取单词发音
@Contact : goaza123@sina.com
@Created info: Susie 2020-04-17 11:29
'''

# -*- coding: utf-8 -*-
from tkinter import Tk, Button, Label, Entry, END, LabelFrame
from tkinter import messagebox
import tkinter.font as font
from random import choice
import pandas as pd
import playsound
import urllib.request
import os
from Sql_connect import Connect
from Log_init import Log

log = Log(os.path.basename('Push_Cards')) #记录打卡情况
bins = Log(os.path.basename('Bin'))        #记录已掌握词汇


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
        try:  # 若词库中有该词，则显示释义并播放声音，否则 提示未收录
            self.Show_Answer()
        except:
            ans.config(text='未收录')
        self.Play_Sound()
    def Show_Answer(self):
        """
        显示单词释义
        """
        global word, ans
        text.configure(text=word)  # 在text控件中显示单词
        l = self.sql.load('word_list where 单词 = \'' + word + '\'')  # 从词库中检索单词
        sstr = lambda s: s or ""  # 将空输入转换为空格
        # 单词有可能因为词性不同，在词库中出现多次，因此每次根据单词在词库中按照where语句进行茶盅，并显示多层释义
        if len(l) == 1:  # 若只有单层释义，直接拼接词性词义等信息
            c = l.iloc[0]
            s = c['词性'] + ' ' + c['词义']
            if c['补充信息'] is not None:
                s = s + '\n' + '\n'.join(c['补充信息'].split(';'))
        elif len(l) == 0:
            raise Exception
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
        if word[0] is ' ' or word[-1] is ' ':
            messagebox.showinfo("提示：", "请检查输入！")
            return
        data = pd.DataFrame({'单词': [word], '词性': [gender], '词义': [meaning], '补充信息': [info]})
        if ' ' in word:  # 根据HTML访问规则，将词组中的空格符号进行替换
            urlword = word.replace(' ', '%20')
        else:
            urlword = word
        self.sql.upload(data, 'word_list', if_exists='append')
        e1.delete(0, END)  # 上传后自动清空输入框文本
        e2.delete(0, END)
        e3.delete(0, END)
        e4.delete(0, END)
        data = self.sql.load('word_list')
        self.word_list = list(set(data['单词']))
        urllib.request.urlretrieve(self.url + urlword,
                                   r'D:\python\py3\interest\English_words\sound\%s.mp3' % word)  # 从接口获取发音并存在本地文件夹
        return

    def Push_Cards(self):
        global A4recite
        s = '\n'
        for widget in A4recite.winfo_children()[:-1]:
            if widget.get() is not '':
                s = s + widget.get() + '\n'
        log.info(s)
        messagebox.showinfo("恭喜", "打卡成功！")

    def Done_Words(self):
        global word, ans
        self.sql.delete('word_list where 单词 = \'' + word + '\'')
        os.remove('sound\%s.mp3' % word)
        data = self.sql.load('word_list')
        self.word_list = list(set(data['单词']))
        ans.configure(text='恭喜，已掌握%s' % word)
        bins.info(word)


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
    global e1, e2, e3, e4, ans, count, text, counter, key, root, A4recite

    # <editor-fold desc="窗体整体设置">
    root = Tk()
    # root.iconbitmap('rainbow.ico')
    root.title('彩虹单词本')
    root.geometry("850x600")
    root.resizable(0, 0)
    # </editor-fold>
    # <editor-fold desc="调用类">
    func = Functions()
    proc = Running_process(func)
    # </editor-fold>
    # <editor-fold desc="背单词模块">
    counter = Label(root, fg='#43A102', anchor='se', font=font.Font(family='Helvetica', size=13, weight="bold"))
    text = Label(root, text='开始背单词吧', font=('Arial', 15, 'bold'), width=20,
                 height=10, wraplength=280)
    ans = Label(root, text='', font=('Arial', 13), width=30, wraplength=280,
                justify='left', height=10, anchor='w')
    Button(root, text="Next", bg='#43A102', fg='white', font=font.Font(family='Helvetica', size=10, weight="bold"),
           width=15, command=func.Next_Random).grid(row=7, column=0, sticky='n')
    Button(root, text="Answer", bg='#A2B700', fg='white', font=font.Font(family='Helvetica', size=10, weight="bold"),
           width=15, command=func.Show_Answer).grid(row=7, column=1, sticky='n')
    counter.grid(row=0, column=0, pady=10)
    text.grid(row=2, column=0, rowspan=4)
    ans.grid(row=2, column=1, rowspan=4, sticky='w', columnspan=2)
    Button(root, text="Sound", bg='#EED205', fg='white', font=font.Font(family='Helvetica', size=10, weight="bold"),
           width=15, command=func.Play_Sound).grid(row=7, column=2, sticky='n')
    Button(root, text="Done it", bg='#cc0000', fg='white', font=font.Font(family='Helvetica', size=10, weight="bold"),
           width=15, command=func.Done_Words).grid(row=7, column=3, sticky='n')
    # </editor-fold>
    # <editor-fold desc="搜索单词模块">
    key = Entry(root)
    Button(root, text="Search", bg='#FF8C05', fg='white', font=font.Font(family='Helvetica', size=10, weight="bold"),
           width=10, command=func.Search_Word).grid(row=0, column=2, pady=10)
    key.grid(row=0, column=1, pady=10)
    # </editor-fold>
    # <editor-fold desc="上传单词模块">
    up_module = LabelFrame(root, text='Upload New Words', height=200, width=260, foreground='#FF8C05',
                           font=font.Font(family='Helvetica', size=10, weight="bold"), relief='ridge')
    up_module.grid(column=3, row=2, rowspan=4, columnspan=2, padx=20, pady=10, ipadx=5, ipady=10, sticky='s')
    # up_module.grid_propagate(False)
    Label(up_module, text="单词：").place(x=75, y=20, anchor="e")
    Label(up_module, text="词性：").place(x=75, y=60, anchor="e")
    Label(up_module, text="词义：").place(x=75, y=100, anchor="e")
    Label(up_module, text="补充信息：").place(x=75, y=140, anchor="e")

    e1 = Entry(up_module)
    e2 = Entry(up_module)
    e3 = Entry(up_module)
    e4 = Entry(up_module)

    Button(up_module, bg='#FDD283', fg='white', font=font.Font(family='Helvetica', size=10, weight="bold"),
           text="Upload", width=15, command=func.Add_Words).place(x=60, y=180, anchor="w")

    e1.place(x=80, y=20, anchor="w")
    e2.place(x=80, y=60, anchor="w")
    e3.place(x=80, y=100, anchor="w")
    e4.place(x=80, y=140, anchor="w")
    # </editor-fold>
    # <editor-fold desc="A4纸背单词模块">
    A4recite = LabelFrame(root, text='20 Words One Day Challenge', height=200, width=750, foreground='#43A102',
                          font=font.Font(family='Helvetica', size=10, weight="bold"), relief='ridge')
    A4recite.grid(column=0, row=8, rowspan=4, columnspan=6, padx=50, pady=20, ipadx=5, ipady=10, sticky='s')

    e2k = Entry(A4recite)
    e20 = Entry(A4recite)
    e301 = Entry(A4recite)
    e22 = Entry(A4recite)
    e101 = Entry(A4recite)
    e23 = Entry(A4recite)
    e24 = Entry(A4recite)
    e401 = Entry(A4recite)
    e31 = Entry(A4recite)
    e41 = Entry(A4recite)
    e40 = Entry(A4recite)
    e21 = Entry(A4recite)
    e25 = Entry(A4recite)
    e10 = Entry(A4recite)
    e501 = Entry(A4recite)
    e50 = Entry(A4recite)
    e30 = Entry(A4recite)
    e201 = Entry(A4recite)
    e11 = Entry(A4recite)
    e51 = Entry(A4recite)
    e50.place(x=350, y=180, anchor="w")
    e101.place(x=520, y=20, anchor="w")
    e301.place(x=520, y=100, anchor="w")
    e30.place(x=350, y=100, anchor="w")
    e22.place(x=10, y=60, anchor="w")
    e23.place(x=10, y=100, anchor="w")
    e31.place(x=180, y=100, anchor="w")
    e41.place(x=180, y=140, anchor="w")
    e501.place(x=520, y=180, anchor="w")
    e10.place(x=350, y=20, anchor="w")
    e51.place(x=180, y=180, anchor="w")
    e25.place(x=10, y=180, anchor="w")
    e201.place(x=520, y=60, anchor="w")
    e40.place(x=350, y=140, anchor="w")
    e2k.place(x=10, y=20, anchor="w")
    e11.place(x=180, y=20, anchor="w")
    e401.place(x=520, y=140, anchor="w")
    e20.place(x=350, y=60, anchor="w")
    e21.place(x=180, y=60, anchor="w")
    e24.place(x=10, y=140, anchor="w")

    Button(A4recite, bg='#A2B700', fg='white', font=font.Font(family='Helvetica', size=10, weight="bold"),
           text="Push", width=8, command=func.Push_Cards).place(x=676, y=100, anchor="w")
    # </editor-fold>
    # <editor-fold desc="键盘响应模块">
    btn = Button(root, text='button')
    btn.bind_all('<KeyPress>', proc.eventhandler)
    # </editor-fold>
    root.mainloop()  # 进入消息循环


if __name__ == '__main__':
    main()
