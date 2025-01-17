import pyperclip
import csv
from itertools import chain
from synonyms_server.request_from_api import get_synonyms
from synonyms_server.request_from_api import tokenize_text
from synonyms_server.request_from_api import remove_punctuation

def PreDataHandler_csv(path):
    '''预处理数据，将csv文件转换为字典格式，方便后续处理'''
    with open(path, 'r', encoding='GB2312') as f:
        reader = csv.DictReader(f)
        data = {}
        for row in reader:
            data[row["姓名"]] = row
        
        for person in data.values():
            person["无匹配字段"] = '-' # 添加一个无匹配字段，用于标记无匹配字段
    
    return data

def PreDataHandler_xlsx(path):
    '''预处理数据，将xlsx文件转换为字典格式，方便后续处理'''
    import pandas as pd
    # 读取 Excel 文件
    df = pd.read_excel(path)
    # 替换整个 DataFrame 中的 `_x000D_`
    df = df.map(lambda x: x.replace('_x000D_\n', '').strip() if isinstance(x, str) else x)

    # 将数据恢复为字典，并添加 "姓名" 键值对
    data_dict = {
        row['姓名']: {
            **row.to_dict(),  # 将行数据转为字典
            "姓名": row['姓名'],  # 显式添加姓名字段
            "无匹配字段": '-'  # 添加额外的 "-": "-"
        }
        for _, row in df.iterrows()
    }
    return data_dict

def get_model_status():
    pass


