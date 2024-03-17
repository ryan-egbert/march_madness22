import pandas as pd
import numpy as np
import csv
import time
import pickle as pck
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression


GENDER = "mens"

def generate_df():
    df = pd.read_csv(f"input/{GENDER}_input.csv")
    df = df.dropna()
    
    return df

def setup_predict_score():
    df = generate_df()
    df.SCORE = df.SCORE.apply(pd.to_numeric, errors="coerce")
    df.OPP_SCORE = df.OPP_SCORE.apply(pd.to_numeric, errors="coerce")
    
    df = df.drop(columns=[
      "WINNER",
      "TEAM",
      "OPP_TEAM"])
    y = df[["SCORE", "OPP_SCORE"]]
    x = df.drop(columns=["SCORE", "OPP_SCORE"])
    
    train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.1, random_state=84318)
    
    return train_x, test_x, train_y, test_y


def predict_score_rf():
    train_x, test_x, train_y, test_y = setup_predict_score()
    start = time.time()
    rf = RandomForestRegressor(
        n_estimators=100,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features='sqrt',
        max_depth=10,
        bootstrap=True
    )
    rf.fit(train_x, train_y)

    end = time.time()
    
    print(f"Finished processing RF in {round(end - start, 2)} seconds...")
    
    rf_pred = rf.predict(test_x)
    rf_mae = mean_absolute_error(test_y, rf_pred)
    print(f"{'Random Forest MAE:':<20} ==> {rf_mae}")
    
    
def predict_score_ann():
    train_x, test_x, train_y, test_y = setup_predict_score()
    
    start = time.time()
    
    ann = MLPRegressor(hidden_layer_sizes = (10,50,10))
    ann.fit(train_x, train_y)
    
    end = time.time()
    
    print(f"Finished processing ANN in {round(end - start, 2)} seconds...")
    
    ann_pred = ann.predict(test_x)
    ann_mae = mean_absolute_error(test_y, ann_pred)
    print(f"{'Neural Net MAE:':<20} ==> {ann_mae}")
    
    
def predict_score_lin():
    train_x, test_x, train_y, test_y = setup_predict_score()
    
    start = time.time()
    
    lin = LinearRegression()
    lin.fit(train_x, train_y)
    
    end = time.time()
    
    print(f"Finished processing linear reg in {round(end - start, 2)} seconds...")
    
    lin_pred = lin.predict(test_x)
    lin_acc = lin.score(test_x, test_y)
    lin_mae = mean_absolute_error(test_y, lin_pred)
    print(f"{'Linear Regression MAE:':<20} ==> {lin_mae}")
    print(f"{'Linear Regression (r-squared)':<20} ==> {lin_acc}")




def predict_winner():
    df = generate_df()