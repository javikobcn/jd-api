from flask import Flask, request, jsonify
from myjdapi import Myjdapi

import os

app = Flask(__name__)

EMAIL = os.environ["MYJD_EMAIL"]
PASSWORD = os.environ["MYJD_PASSWORD"]
DEVICE_NAME = os.environ["MYJD_DEVICE"]

def get_device():
    jd = Myjdapi()

    jd.connect(EMAIL, PASSWORD)
    jd.update_devices()

    device = jd.get_device(
        device_name=DEVICE_NAME
    )

    return jd, device


@app.route("/add", methods=["POST"])
def add_link():
    data = request.get_json()

    if not data or "url" not in data:
        return jsonify({"error": "url requerida"}), 400

    url = data["url"]
    package_name = data.get("packageName", "Telegram")

    try:
        jd, device = get_device()

        #     IMPORTANTE: refrescar linkgrabber desde device fresco
        lg = device.linkgrabber

        lg.add_links([
            {
                "links": url,
                "autostart": True,
                "packageName": package_name
            }
        ])

        return jsonify({
            "success": True,
            "url": url
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
        
@app.route("/pause", methods=["POST"])
def pause():

    jd, device = get_device()

    device.downloadcontroller.pause_downloads(True)

    return jsonify({
        "success": True
    })
    
    
@app.route("/resume", methods=["POST"])
def resume():

    jd, device = get_device()

    device.downloadcontroller.pause_downloads(False)

    return jsonify({
        "success": True
    })
    
    
@app.route("/status", methods=["GET"])
def status():

    try:

        jd, device = get_device()

        packages = device.downloads.query_packages()

        return jsonify({
            "success": True,
            "packages": packages
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500        


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)