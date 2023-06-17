from typing import Type

import pydantic
from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from auth import hash_password
from models import Ad, Session, User
from schema import CreateAd, CreateUser, UpdateAd, UpdateUser

app = Flask("app")


class HttpError(Exception):
    def __init__(self, status_code: int, message: str | dict | list):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HttpError)
def error_handler(er: HttpError):
    response = jsonify({"status": "error", "message": er.message})
    response.status_code = er.status_code
    return response


def get_user(session: Session, user_id: int):
    user = session.get(User, user_id)
    if user is None:
        raise HttpError(404, "user not found")
    return user


def get_ad(session: Session, ad_id: int):
    ad = session.get(Ad, ad_id)
    if ad is None:
        raise HttpError(404, "ad not found")
    return ad


def validate(
    validation_schema: Type[CreateUser]
    | Type[UpdateUser]
    | Type[CreateAd]
    | Type[UpdateAd],
    json_data,
):
    try:
        pydantic_obj = validation_schema(**json_data)
        return pydantic_obj.dict(exclude_none=True)
    except pydantic.ValidationError as er:
        raise HttpError(400, er.errors())


class UserViews(MethodView):
    def get(self, user_id: int):
        with Session() as session:
            user = get_user(session, user_id)
            return jsonify(
                {
                    "id": user.id,
                    "name": user.name,
                    "creation_time": user.creation_time.isoformat(),
                }
            )

    def post(self):
        validated_data = validate(CreateUser, request.json)
        validated_data["password"] = hash_password(validated_data["password"])
        with Session() as session:
            new_user = User(**validated_data)
            session.add(new_user)
            try:
                session.commit()
            except IntegrityError as er:
                raise HttpError(409, "user already exist")
            return jsonify({"id": new_user.id})

    def patch(self, user_id):
        validated_data = validate(UpdateUser, request.json)
        if "password" in validated_data:
            validated_data["password"] = hash_password(validated_data["password"])
        with Session() as session:
            user = get_user(session, user_id)
            for field, value in validated_data.items():
                setattr(user, field, value)
            session.add(user)
            try:
                session.commit()
            except IntegrityError as er:
                raise HttpError(409, "user already exist")
            return jsonify({"id": user.id})

    def delete(self, user_id: int):
        with Session() as session:
            user = get_user(session, user_id)
            session.delete(user)
            session.commit()
            return jsonify({"status": "deleted"})


user_view = UserViews.as_view("users")


app.add_url_rule(
    "/user/<int:user_id>", view_func=user_view, methods=["GET", "DELETE", "PATCH"]
)
app.add_url_rule("/user", view_func=user_view, methods=["POST"])


class AdViews(MethodView):
    def get(self, ad_id: int):
        with Session() as session:
            ad = get_ad(session, ad_id)
            return jsonify(
                {
                    "id": ad.id,
                    "title": ad.title,
                    "description": ad.description,
                    "creation_time": ad.creation_time.isoformat(),
                    "user_id": ad.user_id,
                }
            )

    def post(self):
        validated_data = validate(CreateAd, request.json)
        with Session() as session:
            new_ad = Ad(**validated_data)
            session.add(new_ad)
            try:
                session.commit()
            except IntegrityError as er:
                raise HttpError(409, "ad already exist")
            return jsonify({"id": new_ad.id})

    def patch(self, ad_id):
        validated_data = validate(UpdateAd, request.json)
        with Session() as session:
            ad = get_ad(session, ad_id)
            for field, value in validated_data.items():
                setattr(ad, field, value)
            session.add(ad)
            try:
                session.commit()
            except IntegrityError as er:
                raise HttpError(409, "ad already exist")
            return jsonify({"id": ad.id})

    def delete(self, ad_id):
        with Session() as session:
            ad = get_ad(session, ad_id)
            session.delete(ad)
            session.commit()
            return jsonify({"status": "deleted"})


ad_view = AdViews.as_view("ads")


app.add_url_rule(
    "/ad/<int:ad_id>", view_func=ad_view, methods=["GET", "DELETE", "PATCH"]
)
app.add_url_rule("/ad", view_func=ad_view, methods=["POST"])


if __name__ == "__main__":
    app.run()
