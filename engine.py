import tensorflow as tf
import pandas as pd
import pickle
import numpy as np
import tensorflow as tf

from keras import layers
import keras

with open('tokenizer', 'rb') as tokenz:
    tokenizer= pickle.load(tokenz)

model_path = "final_model"
saved_model = keras.models.load_model(model_path)


def normalise_text (text):
    text = text.str.lower() # lowercase
    text = text.str.replace(r"\#","") # replaces hashtags
    text = text.str.replace(r"http\S+","URL")  # remove URL addresses
    text = text.str.replace(r"@","")
    text = text.str.replace(r"[^A-Za-z0-9()!?\'\`\"]", " ")
    text = text.str.replace("\s{2,}", " ")
    return text
def tokenize_text(text):
    return tokenizer.convert_tokens_to_ids(tokenizer.tokenize(text))

def everythin_is_fine(text_message):
    df_new = pd.DataFrame(data = {'text' : [text_message]})
    df_new['text'] = normalise_text(df_new['text'])
    tokenize_arr = tokenize_text(df_new['text'][0])
    for i in range(10 - len(tokenize_arr) % 10):
        tokenize_arr = np.append(tokenize_arr, 5)
    lenght = len(tokenize_arr)
    percents = 0
    n = 0
    j = 0
    for i in range(10,lenght + 1, 10):
        percents += get_percent(tokenize_arr[j:i])
        j = i
        n += 1
    
    return 100 - percents/n


def get_percent(tokenize_arr):
    BATCH_SIZE = 32

    df_new = [(tokenize_arr, 5)]
    df_ds = tf.data.Dataset.from_generator(lambda: df_new, output_types=(tf.int32, tf.int32))
    batched_text = df_ds.padded_batch(BATCH_SIZE, padded_shapes=((None, ), ()))

    return (saved_model.predict(batched_text)[0][0]*100 )