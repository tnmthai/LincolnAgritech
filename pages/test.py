import streamlit as st
import pandas as pd
import numpy as np

chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['a', 'b', 'c'])

st.line_chart(chart_data)

# Add JavaScript code to capture click events on the chart
st.components.v1.html(
    """
    <script>
    const chart = document.getElementsByTagName('canvas')[0].getContext('2d');
    chart.canvas.addEventListener('click', function(e) {
        const points = chart.getElementsAtEventForMode(e, 'point', { intersect: true });
        if (points.length > 0) {
            const point = points[0];
            const datasetIndex = point.datasetIndex;
            const index = point.index;
            const value = chart.data.datasets[datasetIndex].data[index];
            console.log('Clicked value:', value);
            // You can further process the value as per your requirement
        }
    });
    </script>
    """,
    height=1,
)
