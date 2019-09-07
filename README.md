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

A step by step series of examples that tell you how to get a development env running

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

Load the data from the spreadsheet into the application by running the *train.py* without any parameters.
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

The output will be available in:
```
TFPS/model/[model]/[SCATS]/
```

## Authors

* **Jack Howarth-Green** 
* **Jacob Scott** 
* **Mitchell Reynolds** 
* **Nathan Templar** 

## Acknowledgments

* **xiaochus** - *Base code* - [Traffic Flow Prediction](https://github.com/xiaochus/TrafficFlowPrediction)