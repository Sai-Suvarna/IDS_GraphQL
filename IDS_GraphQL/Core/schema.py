from .models import IDSProductDetails
from graphene_django.types import DjangoObjectType
import graphene
from graphql import GraphQLError 


class IDSProductDetailsType(DjangoObjectType):
    class Meta:
        model = IDSProductDetails

class Query(graphene.ObjectType):
    all_products = graphene.List(IDSProductDetailsType)
    product = graphene.Field(IDSProductDetailsType, id=graphene.String())

    def resolve_all_products(self, info, **kwargs):
        return IDSProductDetails.objects.all()

    def resolve_product(self, info, id):
        return IDSProductDetails.objects.get(productId=id)


class CreateProduct(graphene.Mutation):
    product = graphene.Field(IDSProductDetailsType)

    class Arguments:
        productId = graphene.String(required=True)
        category = graphene.String(required=True)
        item = graphene.String(required=True)
        description = graphene.String()
        units = graphene.String(required=True)
        thresholdValue = graphene.Int(required=True)
        images = graphene.List(graphene.String)

    def mutate(self, info, productId, category, item, units, thresholdValue, description=None, images=None):
        product = IDSProductDetails(
            productId=productId,
            category=category,
            item=item,
            description=description,
            units=units,
            thresholdValue=thresholdValue,
            images=images
        )
        product.save()
        return CreateProduct(product=product)
class UpdateProduct(graphene.Mutation):
    product = graphene.Field(IDSProductDetailsType)

    class Arguments:
        id = graphene.String(required=True)
        category = graphene.String()
        item = graphene.String()
        description = graphene.String()
        units = graphene.Int()
        thresholdValue = graphene.Int()
        images = graphene.List(graphene.String)

    def mutate(self, info, id, category=None, item=None, description=None, units=None, thresholdValue=None, images=None):
        product = IDSProductDetails.objects.get(pk=id)

        if category:
            product.category = category
        if item:
            product.item = item
        if description:
            product.description = description
        if units:
            product.units = units
        if thresholdValue:
            product.thresholdValue = thresholdValue
        if images is not None:
            product.images = images

        product.save()
        return UpdateProduct(product=product)

class DeleteProduct(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.String(required=True)

    def mutate(self, info, id):
        product = IDSProductDetails.objects.get(pk=id)
        product.delete()
        return DeleteProduct(ok=True)

class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()

productdetails_schema = graphene.Schema(query=Query, mutation=Mutation)

