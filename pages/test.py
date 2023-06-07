import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['a', 'b', 'c'])

# Create an Altair line chart
chart = alt.Chart(chart_data).mark_line().encode(
    x='index',
    y=alt.Y(alt.repeat('column'), type='quantitative'),
    color='column'
).properties(
    width=600,
    height=400
)

# Use Streamlit to render the Altair chart
st.altair_chart(chart, use_container_width=True)

# Handle mouseover events to capture values
values = []

@st.cache(allow_output_mutation=True)
def handle_mouseover(value):
    values.append(value)

st.write("Values when dragging the mouse:")
chart.add_selection(
    alt.selection_single(on='mouseover', nearest=True, empty='none')
).transform_filter(
    alt.datum.column == alt.value('a')
).add_mark(
    alt.Rule().encode(
        y='mean(value)',
        size=alt.value(2),
        color=alt.value('red')
    )
).transform_calculate(
    value=alt.datum.a
).interactive().add_listener(
    "mouseover", handle_mouseover
)

# Display the captured values
st.write(values)
