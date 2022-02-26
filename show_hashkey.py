

#%%
import pickle
import time
with open('support_lib.serialized', 'rb') as handle:
    b = pickle.load(handle)

print(b['hash_key'])
time.sleep(25)