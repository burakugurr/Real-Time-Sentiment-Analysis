from turtle import pd
from graphene import Interface
import streamlit as st
from PIL import Image
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import sys

sys.path.append(r"..\Using-GCP")
import MongoModule


"""
---------------- Methods ----------------
"""
def get_data():
    mongo = MongoModule.CONNECT_MONGO()
    results = mongo.find_many()
    df = pd.DataFrame(list(results))
    df.columns = ['_id', 'text', 'search_topic', 'sentiment', 'time']
    return df


def draw_bar(data):
    fig = make_subplots(rows=1, cols=2)

    fig.append_trace(
        go.pie(    x=data['sentiment'].value_count().tolist(),
                   y=data['sentiment'].value_count(),
                   name='Sentiment Pie Chart',
                   marker=dict(color='purple', size=2),
                   showlegend=True), 1, 1)

    fig.append_trace(
        go.Bar(    x=data['sentiment'].value_count().tolist(),
                   y=data['sentiment'].value_count(),
                   name='Sentiment Bar Chart',
                   marker=dict(color='cyan', size=2),
                   showlegend=True), 1, 2)

    fig.update_layout(
        title="Sentiment Analysis",
        xaxis_title="Sentiment Status",
        yaxis_title="Tweet Count",
        legend_title="Legend",
        legend=dict(x=1, y=1),
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"
        )
    )
    return fig

def draw_table(df):
    st.write(df)
    st.write(df.sentiment.value_counts())
    st.write(df.sentiment.value_counts().plot(kind='bar'))



"""
---------------- USER Interface ----------------
"""
image = Image.open(r"..\img\asd.png")


st.header("Search The Topic")
st.image(image, use_column_width=True, output_format='PNG')

col_left,col_right = st.columns(2)
search_topic = col_left.text_input("Please enter the topic",placeholder="Topic Name")

count_size = col_right.number_input("Please insert the count size",value=2000)

# collect data
df = get_data()


# draw chart
fig = draw_bar(df)
st.plotly_chart(fig)



# # Add producer 
# getTweetanalyzer = Producer.Publisher()
# getTweetanalyzer.Analyzer(search_topic,count_size)

# get analyzed tweets