class DataHandler:
    def __init__(self, dict_data):
        # 字典数据格式：{人物名: {字段名: 字段值}}
        self.data = dict_data
        self.current_person = self.get_first_person()
        self.current_field_index = 0
        self.model_status = False
        self.host = '127.0.0.1'
        self.port = '8000'
    
    def run(self):
        pass

    def set_model_status(self, model_status):
        """Set the model status to the given value."""
        self.model_status = model_status
    def set_model_host(self, host):
        """Set the host address for the model."""
    def set_model_host(self, host): # 外部变量直接更改类状态
        self.host = host
    def set_model_port(self, port):
        """Set the model port to the given value."""
    def set_model_port(self, port): # 外部变量直接更改类状态
        self.port = port

    def get_first_person(self):
        return next(iter(self.data))

    def get_all_persons(self):
        return list(self.data.keys())

    def select_person(self, person, ui_updater=None):
        self.current_person = person
        self.current_field_index = 0
        if ui_updater:
            ui_updater.update_ui()

    def get_current_person(self):
        return self.current_person

    def get_current_field(self):
        field_keys = list(self.data[self.current_person].keys())
        return field_keys[self.current_field_index]

    def get_current_value(self):
        return self.data[self.current_person][self.get_current_field()]

    def switch_field(self, direction):
        field_keys = list(self.data[self.current_person].keys())
        self.current_field_index = (self.current_field_index + direction) % len(field_keys)
        # 将当前字段值复制到剪贴板
        self.copy_field_value(field_keys[self.current_field_index])

    def switch_character(self, direction):
        person_keys = list(self.data.keys())
        current_person_index = person_keys.index(self.current_person)
        new_person_index = (current_person_index + direction) % len(person_keys)
        self.select_person(person_keys[new_person_index])
        # 将当前字段值复制到剪贴板
        self.copy_field_value(self.get_current_field())

    def copy_field_value(self, field_name):
        '''根据字段名称复制值到剪贴板'''

        # 去除字段名中的标点符号
        field_name = remove_punctuation(field_name)

        """根据字段名称复制值到剪贴板"""
        if field_name in self.data[self.current_person]: # 如果字段完全匹配
            value = self.data[self.current_person][field_name]
            pyperclip.copy(value)
            print(f"字段 '{field_name}' 的值 '{value}' 已复制到剪贴板。")
            self.current_field_index = list(self.data[self.current_person].keys()).index(field_name)
        else:
            if not self.model_status: # 如果模型未运行，且字段不存在 
                print(f"字段 '{field_name}' 不存在")
                self.current_field_index = -1 # 无匹配字段索引设为-1
                pyperclip.copy('-') # 无匹配字段值设为'-'
            else: # 如果模型正在运行，则尝试通过模型寻找近义词并在数据库里匹配
                print(f"字段 '{field_name}' 不存在，尝试通过模型寻找近义词。")

                # 这里需要调用模型的接口，获取近义词
                # 切割字段名 
                field_name_tokens = tokenize_text(self.host, self.port, field_name)["tokens"]
                depth = 1
                try:
                    '''获取字段名的分词深度，最高为3，更高的深度会极大加深计算复杂度.
                    例如：在默认寻找4个同义词时，“年龄”分词深度为1，匹配近义词有1*4=4个；
                    “项目经历”分词深度为2，匹配近义词有1*(4*4)+2*4=24个；
                    “学术论文成果”分词深度为3，匹配近义词有1*(4*4*4)+2*(4*4)+3*4=108个。
                    以上情况均未考虑词组间的位置关系，例如ab=>b'a'和a'b'，这种情况会使匹配数量翻倍。
                    '''
                    depth = len(field_name_tokens) 
                    
                except Exception as e:
                    print(f"Error: {e}") # 输出错误信息

                synonyms_list = [] # 用于存储近义词

                # 根据分词深度匹配近义词 必须承认，这tm是个脑瘫设计，我写的足够丑陋，但是我不想改了
                match depth:
                    case 1:
                        # 一级分词
                        synonyms_list = get_synonyms(self.host, self.port, field_name, top_n=10)['synonyms'] # 一级默认寻找10个同义词, 4个同义词不够用
                    case 2:
                        # 二级分词
                        synonyms_1 = get_synonyms(self.host, self.port, field_name_tokens[0])['synonyms'] # 写个毛循环 不写了
                        synonyms_2 = get_synonyms(self.host, self.port, field_name_tokens[1])['synonyms']

                        if synonyms_1:
                            synonyms_list = list(chain(synonyms_list, synonyms_1))
                        if synonyms_2:
                            synonyms_list = list(chain(synonyms_list, synonyms_2))
                        
                        tmp_list = [x+y for x in synonyms_1 for y in synonyms_2]
                        tmp_list_reverse = [y+x for x in synonyms_1 for y in synonyms_2] # 逆序

                        synonyms_list = list(chain(synonyms_list, tmp_list))
                        synonyms_list = list(chain(synonyms_list, tmp_list_reverse))
                        del tmp_list, tmp_list_reverse, synonyms_1, synonyms_2

                    case 3:
                        # 三级分词
                        synonyms_1 = get_synonyms(self.host, self.port, field_name_tokens[0])['synonyms']
                        synonyms_2 = get_synonyms(self.host, self.port, field_name_tokens[1])['synonyms']
                        synonyms_3 = get_synonyms(self.host, self.port, field_name_tokens[2])['synonyms']

                        if synonyms_1:
                            synonyms_list = list(chain(synonyms_list, synonyms_1))
                        if synonyms_2:
                            synonyms_list = list(chain(synonyms_list, synonyms_2))
                        if synonyms_3:
                            synonyms_list = list(chain(synonyms_list, synonyms_3))

                        tmp_list_level3a = [x+y+z for x in synonyms_1 for y in synonyms_2 for z in synonyms_3]
                        tmp_list_level3b = [x+y+z for x in synonyms_1 for y in synonyms_3 for z in synonyms_2]
                        tmp_list_level3c = [x+y+z for x in synonyms_2 for y in synonyms_3 for z in synonyms_1]
                        tmp_list_level3d = [x+y+z for x in synonyms_2 for y in synonyms_1 for z in synonyms_3]
                        tmp_list_level3e = [x+y+z for x in synonyms_3 for y in synonyms_1 for z in synonyms_2]
                        tmp_list_level3f = [x+y+z for x in synonyms_3 for y in synonyms_2 for z in synonyms_1]

                        tmp_list_level2a = [x+y for x in synonyms_1 for y in synonyms_2]
                        tmp_list_level2b = [x+y for x in synonyms_2 for y in synonyms_3]
                        tmp_list_level2c = [x+y for x in synonyms_1 for y in synonyms_3]
                        tmp_list_level2d = [y+x for x in synonyms_2 for y in synonyms_1]
                        tmp_list_level2e = [y+x for x in synonyms_3 for y in synonyms_2]
                        tmp_list_level2f = [y+x for x in synonyms_3 for y in synonyms_1]    

                        synonyms_list = list(chain(synonyms_list, tmp_list_level3a))
                        synonyms_list = list(chain(synonyms_list, tmp_list_level3b))
                        synonyms_list = list(chain(synonyms_list, tmp_list_level3c))
                        synonyms_list = list(chain(synonyms_list, tmp_list_level3d))
                        synonyms_list = list(chain(synonyms_list, tmp_list_level3e))    
                        synonyms_list = list(chain(synonyms_list, tmp_list_level3f))
                        synonyms_list = list(chain(synonyms_list, tmp_list_level2a))
                        synonyms_list = list(chain(synonyms_list, tmp_list_level2b))
                        synonyms_list = list(chain(synonyms_list, tmp_list_level2c))
                        synonyms_list = list(chain(synonyms_list, tmp_list_level2d))
                        synonyms_list = list(chain(synonyms_list, tmp_list_level2e))
                        synonyms_list = list(chain(synonyms_list, tmp_list_level2f))                        

                        del tmp_list_level3a, tmp_list_level3b, tmp_list_level3c, tmp_list_level3d, tmp_list_level3e, tmp_list_level3f
                        del tmp_list_level2a, tmp_list_level2b, tmp_list_level2c, synonyms_1, synonyms_2, synonyms_3


                # 遍历字段名的分词结果，并将所有可能的近义词都尝试在数据库中匹配
                for synonym in synonyms_list:
                    if synonym in self.data[self.current_person]:
                        value = self.data[self.current_person][synonym]
                        print(f"已通过模型找到 '{field_name}' 的匹配字段 '{synonym}'。值 '{value}' 已复制到剪贴板。")
                        pyperclip.copy(value)
                        self.current_field_index = list(self.data[self.current_person].keys()).index(synonym)
                        break
                    print(f"找到'{field_name}'的近义词'{synonym}'，但并非匹配字段。")
                    self.current_field_index = -1
                    pyperclip.copy('-')
                    
