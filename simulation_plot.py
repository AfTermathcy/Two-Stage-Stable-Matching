import matplotlib.pyplot as plt
import pickle
import test

with open('obj_values_35.pkl', 'rb') as f:
   value = pickle.load(f)
   
print(value)