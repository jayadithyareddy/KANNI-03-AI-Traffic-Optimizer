from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
import json
from datetime import datetime

from utils import create_features


app = Flask(__name__)
CORS(app)

print("==========================================")
print("       KANNI-03 AI TRAFFIC OPTIMIZER")
print("==========================================")

print("Loading model...")

model = joblib.load("traffic_model.pkl")
label_encoders = joblib.load("label_encoders.pkl")
feature_columns = joblib.load("feature_columns.pkl")

print("✅ XGBoost model loaded and fitted")
print("✅ Label encoders loaded")
print("✅ Feature columns loaded")
print("Number of features:", len(feature_columns))
print("Features:", feature_columns)

print("==========================================")


HISTORY_FILE = "traffic_history.json"


def load_history():

    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)

    except:
        return []


def save_history(history):

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)


@app.route("/")
def home():

    return jsonify({
        "project": "KANNI-03",
        "status": "Running"
    })


@app.route("/predict", methods=["POST"])
def predict():

    try:

        data = request.json

        car = int(data["CarCount"])
        bike = int(data["BikeCount"])
        bus = int(data["BusCount"])
        truck = int(data["TruckCount"])

        day_name = data["Day of the week"]
        traffic = data["Traffic Situation"]

        total = car + bike + bus + truck

        extra = create_features(
            car,
            bike,
            bus,
            truck,
            traffic
        )

        history = load_history()

        predictions = []

        for item in history:

            if isinstance(item, dict):

                predictions.append(
                    float(item["prediction"])
                )

            else:

                predictions.append(
                    float(item)
                )


        # -----------------------------
        # LAG FEATURES
        # -----------------------------

        if len(predictions) == 0:

            lag1 = total
            lag2 = total
            lag3 = total
            lag6 = total
            lag12 = total

        else:

            lag1 = predictions[-1]

            lag2 = (
                predictions[-2]
                if len(predictions) >= 2
                else lag1
            )

            lag3 = (
                predictions[-3]
                if len(predictions) >= 3
                else lag2
            )

            lag6 = (
                predictions[-6]
                if len(predictions) >= 6
                else lag3
            )

            lag12 = (
                predictions[-12]
                if len(predictions) >= 12
                else lag6
            )


        # -----------------------------
        # ROLLING FEATURES
        # -----------------------------

        last3 = (
            predictions[-3:]
            if len(predictions) >= 3
            else [total]
        )

        last6 = (
            predictions[-6:]
            if len(predictions) >= 6
            else [total]
        )

        rolling_mean_3 = np.mean(last3)
        rolling_mean_6 = np.mean(last6)

        rolling_std_3 = np.std(last3)

        rolling_max_6 = np.max(last6)
        rolling_min_6 = np.min(last6)


        # -----------------------------
        # EMA FEATURE
        # -----------------------------

        if len(predictions) == 0:

            ema = total

        else:

            alpha = 2 / (6 + 1)

            ema = predictions[0]

            for value in predictions[1:]:

                ema = (
                    alpha * value
                    + (1 - alpha) * ema
                )

            ema = (
                alpha * total
                + (1 - alpha) * ema
            )


        # -----------------------------
        # CREATE MODEL ROW
        # -----------------------------

        row = {}


        for col in feature_columns:

            if col == "Day of the week":

                row[col] = label_encoders[
                    "Day of the week"
                ].transform([day_name])[0]


            elif col == "Traffic Situation":

                row[col] = label_encoders[
                    "Traffic Situation"
                ].transform([traffic])[0]


            elif col == "CarCount":

                row[col] = car


            elif col == "BikeCount":

                row[col] = bike


            elif col == "BusCount":

                row[col] = bus


            elif col == "TruckCount":

                row[col] = truck


            elif col == "lag_1":

                row[col] = lag1


            elif col == "lag_2":

                row[col] = lag2


            elif col == "lag_3":

                row[col] = lag3


            elif col == "lag_6":

                row[col] = lag6


            elif col == "lag_12":

                row[col] = lag12


            elif col == "rolling_mean_3":

                row[col] = rolling_mean_3


            elif col == "rolling_mean_6":

                row[col] = rolling_mean_6


            elif col == "rolling_std_3":

                row[col] = rolling_std_3


            elif col == "rolling_max_6":

                row[col] = rolling_max_6


            elif col == "rolling_min_6":

                row[col] = rolling_min_6


            elif col == "ema":

                row[col] = ema


            elif col in extra:

                row[col] = extra[col]


            else:

                print(
                    "⚠️ Unknown feature:",
                    col
                )

                row[col] = 0


        # -----------------------------
        # DATAFRAME
        # -----------------------------

        X = pd.DataFrame(
            [row],
            columns=feature_columns
        )


        # -----------------------------
        # PREDICTION
        # -----------------------------

        prediction = model.predict(X)[0]

        prediction = float(prediction)


        # -----------------------------
        # CONGESTION
        # -----------------------------

        if prediction < 30:

            congestion = "Low"
            signal = 30

        elif prediction < 60:

            congestion = "Medium"
            signal = 60

        else:

            congestion = "High"
            signal = 90


        # -----------------------------
        # TIME
        # -----------------------------

        current_time = datetime.now().strftime(
            "%d %b %Y, %I:%M:%S %p"
        )


        # -----------------------------
        # SAVE HISTORY
        # -----------------------------

        history = load_history()

        new_record = {

            "prediction": round(
                prediction,
                2
            ),

            "vehicles": total,

            "cars": car,

            "bikes": bike,

            "buses": bus,

            "trucks": truck,

            "congestion": congestion,

            "signal": signal,

            "day": day_name,

            "traffic": traffic,

            "time": current_time

        }

        history.append(new_record)

        save_history(history)


        print("")
        print("🚦 NEW PREDICTION")
        print("Vehicles:", total)
        print("Prediction:", round(prediction, 2))
        print("Congestion:", congestion)
        print("Signal:", signal)
        print("")


        return jsonify({

            "Predicted Traffic":
                round(prediction, 2),

            "Congestion":
                congestion,

            "Signal Time":
                signal,

            "Current Vehicles":
                total,

            "Time":
                current_time

        })


    except Exception as e:

        print("")
        print("❌ ERROR:", str(e))
        print("")

        return jsonify({

            "error": str(e)

        }), 500


@app.route("/history", methods=["GET"])
def get_history():

    history = load_history()

    predictions = []

    for item in history:

        if isinstance(item, dict):

            predictions.append(
                float(item["prediction"])
            )


    if predictions:

        average = round(
            sum(predictions) /
            len(predictions),
            2
        )

        highest = round(
            max(predictions),
            2
        )

    else:

        average = 0
        highest = 0


    return jsonify({

        "history": history,

        "average": average,

        "highest": highest,

        "count": len(history)

    })


@app.route("/clear-history", methods=["POST"])
def clear_history():

    save_history([])

    return jsonify({

        "message":
            "History cleared successfully"

    })


if __name__ == "__main__":

    print("")
    print("🚦 KANNI-03 SERVER STARTING...")
    print("")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )