import graphene
from graphene_django import DjangoObjectType
from Core.models import IDSProductDetails  
from graphql import GraphQLError 

######## ---------  GraphQL API for retrieving details based on word search   ----------  ##########

class ProductDetailsType(DjangoObjectType):
    class Meta:
        model = IDSProductDetails

class Query(graphene.ObjectType):
    matching_products = graphene.List(ProductDetailsType, search_word=graphene.String())

    def resolve_matching_products(self, info, search_word):
        # Fetch matching items from the database
        products = IDSProductDetails.objects.filter(item__icontains=search_word)
        return products

wordsearch_schema = graphene.Schema(query=Query)


######## ---------  GraphQL API for retrieving details based on word deteted from the image   ----------  ##########

import google.generativeai as genai
import os
from PIL import Image
import graphene
from graphene_file_upload.scalars import Upload
from graphene_django.types import DjangoObjectType
from django.conf import settings
from .models import Image as ImageModel
from Core.models import IDSProductDetails
from django.db.models import Q

# Configure the Google API key
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY environment variable not set")
genai.configure(api_key=api_key)

class ImageType(DjangoObjectType):
    class Meta:
        model = ImageModel

class IDSProductDetailsType(DjangoObjectType):
    class Meta:
        model = IDSProductDetails

class UploadAndProcessImage(graphene.Mutation):
    class Arguments:
        file = Upload(required=True)

    objects = graphene.List(graphene.String)
    matched_items = graphene.List(IDSProductDetailsType)

    def mutate(self, info, file):
        try:
            # Save the uploaded image
            image_instance = ImageModel(image=file)
            image_instance.save()

            # Process the image
            image_path = os.path.join(settings.MEDIA_ROOT, image_instance.image.name)
            img = Image.open(image_path)

            # Send the image to the generative AI model
            model = genai.GenerativeModel('gemini-1.5-flash')  # Adjust model initialization
            response = model.generate_content([
                """Identify only some important things that are in the image.
                If any machinery parts, hardware tools, or components are detected, 
                provide their specific names of each object without any stopwords.
                The response should only consist of names of all the objects 
                in a single word for each one without any stopwords in the object names separated by commas in the image""",
                img
            ], stream=True)

            response.resolve()

            # Process the response
            res = response.text.split(',')
            objects = [word.strip() for word in res if word.strip()]
            print(objects)

            if not objects:
                raise Exception("No objects detected in the image")

            # Query database for matching items
            matched_items = []
            for obj in objects:
                # Example: Match if 'item' contains the object name (case insensitive)
                matched_query = IDSProductDetails.objects.filter(item__icontains=obj)
                if matched_query.exists():
                    matched_items.extend(matched_query)

            return UploadAndProcessImage(objects=objects, matched_items=matched_items)
        
        except Exception as e:
            # Log the exception for debugging purposes
            logger.error(f"Error processing image: {str(e)}")
            # Return a GraphQL error response
            return UploadAndProcessImage(objects=[], matched_items=[])


class Mutation(graphene.ObjectType):
    upload_and_process_image = UploadAndProcessImage.Field()

class Query(graphene.ObjectType):
    images = graphene.List(ImageType)

    def resolve_images(self, info):
        return ImageModel.objects.all()

imageupload_schema = graphene.Schema(query=Query, mutation=Mutation)
