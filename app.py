import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shinywidgets import output_widget, render_widget


##### Read data from CSVs #####

woc_data_df = pd.read_csv("woc_data.csv")
trash_toxicity_dim = pd.read_csv("trash_toxicity_dim.csv")
data_entry_df = pd.read_csv("data_entry.csv") 


##### Data Modeling #####

trash_amount_fact = woc_data_df[['trash_type', 'location', 'ecosystem_impacted', 'trash_amount']]
trash_amount_fact = trash_amount_fact.dropna()
trash_amount_fact['trash_amount'] = trash_amount_fact['trash_amount'].astype(int)

trash_biod_fact = woc_data_df.drop(['trash_amount'], axis=1).reset_index(drop=True)
trash_biod_fact['individuals_affected'] = trash_biod_fact['individuals_affected'].astype(int)

# Left join to keep only items found in input_data
data_entry_df = data_entry_df.dropna().reset_index(drop=True)
trash_amount_df = trash_amount_fact[trash_amount_fact['trash_type'].isin(data_entry_df['trash_type'])]
trash_amount_df = trash_amount_df.sort_values(by=['trash_type']).reset_index(drop=True)
trash_biod_df = trash_biod_fact[trash_biod_fact['trash_type'].isin(data_entry_df['trash_type'])]
trash_biod_df = trash_biod_df.sort_values(by=['trash_type']).reset_index(drop=True)

trash_location_df = trash_biod_fact[['trash_type', 'location']]
trash_location_df = trash_location_df.drop_duplicates()
trash_location_df = trash_location_df.sort_values(by=['trash_type']).reset_index(drop=True)

# Convert certain columns to categorical
categorical_columns = ['trash_type', 'location', 'ecosystem_impacted', 'species_impacted']
trash_biod_df[categorical_columns] = trash_biod_df[categorical_columns].apply(lambda x: x.astype('category'))


##### UI #####

app_ui = ui.page_fluid(
    ui.layout_columns(
        ui.card(
            ui.panel_title("Pollution and Toxicity on Biodiversity")
        ),
        ui.card(
            ui.card_header("Amount of Trash"),
            ui.layout_columns(
                ui.input_select(
                    id="trashQuantitySelector",
                    label=None,
                    choices={"location": "Location", "ecosystem_impacted": "Ecosystem"},
                    selected="location"
                ),
                ui.input_select(
                    id="scaleTQPlot",
                    label=None,
                    choices={"linear": "Linear", "log": "Logarithmic"},
                    selected="linear"
                ),
                ui.span(
                    ui.input_switch("transposeTQPlot", "", False),
                    style="position:relative; top: 6px;",
                ),
                output_widget("trashQuantityPlot"),
                col_widths=[4, 4, 4, 12]
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
                ui.input_select(
                    id="scaleTLPlot",
                    label=None,
                    choices={"linear": "Linear", "log": "Logarithmic"},
                    selected="linear"
                ),
                ui.span(
                    ui.input_switch("transposeTLPlot", "", False),
                    style="position:relative; top: 6px;",
                ),
                output_widget("toxicityLevelPlot"),
                col_widths=[4, 4, 4, 12]
            )
        ),
        ui.card(
            ui.card_header("Exposure to Types of Trash"),
            ui.layout_columns(
                ui.input_select(
                    id="scaleTBPlot",
                    label=None,
                    choices={"linear": "Linear", "log": "Logarithmic"},
                    selected="linear"
                ),
                ui.span(
                    ui.input_switch("transposeTBPlot", "", False),
                    style="position:relative; top: 6px;",
                ),
                output_widget("trashOnBiodPlot"),
                col_widths=[4, 4, 12]
            )
        ),
        ui.card(
            ui.card_header("Total Exposure"),
            ui.layout_columns(
                ui.input_select(
                    id="scalexTEPlot",
                    label=None,
                    choices={"linear": "Linear", "log": "Logarithmic"},
                    selected="log"
                ),
                ui.input_select(
                    id="scaleYTEPlot",
                    label=None,
                    choices={"linear": "Linear", "log": "Logarithmic"},
                    selected="log"
                ),
                output_widget("totalExposurePlot"),
                col_widths=[4, 4, 12]
            ),
        ),
        col_widths=[12, 6, 6, 6, 6]
    )
)


##### Server #####

