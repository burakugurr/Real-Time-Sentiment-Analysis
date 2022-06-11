


from tkinter.messagebox import NO
import streamlit as st
from PIL import Image
import pandas as pd
import pandas_profiling
from streamlit_pandas_profiling import st_profile_report
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import time
import sys

sys.path.append(r"..\Using-GCP")
import producer
import MongoModule

# ---------------- Methods ----------------


def wordCloud(df):
    text = df.text.str.cat(sep=' ')

    # Create and generate a word cloud image:
    wordcloud = WordCloud().generate(text)

    # Display the generated image:
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()


def get_data(search_topic=None):
    mongo = MongoModule.CONNECT_MONGO()
    results = mongo.find_many()
    df = pd.DataFrame(list(results))
    df.columns = ['_id', 'text', 'search_topic', 'sentiment', 'time']
    df.sentiment = df.sentiment.apply(lambda x: x.capitalize())
    df.time = pd.to_datetime(df.time)
    df['Date'] = df.time.dt.date
    df['Time'] = df.time.dt.time.apply(lambda x: x.strftime('%H:%M:%S'))

    df.sort_values(by=['time'], inplace=True)
    df.drop(columns=['_id'], inplace=True)
    df.drop(columns=['time'], inplace=True)

    if search_topic is not None:
        return df[df['search_topic'] == search_topic]
    else:
        return df


def get_hist_data():
    mongos = MongoModule.CONNECT_HIST()
    results = mongos.get_sentimentHistory()

    df = pd.DataFrame(list(results))
    df.columns = ['sentiment', 'time']

    if df.empty:
        df.fillna(0, inplace=True)
    return df


def draw_bar(data):

    append_trace2 = go.Bar(x=df['sentiment'].unique().tolist(),
                           y=data['sentiment'].value_counts(),
                           name='Sentiment Bar Chart',
                           showlegend=True)

    layout = go.Layout(

        xaxis_title="Sentiment Status",
        yaxis_title="Tweet Count",
        legend_title="Legend",
        legend=dict(x=1, y=1),
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family="arial",
            size=18,
            color="#7f7f7f"
        )
    )
    data = [append_trace2]
    fig = go.Figure(data=data, layout=layout)

    return fig


def draw_pie(df):

    append_trace1 = go.Pie(labels=df['sentiment'].unique().tolist(),
                           values=df['sentiment'].value_counts().to_list(),
                           name='Sentiment Pie Chart',
                           showlegend=True)

    layout = go.Layout(
        xaxis_title="Sentiment Status",
        yaxis_title="Tweet Count",
        legend_title="Legend",
        legend=dict(x=1, y=1),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family="arial",
            size=15,
            color="#7f7f7f"
        )
    )
    data = [append_trace1]
    fig = go.Figure(data=data, layout=layout)

    return fig


# ---------------- USER Interface ----------------
st.set_page_config(layout="wide")
st.set_option('deprecation.showPyplotGlobalUse', False)


image = Image.open(r"..\img\asd.png")

with st.container():
    x1, x2 = st.columns(2)
    x1.image(image, width=350)
    HeaderText = '<h1 style="color:green;text-align:left;font-size:460%;font-family:Times">Sentiment Analysis for Twitter </h1>'
    x2.markdown(HeaderText, unsafe_allow_html=True)

search_topic = st.selectbox(
    "Please select the topic you want to search", get_data().search_topic.unique().tolist())


with st.spinner('Loading...'):
    df = get_data(search_topic)

    time.sleep(5)
    st.success('Done!')

    col1, col2, col3 = st.columns(3)
    try:
        col1.metric(label="Negative Sentiment", value=df['sentiment'].value_counts()['Negative'],
                    delta=0,
                    delta_color="inverse")
    except KeyError:
        col1.metric(label="Negative Sentiment", value="No Data",
                    delta=0,
                    delta_color="inverse")
    try:
        col2.metric(label="Pozitive Sentiment", value=df['sentiment'].value_counts()['Positive'],
                    delta=0,
                    delta_color="normal")
    except KeyError:
        col2.metric(label="Pozitive Sentiment", value="No Data",
                    delta=0,
                    delta_color="normal")
    try:
        col3.metric(label="Neutral Sentiment", value=df['sentiment'].value_counts()['Neutral'],
                    delta=0,
                    delta_color="off")

    except KeyError:
        col3.metric(label="Neutral Sentiment", value="No Data",
                    delta=0,
                    delta_color="off")

    st.subheader("Tweets by Sentiment")
    st.dataframe(df)

    x, y = st.columns(2)
    x.header("Sentiment Bar Chart")
    x.plotly_chart(draw_bar(df))

    y.header("Sentiment Pie Chart")
    y.plotly_chart(draw_pie(df))

    with st.expander("See Word Cloud"):
        st.pyplot(wordCloud(df))
