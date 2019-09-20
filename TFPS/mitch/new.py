import os.path
from queue import PriorityQueue

import numpy as np
import pandas as pd
from keras_preprocessing import text
from sklearn.preprocessing import MultiLabelBinarizer
from tensorflow.python.keras import Sequential
from tensorflow.python.keras.layers import Dense, Activation, Dropout
from tensorflow.python.keras.models import load_model

MODEL_NAME = 'MODEL2'
DATA_SET_FILEPATH = 'data/export_data_frame.csv'
MAIN_DIR = 'data/OLD/formatted/'
NUM_LANGUAGES = 5
MAX_CHARS = 24
UNIQUE_CHARS = 27


def generate_data_set():
    # filepath_dict = {'english': 'data/english.csv',
    #                  'french': 'data/french.csv',
    #                  'german': 'data/german.csv',
    #                  'italian': 'data/italian.csv',
    #                  'dutch': 'data/dutch.csv'}
    # df_gen = None
    # for language, filepath in filepath_dict.items():
    #     df_to_add = pd.read_csv(filepath, dtype={'word': str, language: float})
    #     if df_gen is None:
    #         df_gen = df_to_add
    #     else:
    #         df_gen = pd.merge(df_gen,
    #                           df_to_add[['word', language]],
    #                           on='word',
    #                           how='outer').fillna(0)
    # print(df_gen.head())
    # df_gen.to_csv(r'data\export_data_frame.csv', index=None, header=True)
    # return df_gen
    filepath_dict = {'english': MAIN_DIR+'english.csv',
                     'french': MAIN_DIR+'french.csv',
                     'german': MAIN_DIR+'german.csv',
                     'italian': MAIN_DIR+'italian.csv',
                     'dutch': MAIN_DIR+'dutch.csv'}

    df_list = None

    for language, filepath in filepath_dict.items():
        df = pd.read_csv(filepath, dtype={'word': str, 'language': str})
        if df_list is None:
            df_list = df
        else:
            df_list = pd.merge(df_list,
                               df[['word', 'language']],
                               on='word',
                               how='outer')
            df_list['language'] = df_list['language_x'].map(str) + "," + df_list['language_y']
            df_list['language'] = df_list['language'].str.strip(',')
            df_list = df_list.drop(columns='language_x')
            df_list = df_list.drop(columns='language_y')
    df_list.to_csv(r'data\export_data_frame.csv', index=None, header=True)
    print(df_list.head())
    df_out = df_list.assign(language=df_list.language.str.split(','))
    return df_out


def load_data_set():
    df = pd.read_csv(DATA_SET_FILEPATH, dtype={'word': str, 'language': str}).astype(str)
    df = df.assign(language=df.language.str.split(','))
    return df


def tokenize_on_char_level(array):
    tokenize = text.Tokenizer(char_level=True)
    tokenize.fit_on_texts(array)
    output = np.zeros((len(array), MAX_CHARS * UNIQUE_CHARS))
    for word_index, word in enumerate(array):
        print("Encoding word " + str(word_index + 1) + "/" + str(len(array)) + ": " + word)

        for offset, character in enumerate(word):
            if offset >= MAX_CHARS:
                break
            else:
                output[word_index, offset * UNIQUE_CHARS + ord(character) - 97] = 1
    return output


def generate_model():
    if os.path.isfile('data/' + MODEL_NAME + '.h5'):
        model_gen = load_model('data/' + MODEL_NAME + '.h5')
    else:
        model_gen = Sequential()
        model_gen.add(Dense(MAX_CHARS * 6, input_shape=(MAX_CHARS * UNIQUE_CHARS,)))
        model_gen.add(Activation('relu'))
        model_gen.add(Dense(256, activation='sigmoid'))
        model_gen.add(Dropout(0.2))
        model_gen.add(Dense(32, activation='sigmoid'))
        model_gen.add(Dropout(0.2))
        model_gen.add(Dense(NUM_LANGUAGES, activation='sigmoid'))
        model_gen.compile(loss='binary_crossentropy',
                          optimizer='adam',
                          metrics=['accuracy'])
    return model_gen


def train_model(model_to_train, data_set, encoder):
    df = data_set.sample(frac=1)
    train_size = int(len(df) * .8)
    train_words = df['word'][:train_size]
    train_languages = df['language'][:train_size]
    test_words = df['word'][train_size:]
    test_languages = df['language'][train_size:]

    x_train = tokenize_on_char_level(train_words)
    x_test = tokenize_on_char_level(test_words)
    y_train = encoder.fit_transform(train_languages)
    y_test = encoder.fit_transform(test_languages)

    model_to_train.fit(x_train, y_train,
                       batch_size=265,
                       epochs=2,
                       verbose=1,
                       validation_split=0.1)

    score = model_to_train.evaluate(x_test, y_test,
                                    batch_size=2, verbose=1)
    model_to_train.save('data/' + MODEL_NAME + '.h5')
    print('Test score:', score[0])
    print('Test accuracy:', score[1])
    return


def use_model(model, df, encoder):
    df = df.sample(frac=1/100)
    test_words = df['word'][:200]
    test_languages = df[df.columns.difference(['word'])][:200]
    text_labels = encoder.classes_

    x_test = tokenize_on_char_level(test_words)
    prediction = model.predict(x_test)

    for i in range(200):
        testy = input("\nEnter a test word (or just hit enter for random word): ")
        if not testy:
            prediction_to_use = prediction
            range_index = i
            # predicted_label = text_labels[np.argmax(prediction_to_use[range_index])]
            print("\nWord: " + test_words.iloc[range_index][:100] + " {" + ', '.join(
                test_languages.iloc[range_index]) + ")")
            # print("\nPredicted language: " + predicted_label.upper())
            # if test_languages.iloc[range_index] == predicted_label:
            #     print("CORRECT")
            # else:
            #     print("INCORRECT")
        else:
            prediction_to_use = model.predict(tokenize_on_char_level([testy]))
            range_index = 0
            # predicted_label = text_labels[np.argmax(prediction_to_use[range_index])]
            # print("\nPredicted language: " + predicted_label.upper())

        print("\nPredicted chance:")
        q = PriorityQueue()
        for label_index in range(len(text_labels)):
            q.put((100 - int(round(prediction_to_use[range_index][label_index] * 100)),
                   "["
                   + text_labels[label_index]
                   + "\t- "
                   + str(int(round(prediction_to_use[range_index][label_index] * 100)))
                   + "%]"))

        while not q.empty():
            next_item = q.get()
            print(next_item[1].upper())


def main():
    model = generate_model()

    # df = generate_data_set()
    df = load_data_set()

    encoder = MultiLabelBinarizer(classes=('english', 'french', 'german', 'italian', 'dutch'))

    # train_model(model, df, encoder)
    use_model(model, df, encoder)
    return


main()
