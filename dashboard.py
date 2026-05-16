import streamlit as st
import paho.mqtt.client as mqtt
import pandas as pd
import time
import base64
import plotly.express as px
import itertools

from collections import deque
from datetime import datetime

# =====================================
# LOAD LOCAL BACKGROUND IMAGE
# =====================================

def get_base64(bin_file):

    with open(bin_file, "rb") as f:

        data = f.read()

    return base64.b64encode(data).decode()

bg_image = get_base64("greenhouse_bg.jpg")

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Smart Greenhouse Dashboard",
    page_icon="🌱",
    layout="wide"
)

# =====================================
# CUSTOM CSS
# =====================================

st.markdown(f"""
<style>

/* Background Image */
.stApp {{
    background-image: url("data:image/jpg;base64,{bg_image}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

/* Remove white top area */
header {{
    background-color: rgba(0,0,0,0) !important;
}}

[data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
}}

/* Global text */
html, body, [class*="css"] {{
    color: white !important;
}}

/* Main container */
.block-container {{

    padding-top: 1rem;
    padding-bottom: 0rem;
    padding-left: 2rem;
    padding-right: 2rem;

    background-color: rgba(0,0,0,0.55);

    border-radius: 12px;
}}

/* Metric cards */
.stMetric {{

    background-color: rgba(30,30,30,0.88);

    padding: 10px;

    border-radius: 12px;

    border: 1px solid #333333;

    box-shadow: 0px 0px 8px rgba(0,255,100,0.2);
}}

/* Metric labels */
[data-testid="stMetricLabel"] {{

    color: white !important;

    font-size: 18px;

    font-weight: bold;
}}

/* Metric values */
[data-testid="stMetricValue"] {{

    color: white !important;

    font-size: 34px;

    font-weight: bold;
}}

/* Headers */
h1, h2, h3 {{

    color: #7CFC00 !important;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{

    background-color: rgba(22,27,34,0.96);
}}

/* Sidebar text */
section[data-testid="stSidebar"] * {{

    font-size: 18px !important;
}}

/* Alert boxes */
.alert-box {{

    background-color: rgba(42,42,42,0.92);

    padding: 10px;

    border-radius: 10px;

    margin-bottom: 10px;

    font-size: 18px;

    font-weight: bold;

    color: white;

    border-left: 5px solid #7CFC00;
}}

/* Chart cards */
.chart-card {{

    background-color: rgba(30,30,30,0.88);

    padding: 12px;

    border-radius: 14px;

    border: 1px solid #333333;

    box-shadow: 0px 0px 8px rgba(0,255,100,0.2);

    margin-bottom: 10px;
}}

hr {{

    margin-top: 8px;

    margin-bottom: 8px;
}}

</style>
""", unsafe_allow_html=True)

# =====================================
# DATA STORAGE
# =====================================

data = {

    "temp": 0,

    "rh": 0,

    "ec": 0,

    "ph": 0,

    "fan": "OFF",

    "fogger": "OFF"
}

# =====================================
# HISTORY STORAGE
# =====================================

max_points = 20

temp_history = deque(maxlen=max_points)

rh_history = deque(maxlen=max_points)

time_history = deque(maxlen=max_points)

# =====================================
# ALERT STORAGE
# =====================================

alerts = deque(maxlen=10)

# =====================================
# CHART COUNTER
# =====================================

chart_counter = itertools.count()

# =====================================
# ALERT FUNCTION
# =====================================

def add_alert(message):

    current_time = datetime.now().strftime("%H:%M:%S")

    alert_message = f"{current_time} → {message}"

    alerts.appendleft(alert_message)

# =====================================
# MQTT CALLBACK
# =====================================

def on_message(client, userdata, msg):

    topic = msg.topic

    value = msg.payload.decode()

    current_time = datetime.now().strftime("%H:%M:%S")

    if topic == "greenhouse/temp":

        temp = float(value)

        data["temp"] = temp

        temp_history.append(temp)

        time_history.append(current_time)

        if temp > 35:

            add_alert("🔥 Critical Temperature")

        elif temp > 30:

            add_alert("🌡️ High Temperature")

    elif topic == "greenhouse/rh":

        rh = float(value)

        data["rh"] = rh

        rh_history.append(rh)

        if rh < 55:

            add_alert("💧 Low Humidity")

    elif topic == "greenhouse/ec":

        ec = float(value)

        data["ec"] = ec

        if ec < 1.5:

            add_alert("🧪 Low EC")

    elif topic == "greenhouse/ph":

        ph = float(value)

        data["ph"] = ph

        if ph > 6.5:

            add_alert("⚗️ High pH")

    elif topic == "greenhouse/fan_status":

        data["fan"] = value

    elif topic == "greenhouse/fogger_status":

        data["fogger"] = value

# =====================================
# MQTT SETUP
# =====================================

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.on_message = on_message

client.connect("localhost", 1883, 60)

