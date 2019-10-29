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
        keras.layers.Dense(input_shape[0], input_shape=input_shape, activation='relu'),
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
        keras.layers.Dense(input_shape[0], input_shape=input_shape, activation='relu'),
        keras.layers.Dense(units[0], activation='relu'),
        keras.layers.Dense(units[1], activation='relu'),
        keras.layers.Dense(units[2], activation='relu'),
        keras.layers.Dense(units[3], activation='relu')
    ])
    return model


def get_lstm(input_shape, units):
    """ Build LSTM model

    Parameters:
        units (list<int>): number of input, output and hidden units

    Returns:
        model: Model, nn model
    """
    model = Sequential()
    model.add(LSTM(input_shape[1], input_shape=input_shape, return_sequences=True))
    model.add(LSTM(units[2]))
    model.add(Dropout(0.2))
    model.add(Dense(units[3], activation='relu'))

    return model


def get_gru(input_shape, units):
    """ Build GRU model

    Parameters:
        units (list<int>): number of input, output and hidden units

    Returns:
        model: Model, nn model
    """
    model = Sequential()
    model.add(GRU(input_shape[0], input_shape=input_shape, return_sequences=True))
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


def get_saes(input_shape, layers):
    """ Build SAEs model

    Parameters:
        layers (list<int>): number of input, output and hidden units

    Returns:
        list<model>: List of SAE and SAEs
    """
    sae1 = _get_sae(input_shape[0], layers[0], layers[-1])
    sae2 = _get_sae(layers[0], layers[1], layers[-1])
    sae3 = _get_sae(layers[1], layers[2], layers[-1])

    saes = Sequential()
    saes.add(Dense(layers[0], input_dim=input_shape[0], name='hidden1'))
    saes.add(Activation('sigmoid'))
    saes.add(Dense(layers[1], name='hidden2'))
    saes.add(Activation('sigmoid'))
    saes.add(Dense(layers[2], name='hidden3'))
    saes.add(Activation('sigmoid'))
    saes.add(Dropout(0.2))
    saes.add(Dense(layers[3], activation='sigmoid'))

    models = [sae1, sae2, sae3, saes]

    return models
