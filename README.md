# Words_Book
最近在学英语，新单词需要反复背，所以就想写一个可以自己存储单词的应用。在开始写之前搜索了一下有没有人已经做好了，只查到一篇文章有比较相关的思路，但是功能只有随机抽取单词，以及需要从外部构建好CSV表格导入进去，不够方便，所以得自己写了。刚好tkinter也一直没有学过，就趁这次的机会边学边写。

具体文档可见：https://blog.csdn.net/goaza123/article/details/105612941

主程序为English_words.py，程序主要分为三个功能区，分别是：

  Search模块：用于检索词库中的单词
  Upload模块：用于向词库加入新单词
  Next模块：用于背单词，由Next和Answer两个按键共同实现

需要用的工具有：
  python 3.6
  postgreSQL（用于存储词库，也可以用excel，但是响应速度慢，个人不建议）

需要安装的python包
  tkinter：构建python中的Gui窗体
  sqlalchemy：用于sql的连接
  playsound：播放单词发音
  urllib.request：从有道的API接口获取单词发音
  pyinstaller：将py文件打包成exe
