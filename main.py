import re
import sys
import math
import numpy as np
import pandas as pd
import maidenhead as mh
from geopy.distance import geodesic


YOUR_LOCATOR = "<INSERT LOC HERE>"
POWER_FACTOR = 500


def check_maidenhead(locator):
    pattern = re.compile(
        r'^[A-R]{2}([0-9]{2}([a-x]{2}([0-9]{2})?)?)?$'
    )
    return bool(pattern.fullmatch(locator))


def distance_and_bearing(start_locator, end_locator):
    """
    Calculate the distance (in kilometers) and initial bearing (in degrees)
    between two Maidenhead locators.
    """
    # Convert Maidenhead locators to lat/lon
    if not check_maidenhead(end_locator):
        print(f"{end_locator} appears to be an invalid maidenhead locator", file=sys.stderr)
        sys.exit(1)
    lat1, lon1 = mh.to_location(start_locator, center=True)
    lat2, lon2 = mh.to_location(end_locator, center=True)

    # Compute geodesic distance
    distance_km = geodesic((lat1, lon1), (lat2, lon2)).kilometers

    # Compute initial bearing
    delta_lon = math.radians(lon2 - lon1)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    x = math.sin(delta_lon) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lon)

    initial_bearing = math.degrees(math.atan2(x, y))
    bearing = (initial_bearing + 360) % 360

    return distance_km, bearing


def distance_and_bearing_generator(start_loc, list_in):
    for i in list_in:
        #print(i)
        yield distance_and_bearing(start_loc, i)


def data_frame_from_file(filename, verbose=False):
    with open(filename, "r") as file:
        table = [i.split(",") for i in file.read().splitlines()]

    df = pd.DataFrame(table, columns=[
        "Date_s", "Time_s",
        "Date_e", "Time_e",
        "Call", "Locator",
        "Frequency", "Mode",
        "Report Recv", "Report Response", "PWR",
        "Comment", "Unused1", "Unused2"
        ])
    for i in range(len(table)):
        if df.loc[i, "Locator"] == "" and i < len(table):
            df = df.drop(i)
            print(f"row {i + 1} dropped")
            continue
        if i >= len(table):
            break
        if df.loc[i, "PWR"] == "":
            df.loc[i, "PWR"] = "50"  # 50%
        elif not df.loc[i, "PWR"].replace(".", "", 1).isnumeric():
            for j in df.loc[i, "PWR"].split(" "):
                if j.replace(".", "", 1).isnumeric():
                    df.loc[i, "PWR"] = j

    df = df.astype({
        "Frequency": float,
        "Report Recv": int,
        "Report Response": int,
        "PWR": float,
        })
    df["Datetime_s"] = pd.to_datetime(df["Date_s"] + " " + df["Time_s"])
    df["Datetime_e"] = pd.to_datetime(df["Date_e"] + " " + df["Time_e"])

    df["Distance"], df["Bearing"] = zip(*list(distance_and_bearing_generator(
        YOUR_LOCATOR, df["Locator"]
    )))

    if verbose: print(df[["Datetime_s", "Call", "Locator", "Report Recv", "PWR", "Distance", "Bearing"]])
    return df


def plot_df(df):
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    ax.set_title("Distance and Bearring")
    ax.grid(True)
    ax.grid(which="minor", linestyle="dashed", alpha=0.3)
    ax.minorticks_on()
    sc = ax.scatter(
        df["Bearing"].to_list(),
        df["Distance"].to_list(),
        c=df["Report Recv"].to_list(),
        s=(POWER_FACTOR/df["PWR"]).to_list(),
            cmap="berlin"
    )
    
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_rscale("log")
    
    fig.colorbar(sc).set_label("Report") # df["Report Recv"].to_list()
    
    fig1, ax1 = plt.subplots(subplot_kw={"projection": "polar"})
    ax1.set_title("Distance and Bearring")
    ax1.grid(True)
    ax1.grid(which="minor", linestyle="dashed", alpha=0.3)
    ax1.minorticks_on()
    sc = ax1.scatter(
         df["Bearing"].to_list(),
         df["Distance"].to_list(),
         c=df["Report Recv"].to_list(),
         s=(500/df["PWR"]).to_list(),
             cmap="berlin"
    )
    
    ax1.set_theta_zero_location("N")
    ax1.set_theta_direction(-1)
    
    fig1.colorbar(sc).set_label("Report") # df["Report Recv"].to_list()
    
    print(max(df["Distance"]))
    plt.figure("Distance")
    plt.title("Distances")
    plt.xscale("log")
    plt.hist(df["Distance"],
             bins=np.logspace(np.log10(min(df["Distance"])),
                              np.log10(max(df["Distance"])), 13)
    )
    
    
    plt.xlabel("Distance (km)")
    plt.ylabel("Count")
    
    plt.grid()
    
    plt.figure("RCV")
    plt.title("Reports")
    plt.grid()
    plt.grid(which="minor", linestyle="dashed", alpha=0.3)
    plt.minorticks_on()
    plt.xlabel("Report (dB SNR)")
    plt.ylabel("Count")
    
    plt.hist(df["Report Recv"])
    
    
    plt.figure("RCV to DIST")
    plt.title("Report by Distance")
    plt.scatter(
         df["Distance"].to_list(),
         df["Report Recv"].to_list(),
             c=df["PWR"].to_list(),
             cmap="berlin")
    plt.colorbar().set_label("Power")
    plt.xscale("log")
    
    plt.xlabel("Distance (km)")
    plt.ylabel("Report (dB SNR)")
    
    plt.grid()
    plt.grid(which="minor", linestyle="dashed", alpha=0.3)
    plt.minorticks_on()
    
    plt.figure("RCV to PWR")
    plt.title("Report by Power")
    plt.scatter(
         df["PWR"].to_list(),
             df["Report Recv"].to_list())
    plt.title("Report by Power")
    plt.grid()
    plt.grid(which="minor", linestyle="dashed", alpha=0.3)
    plt.minorticks_on()
    
    plt.xlabel("Power (W)")
    plt.ylabel("Report (dB SNR)")
    
    df.boxplot(column="Report Recv", by="PWR")
    
    plt.xlabel("Power (W)")
    plt.ylabel("Report (dB SNR)")
    
    plt.show()


def main():
    if YOUR_LOCATOR == "<INSERT LOC HERE>":
        import os
        if "YOUR_LOCATOR" in os.environ:
            loc = os.environ["YOUR_LOCATOR"]
        else:
            print("No station locator found", file=sys.stderr)
            print("Please set \"YOUR_LOCATOR\" in the enviroment variables", file=sys.stderr)
            print("or provide one as argument", file=sys.stderr)
            sys.exit(1)
    if not check_maidenhead(YOUR_LOCATOR):
        print(f"{YOUR_LOCATOR} appears to be an invalid maidenhead locator", file=sys.stderr)
        sys.exit(1)
    plot_df(data_frame_from_file(sys.argv[1]))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <Log file> [<Your locator>]", file=sys.stderr)
        sys.exit(1)
    if len(sys.argv) == 3:
        YOUR_LOCATOR = sys.argv[2]
    elif len(sys.argv) > 3:
        print(f"Usage: {sys.argv[0]} <Log file> [<Your locator>]", file=sys.stderr)
        sys.exit(1)
    main()
