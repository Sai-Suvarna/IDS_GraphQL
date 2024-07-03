from django.contrib import admin
from django.urls import path
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from Object_Detection.schema import wordsearch_schema, imageupload_schema
from graphene_file_upload.django import FileUploadGraphQLView
from Authentication.schema import login_schema
from Core.schema import productdetails_schema

from idscore.schema import idscore_schema



urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=login_schema))),
    path('productdetails/', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=productdetails_schema))),
    path('idsdetails/', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=idscore_schema))),

    path('searchword/', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=wordsearch_schema))),
    path('upload/', csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True, schema=imageupload_schema))),
    
]







