from gensim.models import KeyedVectors

def convert_model(path, save_path):
    try:
        print('start converting...')
        model = KeyedVectors.load_word2vec_format(path, binary=False)
        print('Convert finish. Saving to new path.')
        model.save(save_path)
        print('Save finish.')
    except Exception as e:
        print(f"Failed to load model: {e}")

model_path = r'C:\Users\86781\VS_Code_Project\test\scripts\models\merge_sgns_bigram_char300.txt'
save_path = r'C:\Users\86781\VS_Code_Project\test\scripts\models\merge_sgns_bigram_char300.txt.bin'
convert_model(model_path, save_path)
pass
