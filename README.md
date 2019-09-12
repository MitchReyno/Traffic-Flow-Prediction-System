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

[![Anaconda-Server Badge](https://anaconda.org/nathantemplar/tfps/badges/installer/env.svg)](https://anaconda.org/nathantemplar/tfps/2019.09.09.174828/download/tfps.yml)

### Installing

Download/clone the repository into a folder on your computer.
```
$ git clone https://github.com/MitchReyno/Traffic-Flow-Prediction-System
```

Move the *Scats Data October 2006.xls* file into the data directory of the project. Your folder structure should look like this:
```
|   data.py
|   Scats Data October 2006.xls
|   scats.py
```

Launch the model training application by running *train_ui.py*.
```
python train_ui.py
```
![Train UI](/TFPS/images/train_ui_screenshot.png)

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

* **Jack Howarth-Green** [101105692@student.swin.edu.au](mailto:101105692@student.swin.edu.au)  
* **Jacob Scott** [101111327@student.swin.edu.au](mailto:101111327@student.swin.edu.au)  
* **Mitchell Reynolds** [101109966@student.swin.edu.au](mailto:101109966@student.swin.edu.au)  
* **Nathan Templar** [101631304@student.swin.edu.au](mailto:101631304@student.swin.edu.au)  

## Acknowledgments

* **xiaochus** - *Base code* - [Traffic Flow Prediction](https://github.com/xiaochus/TrafficFlowPrediction)