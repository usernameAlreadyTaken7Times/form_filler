# ~~FormFiller 表格填充助手~~(已弃用，请转到[form_filler_new](https://github.com/usernameAlreadyTaken7Times/form_filler_new))

## 项目简介
本项目旨在实现根据当前复制字段自动在剪贴板填充对应文字的功能。通过该项目，可以在填充表格等重复性较高的场景提高操作效率。

## 功能特点
- 功能 1：快速调用数据并在指定位置粘贴
- 功能 2：通过语言模型 (Word2Vec) 寻找同义词并匹配字段（仍在开发中）

## 技术栈
- python 版本：3.12
- GUI：tkinter，用于创建图形界面
- Service: Fastapi & Uvicorn，用于构建和运行 api 服务
- Database: .xlsx & .csv，用于存储数据

## 使用方法

### 前提条件
- python == 3.12
(理论上 3.9 以后都可以尝试，3.13 会有 scipy 构建问题)

### 安装步骤
1. 克隆本项目到本地或直接下载 ZIP 包：

```bash
git clone https://github.com/usernameAlreadyTaken7Times/form_filler
```

2. 进入项目目录：

```bash
cd formfiller/
```

3. (a) 构建并启动 conda 或 venv 虚拟环境，并从 requirements.txt 安装依赖。

```bash
# 新建并使用venv虚拟环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1 (Windows)
# conda环境：略
```

```bash
pip install -r requirements.txt
```

3. (b) 如希望使用语言模型，则可下载支持 Word2Vec 的中文模型并置于 formfiller/asset/models/目录，如[fasttext](https://fasttext.cc/)或[Chinese Word Vectors](https://github.com/Embedding/Chinese-Word-Vectors)([下载地址 1](https://drive.google.com/open?id=1kSAl4_AOg3_6ayU7KRM0Nk66uGdSZdnk)或[下载地址 2](https://drive.google.com/open?id=1kSAl4_AOg3_6ayU7KRM0Nk66uGdSZdnk)在页面内)。
随后更改 convert.py 脚本内必要参数 (如名称和地址) 并运行，储存为 bin 模式，用于程序加载。

```bash
cd asset/models/
# fasttext中文模型
curl "https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.zh.300.vec.gz"

# 也可下载Chinese Word Vectors中文模型，包含了Word, Character和Ngram

python convert.py

# 验证.bin文件和.npy文件（如有必要）
file <model_name>.bin && file <model_name>.npy
```

4. 回到目录，更改 main.py 的语言模型路径并运行项目：

```bash
cd ../../
# 更改语言路径：略
python main.py
```
## 实现原理
- 通过 Word2Vec 加载语言模型
- 通过 keyboard 监听 Ctrl+C 复制键，通过 pyperclip 读写剪贴板和键值
- 通过 fastapi 构建语言模型和分割语句的 api，并用 uvicorn 构建服务

## 操作过程
- 启动程序，根据用户选择是否加载语言模型
- 程序读取数据文件里的信息并创建字典，启动服务
- 当选中屏幕字段并按下 Ctrl+C 时，程序读取字段并尝试在字典里匹配
- 如果在字典内匹配到则直接返回对应的键值；如果未匹配到则
    - 返回'-'（不使用语言模型时）
    - 尝试寻找近义词，近义词匹配则返回对应键值，未匹配则返回'-'（使用语言模型时）
- 卸载语言模型并关闭服务

## 项目结构

```
FormFiller/
├── scripts/ # 源代码文件夹
│   ├── main.py # 主程序脚本
│   ├── xxx.py # 其他相关脚本文件
│   ├── synonyms_server/ # 与Fastapi和Uvicorn相关服务部分
│   │   ├── convert.py # 转换Word2Vec模型到.bin格式
│   │   ├── model.py # 语言模型服务
│   │   └── xxx.py # 其他相关脚本文件
├── asset/ # 其他资源
│   ├── data/ # 数据文件夹
│   │   ├── csv_database.csv # CSV数据文件
│   │   └── xlsx_database.xlsx # XLSX数据文件
│   ├── models/ # 语言模型文件夹
│   │   ├── models.bin # 语言模型
│   │   ├── models.npy # 语言模型组件
│   │   └── xxx.xx # 其他语言模型
│   └── test_doc/ # 测试表格
│       └── test_form.docx # 用于测试的示例表格文件
├── readme.md # 本介绍文档
└── requirements.txt # 依赖文件
```

## 贡献指南
如果您【真的】想为本项目贡献代码【请认真三思】，请按照以下步骤操作：
1. Fork 本仓库
2. 创建分支：`git checkout -b feature-branch`
3. 提交代码：`git commit -m "添加了xx功能"`
4. 推送分支：`git push origin feature-branch`
5. 提交 Pull Request

(写得烂成天坑，想来不会有人愿意改的，库里吃灰去吧)

## FAQ
TBD