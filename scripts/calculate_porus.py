from scipy import signal, integrate
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import datetime
import sys


def calculate_porus(csv,threshold):
    data = pd.read_csv(csv)
    fig = go.Figure()
    n_peaks_dict = {}
    magnitude_dict = {}
    integral_dict = {}
    first_time = datetime.datetime.strptime(data["Timestamp"][0], "%H:%M:%S")
    unnamed_cols = [c for c in data.columns if c.startswith("Unnamed")]
    data = data.drop(columns=unnamed_cols)

    data["Timestamp"] = data["Timestamp"].apply(
        lambda x: (datetime.datetime.strptime(x, "%H:%M:%S")-first_time).total_seconds())
    for column in data.columns:
        if column == "Timestamp":
            continue
            
        normalized = data[column] - data[column][0]
        normalized = normalized + abs(min(normalized))
        filtered = signal.medfilt(normalized,kernel_size=5)
        fig.add_trace(
            go.Scatter(
                x=data["Timestamp"],
                y=filtered,
                mode="lines",
                name=column,
            )
        )
        peaks = signal.find_peaks(filtered, height=threshold, distance=200)[0]
        
        if len(peaks) == 0:
            print(f"No peaks found for {column}")
            integrals = []
        else:
            integrals = []
            for peak in peaks:
                integrals.append(integrate.trapezoid(filtered[peak-30:peak+300],data["Timestamp"][peak-30:peak + 300]))
                #minus the square
                fig.add_annotation(text=f"{integrals[-1]:.2f}",x=data["Timestamp"][peak],y=filtered[peak], showarrow=True)
        
        n_peaks_dict[column] = len(peaks)
        integral_dict[column] = integrals
        magnitude_dict[column] = sum([filtered[i] for i in peaks])
        fig.add_trace(
            go.Scatter(
                x=[data["Timestamp"][peak] for peak in peaks],
                y=[filtered[i] for i in peaks],
                mode="markers",
                marker=dict(size=8, color="red", symbol="cross"),
                name=f"{column} peaks",
            )
        )
        
    fig.show()
    print(n_peaks_dict)
    print(integral_dict)


if __name__ == "__main__":
    calculate_porus("data/test_13_T.csv",threshold=0.7)
    #calculate_porus(str(sys.argv[1]),str(sys.argv[2]))
