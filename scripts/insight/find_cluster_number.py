import os
from collections import defaultdict
import random

import pandas as pd
from bokeh.core.property.dataspec import value
from bokeh.io.export import export_svg, export_png
from bokeh.models import ColumnDataSource, HoverTool, Label
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
    0: "#2E86C8",
    1: "#D24864",
    2: "#2C986A",
    3: "#DCA832",
    4: "#8E80BA",
    5: "#67C4CD",
    6: "#03a9f4",
    7: "#00bcd4",
    8: "#009688",
    9: "#cddc39",
}

node_shape_map = {
    0: "o",
    1: "o",
    2: "o",
    3: "o",
    4: "o",
    5: "o",
    6: "o",
    7: "o",
    8: "o",
    9: "o",
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


def write_score_cluster_mean(df, cluster_output_path, k):
    df = df.loc[:, [*df.columns[-12:]]]
    df["cluster"] += 1
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


def write_cross_chart(df, cluster_output_path, k):
    height = 1600
    width = 1600
    driver = webdriver.Chrome(
        os.path.join(BASE_DIR, "chromedriver"), options=opts
    )
    x = df.c3.to_list()
    y = df.c1.to_list()
    clusters = df.cluster.to_list()
    plot = figure(
        # title='TSNE Twitter BIO Embeddings',
        plot_width=width,
        plot_height=height,
        active_scroll="wheel_zoom",
        # x_range=r,
        # y_range=r,
        output_backend="svg",
    )
    plot.add_tools(HoverTool(tooltips="@title"))
    new_x = []
    new_y = []
    for coord in zip(x, y):
        x_coord, y_coord = coord
        x_rand = random.uniform(-(0.5 ** 0.5), 0.5 ** 0.5)
        y_rand_range = (0.5 - x_rand ** 2) ** 0.5
        y_rand = random.uniform(-y_rand_range, y_rand_range)
        new_x.append(x_coord + x_rand)
        new_y.append(y_coord + y_rand)
    colors = [colormap[clusters[i]] for i in range(len(new_y))]
    source = ColumnDataSource(data={"x": new_x, "y": new_y, "color": colors})
    plot.scatter(
        source=source,
        x="x",
        y="y",
        line_alpha=0.6,
        fill_alpha=0.6,
        size=10,
        color="color",
    )

    # size
    # count_map = defaultdict(int)
    # for coord in zip(x, y):
    #     count_map[coord] += 1 * 0.5
    # source = ColumnDataSource(
    #     data={
    #         "x": [k[0] for k in count_map.keys()],
    #         "y": [k[1] for k in count_map.keys()],
    #         "size": list(count_map.values()),
    #     }
    # )
    # plot.scatter(
    #     source=source,
    #     x="x",
    #     y="y",
    #     line_alpha=0.6,
    #     fill_alpha=0.6,
    #     size="size",
    # )

    plot.yaxis.axis_label_text_font_size = "25pt"
    plot.yaxis.major_label_text_font_size = "25pt"
    plot.xaxis.axis_label_text_font_size = "25pt"
    plot.xaxis.major_label_text_font_size = "25pt"
    plot.title.text_font_size = value("32pt")
    plot.xaxis.visible = True
    # plot.xaxis.bounds = (0, 0)
    plot.yaxis.visible = True
    label_opts1 = dict(x_offset=0, y_offset=750, text_font_size="30px",)
    msg1 = "C1"
    caption1 = Label(text=msg1, **label_opts1)
    label_opts2 = dict(x_offset=0, y_offset=-750, text_font_size="30px",)
    msg2 = "-C1"
    caption2 = Label(text=msg2, **label_opts2)
    label_opts3 = dict(x_offset=750, y_offset=0, text_font_size="30px",)
    msg3 = "C3"
    caption3 = Label(text=msg3, **label_opts3)
    label_opts4 = dict(x_offset=-750, y_offset=0, text_font_size="30px",)
    msg4 = "-C3"
    caption4 = Label(text=msg4, **label_opts4)
    plot.add_layout(caption1, "center")
    plot.add_layout(caption2, "center")
    plot.add_layout(caption3, "center")
    plot.add_layout(caption4, "center")
    plot.background_fill_color = None
    plot.border_fill_color = None
    plot.grid.grid_line_color = None
    plot.outline_line_color = None
    plot.yaxis.fixed_location = 0
    plot.xaxis.fixed_location = 0
    plot.toolbar.logo = None
    plot.toolbar_location = None
    export_svg(
        plot,
        filename=os.path.join(cluster_output_path, f"cross-{k}.svg"),
        webdriver=driver,
        height=height,
        width=width,
    )
    export_png(
        plot,
        filename=os.path.join(cluster_output_path, f"cross-{k}.png"),
        webdriver=driver,
        height=height,
        width=width,
    )


def write_cluster_center(df, cluster_centers_, k, cluster_output_path):
    ret = [[i, *c] for i, c in enumerate(cluster_centers_, 1)]
    center_df = pd.DataFrame(ret, columns=["cluster", *df.columns[-11:]])
    center_df.to_csv(
        os.path.join(cluster_output_path, f"cluster-{k}-center.csv"),
        index=False,
    )


def calculate_cluster_number():
    df = pd.read_csv(os.path.join(H_IN_DIRS, "happiness_score_utf8.csv"))

    x = []
    for row in df.iterrows():
        idx, r = row
        temp = []
        for c in df.columns[-11:]:
            temp.append(r[c])
        x.append(temp)
    kmax = 6
    insight_output_path = os.path.join(OUTPUTS_DIR, "score_insights")
    if not os.path.isdir(insight_output_path):
        os.mkdir(insight_output_path)
    for k in range(2, kmax + 1):

        cluster_output_path = os.path.join(insight_output_path, f"cluster-{k}")
        if not os.path.isdir(cluster_output_path):
            os.mkdir(cluster_output_path)

        kmeans = KMeans(n_clusters=k, random_state=42)
        idx = kmeans.fit_predict(x)
        write_cluster_center(
            df, kmeans.cluster_centers_, k, cluster_output_path
        )
        df["cluster"] = idx

        #     df.to_csv(
        #         os.path.join(cluster_output_path, f"with_cluster-{k}-raw.csv"),
        #         index=False,
        #     )
        #     write_similarity(df, cluster_output_path, k)
        write_score_cluster_mean(df, cluster_output_path, k)
        draw_2d_chart(idx, x, cluster_output_path, k)
    #     write_cross_chart(df, cluster_output_path, k)
    #     print(k)


def score_clustering():
    df = pd.read_csv(os.path.join(H_IN_DIRS, "happiness_score_utf8.csv"))
    print(df)


def main():
    # df = pd.read_csv(os.path.join(H_IN_DIRS, "happiness.csv"))
    calculate_cluster_number()
    # print(df)
    # score_clustering()


if __name__ == "__main__":
    main()
