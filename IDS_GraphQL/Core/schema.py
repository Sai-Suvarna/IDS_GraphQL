import graphene
from graphene_django.types import DjangoObjectType
from .models import IDSProductDetails
from graphql_jwt.decorators import login_required
from graphql import GraphQLError

class IDSProductDetailsType(DjangoObjectType):
    class Meta:
        model = IDSProductDetails

class Query(graphene.ObjectType):
    all_products = graphene.List(IDSProductDetailsType)
    product = graphene.Field(IDSProductDetailsType, id=graphene.String())

    @login_required
    def resolve_all_products(self, info, **kwargs):
        return IDSProductDetails.objects.all()

    @login_required
    def resolve_product(self, info, id):
        try:
            return IDSProductDetails.objects.get(productId=id)
        except IDSProductDetails.DoesNotExist:
            raise GraphQLError('Product not found.')

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

    @login_required
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

    @login_required
    def mutate(self, info, id, category=None, item=None, description=None, units=None, thresholdValue=None, images=None):
        try:
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
        except IDSProductDetails.DoesNotExist:
            raise GraphQLError('Product not found.')

class DeleteProduct(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.String(required=True)

    @login_required
    def mutate(self, info, id):
        try:
            product = IDSProductDetails.objects.get(pk=id)
            product.delete()
            return DeleteProduct(ok=True)
        except IDSProductDetails.DoesNotExist:
            raise GraphQLError('Product not found.')

class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()

productdetails_schema = graphene.Schema(query=Query, mutation=Mutation)