import json
import graphene
from graphene_django import DjangoObjectType
from .models import Product, Inventory, Warehouse, Location, Category, Batch, Placement
from graphql_jwt.decorators import login_required


# Define GraphQL Types for Django Models

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class InventoryType(DjangoObjectType):
    warehouseid = graphene.Int()   

    class Meta:
        model = Inventory
    
    def resolve_warehouseid(self, info):
        return self.warehouseid.pk  # Return the primary key of the warehouse

class LocationType(DjangoObjectType):
    class Meta:
        model = Location

class WarehouseType(DjangoObjectType):
    class Meta:
        model = Warehouse

    # Resolve the relationship with Location
    location = graphene.Field(LocationType)

    def resolve_location(self, info):
        return self.locationid

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category

class BatchType(DjangoObjectType):
    class Meta:
        model = Batch

class PlacementType(DjangoObjectType):
    warehousename = graphene.String()

    class Meta:
        model = Placement
        # fields = ("placementId", "warehouseid", "aile", "bin")  # Include other necessary fields


    def resolve_warehousename(self, info):
        # Resolve warehousename from the related Warehouse object
        return self.warehouseid.warehousename if self.warehouseid else None

# Mutations for Creating, Updating, and Deleting Categories

class CreateCategory(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        image = graphene.String()  
        rowstatus = graphene.Boolean(default_value=True)

    category = graphene.Field(CategoryType)
    status_code = graphene.Int()
    message = graphene.String()
    
    @login_required
    def mutate(self, info, name, image=None, rowstatus=True):
        try:
            category = Category(name=name, image=image, rowstatus=rowstatus)
            category.save()
            return CreateCategory(category=category, status_code=200, message="Category created successfully.")
        except Exception as e:
            return CreateCategory(status_code=400, message=str(e))


class UpdateCategory(graphene.Mutation):
    class Arguments:
        category_id = graphene.ID(required=True)
        name = graphene.String()
        image = graphene.String()
        rowstatus = graphene.Boolean()

    category = graphene.Field(CategoryType)
    status_code = graphene.Int()
    message = graphene.String()
    
    @login_required
    def mutate(self, info, category_id, name=None, image=None, rowstatus=None):
        try:
            # Retrieve the existing Category object
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            raise Exception(f"Category with id {category_id} does not exist.")

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
            return UpdateCategory(status_code=400, message=str(e))


class DeleteCategory(graphene.Mutation):
    class Arguments:
        category_id = graphene.ID(required=True)

    category_id = graphene.ID()
    status_code = graphene.Int()
    message = graphene.String()
   
    @login_required
    def mutate(self, info, category_id):
        try:
            # Soft delete the Category by setting rowstatus to False
            category = Category.objects.get(pk=category_id)
            category.rowstatus = False  # Soft delete by setting rowstatus to False
            category.save()
            return DeleteCategory(category_id=category_id, status_code=200, message="Category deleted successfully.")
        except Category.DoesNotExist:
            raise Exception(f"Category with id {category_id} does not exist.")
        except Exception as e:
            return DeleteCategory(status_code=400, message=str(e))

class InventoryInput(graphene.InputObjectType):
    productid = graphene.ID(required=True)
    quantityavailable = graphene.String(required=True)
    minstocklevel = graphene.String(required=True)
    maxstocklevel = graphene.String(required=True)
    invreorderpoint = graphene.Int(required=True)
    warehouseid = graphene.ID(required=True)
    createduser = graphene.String(required=True)
    modifieduser = graphene.String(required=True)
    rowstatus = graphene.Boolean(required=True)


class CreateInventory(graphene.Mutation):
    class Arguments:
        input = InventoryInput(required=True)

    inventories = graphene.List(InventoryType)
    status_code = graphene.Int()
    message = graphene.String()

    
    @login_required
    def mutate(self, info, input):
        try:
            product = Product.objects.get(pk=input.productid)
            warehouse = Warehouse.objects.get(pk=input.warehouseid)

            inventory = Inventory(
                productid=product,
                quantityavailable=input.quantityavailable,
                minstocklevel=input.minstocklevel,
                maxstocklevel=input.maxstocklevel,
                invreorderpoint=input.invreorderpoint,
                warehouseid=warehouse,
                createduser=input.createduser,
                modifieduser=input.modifieduser,
                rowstatus=input.rowstatus,
            )
            inventory.save()

            # Fetch all inventories related to the product
            inventories = Inventory.objects.filter(productid=product)

            return CreateInventory(
                inventories=inventories,
                status_code=200,
                message="Inventory entry created successfully."
            )
        except Exception as e:
            return CreateInventory(status_code=400, message=str(e))









# Input Object Type for Inventory details
class InventoryInputType(graphene.InputObjectType):
    warehouseid = graphene.Int(required=True)
    minstocklevel = graphene.String(required=True)
    maxstocklevel = graphene.String(required=True)
    quantityavailable = graphene.String()
    invreorderpoint = graphene.Int()  


# Mutation for Creating a Product and its related Inventories
class CreateProduct(graphene.Mutation):
    class Arguments:
        productcode = graphene.String(required=True)
        qrcode = graphene.String()
        productname = graphene.String(required=True)
        productdescription = graphene.String(required=True)
        productcategory = graphene.String(required=True)
        reorderpoint = graphene.Int()
        brand = graphene.String()
        weight = graphene.String()
        dimensions = graphene.String()
        images = graphene.List(graphene.String)
        createduser = graphene.String()
        modifieduser = graphene.String()
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

            # Create Inventory instances related to the Product
            for inventory_detail in inventory_details:
                warehouse = Warehouse.objects.get(pk=inventory_detail['warehouseid'])
                inventory = Inventory(
                    productid=product,
                    quantityavailable=inventory_detail['quantityavailable'],
                    minstocklevel=inventory_detail['minstocklevel'],
                    maxstocklevel=inventory_detail['maxstocklevel'],
                    invreorderpoint=inventory_detail['invreorderpoint'],
                    warehouseid=warehouse,
                    createduser=createduser,
                    modifieduser=modifieduser
                )
                inventory.save()

            return CreateProduct(status_code=200, message="Product and inventories created successfully.")
        except Exception as e:
            return CreateProduct(status_code=400, message=str(e))

# Mutation for Updating a Product and its related Inventories

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

            # Update related Inventory instances
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
                            'invreorderpoint': inventory_detail['invreorderpoint'],
                            'createduser': createduser if createduser else product.createduser,
                            'modifieduser': modifieduser if modifieduser else product.modifieduser
                        }
                    )

            return UpdateProduct(status_code=200, message="Product and inventories updated successfully.")
        except Product.DoesNotExist:
            return UpdateProduct(status_code=404, message="Product not found.")
        except Exception as e:
            return UpdateProduct(status_code=400, message=str(e))

