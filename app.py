import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shinywidgets import output_widget, render_widget

raw_data_trash = pd.read_csv("test_data_trash.csv")
raw_data_biod = pd.read_csv("test_data_biod.csv")

app_ui = ui.page_fluid(
    ui.layout_columns(
        ui.card("Pollution, Toxicity and Biodiversity"),
        ui.card(output_widget("typesOfTrashPlot")),
        ui.card(output_widget("trashInLocationPlot")),
        ui.card(output_widget("toxicityPlot")),
        ui.card(output_widget("toxicityOnBiodPlot")),
        ui.card(ui.output_data_frame("toxicityAtLocationTbl")),
        ui.card(ui.output_data_frame("toxicityOnBiodTbl")),
        col_widths=[12, 6, 6, 6, 6, 6, 6]
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    @render_widget
    def typesOfTrashPlot():
        df = raw_data_trash.copy()
        fig = px.histogram(
            df,
            x="Trash",
            title="Types of Trash",
            template="seaborn"
        )
        return fig


    @render_widget
    def trashInLocationPlot():
        df = raw_data_trash.copy()
        fig = px.histogram(
            df,
            x="Location",
            color="Trash",
            title="Trash in Location",
            template="seaborn"
        )
        return fig

    @render_widget
    def toxicityPlot():
        df = raw_data_trash.copy()
        df = df.groupby(['Location'])['Toxicity'].sum().reset_index()
        fig = px.bar(
            df,
            x="Location",
            y = "Toxicity",
            title="Total Toxicity",
            template="seaborn"
        )
        return fig

    @render_widget
    def toxicityOnBiodPlot():
        df_trash = raw_data_trash.copy()
        df_biod = raw_data_biod.copy()

        df_trash = df_trash.groupby(['Location'])['Toxicity'].sum().reset_index()
        df_biod = df_biod.groupby(['Location'])['Quantity'].sum().reset_index()

        df = pd.merge(df_trash, df_biod, on="Location")

        fig = px.scatter(
            df,
            x="Toxicity",
            y="Quantity",
            trendline="ols",
            title="Toxicity vs Wildlife",
            template="seaborn"
        )

        return fig


    @render.data_frame
    def toxicityAtLocationTbl():
        df = raw_data_trash.copy()
        df = df.groupby(['Location'])['Toxicity'].sum().reset_index()

        return render.DataGrid(
            df,
            width = "100%"
        )


    @render.data_frame
    def toxicityOnBiodTbl():
        df_trash = raw_data_trash.copy()
        df_biod = raw_data_biod.copy()

        df_trash = df_trash.groupby(['Location'])['Toxicity'].sum().reset_index()
        df_biod = df_biod.groupby(['Location'])['Quantity'].sum().reset_index()

        df = pd.merge(df_trash, df_biod, on="Location")

        return render.DataGrid(
            df,
            width = "100%"
        )


app = App(app_ui, server)
