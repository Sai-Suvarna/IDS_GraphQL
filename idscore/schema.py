import json
import graphene
from graphene_django import DjangoObjectType
from .models import Product, Inventory, Warehouse, Batch, Location, Category, Placement, DeleteRequest, RequestProduct, Features
from graphql_jwt.decorators import login_required
import jwt

# Define GraphQL Types for Django Models

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
    
class InventoryType(DjangoObjectType):
    invreOrderPoint = graphene.Int()  # Make it nullable
    warehouseName = graphene.String()
    warehouseId = graphene.Int()   

    class Meta:
        model = Inventory
    
    def resolve_warehouseid(self, info):
        return self.warehouseId.pk  # Return the primary key of the warehouse
    
    def resolve_warehousename(self, info):
        # Resolve warehousename from the related Warehouse object
        return self.warehouseId.warehouseName if self.warehouseId else None


class LocationType(DjangoObjectType):
    class Meta:
        model = Location

class WarehouseType(DjangoObjectType):
    class Meta:
        model = Warehouse

    # Resolve the relationship with Location
    location = graphene.Field(LocationType)

    def resolve_location(self, info):
        return self.locationId

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category

class BatchType(DjangoObjectType):
    class Meta:
        model = Batch


class PlacementType(DjangoObjectType):
    productId = graphene.Field(ProductType)
    warehouseId = graphene.Field(WarehouseType)

    warehouseName = graphene.String()

    class Meta:
        model = Placement
        fields = ('placementId', 'productId', 'warehouseId', 'placementQuantity', 'aile', 'bin', 'createdUser', 'modifiedUser', 'createdTime', 'modifiedTime')


    def resolve_warehousename(self, info):
        # Resolve warehousename from the related Warehouse object
        return self.warehouseId.warehouseName if self.warehouseId else None


class DeleteRequestType(DjangoObjectType):
    class Meta:
        model = DeleteRequest


class RequestProductType(DjangoObjectType):
    class Meta:
        model = RequestProduct



class FeaturesType(DjangoObjectType):
    class Meta:
        model = Features



# Mutations for Creating, Updating, and Deleting Categories

