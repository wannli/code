from datetime import datetime

# from flask import Flask, jsonify, request
from fastapi import FastAPI
from starlette.requests import Request
from allocation.domain import commands
from allocation.service_layer.handlers import InvalidSku
from allocation import bootstrap, views

# app = Flask(__name__)
app = FastAPI()
bus = bootstrap.bootstrap()


# @app.route("/add_batch", methods=["POST"])
@app.post("/add_batch")
def add_batch(request: Request):
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    cmd = commands.CreateBatch(
        request.json["ref"], request.json["sku"], request.json["qty"], eta
    )
    bus.handle(cmd)
    return "OK", 201


# @app.route("/allocate", methods=["POST"])
@app.post("/allocate")
def allocate_endpoint(request: Request):
    try:
        cmd = commands.Allocate(
            request.json["orderid"], request.json["sku"], request.json["qty"]
        )
        bus.handle(cmd)
    except InvalidSku as e:
        return {"message": str(e)}, 400

    return "OK", 202


# @app.route("/allocations/<orderid>", methods=["GET"])
@app.get("/allocations/{orderid}")
def allocations_view_endpoint(orderid: int, request: Request):
    result = views.allocations(orderid, bus.uow)
    if not result:
        return "not found", 404
    return jsonify(result), 200
