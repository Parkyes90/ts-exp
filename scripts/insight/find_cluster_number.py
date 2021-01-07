import os
from collections import defaultdict

import pandas as pd
from bokeh.core.property.dataspec import value
from bokeh.io.export import export_svg, export_png
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from selenium import webdriver
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

from config.settings import BASE_DIR, OUTPUTS_DIR
from src.career_experiences.parses import opts
from src.happiness.constants import H_IN_DIRS
import networkx as nx

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

node_shape_map = {
    0: "^",
    1: "o",
    2: "v",
    3: "s",
    4: ">",
    5: "<",
    6: "8",
    7: "h",
    8: "p",
    9: "d",
}


def draw_2d_chart(idx, x, cluster_output_path, k):
    driver = webdriver.Chrome(
        os.path.join(BASE_DIR, "chromedriver"), options=opts
    )
    tsne = TSNE(random_state=42)
    points = tsne.fit_transform(x)
    t_df = pd.DataFrame(points, index=range(len(x)), columns=["x", "y"])
    t_df["cluster_no"] = idx
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
        p,
        filename=os.path.join(cluster_output_path, f"cluster2d-{k}.svg"),
        webdriver=driver,
    )
    export_png(
        p,
        filename=os.path.join(cluster_output_path, f"cluster2d-{k}.png"),
        webdriver=driver,
    )


def write_cluster_mean(df, cluster_output_path, k):
    average_df_by_cluster = df.groupby(["cluster"]).mean()
    average_df_by_cluster.to_csv(
        os.path.join(cluster_output_path, f"cluster-{k}.csv")
    )


def write_similarity(df, cluster_output_path, k):
    matrix = df.to_numpy()
    without_cluster = df.drop(["cluster"], axis=1).to_numpy()
    similarity = cosine_similarity(without_cluster, without_cluster)
    networks = defaultdict(list)
    edge_colors = []
    for idx, s in enumerate(similarity):
        indexed = sorted(list(enumerate(s)), key=lambda x: x[1], reverse=True)
        for record in indexed[:6]:
            target = record[0]
            if target != idx:
                networks[idx].append(target)
    g = nx.Graph()
    for node in networks.keys():
        cluster = matrix[node][len(matrix[node]) - 1]
        g.add_node(node, s=node_shape_map[cluster], color=colormap[cluster])
    for source, targets in networks.items():
        for target in targets:
            cluster = matrix[target][len(matrix[target]) - 1]
            edge_colors.append(colormap[cluster])
            g.add_edge(source, target)
    pos = nx.spring_layout(g)
    plt.figure(figsize=(16, 16))
    ax = plt.gca()
    for idx, edge in enumerate(g.edges()):
        source, target = edge
        rad = 0.4
        cluster = matrix[source][len(matrix[source]) - 1]
        arrowprops = dict(
            linewidth=0.1,
            arrowstyle="-",
            color=colormap[cluster],
            connectionstyle=f"arc3,rad={rad}",
            alpha=0.5,
        )
        ax.annotate(
            "", xy=pos[source], xytext=pos[target], arrowprops=arrowprops
        )
    options = {
        "linewidths": 0,
        "alpha": 0.8,
    }
    node_shapes = set((aShape[1]["s"] for aShape in g.nodes(data=True)))
    for a_shape in node_shapes:
        node_list = []
        colors = []
        for sNode in filter(
            lambda x: x[1]["s"] == a_shape, g.nodes(data=True)
        ):
            colors.append(sNode[1]["color"])
            node_list.append(sNode[0])
        nx.draw_networkx_nodes(
            g,
            pos,
            node_shape=a_shape,
            nodelist=node_list,
            node_size=10,
            node_color=colors,
            **options,
        )
    plt.axis("off")
    plt.savefig(
        os.path.join(cluster_output_path, f"cluster-{k}-network.svg"),
        format="svg",
        dpi=400,
    )
    plt.savefig(
        os.path.join(cluster_output_path, f"cluster-{k}-network.png"),
        format="png",
        dpi=400,
    )


def calculate_cluster_number():

    df = pd.read_csv(os.path.join(H_IN_DIRS, "df_happiness.csv"))
    x = []

    for row in df.iterrows():
        idx, r = row
        temp = []
        for c in df.columns[:10]:
            temp.append(r[c])
        x.append(temp)

    kmax = 10
    insight_output_path = os.path.join(OUTPUTS_DIR, "insights")
    if not os.path.isdir(insight_output_path):
        os.mkdir(insight_output_path)
    for k in range(2, kmax + 1):
        cluster_output_path = os.path.join(insight_output_path, f"cluster-{k}")
        if not os.path.isdir(cluster_output_path):
            os.mkdir(cluster_output_path)

        kmeans = KMeans(n_clusters=k, random_state=42)
        idx = kmeans.fit_predict(x)
        df["cluster"] = idx
        # write_similarity(df, cluster_output_path, k)
        # write_cluster_mean(df, idx, cluster_output_path, k)
        # draw_2d_chart(idx, x, cluster_output_path, k)
        if k == 2:
            break


def main():
    # df = pd.read_csv(os.path.join(H_IN_DIRS, "happiness.csv"))
    calculate_cluster_number()
    # print(df)


if __name__ == "__main__":
    main()