class CreateCategory(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        image = graphene.String()  
        rowstatus = graphene.Boolean(default_value=True)

    category = graphene.Field(CategoryType)
    statusCode = graphene.Int()
    message = graphene.String()
    
    @login_required
    def mutate(self, info, name, image=None, rowstatus=True):
        try:
            category = Category(name=name, image=image, rowstatus=rowstatus)
            category.save()
            return CreateCategory(category=category, status_code=200, message="Category created successfully.")
        except Exception as e:
            return CreateCategory(statusCode=400, message=str(e))


class UpdateCategory(graphene.Mutation):
    class Arguments:
        categoryId = graphene.ID(required=True)
        name = graphene.String()
        image = graphene.String()
        rowstatus = graphene.Boolean()

    category = graphene.Field(CategoryType)
    statusCode = graphene.Int()
    message = graphene.String()
    
    @login_required
    def mutate(self, info, categoryId, name=None, image=None, rowstatus=None):
        try:
            # Retrieve the existing Category object
            category = Category.objects.get(pk=categoryId)
        except Category.DoesNotExist:
            raise Exception(f"Category with id {categoryId} does not exist.")

        try:
            # Update the Category fields if provided
            if name is not None:
                category.name = name
            if image is not None:
                category.image = image
            if rowstatus is not None:
                category.rowstatus = rowstatus

            category.save()
            return UpdateCategory(category=category, status_code=200, message="Category updated successfully.")
        except Exception as e:
            return UpdateCategory(statusCode=400, message=str(e))


class DeleteCategory(graphene.Mutation):
    class Arguments:
        categoryId = graphene.ID(required=True)

    categoryId = graphene.ID()
    statusCode = graphene.Int()
    message = graphene.String()
   
    @login_required
    def mutate(self, info, categoryId):
        try:
            # Soft delete the Category by setting rowstatus to False
            category = Category.objects.get(pk=categoryId)
            category.rowstatus = False  # Soft delete by setting rowstatus to False
            category.save()
            return DeleteCategory(category_id=categoryId, status_code=200, message="Category deleted successfully.")
        except Category.DoesNotExist:
            raise Exception(f"Category with id {categoryId} does not exist.")
        except Exception as e:
            return DeleteCategory(statusCode=400, message=str(e))


class CreateInventory(graphene.Mutation):
    inventories = graphene.List(InventoryType)
    statusCode = graphene.Int()
    message = graphene.String()

    class Arguments:
        productId = graphene.ID(required=True)
        quantityAvailable = graphene.String()
        minStockLevel = graphene.String(required=True)
        maxStockLevel = graphene.String(required=True)
        invreOrderPoint = graphene.Int()  # Optional argument
        warehouseId = graphene.ID(required=True)
        rowstatus = graphene.Boolean(default_value=True)

    @login_required
    def mutate(self, info, productId, warehouseId, **kwargs):
        try:
            product = Product.objects.get(pk=productId)
            warehouse = Warehouse.objects.get(pk=warehouseId)

            # Get the username from the token
            token = info.context.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            username = get_username_from_token(token)

            # Set default values or handle None
            invreOrderPoint = kwargs.get('invreorderpoint', None)

            # Use get_or_create to handle unique constraint
            inventory, created = Inventory.objects.get_or_create(
                productId=product,
                warehouseId=warehouse,
                defaults={
                    'quantityAvailable': kwargs['quantityAvailable'],
                    'minStockLevel': kwargs['minStockLevel'],
                    'maxStockLevel': kwargs['maxStockLevel'],
                    'invreOrderPoint': invreOrderPoint,
                    'createdUser': username,
                    'modifiedUser': username,
                    'rowstatus': kwargs['rowstatus']
                }
            )

            if not created:
                # If the inventory entry already exists, update it
                inventory.quantityAvailable = kwargs['quantityAvailable']
                inventory.minStockLevel = kwargs['minStockLevel']
                inventory.maxStockLevel = kwargs['maxStockLevel']
                inventory.invreOrderPoint = invreOrderPoint
                inventory.modifiedUser = username
                inventory.rowstatus = kwargs['rowstatus']
                inventory.save()

            # Fetch all inventories related to the product
            inventories = Inventory.objects.filter(productId=product)

            return CreateInventory(
                inventories=inventories,
                statusCode=200,
                message="Inventory entry created successfully."
            )
        except Product.DoesNotExist:
            return CreateInventory(
                statusCode=404,
                message="Product not found."
            )
        except Warehouse.DoesNotExist:
            return CreateInventory(
                statusCode=404,
                message="Warehouse not found."
            )
        except Exception as e:
            return CreateInventory(
                statusCode=400,
                message=str(e)
            )


class UpdateInventory(graphene.Mutation):
    inventories = graphene.List(InventoryType)
    statusCode = graphene.Int()
    message = graphene.String()

    class Arguments:
        inventoryId = graphene.ID(required=True)
        quantityAvailable = graphene.String(required=False)
        minStockLevel = graphene.String(required=False)
        maxStockLevel = graphene.String(required=False)
        invreOrderPoint = graphene.Int(required=False)  # Optional argument
        warehouseId = graphene.ID(required=False)
        rowstatus = graphene.Boolean()

    @login_required
    def mutate(self, info, inventoryId, **kwargs):
        try:
            inventory = Inventory.objects.get(pk=inventoryId)

            # Get the username from the token
            token = info.context.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            username = get_username_from_token(token)

            if 'quantityAvailable' in kwargs:
                inventory.quantityAvailable = kwargs['quantityAvailable']
            if 'minStockLevel' in kwargs:
                inventory.minStockLevel = kwargs['minStockLevel']
            if 'maxStockLevel' in kwargs:
                inventory.maxStockLevel = kwargs['maxStockLevel']
            if 'invreOrderPoint' in kwargs:
                inventory.invreOrderPoint = kwargs['invreOrderPoint']
            if 'warehouseId' in kwargs:
                warehouse = Warehouse.objects.get(pk=kwargs['warehouseId'])
                inventory.warehouseId = warehouse
            inventory.modifiedUser = username
            if 'rowstatus' in kwargs:
                inventory.rowstatus = kwargs['rowstatus']

            inventory.save()

            # Fetch all inventories related to the product
            inventories = Inventory.objects.filter(productId=inventory.productId)

            return UpdateInventory(
                inventories=inventories,
                statusCode=200,
                message="Inventory updated successfully."
            )
        except Inventory.DoesNotExist:
            return UpdateInventory(
                statusCode=404,
                message="Inventory not found."
            )
        except Warehouse.DoesNotExist:
            return UpdateInventory(
                statusCode=404,
                message="Warehouse not found."
            )
        except Exception as e:
            return UpdateInventory(
                statusCode=400,
                message=str(e)
            )



# Input Object Type for Inventory details
class InventoryInputType(graphene.InputObjectType):
    warehouseId = graphene.Int(required=True)
    minStockLevel = graphene.String(required=True)
    maxStockLevel = graphene.String(required=True)
    quantityAvailable = graphene.String(required=False)
    invreOrderPoint = graphene.Int()  

from IDS_GraphQL.utils import get_username_from_token


class CreateProduct(graphene.Mutation):
    class Arguments:
        productCode = graphene.String(required=True)
        qrCode = graphene.String()
        productName = graphene.String(required=True)
        productDescription = graphene.String(required=True)
        productCategory = graphene.String(required=True)
        reOrderPoint = graphene.Int()
        brand = graphene.String()
        weight = graphene.String()
        dimensions = graphene.String()
        images = graphene.List(graphene.String)
        inventory_details = graphene.List(InventoryInputType, required=True)

    statusCode = graphene.Int()
    message = graphene.String()

    @login_required
    def mutate(self, info, productCode, qrCode, productName, productDescription, productCategory, reOrderPoint, brand, weight, dimensions, images, inventory_details):
        try:
            # Get the username from the token
            token = info.context.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            username = get_username_from_token(token)

            # Convert the images list to a JSON string
            images_json = json.dumps(images)

            # Check if productcategory is an integer
            try:
                productCategory_id = int(productCategory)
            except ValueError:
                # If productcategory cannot be converted to an integer, treat it as a string
                category, created = Category.objects.get_or_create(name=productCategory)
                productCategory_id = category.categoryId

            # Create the Product instance
            product = Product(
                productCode=productCode,
                qrCode=qrCode,
                productName=productName,
                productDescription=productDescription,
                productCategory=productCategory_id,
                reOrderPoint=reOrderPoint,
                brand=brand,
                weight=weight,
                dimensions=dimensions,
                images=images_json,
                createdUser=username,
                modifiedUser=username
            )
            product.save()

            # Create Inventory instances related to the Product
            for inventory_detail in inventory_details:
                warehouse = Warehouse.objects.get(pk=inventory_detail['warehouseId'])
                quantityAvailable = inventory_detail.get('quantityAvailable', None)  # Default to None if not provided
                inventory, created = Inventory.objects.get_or_create(
                    productId=product,
                    warehouseId=warehouse,
                    defaults={
                        'quantityAvailable': quantityAvailable,
                        'minStockLevel': inventory_detail['minStockLevel'],
                        'maxStockLevel': inventory_detail['maxStockLevel'],
                        'invreOrderPoint': inventory_detail['invreOrderPoint'],
                        'createdUser': username,
                        'modifiedUser': username
                    }
                )
                if not created:
                    # If inventory entry already exists, update it
                    inventory.quantityAvailable = quantityAvailable
                    inventory.minStockLevel = inventory_detail['minStockLevel']
                    inventory.maxStockLevel = inventory_detail['maxStockLevel']
                    inventory.invreOrderPoint = inventory_detail['invreOrderPoint']
                    inventory.modifiedUser = username
                    inventory.save()

            return CreateProduct(statusCode=200, message="Product and inventories created successfully.")
        except Exception as e:
            return CreateProduct(statusCode=400, message=str(e))


class UpdateProduct(graphene.Mutation):
    class Arguments:
        productId = graphene.ID(required=True)
        productCode = graphene.String()
        qrCode = graphene.String()
        productName = graphene.String()
        productDescription = graphene.String()
        productCategory = graphene.String()
        reOrderPoint = graphene.Int()
        brand = graphene.String()
        weight = graphene.String()
        dimensions = graphene.String()
        images = graphene.List(graphene.String)
        inventory_details = graphene.List(InventoryInputType)

    statusCode = graphene.Int()
    message = graphene.String()

    @login_required
    def mutate(self, info, productId, productCode=None, qrCode=None, productName=None, productDescription=None, productCategory=None, reOrderPoint=None, brand=None, weight=None, dimensions=None, images=None, inventory_details=None):
        try:
            # Get the username from the token
            token = info.context.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            username = get_username_from_token(token)

            # Fetch the existing Product instance
            product = Product.objects.get(pk=productId)

            # Update the product fields if provided
            if productCode:
                product.productCode = productCode
            if qrCode:
                product.qrCode = qrCode
            if productName:
                product.productName = productName
            if productDescription:
                product.productDescription = productDescription
            if productCategory:
                try:
                    productCategory_id = int(productCategory)
                except ValueError:
                    category, created = Category.objects.get_or_create(name=productCategory)
                    productCategory_id = category.category_id
                product.productCategory = productCategory_id
            if reOrderPoint is not None:
                product.reOrderPoint = reOrderPoint
            if brand:
                product.brand = brand
            if weight:
                product.weight = weight
            if dimensions:
                product.dimensions = dimensions
            if images:
                product.images = json.dumps(images)

            product.modifiedUser = username
            product.save()

            # Update related Inventory instances
            if inventory_details:
                for inventory_detail in inventory_details:
                    warehouse = Warehouse.objects.get(pk=inventory_detail['warehouseId'])
                    inventory, created = Inventory.objects.update_or_create(
                        productId=product,
                        warehouseId=warehouse,
                        defaults={
                            'quantityAvailable': inventory_detail['quantityAvailable'],
                            'minStockLevel': inventory_detail['minStockLevel'],
                            'maxStockLevel': inventory_detail['maxStockLevel'],
                            'invreOrderPoint': inventory_detail['invreOrderPoint'],
                            'modifiedUser': username
                        }
                    )

            return UpdateProduct(statusCode=200, message="Product and inventories updated successfully.")
        except Product.DoesNotExist:
            return UpdateProduct(statusCode=404, message="Product not found.")
        except Exception as e:
            return UpdateProduct(statusCode=400, message=str(e))


# Mutation for Deleting a Product and its related Inventories

class DeleteProduct(graphene.Mutation):
    class Arguments:
        productId = graphene.ID(required=True)

    productId = graphene.ID()
    statusCode = graphene.Int()
    message = graphene.String()

    @login_required
    def mutate(self, info, productId):
        try:
            # Soft delete the Product by setting rowstatus to False
            product = Product.objects.get(pk=productId)
            product.rowstatus = False  
            product.save()

            # Soft delete related Inventory instances
            inventories = Inventory.objects.filter(productId=product)
            for inventory in inventories:
                inventory.rowstatus = False
                inventory.save()

            return DeleteProduct(productId=productId, statusCode=200, message="Product deleted successfully.")
        except Product.DoesNotExist:
            raise Exception(f"Product with id {productId} does not exist.")
        except Exception as e:
            return DeleteProduct(statusCode=400, message=str(e))


# Mutation for Creating Warehouses

class CreateWarehouse(graphene.Mutation):
    class Arguments:
        locationId = graphene.ID(required=True)
        warehouseName = graphene.String(required=True)

    warehouse = graphene.Field(WarehouseType)
    statusCode = graphene.Int()
    message = graphene.String()

    @login_required
    def mutate(self, info, locationId, warehouseName):
        try:
            location = Location.objects.get(pk=locationId)

            # Get the username from the token
            token = info.context.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            username = get_username_from_token(token)

            warehouse = Warehouse.objects.create(
                locationId=location,
                warehouseName=warehouseName,
                createdUser=username,
                modifiedUser=username
            )
            return CreateWarehouse(warehouse=warehouse, statusCode=200, message="Warehouse created successfully.")
        except Location.DoesNotExist:
            raise Exception(f"Location with id {locationId} does not exist.")
        except Exception as e:
            return CreateWarehouse(statusCode=400, message=str(e))

# # Mutation for Creating Locations

class CreateLocation(graphene.Mutation):
    class Arguments:
        locationName = graphene.String(required=True)
        locationAddress = graphene.String(required=True)

    location = graphene.Field(LocationType)
    statusCode = graphene.Int()
    message = graphene.String()

    @login_required
    def mutate(self, info, locationName, locationAddress):
        try:

            # Get the username from the token
            token = info.context.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            username = get_username_from_token(token)

            location = Location.objects.create(
                locationName=locationName,
                locationAddress=locationAddress,
                createdUser=username,
                modifiedUser=username
            )
            return CreateLocation(location=location, statusCode=200, message="Location created successfully.")
        except Exception as e:
            return CreateLocation(statusCode=400, message=str(e))
        

# Mutations for Creating, Updating, and Deleting Placements

from collections import defaultdict
from django.db import transaction

class PlacementInputType(graphene.InputObjectType):
    warehouseId = graphene.Int(required=True)
    placementQuantity = graphene.String(required=True)
    aile = graphene.String(required=True)
    bin = graphene.String(required=True)


from django.db import transaction
from django.db.models import Sum

class CreatePlacement(graphene.Mutation):
    placements = graphene.List(PlacementType)
    statusCode = graphene.Int()
    message = graphene.String()

    class Arguments:
        productId = graphene.Int(required=True)
        manufactureDate = graphene.Date(required=False)
        expiryDate = graphene.Date(required=False)
        quantity = graphene.String(required=True)
        placements = graphene.List(PlacementInputType, required=True)

    @classmethod
    @login_required
    @transaction.atomic
    def mutate(cls, root, info, productId, manufactureDate=None, expiryDate=None, quantity=None, placements=None):
        try:
            product = Product.objects.get(pk=productId)

            # Get the username from the token
            token = info.context.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            username = get_username_from_token(token)

            # Create a new Batch object
            batch = Batch.objects.create(
                productId=product,
                manufactureDate=manufactureDate,
                expiryDate=expiryDate,
                quantity=quantity,
                createdUser=username,
                modifiedUser=username
            )

            # Create Placement objects
            created_placements = cls.create_placements(batch, product, placements, username)

            # Update or create Inventory entries
            cls.update_inventory(product, placements, username)

            return cls(placements=created_placements, statusCode=200, message="Placement created successfully.")
        except Product.DoesNotExist:
            return cls(statusCode=404, message=f"Product with id {productId} does not exist.")
        except Warehouse.DoesNotExist:
            return cls(statusCode=404, message=f"One or more warehouses do not exist.")
        except Exception as e:
            return cls(statusCode=400, message=str(e))

    @classmethod
    def create_placements(cls, batch, product, placements, username):
        created_placements = []
        for placement_input in placements:
            warehouse = Warehouse.objects.get(pk=placement_input.warehouseId)
            placement = Placement.objects.create(
                batchId=batch,
                productId=product,
                warehouseId=warehouse,
                placementQuantity=placement_input.placementQuantity,
                aile=placement_input.aile,
                bin=placement_input.bin,
                createdUser=username,
                modifiedUser=username
            )
            created_placements.append(placement)
        return created_placements

    @classmethod
    def update_inventory(cls, product, placements, username):
        from collections import defaultdict

        # Calculate total quantities per warehouse
        warehouse_totals = defaultdict(int)
        for placement_input in placements:
            warehouse_totals[placement_input.warehouseId] += int(placement_input.placementQuantity)

        # Update or create Inventory entries
        for warehouseId, total_quantity in warehouse_totals.items():
            warehouse = Warehouse.objects.get(pk=warehouseId)

            # Calculate total quantity for the warehouse and product
            total_quantity = Placement.objects.filter(productId=product, warehouseId=warehouse).aggregate(total_quantity=Sum('placementQuantity'))['total_quantity']

            # Update or create the inventory entry
            inventory, created = Inventory.objects.update_or_create(
                productId=product,
                warehouseId=warehouse,
                defaults={
                    'quantityAvailable': str(total_quantity),
                    'createdUser': username,
                    'modifiedUser': username
                }
            )
            if not created:
                # Update existing Inventory entry
                inventory.quantityAvailable = str(total_quantity)
                inventory.modifiedUser = username
                inventory.save()

        return



class UpdatePlacement(graphene.Mutation):
    placements = graphene.List(PlacementType)
    statusCode = graphene.Int()
    message = graphene.String()

    class Arguments:
        placementId = graphene.Int(required=True)
        productId = graphene.Int()
        warehouseId = graphene.Int()
        aile = graphene.String()
        bin = graphene.String()
        # batchid = graphene.Int()

    @login_required
    def mutate(self, info, placementId, **kwargs):
        try:
            placement = Placement.objects.get(pk=placementId)

            # Get the username from the token
            token = info.context.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            username = get_username_from_token(token)

            productId = kwargs.get('productId')
            if productId:
                try:
                    product_instance = Product.objects.get(pk=productId)
                    placement.productId = product_instance
                except Product.DoesNotExist:
                    return UpdatePlacement(statusCode=404, message=f"Product with id {productId} does not exist.")

            warehouseId = kwargs.get('warehouseId')
            if warehouseId:
                try:
                    warehouse_instance = Warehouse.objects.get(pk=warehouseId)
                    placement.warehouseId = warehouse_instance
                except Warehouse.DoesNotExist:
                    return UpdatePlacement(statusCode=404, message=f"Warehouse with id {warehouseId} does not exist.")

        
            for key, value in kwargs.items():
                if key in ['aile', 'bin']:
                    setattr(placement, key, value)

            placement.modifiedUser = username
            placement.save()

            # Retrieve all placements related to the updated productid
            placements = Placement.objects.filter(productId=placement.productId)

            return UpdatePlacement(placements=placements, statusCode=200, message="Placement updated successfully.")
        except Placement.DoesNotExist:
            return UpdatePlacement(statusCode=404, message=f"Placement with id {placementId} does not exist.")
        except Exception as e:
            return UpdatePlacement(statusCode=400, message=str(e))


class DeletePlacement(graphene.Mutation):
    class Arguments:
        placementId = graphene.Int(required=True)

    statusCode = graphene.Int()
    message = graphene.String()

    @login_required
    def mutate(self, info, placementId):
        try:
            placement = Placement.objects.get(pk=placementId)
            placement.rowstatus = False  # Soft delete by setting rowstatus to False
            placement.save()

            return DeletePlacement(statusCode=200, message="Placement deleted successfully.")
        except Placement.DoesNotExist:
            raise Exception(f"Placement with id {placementId} does not exist.")
        except Exception as e:
            return DeletePlacement(statusCode=400, message=str(e))


#  Mutation for Creating DeleteRequest

from IDS_GraphQL import settings
from Authentication.models import Login

class CreateDeleteRequest(graphene.Mutation):
    delete_request = graphene.Field(DeleteRequestType)

    class Arguments:
        productId = graphene.ID(required=True)
        message = graphene.String(required=True)
        approverId = graphene.Int(required=False)  
        status = graphene.String(required=False)

    @login_required
    def mutate(self, info, productId, message, approverId=None, status=None):
        user = info.context.user
        token = info.context.META.get('HTTP_AUTHORIZATION').split(' ')[1]
        
        decoded_token = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token['id']

        user_instance = Login.objects.get(pk=user_id)
        product_instance = Product.objects.get(pk=productId)

        delete_request = DeleteRequest.objects.create(
            userId=user_instance,
            productId=product_instance,
            message=message,
            approverId=approverId,
            status=status
        )

        return CreateDeleteRequest(delete_request=delete_request)


#  Mutation for Creating RequestProduct

class CreateRequestProduct(graphene.Mutation):
    request_product = graphene.Field(RequestProductType)

    class Arguments:
        productId = graphene.ID(required=True)
        quantity = graphene.Int(required=True)
        approvedManagerId = graphene.Int(required=False)  # Optional field
        approvedAdminId = graphene.Int(required=False)  # Optional field
        status = graphene.String(required=True)

    @login_required
    def mutate(self, info, productId, quantity, status, approvedManagerId=None, approvedAdminId=None):
        user = info.context.user
        token = info.context.META.get('HTTP_AUTHORIZATION').split(' ')[1]

        decoded_token = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token['id']

        user_instance = Login.objects.get(pk=user_id)
        product_instance = Product.objects.get(pk=productId)

        request_product = RequestProduct.objects.create(
            userId=user_instance,
            productId=product_instance,
            quantity=quantity,
            approvedManagerId=approvedManagerId,
            approvedAdminId=approvedAdminId,
            status=status,
        )

        return CreateRequestProduct(request_product=request_product)


# Mutation for creating Features assigned to a user


class CreateFeature(graphene.Mutation):
    feature = graphene.Field(FeaturesType)

    class Arguments:
        # Arguments for the mutation
        stockControl = graphene.Boolean()
        overrideManagerApproval = graphene.Boolean()
        viewProductDetails = graphene.Boolean()
        updateStock = graphene.Boolean()
        deleteProduct = graphene.Boolean()
        imageSearch = graphene.Boolean()
        qrScan = graphene.Boolean()
        qrGeneration = graphene.Boolean()
        addProduct = graphene.Boolean()
        approval = graphene.Boolean()
        requestProduct = graphene.Boolean()
        notifications = graphene.Boolean()
        raiseRequest = graphene.Boolean()
        lowStockItems = graphene.Boolean()
        expiryDateItems = graphene.Boolean()

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        token = info.context.META.get('HTTP_AUTHORIZATION').split(' ')[1]

        decoded_token = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token['id']

        user_instance = Login.objects.get(pk=user_id)

        # Create a new Features instance
        feature = Features.objects.create(
            userId=user_instance,
            **kwargs  # Pass all provided boolean fields
        )

        return CreateFeature(feature=feature)



class InventoryDetailType(graphene.ObjectType):
    inventoryId = graphene.Int()
    warehouseId = graphene.Int()
    minStockLevel = graphene.String()
    maxStockLevel = graphene.String()
    quantityAvailable = graphene.String(required=False)
    invreOrderPoint = graphene.Int()

class BatchDetailType(graphene.ObjectType):
    batchId = graphene.Int()
    manufactureDate = graphene.Date()
    expiryDate = graphene.Date()
    quantity = graphene.String()
    createdUser = graphene.String()
    modifiedUser = graphene.String()


class PlacementType(graphene.ObjectType):
    productId = graphene.Field(ProductType)
    warehouseId = graphene.Field(WarehouseType)
    placementId = graphene.Int()
    placementQuantity = graphene.Int()
    aile = graphene.String()
    bin = graphene.String()
    createdUser = graphene.String()
    modifiedUser = graphene.String()
    createdTime = graphene.DateTime()
    modifiedTime = graphene.DateTime()    
    batches = graphene.List(BatchDetailType)

class PlacementDetailType(graphene.ObjectType):
    warehouseId = graphene.Int()
    warehouseName = graphene.String()
    placements = graphene.List(PlacementType)


class ProductResponseType(graphene.ObjectType):
    productId = graphene.Int()
    productCode = graphene.String()
    qrCode = graphene.String()
    productName = graphene.String()
    productDescription = graphene.String()
    productCategory = graphene.String()
    category_name = graphene.String()
    reOrderPoint = graphene.Int()
    brand = graphene.String()
    weight = graphene.String()
    dimensions = graphene.String()
    images = graphene.List(graphene.String)
    createdUser = graphene.String()
    modifiedUser = graphene.String()
    createdTime = graphene.DateTime()
    modifiedTime = graphene.DateTime()
    rowstatus = graphene.Boolean()
    inventoryDetails = graphene.List(InventoryDetailType)
    placementDetails = graphene.List(PlacementDetailType)
    # batchDetails = graphene.List(BatchDetailType)  # Uncomment if needed


# Root Query class to define all queries

class Query(graphene.ObjectType):

    # product = graphene.Field(ProductType, id=graphene.Int(required=True))
    all_products = graphene.List(ProductResponseType)
    product_response = graphene.Field(ProductResponseType, productId=graphene.Int())


    category = graphene.Field(CategoryType, id=graphene.Int(required=True))
    all_categories = graphene.List(CategoryType)

    inventory = graphene.Field(InventoryType, id=graphene.Int(required=True))
    all_inventories = graphene.List(InventoryType)
    inventory_by_product = graphene.List(InventoryType, productId=graphene.Int(required=True))

    warehouse = graphene.Field(WarehouseType, id=graphene.ID(required=True))
    all_warehouses = graphene.List(WarehouseType)

    all_locations = graphene.List(LocationType)
    location = graphene.Field(LocationType, id=graphene.ID(required=True))

    allPlacements = graphene.List(PlacementType)
    placementById = graphene.Field(PlacementType, placementId=graphene.Int(required=True))

    # Fetch all placements where rowstatus=True
    @login_required
    def resolve_allPlacements(self, info):
        return Placement.objects.filter(rowstatus=True)
            
    # Fetch a single placement by placementId where rowstatus=True
    @login_required
    def resolve_placementById(self, info, placementId):
        try:
            return Placement.objects.get(pk=placementId, rowstatus=True)
        except Placement.DoesNotExist:
            return None
        

    # Fetch all warehouses 
    @login_required                       
    def resolve_all_warehouses(self, info, **kwargs):
        return Warehouse.objects.all()

    # Fetch all locations
    @login_required                       
    def resolve_all_locations(self, info, **kwargs):
        return Location.objects.all()

    # Fetch a single warehouse by id 
    @login_required                       
    def resolve_warehouse(self, info, id, **kwargs):
        return Warehouse.objects.get(pk=id)

    # Fetch a single location by id 
    @login_required                       
    def resolve_location(self, info, id, **kwargs):
        return Location.objects.get(pk=id)

    # Fetch all products and related inventories where rowstatus=True
    @login_required                   
    def resolve_all_products(self, info):
        products = Product.objects.filter(rowstatus=True)
        product_responses = []

        for product in products:
            inventories = Inventory.objects.filter(productId=product)

            inventory_details = []
            for inventory in inventories:
                inventory_detail = {
                    'inventoryId': inventory.inventoryId,
                    'warehouseId': inventory.warehouseId.pk,
                    'minStockLevel': inventory.minStockLevel,
                    'maxStockLevel': inventory.maxStockLevel,
                    'quantityAvailable': inventory.quantityAvailable,
                    'invreOrderPoint': inventory.invreOrderPoint,

            }
                inventory_details.append(inventory_detail)

            images_list = product.images
            if isinstance(images_list, str):
                images_list = json.loads(images_list)

        # Fetch category name using the category ID
            category = Category.objects.get(pk=product.productCategory)
            category_name = category.name

        # Fetch placements associated with the product
            placements = Placement.objects.filter(productId=product, rowstatus=True)

            placement_details = []
            for placement in placements:
                placement_detail = {
                    'placementId': placement.placementId,
                    # 'warehouseid': placement.warehouseid.pk,
                    'warehouseName': placement.warehouseId.warehouseName,  
                    'aile': placement.aile,
                    'bin': placement.bin,
                    # 'batchid': placement.batchid.pk
            }
                placement_details.append(placement_detail)

            product_response = ProductResponseType(
                productId=product.pk,
                productCode=product.productCode,
                qrCode=product.qrCode,
                productName=product.productName,
                productDescription=product.productDescription,
                productCategory=str(product.productCategory),
                category_name=category_name,
                reOrderPoint=product.reOrderPoint,
                brand=product.brand,
                weight=product.weight,
                dimensions=product.dimensions,
                images=images_list,
                createdUser=product.createdUser,
                modifiedUser=product.modifiedUser,
                createdTime=product.createdTime,
                modifiedTime=product.modifiedTime,
                rowstatus=product.rowstatus,
                inventoryDetails=inventory_details,
                placementDetails=placement_details,  # Include placement details
                # batchDetails=batch_details  # Include batch details
        )
            product_responses.append(product_response)

        return product_responses
    
    # Fetch a single category by id where rowstatus=True
    @login_required                       
    def resolve_category(self, info, id):
        return Category.objects.get(pk=id, rowstatus=True)
    
    # Fetch all categories where rowstatus=True
    @login_required                       
    def resolve_all_categories(self, info):
        return Category.objects.filter(rowstatus=True)
        
    # Fetch a single inventory by id 
    @login_required                       
    def resolve_inventory(self, info, id):
        return Inventory.objects.get(pk=id)
    
    # Fetch all inventories where rowstatus=True
    @login_required                       
    def resolve_all_inventories(self, info):
        return Inventory.objects.all()
    
    @login_required                       
    def resolve_inventory_by_product(self, info, productId):
        return Inventory.objects.filter(productId=productId)
   
    @login_required    
    def resolve_product_response(self, info, productId=None):
        try:
            if productId is None:
                raise Exception("Either productid or productcode must be provided")

        # Fetch the product
            product = Product.objects.get(pk=productId, rowstatus=True)

        # Fetch inventories associated with the product
            inventory_details = []
            inventories = Inventory.objects.filter(productId=product)
            for inventory in inventories:
                inventory_details.append({
                'inventoryId': inventory.inventoryId,
                'warehouseId': inventory.warehouseId.pk,
                'minStockLevel': inventory.minStockLevel,
                'maxStockLevel': inventory.maxStockLevel,
                'quantityAvailable': str(inventory.quantityAvailable),  # Ensure quantityavailable is string
                'invreOrderPoint': inventory.invreOrderPoint,
            })

        # Fetch category name using the category ID
            category = Category.objects.get(pk=product.productCategory)
            category_name = category.name

        # Initialize response structure
            response = {
            'productId': product.pk,
            'productCode': product.productCode,
            'qrCode': product.qrCode,
            'productName': product.productName,
            'productDescription': product.productDescription,
            'productCategory': str(product.productCategory),
            'category_name': category_name,
            'reOrderPoint': product.reOrderPoint,
            'brand': product.brand,
            'weight': product.weight,
            'dimensions': product.dimensions,
            'images': json.loads(product.images),
            'createdUser': product.createdUser,
            'modifiedUser': product.modifiedUser,
            'createdTime': product.createdTime,
            'modifiedTime': product.modifiedTime,
            'rowstatus': product.rowstatus,
            'inventoryDetails': inventory_details,
            'placementDetails': [],  # Initialize placement details as a list
        }

        # Fetch placements associated with the product
            placements = Placement.objects.filter(productId=product, rowstatus=True)

            warehouse_placements = {}

            for placement in placements:
                warehouseId = placement.warehouseId.pk
                if warehouseId not in warehouse_placements:
                    warehouse_placements[warehouseId] = {
                    'warehouseId': warehouseId,
                    'warehouseName': placement.warehouseId.warehouseName,
                    'placements': []
                }

                placement_detail = {
                'placementId': placement.placementId,
                'placementQuantity': placement.placementQuantity,
                'aile': placement.aile,
                'bin': placement.bin,
                'batches': []
            }

            # Fetch batches associated with this placement
                batches = Batch.objects.filter(placement=placement, rowstatus=True)
                for batch in batches:
                    batch_detail = {
                    'batchId': batch.batchId,  # Ensure batchid is serialized correctly
                    'expiryDate': batch.expiryDate,
                    'manufactureDate': batch.manufactureDate,
                    'quantity': batch.quantity,
                    'createdUser': batch.createdUser,
                    'modifiedUser': batch.modifiedUser,
                }
                    placement_detail['batches'].append(batch_detail)

                warehouse_placements[warehouseId]['placements'].append(placement_detail)

            response['placementDetails'] = list(warehouse_placements.values())

            return ProductResponseType(**response)

        except Product.DoesNotExist:
            return None



# Root Mutation class to define all mutations

class Mutation(graphene.ObjectType):
    update_product = UpdateProduct.Field()
    create_product = CreateProduct.Field()
    delete_product = DeleteProduct.Field()

    create_warehouse = CreateWarehouse.Field()
    create_location = CreateLocation.Field()

    create_category = CreateCategory.Field()
    update_category = UpdateCategory.Field()
    delete_category = DeleteCategory.Field()

    create_placement = CreatePlacement.Field()
    update_placement = UpdatePlacement.Field()
    delete_placement = DeletePlacement.Field()

    create_inventory = CreateInventory.Field()
    update_inventory = UpdateInventory.Field()

    create_delete_request = CreateDeleteRequest.Field()

    create_request_product = CreateRequestProduct.Field()

    create_feature = CreateFeature.Field()





# Define the GraphQL schema with defined Query and Mutation
idscore_schema = graphene.Schema(query=Query, mutation=Mutation)
