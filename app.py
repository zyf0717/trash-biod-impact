import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shinywidgets import output_widget, render_widget


##### Data #####

# Read CSVs
raw_data_trash = pd.read_csv("test_data_trash.csv")
raw_data_biod = pd.read_csv("test_data_biod.csv")

# Remove leading and trailing whitespace
raw_data_trash['Location'] = raw_data_trash['Location'].str.strip()
raw_data_trash['Trash'] = raw_data_trash['Trash'].str.strip()
raw_data_biod['Location'] = raw_data_biod['Location'].str.strip()
raw_data_biod['Species'] = raw_data_biod['Species'].str.strip()

# Convert certain columns to categorical
raw_data_trash['Location'] = raw_data_trash['Location'].astype('category')
raw_data_trash['Trash'] = raw_data_trash['Trash'].astype('category')
raw_data_biod['Location'] = raw_data_biod['Location'].astype('category')
raw_data_biod['Species'] = raw_data_biod['Species'].astype('category')

# Sorted categories for axis sorting if necessary
locations = set(raw_data_trash['Location'].cat.categories).union(set(raw_data_biod['Location'].cat.categories))
locations = list(locations).sort()
trash_types = set(raw_data_trash['Trash'].cat.categories)
trash_types = list(trash_types).sort()
species = set(raw_data_biod['Species'].cat.categories)
species = list(species).sort()


##### UI #####

app_ui = ui.page_fluid(
    ui.layout_columns(
        ui.card("Pollution, Toxicity and Biodiversity"),
        ui.card(
            ui.card_header("Types of Trash"),
            output_widget("typesOfTrashPlot")
        ),
        ui.card(
            ui.card_header("Trash at Location"),
            output_widget("trashAtLocationPlot")
        ),
        ui.card(
            ui.card_header("Total Toxicity"),
            output_widget("toxicityPlot")
        ),
        ui.card(
            ui.card_header("Toxicity vs Wildlife"),
            output_widget("toxicityOnBiodPlot")
        ),
        ui.card(
            ui.card_header("Toxicity at Location"),
            ui.output_data_frame("toxicityAtLocationTbl")
        ),
        ui.card(
            ui.card_header("Toxicity at Location"),
            ui.output_data_frame("toxicityOnBiodTbl")
        ),
        col_widths=[12, 6, 6, 6, 6, 6, 6]
    )
)


##### Server #####

def server(input: Inputs, output: Outputs, session: Session):
    @render_widget
    def typesOfTrashPlot():
        df_trash = raw_data_trash.copy()
        df_trash = df_trash.sort_values(by=['Trash'])
        fig = px.histogram(
            df_trash,
            x="Trash",
            template="seaborn"
        )
        return fig


    @render_widget
    def trashAtLocationPlot():
        df_trash = raw_data_trash.copy()
        df_trash = df_trash.sort_values(by=['Trash'])
        fig = px.histogram(
            df_trash,
            x="Location",
            color="Trash",
            template="seaborn"
        )
        fig.update_layout(
            xaxis={'categoryorder':'category ascending'}
        )
        return fig


    @render_widget
    def toxicityPlot():
        df_trash = raw_data_trash.copy()
        df_trash = df_trash.groupby(['Location', 'Trash'], observed=False)['Toxicity'].sum().reset_index()
        df_trash = df_trash.sort_values(by=['Trash'])
        fig = px.bar(
            df_trash,
            x="Location",
            y="Toxicity",
            color="Trash",
            template="seaborn"
        )
        fig.update_layout(
            xaxis={'categoryorder':'category ascending'}
        )
        return fig


    @render_widget
    def toxicityOnBiodPlot():
        df_trash = raw_data_trash.copy()
        df_biod = raw_data_biod.copy()

        df_trash = df_trash.groupby(['Location'], observed=False)['Toxicity'].sum().reset_index()
        df_biod = df_biod.groupby(['Location'], observed=False)['Quantity'].sum().reset_index()

        df = pd.merge(df_trash, df_biod, on="Location")

        fig = px.scatter(
            df,
            x="Toxicity",
            y="Quantity",
            trendline="ols",
            template="seaborn"
        )

        return fig


    @render.data_frame
    def toxicityAtLocationTbl():
        df_trash = raw_data_trash.copy()
        df_trash = df_trash.groupby(['Location'], observed=False)['Toxicity'].sum().reset_index()
        df_trash = df_trash.sort_values(by=['Location'])

        return render.DataGrid(
            df_trash,
            width = "100%"
        )


    @render.data_frame
    def toxicityOnBiodTbl():
        df_trash = raw_data_trash.copy()
        df_biod = raw_data_biod.copy()

        df_trash = df_trash.groupby(['Location'], observed=False)['Toxicity'].sum().reset_index()
        df_biod = df_biod.groupby(['Location'], observed=False)['Quantity'].sum().reset_index()

        df = pd.merge(df_trash, df_biod, on="Location")
        df = df.sort_values(by=['Location'])

        return render.DataGrid(
            df,
            width = "100%"
        )


app = App(app_ui, server)
