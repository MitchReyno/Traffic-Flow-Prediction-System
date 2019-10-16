from keras.layers import Dense, Dropout, Activation
from keras.layers.recurrent import LSTM, GRU
from keras.models import Sequential
import keras


def get_feed_fwd(input_shape, units):
    """ Build Shallow Feed Forward model

    Parameters:
        units (list<int>): number of input, output and hidden units

    Returns:
        model: Model, nn model
    """
    model = Sequential([
        keras.layers.Dense(input_shape=input_shape, activation='relu'),
        keras.layers.Dense(units[0], activation='sigmoid'),
        keras.layers.Dense(units[1], activation='sigmoid')
    ])
    return model


def get_deep_feed_fwd(input_shape, units):
    """ Build Deep Feed Forward model

    Parameters:
        units (list<int>): number of input, output and hidden units

    Returns:
        model: Model, nn model
    """
    model = Sequential([
        keras.layers.Dense(input_shape[1], input_shape=(input_shape[1],), activation='relu'),
        keras.layers.Dense(units[0], activation='relu'),
        keras.layers.Dense(units[1], activation='relu'),
        keras.layers.Dense(units[2], activation='relu'),
        keras.layers.Dense(units[3], activation='relu')
    ])
    return model


def get_lstm(units):
    """ Build LSTM model

    Parameters:
        units (list<int>): number of input, output and hidden units

    Returns:
        model: Model, nn model
    """
    model = Sequential()
    model.add(LSTM(units[1], input_shape=(units[0], 1), return_sequences=True))
    model.add(LSTM(units[2]))
    model.add(Dropout(0.2))
    model.add(Dense(units[3], activation='relu'))

    return model


def get_gru(units):
    """ Build GRU model

    Parameters:
        units (list<int>): number of input, output and hidden units

    Returns:
        model: Model, nn model
    """
    model = Sequential()
    model.add(GRU(units[1], input_shape=(units[0], 1), return_sequences=True))
    model.add(GRU(units[2]))
    model.add(Dropout(0.2))
    model.add(Dense(units[3], activation='sigmoid'))

    return model


def _get_sae(inputs, hidden, output):
    """ Build SAE model

    Parameters:
        inputs (int): number of input units
        hidden (int): number of hidden units
        output (int): number of output units

    Returns:
        model: Model, nn model
    """
    model = Sequential()
    model.add(Dense(hidden, input_dim=inputs, name='hidden'))
    model.add(Activation('sigmoid'))
    model.add(Dropout(0.2))
    model.add(Dense(output, activation='sigmoid'))

    return model


def get_saes(layers):
    """ Build SAEs model

    Parameters:
        layers (list<int>): number of input, output and hidden units

    Returns:
        list<model>: List of SAE and SAEs
    """
    sae1 = _get_sae(layers[0], layers[1], layers[-1])
    sae2 = _get_sae(layers[1], layers[2], layers[-1])
    sae3 = _get_sae(layers[2], layers[3], layers[-1])

    saes = Sequential()
    saes.add(Dense(layers[1], input_dim=layers[0], name='hidden1'))
    saes.add(Activation('relu'))
    saes.add(Dense(layers[2], name='hidden2'))
    saes.add(Activation('relu'))
    saes.add(Dense(layers[3], name='hidden3'))
    saes.add(Activation('relu'))
    saes.add(Dropout(0.2))
    saes.add(Dense(layers[4], activation='relu'))

    models = [sae1, sae2, sae3, saes]

    return models
