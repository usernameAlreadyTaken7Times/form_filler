import jieba

def tokenize(text):
    return jieba.lcut(text)


a = tokenize('八百标兵奔北坡，北坡炮兵并排跑')
pass
