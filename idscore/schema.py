import json
import graphene
from graphene_django import DjangoObjectType
from .models import Product, Inventory, Warehouse, Location, Category, Batch
# from .types import ProductType, InventoryType, WarehouseType,LocationType, CategoryType, BatchType
from graphql_jwt.decorators import login_required



class ProductType(DjangoObjectType):

    class Meta:
        model = Product

class InventoryType(DjangoObjectType):
    class Meta:
        model = Inventory


class LocationType(DjangoObjectType):
    class Meta:
        model = Location

class WarehouseType(DjangoObjectType):
    class Meta:
        model = Warehouse

    location = graphene.Field(LocationType)

    def resolve_location(self, info):
        return self.locationid



class CategoryType(DjangoObjectType):
    class Meta:
        model = Category

class BatchType(DjangoObjectType):
    class Meta:
        model = Batch





class CreateCategory(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        image = graphene.String()  
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



class UpdateProduct(graphene.Mutation):
    class Arguments:
        product_id = graphene.ID(required=True)
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
        inventory_details = graphene.List(InventoryInputType)

    status_code = graphene.Int()
    message = graphene.String()

    @login_required
    def mutate(self, info, product_id, productcode=None, qrcode=None, productname=None, productdescription=None, productcategory=None, reorderpoint=None, brand=None, weight=None, dimensions=None, images=None, createduser=None, modifieduser=None, inventory_details=None):
        try:
            # Fetch the existing Product instance
            product = Product.objects.get(pk=product_id)

            # Update the product fields if provided
            if productcode:
                product.productcode = productcode
            if qrcode:
                product.qrcode = qrcode
            if productname:
                product.productname = productname
            if productdescription:
                product.productdescription = productdescription
            if productcategory:
                try:
                    productcategory_id = int(productcategory)
                except ValueError:
                    category, created = Category.objects.get_or_create(name=productcategory)
                    productcategory_id = category.category_id
                product.productcategory = productcategory_id
            if reorderpoint is not None:
                product.reorderpoint = reorderpoint
            if brand:
                product.brand = brand
            if weight:
                product.weight = weight
            if dimensions:
                product.dimensions = dimensions
            if images:
                product.images = json.dumps(images)
            if createduser:
                product.createduser = createduser
            if modifieduser:
                product.modifieduser = modifieduser

            product.save()

            # Update Inventory instances
            if inventory_details:
                for inventory_detail in inventory_details:
                    warehouse = Warehouse.objects.get(pk=inventory_detail['warehouseid'])
                    inventory, created = Inventory.objects.update_or_create(
                        productid=product,
                        warehouseid=warehouse,
                        defaults={
                            'quantityavailable': inventory_detail['quantityavailable'],
                            'minstocklevel': inventory_detail['minstocklevel'],
                            'maxstocklevel': inventory_detail['maxstocklevel'],
                            'reorderpoint': reorderpoint if reorderpoint is not None else product.reorderpoint,
                            'createduser': createduser if createduser else product.createduser,
                            'modifieduser': modifieduser if modifieduser else product.modifieduser
                        }
                    )

            return UpdateProduct(status_code=200, message="Product and inventories updated successfully.")
        except Product.DoesNotExist:
            return UpdateProduct(status_code=404, message="Product not found.")
        except Exception as e:
            return UpdateProduct(status_code=400, message=str(e))



class DeleteProduct(graphene.Mutation):
    class Arguments:
        product_id = graphene.ID(required=True)

    product_id = graphene.ID()

    @login_required
    def mutate(self, info, product_id):
        try:
            product = Product.objects.get(pk=product_id)
            product.rowstatus = False  # Soft delete by setting rowstatus to False
            product.save()

            # Update corresponding inventory rows
            inventories = Inventory.objects.filter(productid=product)
            for inventory in inventories:
                inventory.rowstatus = False
                inventory.save()

            return DeleteProduct(product_id=product_id)
        except Product.DoesNotExist:
            raise Exception(f"Product with id {product_id} does not exist.")


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


class CreateBatch(graphene.Mutation):
    class Arguments:
        productid = graphene.Int(required=True)
        manufacturedate = graphene.Date(required=True)
        expirydate = graphene.Date(required=True)
        quantity = graphene.String(required=True)
        createduser = graphene.String(required=True)
        modifieduser = graphene.String(required=True)

    batch = graphene.Field(BatchType)

    def mutate(self, info, productid, manufacturedate, expirydate, quantity, createduser, modifieduser):
        product = Product.objects.get(pk=productid)
        batch = Batch(
            productid=product,
            manufacturedate=manufacturedate,
            expirydate=expirydate,
            quantity=quantity,
            createduser=createduser,
            modifieduser=modifieduser
        )
        batch.save()
        return CreateBatch(batch=batch)

class UpdateBatch(graphene.Mutation):
    class Arguments:
        batchid = graphene.Int(required=True)
        manufacturedate = graphene.Date()
        expirydate = graphene.Date()
        quantity = graphene.String()
        modifieduser = graphene.String()

    batch = graphene.Field(BatchType)

    def mutate(self, info, batchid, manufacturedate=None, expirydate=None, quantity=None, modifieduser=None):
        batch = Batch.objects.get(pk=batchid)
        if manufacturedate:
            batch.manufacturedate = manufacturedate
        if expirydate:
            batch.expirydate = expirydate
        if quantity:
            batch.quantity = quantity
        if modifieduser:
            batch.modifieduser = modifieduser
        batch.save()
        return UpdateBatch(batch=batch)


class DeleteBatch(graphene.Mutation):
    class Arguments:
        batchid = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, batchid):
        try:
            batch = Batch.objects.get(pk=batchid)
            batch.rowstatus = False  # Soft delete
            batch.save()
            success = True
        except Batch.DoesNotExist:
            success = False
        return DeleteBatch(success=success)


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
    category_name = graphene.String()
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


    all_warehouses = graphene.List(WarehouseType)
    all_locations = graphene.List(LocationType)
    warehouse = graphene.Field(WarehouseType, id=graphene.ID(required=True))
    location = graphene.Field(LocationType, id=graphene.ID(required=True))

    @login_required                       
    def resolve_all_warehouses(self, info, **kwargs):
        return Warehouse.objects.all()

    @login_required                       
    def resolve_all_locations(self, info, **kwargs):
        return Location.objects.all()

    @login_required                       
    def resolve_warehouse(self, info, id, **kwargs):
        return Warehouse.objects.get(pk=id)

    @login_required                       
    def resolve_location(self, info, id, **kwargs):
        return Location.objects.get(pk=id)

    @login_required                       
    def resolve_all_products(self, info):
        products = Product.objects.filter(rowstatus=True)
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

            # Fetch category name using the category ID
            category = Category.objects.get(pk=product.productcategory)
            category_name = category.name


            product_response = ProductResponseType(
                productid=product.pk,
                productcode=product.productcode,
                qrcode=product.qrcode,
                productname=product.productname,
                productdescription=product.productdescription,
                productcategory=str(product.productcategory),
                category_name=category_name,

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

    @login_required                       
    def resolve_category(self, info, id):
        return Category.objects.get(pk=id, rowstatus=True)
    
    @login_required                       
    def resolve_all_categories(self, info):
        return Category.objects.filter(rowstatus=True)
    
    @login_required                       
    def resolve_inventory(self, info, id):
        return Inventory.objects.get(pk=id)
    
    @login_required                       
    def resolve_all_inventories(self, info):
        return Inventory.objects.all()
    
    @login_required                       
    def resolve_inventory_by_product(self, info, productid):
        return Inventory.objects.filter(productid=productid)
   
    @login_required
    def resolve_product_response(self, info, productid=None):
        try:
            if productid is not None:
                product = Product.objects.get(pk=productid,rowstatus=True)
            
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


            # Fetch category name using the category ID
            category = Category.objects.get(pk=product.productcategory)
            category_name = category.name


            return ProductResponseType(
                productcode=product.productcode,
                qrcode=product.qrcode,
                productname=product.productname,
                productdescription=product.productdescription,
                productcategory=str(product.productcategory),
                category_name=category_name,

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
    update_product = UpdateProduct.Field()
    create_product = CreateProduct.Field()
    delete_product = DeleteProduct.Field()

    create_warehouse = CreateWarehouse.Field()
    create_location = CreateLocation.Field()

    create_category = CreateCategory.Field()
    update_category = UpdateCategory.Field()
    delete_category = DeleteCategory.Field()

    create_batch = CreateBatch.Field()
    update_batch = UpdateBatch.Field()
    delete_batch = DeleteBatch.Field()

idscore_schema = graphene.Schema(query=Query, mutation=Mutation)
