# /usr/bin/env python3
# coding: utf-8
import os
import time
import logging
#from xpinyin import Pinyin


class Pattern(object):
    def __init__(self, column_num, column_delimiter, header):
        """
        构造一个 Word list 的样式
        :param column_num: 列数
        :param column_delimiter: 列分隔符
        :param header: 是否有头
        """
        self.column_num = column_num
        self.column_delimiter = column_delimiter
        self.header = header


class WordList(object):
    def __init__(self, file_name, pattern=Pattern(1, ' ', False), predata_file=None):
        self.file_name = file_name
        self.pattern = pattern
        self.content = list()
        self.index = 2
        self.predata_file = predata_file

        start_time = time.time()

        # 根据读取 list
        if os.path.exists(self.file_name):
            self.__build_word_list(self.file_name)
        # d_dict = dict()
        # if predata_file is not None:
        #     with open(predata_file, "r") as f:
        #         json_content = f.read()
        #     d_dict = json.loads(json_content)

        # conn = sqlite3.connect('D:\dev\svn\dataplatform\\trunk\src\servers\pandora_analysis\predata\\test.db')
        # print("Opened database successfully")
        # c = conn.cursor()

        # 增加汉字拼音，同音字，形近字，繁体字
        #修改
        #lens = len(self.content)
        #py = Pinyin()
        # for i in range(lens):
        #     columns = self.content[i]
        #     words = columns[0]
        #     add_words = []
        #     for w in words:
        #         w_p = py.get_pinyin(w, "")
        #         a_list = []
        #         if w == w_p:
        #             a_list.append(w)
        #         else:
        #             a_list.extend([w, w_p])
        #         if d_dict.get(w):
        #             a_list.extend(d_dict[w])
        #         add_words.append(a_list)
        #     for pd in itertools.product(*add_words):
        #         new_word = "".join(pd)
        #         # if new_word != words:
        #         print("word index {}".format(self.index))
        #         c.execute("INSERT INTO COMPANY (ID,WORDS,DOMAIN,WEIGHT) \
        #               VALUES ({0}, '{1}', '{2}', {3} )".format(self.index, new_word, columns[1], columns[2]))
        #         self.index += 1
                # self.content.append([new_word, columns[1], columns[2]])
        # conn.commit()
        # conn.close()

        # for i in range(lens):
        #     columns = self.content[i]
        #     words = columns[0]
        #     for j, w in enumerate(words):
        #         w_p = py.get_pinyin(w, "")
        #         if w != w_p:
        #             n_wd = list(copy.deepcopy(columns[0]))
        #             n_wd[j] = w_p
        #             self.content.append(["".join(n_wd), columns[1], columns[2],  "{0}{1}".format(words, "<拼音>")])
                # if d_dict.get(w):
                #     n_wd = list(copy.deepcopy(columns[0]))
                #     for ty, klist in d_dict[w].items():
                #         for kw in klist:
                #             n_wd[j] = kw
                #             change_type = {"繁": "繁体", "形": "形变", "音": "同音"}[ty]
                #             self.content.append(["".join(n_wd), columns[1], columns[2],
                #                                  "{0}{1}".format(words, "<{}>".format(change_type))])
        logging.info("dict add cost {}s".format(time.time()-start_time))

    def __getitem__(self, item):
        return self.content[item]

    def __len__(self):
        return len(self.content)

    def __build_word_list(self, file_name):
        if os.path.isfile(file_name):
            self.__get_word_list(file_name, self.pattern)
        elif os.path.isdir(file_name):
            for file in os.listdir(file_name):
                new_file_path = os.path.join(file_name, file)
                self.__build_word_list(new_file_path)

    def __get_word_list(self, file_name, pattern):
        # self.content = []

        with open(file_name, encoding="utf-8") as wf:
            first_line = True
            for line in wf:
                # 处理特殊字符
                line = line.strip()
                if len(line) < 1:
                    continue

                # 有表头的情况下跳过第一行
                if pattern.header and first_line:
                    first_line = False
                    continue

                if pattern.column_num == 1:

                    # 如果转成 Unicode 会慢很多, 差了10倍....
                    # words_str = unicode(words_str, 'utf-8')

                    self.content += [c for c in line.split(pattern.column_delimiter) if c]
                else:
                    columns = [c for c in line.split(pattern.column_delimiter) if c]
                    columns.append("")
                    self.content.append(columns)

    def get_word_list(self):
        return self.content


def get_word_list(filename):
    wl = WordList(filename)
    return wl.get_word_list()