# Mutation for Deleting a Product and its related Inventories

class DeleteProduct(graphene.Mutation):
    class Arguments:
        product_id = graphene.ID(required=True)

    product_id = graphene.ID()
    status_code = graphene.Int()
    message = graphene.String()

    @login_required
    def mutate(self, info, product_id):
        try:
            # Soft delete the Product by setting rowstatus to False
            product = Product.objects.get(pk=product_id)
            product.rowstatus = False  
            product.save()

            # Soft delete related Inventory instances
            inventories = Inventory.objects.filter(productid=product)
            for inventory in inventories:
                inventory.rowstatus = False
                inventory.save()

            return DeleteProduct(product_id=product_id, status_code=200, message="Product deleted successfully.")
        except Product.DoesNotExist:
            raise Exception(f"Product with id {product_id} does not exist.")
        except Exception as e:
            return DeleteProduct(status_code=400, message=str(e))


# Mutation for Creating Warehouses

class CreateWarehouse(graphene.Mutation):
    class Arguments:
        locationid = graphene.ID(required=True)
        warehousename = graphene.String(required=True)
        createduser = graphene.String(required=True)
        modifieduser = graphene.String(required=True)

    warehouse = graphene.Field(WarehouseType)
    status_code = graphene.Int()
    message = graphene.String()

    @login_required
    def mutate(self, info, locationid, warehousename, createduser, modifieduser):
        try:
            location = Location.objects.get(pk=locationid)
            warehouse = Warehouse.objects.create(
                locationid=location,
                warehousename=warehousename,
                createduser=createduser,
                modifieduser=modifieduser
            )
            return CreateWarehouse(warehouse=warehouse, status_code=200, message="Warehouse created successfully.")
        except Location.DoesNotExist:
            raise Exception(f"Location with id {locationid} does not exist.")
        except Exception as e:
            return CreateWarehouse(status_code=400, message=str(e))


# Mutation for Creating Locations

class CreateLocation(graphene.Mutation):
    class Arguments:
        locationname = graphene.String(required=True)
        locationaddress = graphene.String(required=True)
        createduser = graphene.String(required=True)
        modifieduser = graphene.String(required=True)

    location = graphene.Field(LocationType)
    status_code = graphene.Int()
    message = graphene.String()

    @login_required
    def mutate(self, info, locationname, locationaddress, createduser, modifieduser):
        try:
            location = Location.objects.create(
                locationname=locationname,
                locationaddress=locationaddress,
                createduser=createduser,
                modifieduser=modifieduser
            )
            return CreateLocation(location=location, status_code=200, message="Location created successfully.")
        except Exception as e:
            return CreateLocation(status_code=400, message=str(e))