def server(input: Inputs, output: Outputs, session: Session):
    @render_widget
    @reactive.event(input.trashQuantitySelector, input.transposeTQPlot, input.scaleTQPlot)
    def trashQuantityPlot():
        trash_df = trash_amount_df.copy()

        if input.trashQuantitySelector() == "ecosystem_impacted":
            trash_df = trash_df.groupby(['ecosystem_impacted', 'trash_type'], observed=False)['trash_amount'].sum().reset_index()
            trash_df = trash_df.sort_values(by=['trash_type']).reset_index(drop=True)

        axes = [input.trashQuantitySelector(), "trash_amount"]
        if input.transposeTQPlot():
            axes = axes[::-1]

        fig = px.bar(
            trash_df,
            x=axes[0],
            y=axes[1],
            color="trash_type",
            template="seaborn"
        )

        if input.scaleTQPlot() == "log" and not input.transposeTQPlot():
            fig.update_layout(
                yaxis_type="log"
            )
        elif input.scaleTQPlot() == "log" and input.transposeTQPlot():
            fig.update_layout(
                xaxis_type="log"
            )

        fig.update_layout(
            xaxis={'categoryorder':'category ascending'},
            yaxis={'categoryorder':'category descending'},
            xaxis_title=None,
            yaxis_title=None,
            legend_title_text='Trash Type'
        )
        return fig


    @render_widget
    @reactive.event(input.toxicityLevelSelector, input.transposeTLPlot, input.scaleTLPlot)
    def toxicityLevelPlot():
        trash_df = trash_amount_df.merge(trash_toxicity_dim, how='left', on='trash_type')
        trash_df['total_toxicity'] = trash_df['toxicity_level'] * trash_df['trash_amount']

        trash_df = trash_df.groupby([input.toxicityLevelSelector(), 'trash_type'], observed=False)['total_toxicity'].sum().reset_index()
        trash_df = trash_df.sort_values(by=['trash_type']).reset_index(drop=True)

        axes = [input.toxicityLevelSelector(), "total_toxicity"]
        if input.transposeTLPlot():
            axes = axes[::-1]

        fig = px.bar(
            trash_df,
            x=axes[0],
            y=axes[1],
            color="trash_type",
            template="seaborn"
        )

        if input.scaleTLPlot() == "log" and not input.transposeTLPlot():
            fig.update_layout(
                yaxis_type="log"
            )
        elif input.scaleTLPlot() == "log" and input.transposeTLPlot():
            fig.update_layout(
                xaxis_type="log"
            )

        fig.update_layout(
            xaxis={'categoryorder':'category ascending'},
            yaxis={'categoryorder':'category descending'},
            xaxis_title=None,
            yaxis_title=None,
            legend_title_text='Trash Type'
        )
        return fig


    @render_widget
    @reactive.event(input.scaleTBPlot, input.transposeTBPlot)
    def trashOnBiodPlot():
        trash_df = trash_biod_df.groupby(['trash_type', 'species_impacted'], observed=False)['individuals_affected'].sum().reset_index()

        axes = ['trash_type', 'individuals_affected']
        if input.transposeTBPlot():
            axes = axes[::-1]

        fig = px.bar(
            trash_df,
            x=axes[0],
            y=axes[1],
            color="species_impacted",
            template="seaborn"
        )

        if input.scaleTBPlot() == "log" and not input.transposeTBPlot():
            fig.update_layout(
                yaxis_type="log"
            )
        elif input.scaleTBPlot() == "log" and input.transposeTBPlot():
            fig.update_layout(
                xaxis_type="log"
            )

        fig.update_layout(
            xaxis={'categoryorder':'category ascending'},
            yaxis={'categoryorder':'category descending'},
            xaxis_title=None,
            yaxis_title=None,
            legend_title_text='Species Impacted'
        )
        return fig


    @render_widget
    @reactive.event(input.scalexTEPlot, input.scaleYTEPlot)
    def totalExposurePlot():
        trash_df = trash_biod_df.drop(columns=['ecosystem_impacted'])
        trash_df = trash_df.merge(trash_amount_fact, how='left', on=['trash_type', 'location'])
        trash_df = trash_df.merge(trash_toxicity_dim, how='left', on='trash_type')
        trash_df['total_toxicity'] = trash_df['toxicity_level'] * trash_df['trash_amount']
        trash_df = trash_df.drop(columns=['location', 'ecosystem_impacted', 'trash_type', 'toxicity_level'])
        trash_df = trash_df.groupby(['species_impacted'], observed=True).sum().reset_index()
        trash_df['total_trash'] = trash_df['trash_amount']

        fig = px.scatter(
            trash_df,
            x="total_trash",
            y="total_toxicity",
            color="species_impacted",
            size="individuals_affected",
            template="seaborn"
        )

        if input.scalexTEPlot() == "log":
            fig.update_layout(
                xaxis_type="log"
            )
        if input.scaleYTEPlot() == "log":
            fig.update_layout(
                yaxis_type="log"
            )

        fig.update_layout(
            xaxis_title="Total Trash (log scale)",
            yaxis_title="Total Toxicity (log scale)",
            legend_title_text="Species Impacted"
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
