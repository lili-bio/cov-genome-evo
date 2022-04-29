import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
import sys
import argparse
import re

# ref: https://www.geeksforgeeks.org/ml-t-distributed-stochastic-neighbor-embedding-t-sne-algorithm/ 
parser = argparse.ArgumentParser(description="t-sne on landscape file")
parser.add_argument('-land', '--landscape_file', required = True,
    help='landscape file generated by gen-fit-landscape.py. Required')
parser.add_argument('-proj', '--projection', choices = ['pca', 'tsne'], default = 'pca',
    help='method for dimension reduction')
    
args = parser.parse_args()

######## Read landscape file
if args.landscape_file is None:
    logging.info("Need a landscape file generated from the script gen-fit-landscape.py")
    sys.exit()

landscape = {}
haps = []
fitness = []
model_name = ''
with open(args.landscape_file, 'r') as fh:
    lines = fh.readlines()
    for line in lines:
        data = line.split()
        if re.match("^H\d+", data[0]): 
            landscape[data[0]] = {
                'hap': str(data[1]),
                'fit': float(data[2]),
                'model': data[3]
                }
            haps.append(list(str(data[1])))
            fitness.append(float(data[2]))
            model_name = data[3]
df_hap = pd.DataFrame(haps, dtype = int)
hap_ids = list(landscape.keys())

def by_tsne():
# Data-preprocessing: Standardizing the data
    from sklearn.preprocessing import StandardScaler
    standardized_data = StandardScaler().fit_transform(df_hap)
    #print(standardized_data.shape)

    # TSNE
    model = TSNE(n_components = 2, random_state = 0)

    # configuring the parameters
    # the number of components = 2
    # default perplexity = 30
    # default learning rate = 200
    # default Maximum number of iterations
    # for the optimization = 1000
    tsne_data = model.fit_transform(df_hap)
 
    tsne_data = np.vstack((tsne_data.T, hap_ids)).T
    tsne_df = pd.DataFrame(data = tsne_data,
        columns =("Dim_1", "Dim_2", "label"))

    tsne_df = tsne_df.assign(fit = fitness)
    return tsne_df

# PCA
def by_pca():
    from sklearn import decomposition
    pca = decomposition.PCA(n_components = 2) 
    pca.fit(df_hap)
    X = pca.transform(df_hap)
    pca_df = pd.DataFrame(data = X, columns = ("Dim_1", "Dim_2"))
    pca_df = pca_df.assign(label = hap_ids, fit = fitness)
    #print(pca_df.head())
    return pca_df

if args.projection == 'pca':
    out_df = by_pca()

if args.projection == 'tsne':
    out_df = by_tsne()
    
outFile = model_name + "-" + args.projection + ".csv"
out_df.to_csv(outFile, index = False)

sys.exit()