# Mutations for Creating, Updating, and Deleting Batches

class CreateBatch(graphene.Mutation):
    batches = graphene.List(BatchType)
    status_code = graphene.Int()
    message = graphene.String()

    class Arguments:
        productid = graphene.Int(required=True)
        manufacturedate = graphene.Date()
        expirydate = graphene.Date()
        quantity = graphene.String(required=True)
        createduser = graphene.String(required=True)
        modifieduser = graphene.String(required=True)
        rowstatus = graphene.Boolean()

    @login_required
    def mutate(self, info, productid, quantity, createduser, modifieduser, manufacturedate=None, expirydate=None, rowstatus=True):
        try:
            product = Product.objects.get(productid=productid)
            batch = Batch(
                productid=product,
                manufacturedate=manufacturedate,
                expirydate=expirydate,
                quantity=quantity,
                createduser=createduser,
                modifieduser=modifieduser,
                rowstatus=rowstatus
            )
            batch.save()

            # Retrieve all batches after creation
            batches = Batch.objects.filter(productid=product)

            return CreateBatch(batches=batches, status_code=200, message="Batch created successfully.")
        except Exception as e:
            return CreateBatch(status_code=400, message=str(e))



class UpdateBatch(graphene.Mutation):
    batches = graphene.List(BatchType)
    status_code = graphene.Int()
    message = graphene.String()

    class Arguments:
        batchid = graphene.Int(required=True)
        productid = graphene.Int(required=False)
        manufacturedate = graphene.Date(required=False)
        expirydate = graphene.Date(required=False)
        quantity = graphene.String(required=False)
        createduser = graphene.String(required=False)
        modifieduser = graphene.String(required=False)
        rowstatus = graphene.Boolean(required=False)

    @login_required
    def mutate(self, info, batchid, **kwargs):
        try:
            batch = Batch.objects.get(batchid=batchid)
            productid = kwargs.get('productid')
            if productid:
                batch.productid = Product.objects.get(productid=productid)
            for key, value in kwargs.items():
                if key != 'productid':
                    setattr(batch, key, value)
            batch.save()

            # Retrieve all batches after update
            batches = Batch.objects.filter(productid=product)

            return UpdateBatch(batches=batches, status_code=200, message="Batch updated successfully.")
        except Exception as e:
            return UpdateBatch(status_code=400, message=str(e))




class DeleteBatch(graphene.Mutation):
    status_code = graphene.Int()
    message = graphene.String()

    class Arguments:
        batchid = graphene.Int(required=True)

    @login_required
    def mutate(self, info, batchid):
        try:
            batch = Batch.objects.get(batchid=batchid)
            batch.rowstatus = False
            batch.save()
            return DeleteBatch(status_code=200, message="Batch deleted successfully (soft delete).")
        except Batch.DoesNotExist:
            return DeleteBatch(status_code=404, message="Batch not found.")
        except Exception as e:
            return DeleteBatch(status_code=400, message=str(e))


# Mutations for Creating, Updating, and Deleting Placements

class CreatePlacement(graphene.Mutation):
    placements = graphene.List(PlacementType)
    status_code = graphene.Int()
    message = graphene.String()

    class Arguments:
        productid = graphene.Int(required=True)
        warehouseid = graphene.Int(required=True)
        aile = graphene.String(required=True)
        bin = graphene.String(required=True)
        batchid = graphene.Int(required=True)
        createduser = graphene.String(required=True)
        modifieduser = graphene.String(required=True)

    @login_required
    def mutate(self, info, productid, warehouseid, aile, bin, batchid, createduser, modifieduser):
        try:
            product = Product.objects.get(pk=productid)
            warehouse = Warehouse.objects.get(pk=warehouseid)
            batch = Batch.objects.get(pk=batchid)

            placement = Placement.objects.create(
                productid=product,
                warehouseid=warehouse,
                aile=aile,
                bin=bin,
                batchid=batch,
                createduser=createduser,
                modifieduser=modifieduser
            )

            # Retrieve placements related to the specific productid
            placements = Placement.objects.filter(productid=product)

            return CreatePlacement(placements=placements, status_code=200, message="Placement created successfully.")
        except Product.DoesNotExist:
            raise Exception(f"Product with id {productid} does not exist.")
        except Warehouse.DoesNotExist:
            raise Exception(f"Warehouse with id {warehouseid} does not exist.")
        except Batch.DoesNotExist:
            raise Exception(f"Batch with id {batchid} does not exist.")
        except Exception as e:
            return CreatePlacement(status_code=400, message=str(e))


