import requests
import re

# Function to get synonyms of a word
def get_synonyms(host, port, word, top_n=4):
    url = f"http://{host}:{port}/synonyms/{word}"
    params = {"top_n": top_n}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Function to tokenize a texts
def tokenize_text(host, port, text):
    url = f"http://{host}:{port}/tokenize"
    params = {"text": text}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Function to remove punctuation from Chinese text
def remove_punctuation(text):
    """
    Function to remove punctuation from Chinese text
    :param text: input Chinese text
    :return: text without punctuation
    """
    # Define the pattern of Chinese punctuation
    punctuation = r"[。，、？！；：‘’“”（）【】《》〈〉—…·,.\?!;:'\"\(\)\[\]<>~\-]"
    result = re.sub(punctuation, "", text)
    return result

# # Example usage
# if __name__ == "__main__":
#     # Test the synonyms API
#     word = "苹果"
#     result = get_synonyms(word)
#     print("Synonyms API result:", result)

#     # Test the tokenize API
#     text = "我喜欢吃苹果。"
#     result = tokenize_text(text)
#     print("Tokenize API result:", result)
