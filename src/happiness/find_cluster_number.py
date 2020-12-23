import os

import pandas as pd
from bokeh.core.property.dataspec import value
from bokeh.io import show
from bokeh.io.export import export_svg, export_png
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from selenium import webdriver
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score

from config.settings import BASE_DIR
from src.career_experiences.parses import opts
from src.happiness.constants import H_IN_DIRS


def draw_cluster_2d_chart():
    pass


def calculate_cluster_number():
    driver = webdriver.Chrome(
        os.path.join(BASE_DIR, "chromedriver"), options=opts
    )
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
        kmeans = KMeans(n_clusters=k)
        fit = kmeans.fit(x)
        labels = fit.labels_
        score = silhouette_score(x, labels, metric="euclidean")
        idx = kmeans.fit_predict(x)
        tsne = TSNE(random_state=42)
        points = tsne.fit_transform(x)
        t_df = pd.DataFrame(points, index=range(len(x)), columns=["x", "y"])
        t_df["cluster_no"] = idx
        colormap = {
            0: "#f44336",
            1: "#673ab7",
            2: "#9c27b0",
            3: "#e91e63",
            4: "#3f51b5",
            5: "#2196f3",
            6: "#03a9f4",
            7: "#00bcd4",
            8: "#009688",
            9: "#cddc39",
        }
        colors = [colormap[x] for x in t_df["cluster_no"]]
        t_df["color"] = colors
        plot_data = ColumnDataSource(data=t_df.to_dict(orient="list"))
        p = figure(
            # title='TSNE Twitter BIO Embeddings',
            plot_width=1200,
            plot_height=1200,
            active_scroll="wheel_zoom",
            output_backend="svg",
        )
        p.add_tools(HoverTool(tooltips="@title"))
        p.circle(
            source=plot_data,
            x="x",
            y="y",
            line_alpha=0.9,
            fill_alpha=0.9,
            # size="radius",
            fill_color="color",
            line_color="color",
        )
        p.title.text_font_size = value("16pt")
        p.xaxis.visible = True
        p.yaxis.visible = True
        p.background_fill_color = None
        p.border_fill_color = None
        p.grid.grid_line_color = None
        p.outline_line_color = None
        # tsne_plot.grid.grid_line_color = None
        # tsne_plot.outline_line_color = None
        p.toolbar.logo = None
        p.toolbar_location = None
        export_svg(
            p, filename=f"cluster-number{k}.svg", webdriver=driver,
        )
        export_png(
            p, filename=f"cluster-number{k}.png", webdriver=driver,
        )
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
