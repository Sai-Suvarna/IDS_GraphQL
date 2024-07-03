import json
import graphene
from graphene_django import DjangoObjectType
from .models import Product, Inventory, Warehouse, Location, Category
from graphql_jwt.decorators import login_required


class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class InventoryType(DjangoObjectType):
    class Meta:
        model = Inventory

class WarehouseType(DjangoObjectType):
    class Meta:
        model = Warehouse

class LocationType(DjangoObjectType):
    class Meta:
        model = Location

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category

class CreateCategory(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        image = graphene.String()  # Assuming you are storing image as a base64 encoded string
        rowstatus = graphene.Boolean(default_value=True)

    category = graphene.Field(CategoryType)
    
    @login_required
    def mutate(self, info, name, image=None, rowstatus=True):
        category = Category(name=name, image=image, rowstatus=rowstatus)
        category.save()
        return CreateCategory(category=category)


class UpdateCategory(graphene.Mutation):
    class Arguments:
        category_id = graphene.ID(required=True)
        name = graphene.String()
        image = graphene.String()
        rowstatus = graphene.Boolean()

    category = graphene.Field(CategoryType)
    
    @login_required
    def mutate(self, info, category_id, name=None, image=None, rowstatus=None):
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            raise Exception(f"Category with id {category_id} does not exist.")

        if name is not None:
            category.name = name
        if image is not None:
            category.image = image
        if rowstatus is not None:
            category.rowstatus = rowstatus

        category.save()
        return UpdateCategory(category=category)


class DeleteCategory(graphene.Mutation):
    class Arguments:
        category_id = graphene.ID(required=True)

    category_id = graphene.ID()
   
    @login_required
    def mutate(self, info, category_id):
        try:
            category = Category.objects.get(pk=category_id)
            category.rowstatus = False  # Soft delete by setting rowstatus to False
            category.save()
            return DeleteCategory(category_id=category_id)
        except Category.DoesNotExist:
            raise Exception(f"Category with id {category_id} does not exist.")


class InventoryInputType(graphene.InputObjectType):
    warehouseid = graphene.Int(required=True)
    minstocklevel = graphene.String(required=True)
    maxstocklevel = graphene.String(required=True)
    quantityavailable = graphene.String(required=True)

class CreateProduct(graphene.Mutation):
    class Arguments:
        productcode = graphene.String(required=True)
        qrcode = graphene.String(required=True)
        productname = graphene.String(required=True)
        productdescription = graphene.String(required=True)
        productcategory = graphene.String(required=True)
        reorderpoint = graphene.Int(required=True)
        brand = graphene.String(required=True)
        weight = graphene.String(required=True)
        dimensions = graphene.String(required=True)
        images = graphene.List(graphene.String, required=True)
        createduser = graphene.String(required=True)
        modifieduser = graphene.String(required=True)
        inventory_details = graphene.List(InventoryInputType, required=True)

    status_code = graphene.Int()
    message = graphene.String()

    @login_required

    def mutate(self, info, productcode, qrcode, productname, productdescription, productcategory, reorderpoint, brand, weight, dimensions, images, createduser, modifieduser, inventory_details):
        try:
            # Convert the images list to a JSON string
            images_json = json.dumps(images)

            # Check if productcategory is an integer
            try:
                productcategory_id = int(productcategory)
            except ValueError:
                # If productcategory cannot be converted to an integer, treat it as a string
                category, created = Category.objects.get_or_create(name=productcategory)
                productcategory_id = category.category_id

            # Create the Product instance
            product = Product(
                productcode=productcode,
                qrcode=qrcode,
                productname=productname,
                productdescription=productdescription,
                productcategory=productcategory_id,
                reorderpoint=reorderpoint,
                brand=brand,
                weight=weight,
                dimensions=dimensions,
                images=images_json,
                createduser=createduser,
                modifieduser=modifieduser
            )
            product.save()

            # Create Inventory instances
            for inventory_detail in inventory_details:
                warehouse = Warehouse.objects.get(pk=inventory_detail['warehouseid'])
                inventory = Inventory(
                    productid=product,
                    quantityavailable=inventory_detail['quantityavailable'],
                    minstocklevel=inventory_detail['minstocklevel'],
                    maxstocklevel=inventory_detail['maxstocklevel'],
                    reorderpoint=reorderpoint,
                    warehouseid=warehouse,
                    createduser=createduser,
                    modifieduser=modifieduser
                )
                inventory.save()

            return CreateProduct(status_code=200, message="Product and inventories created successfully.")
        except Exception as e:
            return CreateProduct(status_code=400, message=str(e))



class CreateWarehouse(graphene.Mutation):
    class Arguments:
        locationid = graphene.ID(required=True)
        warehousename = graphene.String(required=True)
        createduser = graphene.String(required=True)
        modifieduser = graphene.String(required=True)

    warehouse = graphene.Field(WarehouseType)

    @login_required

    def mutate(self, info, locationid, **kwargs):
        location = Location.objects.get(pk=locationid)
        warehouse = Warehouse.objects.create(locationid=location, **kwargs)
        return CreateWarehouse(warehouse=warehouse)

class CreateLocation(graphene.Mutation):
    class Arguments:
        locationname = graphene.String(required=True)
        locationaddress = graphene.String(required=True)
        createduser = graphene.String(required=True)
        modifieduser = graphene.String(required=True)

    location = graphene.Field(LocationType)

    @login_required

    def mutate(self, info, **kwargs):
        location = Location.objects.create(**kwargs)
        return CreateLocation(location=location)

    
class InventoryDetailType(graphene.ObjectType):
    warehouseid = graphene.Int()
    minstocklevel = graphene.String()
    maxstocklevel = graphene.String()
    quantityavailable = graphene.String()

class ProductResponseType(graphene.ObjectType):
    productid = graphene.Int()

    productcode = graphene.String()
    qrcode = graphene.String()
    productname = graphene.String()
    productdescription = graphene.String()
    productcategory = graphene.String()
    reorderpoint = graphene.Int()
    brand = graphene.String()
    weight = graphene.String()
    dimensions = graphene.String()
    images = graphene.List(graphene.String)
    createduser = graphene.String()
    modifieduser = graphene.String()
    createdtime = graphene.DateTime()
    modifiedtime = graphene.DateTime()
    rowstatus = graphene.Boolean()
    inventoryDetails = graphene.List(InventoryDetailType)




class Query(graphene.ObjectType):
    product = graphene.Field(ProductType, id=graphene.Int(required=True))
    # all_products = graphene.List(ProductType)
    all_products = graphene.List(ProductResponseType)

    category = graphene.Field(CategoryType, id=graphene.Int(required=True))
    all_categories = graphene.List(CategoryType)
    inventory = graphene.Field(InventoryType, id=graphene.Int(required=True))
    all_inventories = graphene.List(InventoryType)
    inventory_by_product = graphene.List(InventoryType, productid=graphene.Int(required=True))
    product_response = graphene.Field(ProductResponseType, productid=graphene.Int())


    @login_required

    def resolve_all_products(self, info):
        products = Product.objects.all()
        product_responses = []

        for product in products:
            inventories = Inventory.objects.filter(productid=product)

            inventory_details = []
            for inventory in inventories:
                inventory_detail = {
                    'warehouseid': inventory.warehouseid.pk,
                    'minstocklevel': inventory.minstocklevel,
                    'maxstocklevel': inventory.maxstocklevel,
                    'quantityavailable': inventory.quantityavailable
                }
                inventory_details.append(inventory_detail)

            images_list = product.images
            if isinstance(images_list, str):
                images_list = json.loads(images_list)

            product_response = ProductResponseType(
                productid=product.pk,
                productcode=product.productcode,
                qrcode=product.qrcode,
                productname=product.productname,
                productdescription=product.productdescription,
                productcategory=str(product.productcategory),
                reorderpoint=product.reorderpoint,
                brand=product.brand,
                weight=product.weight,
                dimensions=product.dimensions,
                images=images_list,
                createduser=product.createduser,
                modifieduser=product.modifieduser,
                createdtime=product.createdtime,
                modifiedtime=product.modifiedtime,
                rowstatus=product.rowstatus,
                inventoryDetails=inventory_details
            )
            product_responses.append(product_response)

        return product_responses


    def resolve_product(self, info, id):
        return Product.objects.get(pk=id)

    # def resolve_all_products(self, info):
    #     return Product.objects.all()

    def resolve_category(self, info, id):
        return Category.objects.get(pk=id, rowstatus=True)

    def resolve_all_categories(self, info):
        return Category.objects.filter(rowstatus=True)
    
    def resolve_inventory(self, info, id):
        return Inventory.objects.get(pk=id)

    def resolve_all_inventories(self, info):
        return Inventory.objects.all()
    
    def resolve_inventory_by_product(self, info, productid):
        return Inventory.objects.filter(productid=productid)
   
    @login_required
    def resolve_product_response(self, info, productid=None):
        try:
            if productid is not None:
                product = Product.objects.get(pk=productid)
            
            else:
                raise Exception("Either productid or productcode must be provided")

            inventories = Inventory.objects.filter(productid=product)

            inventory_details = []
            for inventory in inventories:
                inventory_detail = {
                    'warehouseid': inventory.warehouseid.pk,
                    'minstocklevel': inventory.minstocklevel,
                    'maxstocklevel': inventory.maxstocklevel,
                    'quantityavailable': inventory.quantityavailable
                }
                inventory_details.append(inventory_detail)

            return ProductResponseType(
                productcode=product.productcode,
                qrcode=product.qrcode,
                productname=product.productname,
                productdescription=product.productdescription,
                productcategory=str(product.productcategory),
                reorderpoint=product.reorderpoint,
                brand=product.brand,
                weight=product.weight,
                dimensions=product.dimensions,
                images=json.loads(product.images),
                createduser=product.createduser,
                modifieduser=product.modifieduser,
                inventoryDetails=inventory_details
            )
        except Product.DoesNotExist:
            return None


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    create_warehouse = CreateWarehouse.Field()
    create_location = CreateLocation.Field()
    create_category = CreateCategory.Field()
    update_category = UpdateCategory.Field()
    delete_category = DeleteCategory.Field()

idscore_schema = graphene.Schema(query=Query, mutation=Mutation)
