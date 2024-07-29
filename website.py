import streamlit as st
import duckdb
import pandas as pd

import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
import matplotlib.colors

st.write("Hellowwwww!!")
df = pd.read_parquet('https://storage.data.gov.my/dashboards/prasarana_timeseries.parquet')

def sankey_passengers():
    df1 = duckdb.sql("""
            with a as (
            SELECT
            concat(origin, ' (Origin)') as train_origin, 
            concat(destination, ' (Destination)') as train_destination,
            sum(passengers) as total_passengers
            FROM df
            WHERE origin <> destination
                AND origin not ilike '%all station%'
                AND destination not ilike '%all station%'
                AND frequency = 'monthly'
            GROUP BY ALL)
            
            SELECT *
            FROM a
            ORDER BY total_passengers DESC
            LIMIT 30
        """).df()

    #for using with 'label' parameter in plotly 
    #https://sparkbyexamples.com/pandas/pandas-find-unique-values-from-columns
    unique_source_target = list(pd.unique(df1[['train_origin', 'train_destination']].values.ravel('K')))

    link_opacity = 0.3  # Set a value from 0 to 1: the lower, the more transparent the links

    # Define a list of hex color codes for nodes
    node_colors = px.colors.qualitative.G10  

    # Convert list of colors to RGB format to override default gray link colors
    colors = [matplotlib.colors.to_rgb(i) for i in node_colors]  

    # Create objects to hold node/label and link colors
    label_colors, df1["link_c"] = [], str(0)

    # Loop through all the labels to specify color and to use label indices
    c, max_colors = 0, len(colors)  # To loop through the colors array
    for l in range(len(unique_source_target)):
        label_colors.append(colors[c])
        link_color = colors[c] + (link_opacity,)  # Make link more transparent than the node
        df1.loc[df1['train_origin'] == unique_source_target[l], "link_c"] = "rgba" + str(link_color)
        # df1 = df1.replace({unique_source_target[l]: l})  # Replace node labels with the label's index
        if c == max_colors - 1:
            c = 0
        else:
            c += 1

    # Convert colors into RGB string format for Plotly
    label_colors = ["rgb" + str(i) for i in label_colors]

    #converting full dataframe as list for using with in plotly
    links_dict = df1.to_dict(orient='list')


    #for assigning unique number to each source and target
    mapping_dict = {k: v for v, k in enumerate(unique_source_target)}

    #mapping of full data
    df1['train_origin'] = df1['train_origin'].map(mapping_dict)
    df1['train_destination'] = df1['train_destination'].map(mapping_dict)


    links_dict = df1.to_dict(orient='list')


    #Sankey Diagram Code 
    fig = go.Figure(data=[go.Sankey(
        arrangement = "snap",
        node = dict(
        pad = 25,
        thickness = 50,
        line = dict(color = "black", width = 0.7),
        label = unique_source_target,
        color = label_colors
        
        ),
        link = dict(
        arrowlen=15,
        source = links_dict["train_origin"],
        target = links_dict["train_destination"],
        value = links_dict["total_passengers"],
        color = links_dict["link_c"]
    
    ))])

    fig.update_layout(title_text="Total Passengers To-From Stations")
    
    return fig

st.plotly_chart(sankey_passengers(), use_container_width=True)

# st.bar_chart(x='line_name_origin', y='total_passengers', data=df)
