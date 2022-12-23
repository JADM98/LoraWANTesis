from flask import Flask
from typing import Callable
from utility.functions import LambdaUtils

class RouteMethods:
    #static Variables
    GET = ["GET"]
    POST = ["POST"]
    PUT = ["PUT"]
    DELETE = ["DELETE"]

    @staticmethod
    def withMethods(get:bool=False, post:bool=False, put:bool=False, delete:bool=False) -> list[str]:
        methods = []
        if get: methods.append("GET")
        if post: methods.append("POST")
        if put: methods.append("PUT")
        if delete: methods.append("DELETE")
        if len(methods) == 0: raise RuntimeError("No methods were specified to be returned, must receive at least one")
        return methods

class Routes:

    @staticmethod
    def addRoute(app:Flask, url:str, function:Callable, methods:list[str] = RouteMethods.GET ):
        if LambdaUtils.isLambda(function):
            function = LambdaUtils.createNamedLambda(function)
        app.add_url_rule(rule=url, endpoint=function.__name__, methods=methods, view_func=function)
        # LambdaUtils.

    
        