class UpdatePlacement(graphene.Mutation):
    placements = graphene.List(PlacementType)
    status_code = graphene.Int()
    message = graphene.String()

    class Arguments:
        placementId = graphene.Int(required=True)
        productid = graphene.Int()
        warehouseid = graphene.Int()
        aile = graphene.String()
        bin = graphene.String()
        batchid = graphene.Int()
        createduser = graphene.String()
        modifieduser = graphene.String()

    @login_required
    def mutate(self, info, placementId, **kwargs):
        try:
            placement = Placement.objects.get(pk=placementId)

            productid = kwargs.get('productid')
            if productid:
                try:
                    product_instance = Product.objects.get(pk=productid)
                    placement.productid = product_instance
                except Product.DoesNotExist:
                    raise Exception(f"Product with id {productid} does not exist.")

            warehouseid = kwargs.get('warehouseid')
            if warehouseid:
                try:
                    warehouse_instance = Warehouse.objects.get(pk=warehouseid)
                    placement.warehouseid = warehouse_instance
                except Warehouse.DoesNotExist:
                    raise Exception(f"Warehouse with id {warehouseid} does not exist.")

            batchid = kwargs.get('batchid')
            if batchid:
                try:
                    batch_instance = Batch.objects.get(pk=batchid)
                    placement.batchid = batch_instance
                except Batch.DoesNotExist:
                    raise Exception(f"Batch with id {batchid} does not exist.")

            for key, value in kwargs.items():
                if key in ['aile', 'bin', 'createduser', 'modifieduser']:
                    setattr(placement, key, value)

            placement.save()

            # Retrieve all placements related to the updated productid
            placements = Placement.objects.filter(productid=product_instance)

            return UpdatePlacement(placements=placements, status_code=200, message="Placement updated successfully.")
        except Placement.DoesNotExist:
            raise Exception(f"Placement with id {placementId} does not exist.")
        except Exception as e:
            return UpdatePlacement(status_code=400, message=str(e))


class DeletePlacement(graphene.Mutation):
    class Arguments:
        placementId = graphene.Int(required=True)

    status_code = graphene.Int()
    message = graphene.String()

    @login_required
    def mutate(self, info, placementId):
        try:
            placement = Placement.objects.get(pk=placementId)
            placement.rowstatus = False  # Soft delete by setting rowstatus to False
            placement.save()

            return DeletePlacement(status_code=200, message="Placement deleted successfully.")
        except Placement.DoesNotExist:
            raise Exception(f"Placement with id {placementId} does not exist.")
        except Exception as e:
            return DeletePlacement(status_code=400, message=str(e))



class BatchDetailType(graphene.ObjectType):
    batchid = graphene.Int()
    manufacturedate = graphene.Date()
    expirydate = graphene.Date()
    quantity = graphene.String()
    createduser = graphene.String()
    modifieduser = graphene.String()

class InventoryDetailType(graphene.ObjectType):
    warehouseid = graphene.Int()
    minstocklevel = graphene.String()
    maxstocklevel = graphene.String()
    quantityavailable = graphene.String()
    invreorderpoint = graphene.Int()  



class PlacementDetailType(graphene.ObjectType):
    placementId = graphene.Int()
    # warehouseid = graphene.Int()
    warehousename = graphene.String()
    aile = graphene.String()
    bin = graphene.String()
    # batchid = graphene.Int()

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
    placementDetails = graphene.List(PlacementDetailType)  # Add this field
    batchDetails = graphene.List(BatchDetailType)  # Add this field


# Root Query class to define all queries

