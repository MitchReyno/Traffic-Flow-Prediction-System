# Traffic Flow Prediction System
COS30018 - Intelligent Systems

## Getting Started

These instructions will explain the process of getting the system up and running on your local machine.

### Prerequisites

Graphviz - Graph Visualization Software  
Python 3.6.x
```
keras
matplotlib
pydot
pandas
scikit-learn
tensorflow
```

### Installing

Download/clone the repository into a folder on your computer.
```
$ git clone https://github.com/MitchReyno/Traffic-Flow-Prediction-System
```

Move the *Scats Data October 2006.xls* file into the data directory of the project. Your folder structure should look like this:
```
|   config.json
|   config.py
|   train.py
+---data
|   |   data.py
|   |   Scats Data October 2006.xls
|   |   scats.py
+---model
|   |   model.py
```

Load the data from the spreadsheet into the application by running *train.py* without any parameters.
```
$ python train.py
```

Run *train.py* again without any parameters to generate a Long Short-Term Memory model for all SCATS.
```
$ python train.py
```

Alternatively, you can specify specific SCATS/junctions and the neural network model to train by adding special parameters.
```
$ python train.py --scats 970 --junction 1 --model lstm
```

### Running the Program

Run *main.py* to get a graph output for the specifc SCATS/junction:
```
python main.py --scats 970 --junction 1
```
These are the details from the output when the program is executed with the parameters shown above and when all models have been trained:  

| Metrics | MAE | MSE | RMSE | MAPE |  R2  | Explained Variance Score |
| ------- |:---:| :--:| :--: | :--: | :--: | :----------------------: |
| LSTM | 15.71 | 468.10 | 21.64 | 15.71% | 0.9713 | 0.9714 |
| GRU | 17.32 | 573.50 | 23.95 | 17.61% | 0.9649 | 0.9649 |
| SAEs | 18.39 | 600.81 | 24.51 | 24.05% | 0.9632 | 0.9678 |

![Graph](/TFPS/images/scats970-1.png)

## Authors

* **Jack Howarth-Green** 
* **Jacob Scott** 
* **Mitchell Reynolds** 
* **Nathan Templar** 

## Acknowledgments

* **xiaochus** - *Base code* - [Traffic Flow Prediction](https://github.com/xiaochus/TrafficFlowPrediction)