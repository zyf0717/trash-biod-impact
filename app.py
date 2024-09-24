import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shinywidgets import output_widget, render_widget


##### Data #####

# Read CSVs
trash_toxicity_dim = pd.read_csv("trash_toxicity_dim.csv")
trash_amount_fact = pd.read_csv("trash_amount_fact.csv")
trash_biod_fact = pd.read_csv("trash_biod_fact.csv")
trash_location_input = pd.read_csv("trash_location_all.csv")  # To replace with input data "input_data.csv"

# Left join to keep only items found in input_data
trash_amount_df = trash_location_input.merge(trash_amount_fact, how='left', on=['trash_type', 'location'])
trash_biod_df = trash_location_input.merge(trash_biod_fact, how='left', on=['trash_type', 'location'])

# Convert certain columns to categorical
categorical_columns = ['trash_type', 'location', 'ecosystem_impacted', 'species_impacted']
trash_biod_df[categorical_columns] = trash_biod_df[categorical_columns].apply(lambda x: x.astype('category'))


##### UI #####

app_ui = ui.page_fluid(
    ui.layout_columns(
        ui.card("Pollution, Toxicity and Biodiversity"),
        ui.card(
            ui.card_header("Amount of Trash"),
            ui.layout_columns(
                ui.input_select(
                    id="trashQuantitySelector",
                    label=None,
                    choices={"location": "Location", "ecosystem_impacted": "Ecosystem"},
                    selected="location"
                ),
                output_widget("trashQuantityPlot"),
                col_widths=[6, 12]
            )
        ),
        ui.card(
            ui.card_header("Total Toxicity"),
            ui.layout_columns(
                ui.input_select(
                    id="toxicityLevelSelector",
                    label=None,
                    choices={"location": "Location", "ecosystem_impacted": "Ecosystem"},
                    selected="location"
                ),
                output_widget("toxicityLevelPlot"),
                col_widths=[6, 12]
            )
        ),
        # ui.card(
        #     ui.card_header("Total Toxicity"),
        #     output_widget("toxicityPlot")
        # ),
        ui.card(
            ui.card_header("Impact on Biodiversity"),
            output_widget("trashOnBiodPlot")
        ),
        # ui.card(
        #     ui.card_header("Toxicity at Location"),
        #     ui.output_data_frame("toxicityAtLocationTbl")
        # ),
        # ui.card(
        #     ui.card_header("Toxicity at Location"),
        #     ui.output_data_frame("toxicityOnBiodTbl")
        # ),
        col_widths=[12, 6, 6, 6]
    )
)


##### Server #####

def server(input: Inputs, output: Outputs, session: Session):
    @render_widget
    @reactive.event(input.trashQuantitySelector)
    def trashQuantityPlot():
        trash_df = trash_amount_df.copy()

        if input.trashQuantitySelector() == "ecosystem_impacted":
            trash_df = trash_df.groupby(['ecosystem_impacted', 'trash_type'], observed=False)['trash_amount'].sum().reset_index()
            trash_df = trash_df.sort_values(by=['trash_type']).reset_index(drop=True)
        elif input.trashQuantitySelector() == "location":
            trash_df = trash_df.sort_values(by='trash_type')

        fig = px.bar(
            trash_df,
            x=input.trashQuantitySelector(),
            y="trash_amount",
            color="trash_type",
            template="seaborn"
        )
        fig.update_layout(
            xaxis={'categoryorder':'category ascending'},
            xaxis_title=None,
            yaxis_title=None,
        )
        return fig


    @render_widget
    @reactive.event(input.toxicityLevelSelector)
    def toxicityLevelPlot():
        trash_df = trash_amount_df.merge(trash_toxicity_dim, how='left', on='trash_type')
        trash_df['total_toxicity'] = trash_df['toxicity_level'] * trash_df['trash_amount']

        if input.toxicityLevelSelector() == "location":
            trash_df = trash_df.groupby(['location', 'trash_type'], observed=False)['total_toxicity'].sum().reset_index()
            trash_df = trash_df.sort_values(by=['trash_type']).reset_index(drop=True)

        elif input.toxicityLevelSelector() == "ecosystem_impacted":
            trash_df = trash_df.groupby(['ecosystem_impacted', 'trash_type'], observed=False)['total_toxicity'].sum().reset_index()
            trash_df = trash_df.sort_values(by=['trash_type']).reset_index(drop=True)
        
        fig = px.bar(
            trash_df,
            x=input.toxicityLevelSelector(),
            y="total_toxicity",
            color="trash_type",
            template="seaborn"
        )
        fig.update_layout(
            xaxis={'categoryorder':'category ascending'},
            xaxis_title=None,
            yaxis_title=None,
        )
        return fig


    # @render_widget
    # def toxicityPlot():
    #     trash_df = raw_data_trash.copy()
    #     trash_df = trash_df.groupby(['Location', 'Trash'], observed=False)['Toxicity'].sum().reset_index()
    #     trash_df = trash_df.sort_values(by=['Trash'])
    #     fig = px.bar(
    #         trash_df,
    #         x="Location",
    #         y="Toxicity",
    #         color="Trash",
    #         template="seaborn"
    #     )
    #     fig.update_layout(
    #         xaxis={'categoryorder':'category ascending'}
    #     )
    #     return fig


    @render_widget
    def trashOnBiodPlot():
        trash_df_effect = trash_biod_df.groupby(['trash_type', 'species_impacted'], observed=False)['individuals_affected'].sum().reset_index()

        fig = px.bar(
            trash_df_effect,
            x="trash_type",
            y="individuals_affected",
            color="species_impacted",
            template="seaborn"
        )
        fig.update_layout(
            xaxis={'categoryorder':'category ascending'},
            xaxis_title="Trash Type",
            yaxis_title="Trash Amount",
        )
        return fig


    # @render.data_frame
    # def toxicityAtLocationTbl():
    #     trash_df = raw_data_trash.copy()
    #     trash_df = trash_df.groupby(['Location'], observed=False)['Toxicity'].sum().reset_index()
    #     trash_df = trash_df.sort_values(by=['Location'])

    #     return render.DataGrid(
    #         trash_df,
    #         width = "100%"
    #     )


    # @render.data_frame
    # def toxicityOnBiodTbl():
    #     trash_df = raw_data_trash.copy()
    #     df_biod = raw_data_biod.copy()

    #     trash_df = trash_df.groupby(['Location'], observed=False)['Toxicity'].sum().reset_index()
    #     df_biod = df_biod.groupby(['Location'], observed=False)['Quantity'].sum().reset_index()

    #     df = pd.merge(trash_df, df_biod, on="Location")
    #     df = df.sort_values(by=['Location'])

    #     return render.DataGrid(
    #         df,
    #         width = "100%"
    #     )


app = App(app_ui, server)