client.subscribe("greenhouse/#")

client.loop_start()

# =====================================
# SIDEBAR
# =====================================

st.sidebar.title("⚙️ System Status")

st.sidebar.success("MQTT Broker Connected")

st.sidebar.info("Intelligent Controller Active")

st.sidebar.write("---")

st.sidebar.subheader("🚨 Alerts")

alert_placeholder = st.sidebar.empty()

# =====================================
# TITLE
# =====================================

st.title("🌱 Smart Greenhouse IoT Dashboard")

# =====================================
# MAIN PLACEHOLDER
# =====================================

main_placeholder = st.empty()

# =====================================
# DASHBOARD LOOP
# =====================================

while True:

    with main_placeholder.container():

        # SENSOR METRICS

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "🌡️ Temperature",
            f"{data['temp']} °C"
        )

        col2.metric(
            "💧 Humidity",
            f"{data['rh']} %"
        )

        col3.metric(
            "🧪 EC",
            f"{data['ec']}"
        )

        col4.metric(
            "⚗️ pH",
            f"{data['ph']}"
        )

        st.write("---")

        # ACTUATOR STATUS

        act1, act2 = st.columns(2)

        fan_status = "🟢 ON" if data["fan"] == "ON" else "🔴 OFF"

        fogger_status = "🟢 ON" if data["fogger"] == "ON" else "🔴 OFF"

        act1.metric(
            "🌀 Fan-Pad",
            fan_status
        )

        act2.metric(
            "🌫️ Fogger",
            fogger_status
        )

        st.write("---")

        # ALERTS

        with alert_placeholder.container():

            alert_snapshot = list(alerts)

            for alert in alert_snapshot:

                st.markdown(
                    f'<div class="alert-box">{alert}</div>',
                    unsafe_allow_html=True
                )

        # CHARTS

        chart_col1, chart_col2 = st.columns(2)

        # TEMPERATURE CHART

        with chart_col1:

            st.markdown(
                '<div class="chart-card">',
                unsafe_allow_html=True
            )

            if len(temp_history) > 1:

                temp_df = pd.DataFrame({

                    "Time": list(time_history),

                    "Temperature": list(temp_history)

                })

                fig_temp = px.line(

                    temp_df,

                    x="Time",

                    y="Temperature",

                    title="Temperature Trend"
                )

                fig_temp.update_layout(

                    xaxis_title="Time",

                    yaxis_title="Temperature (°C)",

                    title_font=dict(
                        size=22,
                        color="white"
                    ),

                    xaxis=dict(
                        title_font=dict(
                            size=18,
                            color="white"
                        ),

                        tickfont=dict(
                            size=14,
                            color="white"
                        ),

                        showgrid=False
                    ),

                    yaxis=dict(
                        title_font=dict(
                            size=18,
                            color="white"
                        ),

                        tickfont=dict(
                            size=14,
                            color="white"
                        ),

                        showgrid=False
                    ),

                    template="plotly_dark",

                    height=300,

                    plot_bgcolor="rgba(30,30,30,0.88)",

                    paper_bgcolor="rgba(30,30,30,0.88)",

                    font=dict(
                        color="white",
                        size=16
                    )
                )

                st.plotly_chart(
                    fig_temp,
                    use_container_width=True,
                    key=f"temp_chart_{next(chart_counter)}"
                )

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )

        # HUMIDITY CHART

        with chart_col2:

            st.markdown(
                '<div class="chart-card">',
                unsafe_allow_html=True
            )

            if len(rh_history) > 1:

                rh_df = pd.DataFrame({

                    "Time": list(time_history),

                    "Humidity": list(rh_history)

                })

                fig_rh = px.line(

                    rh_df,

                    x="Time",

                    y="Humidity",

                    title="Humidity Trend"
                )

                fig_rh.update_layout(

                    xaxis_title="Time",

                    yaxis_title="Humidity (%)",

                    title_font=dict(
                        size=22,
                        color="white"
                    ),

                    xaxis=dict(
                        title_font=dict(
                            size=18,
                            color="white"
                        ),

                        tickfont=dict(
                            size=14,
                            color="white"
                        ),

                        showgrid=False
                    ),

                    yaxis=dict(
                        title_font=dict(
                            size=18,
                            color="white"
                        ),

                        tickfont=dict(
                            size=14,
                            color="white"
                        ),

                        showgrid=False
                    ),

                    template="plotly_dark",

                    height=300,

                    plot_bgcolor="rgba(30,30,30,0.88)",

                    paper_bgcolor="rgba(30,30,30,0.88)",

                    font=dict(
                        color="white",
                        size=16
                    )
                )

                st.plotly_chart(
                    fig_rh,
                    use_container_width=True,
                    key=f"rh_chart_{next(chart_counter)}"
                )

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )

        st.caption(
            "MQTT + Streamlit + Intelligent Greenhouse Control"
        )

    time.sleep(1)