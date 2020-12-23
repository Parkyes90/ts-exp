import os

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.metrics import silhouette_score

from src.happiness.constants import H_IN_DIRS


def calculate_cluster_number():
    df = pd.read_csv(os.path.join(H_IN_DIRS, "happiness.csv"))
    x = []

    for row in df.iterrows():
        idx, r = row
        temp = []
        for c in df.columns[1:-1]:
            temp.append(r[c])
        x.append(temp)

    ok = 0
    kmax = 10
    maximum = 0
    for k in range(2, kmax + 1):
        kmeans = KMeans(n_clusters=k).fit(x)
        labels = kmeans.labels_
        score = silhouette_score(x, labels, metric="euclidean")
        if score > maximum:
            maximum = score
            ok = k
    print(ok)


def main():
    # df = pd.read_csv(os.path.join(H_IN_DIRS, "happiness.csv"))
    calculate_cluster_number()
    # print(df)


if __name__ == "__main__":
    main()
