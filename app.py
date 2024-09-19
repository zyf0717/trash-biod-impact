import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.types import FileInfo
from shinywidgets import output_widget, render_widget

raw_data = pd.read_csv("test_data.csv")

app_ui = ui.page_fluid(
    ui.layout_columns(
        ui.card("Insert Title"),
        ui.card(output_widget("typesOfTrashPlot")),
        ui.card(output_widget("trashInLocationPlot")),
        ui.card(output_widget("biodImpactPlot")),
        ui.card(ui.output_data_frame("toxicityOnBiod"),),
        col_widths=[12, 6, 6, 6, 6]
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    @render_widget
    def typesOfTrashPlot():
        df = raw_data.copy()
        fig = px.histogram(df, x="Type of Trash", title="Types of Trash")
        return fig


    @render_widget
    def trashInLocationPlot():
        df = raw_data.copy()
        fig = px.histogram(df, x="Location", color="Type of Trash", title="Trash in Location")
        return fig

    @render_widget
    def biodImpactPlot():
        df = raw_data.copy()
        df = df.groupby(['Location'])['Biodiversity Impact'].sum().reset_index()
        fig = px.bar(df, x="Location", y = "Biodiversity Impact", title="Impact on Biodiversity")
        return fig
    
    @render.data_frame
    def toxicityOnBiod():
        df = raw_data.copy()
        return render.DataGrid(
            df,
            width = "100%"
        )



app = App(app_ui, server)