class Query(graphene.ObjectType):

    product = graphene.Field(ProductType, id=graphene.Int(required=True))
    all_products = graphene.List(ProductResponseType)
    product_response = graphene.Field(ProductResponseType, productid=graphene.Int())


    category = graphene.Field(CategoryType, id=graphene.Int(required=True))
    all_categories = graphene.List(CategoryType)

    inventory = graphene.Field(InventoryType, id=graphene.Int(required=True))
    all_inventories = graphene.List(InventoryType)
    inventory_by_product = graphene.List(InventoryType, productid=graphene.Int(required=True))

    warehouse = graphene.Field(WarehouseType, id=graphene.ID(required=True))
    all_warehouses = graphene.List(WarehouseType)

    all_locations = graphene.List(LocationType)
    location = graphene.Field(LocationType, id=graphene.ID(required=True))

    all_batches = graphene.List(BatchType)
    batch_by_id = graphene.Field(BatchType, batchid=graphene.Int(required=True))

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
        
    # Fetch all batchs where rowstatus=True
    @login_required
    def resolve_all_batches(self, info):
        return Batch.objects.filter(rowstatus=True)

    # Fetch a single batch by batchid where rowstatus=True
    @login_required
    def resolve_batch_by_id(self, info, batchid):
        try:
            return Batch.objects.get(batchid=batchid, rowstatus=True)
        except Batch.DoesNotExist:
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
    # @login_required                   
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
                    'quantityavailable': inventory.quantityavailable,
                    'invreorderpoint': inventory.invreorderpoint,

            }
                inventory_details.append(inventory_detail)

            images_list = product.images
            if isinstance(images_list, str):
                images_list = json.loads(images_list)

        # Fetch category name using the category ID
            category = Category.objects.get(pk=product.productcategory)
            category_name = category.name

        # Fetch placements associated with the product
            placements = Placement.objects.filter(productid=product, rowstatus=True)

            placement_details = []
            for placement in placements:
                placement_detail = {
                    'placementId': placement.placementId,
                    # 'warehouseid': placement.warehouseid.pk,
                    'warehousename': placement.warehouseid.warehousename,  
                    'aile': placement.aile,
                    'bin': placement.bin,
                    # 'batchid': placement.batchid.pk
            }
                placement_details.append(placement_detail)

        # Fetch batches associated with the product
            batches = Batch.objects.filter(productid=product, rowstatus=True)

            batch_details = []
            for batch in batches:
                batch_detail = {
                    'batchid': batch.batchid,
                    'manufacturedate': batch.manufacturedate,
                    'expirydate': batch.expirydate,
                    'quantity': batch.quantity,
                    'createduser': batch.createduser,
                    'modifieduser': batch.modifieduser
            }
                batch_details.append(batch_detail)

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
                inventoryDetails=inventory_details,
                placementDetails=placement_details,  # Include placement details
                batchDetails=batch_details  # Include batch details
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
    def resolve_inventory_by_product(self, info, productid):
        return Inventory.objects.filter(productid=productid)
   
    @login_required                       
    def resolve_product_response(self, info, productid=None):
        try:
            if productid is not None:
                product = Product.objects.get(pk=productid, rowstatus=True)
            else:
                raise Exception("Either productid or productcode must be provided")

            inventories = Inventory.objects.filter(productid=product)

            inventory_details = []
            for inventory in inventories:
                inventory_detail = {
                    'warehouseid': inventory.warehouseid.pk,
                    'minstocklevel': inventory.minstocklevel,
                    'maxstocklevel': inventory.maxstocklevel,
                    'quantityavailable': inventory.quantityavailable,
                    'invreorderpoint' : inventory.invreorderpoint,

            }
                inventory_details.append(inventory_detail)

        # Fetch category name using the category ID
            category = Category.objects.get(pk=product.productcategory)
            category_name = category.name

        # Fetch placements associated with the product
            placements = Placement.objects.filter(productid=product, rowstatus=True)

            placement_details = []
            for placement in placements:
                placement_detail = {
                    'placementId': placement.placementId,
                    # 'warehouseid': placement.warehouseid.pk,
                    'warehousename': placement.warehouseid.warehousename,  
                    'aile': placement.aile,
                    'bin': placement.bin,
                    # 'batchid': placement.batchid.pk
            }
                placement_details.append(placement_detail)

        # Fetch batches associated with the product
            batches = Batch.objects.filter(productid=product, rowstatus=True)

            batch_details = []
            for batch in batches:
                batch_detail = {
                    'batchid': batch.batchid,
                    'manufacturedate': batch.manufacturedate,
                    'expirydate': batch.expirydate,
                    'quantity': batch.quantity,
                    'createduser': batch.createduser,
                    'modifieduser': batch.modifieduser
            }
                batch_details.append(batch_detail)

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
                inventoryDetails=inventory_details,
                placementDetails=placement_details,  # Include placement details
                batchDetails=batch_details  # Include batch details
        )
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

    create_batch = CreateBatch.Field()
    update_batch = UpdateBatch.Field()
    delete_batch = DeleteBatch.Field()

    create_placement = CreatePlacement.Field()
    update_placement = UpdatePlacement.Field()
    delete_placement = DeletePlacement.Field()

    create_inventory = CreateInventory.Field()



# Define the GraphQL schema with defined Query and Mutation
idscore_schema = graphene.Schema(query=Query, mutation=Mutation)
