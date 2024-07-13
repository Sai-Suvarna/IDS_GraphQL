# from django.db import models
# from django.contrib.postgres.fields import ArrayField

# # Model for product categories
# class Category(models.Model):
#     category_id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
#     name = models.CharField(max_length=255, unique=True)  # Name of the category
#     image = models.URLField(null=True, blank=True)  # URL field to store image
#     rowstatus = models.BooleanField(default=True)  # Boolean field for row status

# # Model for products
# class Product(models.Model):
#     productid = models.AutoField(primary_key=True)  # Auto-incrementing primary key
#     productcode = models.CharField(max_length=100)  # Product code
#     qrcode = models.TextField()  # QR code for the product
#     productname = models.CharField(max_length=255)  # Name of the product
#     productdescription = models.TextField()  # Description of the product
#     productcategory = models.IntegerField()  # Category ID for the product
#     reorderpoint = models.IntegerField()  # Reorder point quantity
#     brand = models.CharField(max_length=100)  # Brand name of the product
#     weight = models.CharField(max_length=50)  # Weight of the product
#     dimensions = models.CharField(max_length=100)  # Dimensions of the product
#     images = models.JSONField()  # JSON field to store multiple images
#     createduser = models.CharField(max_length=100)  # User who created the product
#     modifieduser = models.CharField(max_length=100)  # User who last modified the product
#     createdtime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
#     modifiedtime = models.DateTimeField(auto_now=True)  # Timestamp when last modified
#     rowstatus = models.BooleanField(default=True)  # Boolean field for row status

#     def __str__(self):
#         return self.productname  # String representation of the product

# # Model for inventory
# class Inventory(models.Model):
#     inventoryid = models.AutoField(primary_key=True)  # Auto-incrementing primary key
#     productid = models.ForeignKey(Product, on_delete=models.CASCADE)  # Foreign key to Product table
#     quantityavailable = models.CharField(max_length=50)  # Available quantity in inventory
#     minstocklevel = models.CharField(max_length=50)  # Minimum stock level
#     maxstocklevel = models.CharField(max_length=50)  # Maximum stock level
#     invreorderpoint = models.IntegerField()  # Reorder point for the product
#     warehouseid = models.ForeignKey('Warehouse', on_delete=models.CASCADE)  # Foreign key to Warehouse table
#     createduser = models.CharField(max_length=100)  # User who created the inventory entry
#     modifieduser = models.CharField(max_length=100)  # User who last modified the inventory entry
#     createdtime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
#     modifiedtime = models.DateTimeField(auto_now=True)  # Timestamp when last modified
#     rowstatus = models.BooleanField(default=True)  # Boolean field for row status

#     def __str__(self):
#         return f"Inventory for {self.productid.productname}"  # String representation of the inventory entry

# # Model for warehouses
# class Warehouse(models.Model):
#     warehouseid = models.AutoField(primary_key=True)  # Auto-incrementing primary key
#     locationid = models.ForeignKey('Location', on_delete=models.CASCADE)  # Foreign key to Location table
#     warehousename = models.CharField(max_length=255)  # Name of the warehouse
#     createduser = models.CharField(max_length=100)  # User who created the warehouse
#     modifieduser = models.CharField(max_length=100)  # User who last modified the warehouse
#     createdtime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
#     modifiedtime = models.DateTimeField(auto_now=True)  # Timestamp when last modified
#     rowstatus = models.BooleanField(default=True)  # Boolean field for row status

#     def __str__(self):
#         return self.warehousename  # String representation of the warehouse

# # Model for locations
# class Location(models.Model):
#     locationid = models.AutoField(primary_key=True)  # Auto-incrementing primary key
#     locationname = models.CharField(max_length=255)  # Name of the location
#     locationaddress = models.TextField()  # Address of the location
#     createduser = models.CharField(max_length=100)  # User who created the location
#     modifieduser = models.CharField(max_length=100)  # User who last modified the location
#     createdtime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
#     modifiedtime = models.DateTimeField(auto_now=True)  # Timestamp when last modified
#     rowstatus = models.BooleanField(default=True)  # Boolean field for row status

#     def __str__(self):
#         return self.locationname  # String representation of the location

# # Model for batches of products
# class Batch(models.Model):
#     batchid = models.AutoField(primary_key=True)  # Auto-incrementing primary key
#     productid = models.ForeignKey(Product, on_delete=models.CASCADE)  # Foreign key to Product table
#     manufacturedate = models.DateField(null=True, blank=True)  # Date of batch manufacturing
#     expirydate = models.DateField(null=True, blank=True)  # Expiry date of the batch
#     quantity = models.CharField()  # Quantity of products in the batch
#     createduser = models.CharField(max_length=100)  # User who created the batch
#     modifieduser = models.CharField(max_length=100)  # User who last modified the batch
#     createdtime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
#     modifiedtime = models.DateTimeField(auto_now=True)  # Timestamp when last modified
#     rowstatus = models.BooleanField(default=True)  # Boolean field for row status

#     def __str__(self):
#         return f'Batch {self.batchid} for {self.productid}'  # String representation of the batch

# # Model for placement of products in warehouses
# class Placement(models.Model):
#     placementId = models.AutoField(primary_key=True)  # Auto-incrementing primary key
#     productid = models.ForeignKey(Product, on_delete=models.CASCADE)  # Foreign key to Product table
#     warehouseid = models.ForeignKey(Warehouse, on_delete=models.CASCADE)  # Foreign key to Warehouse table
#     aile = models.CharField(max_length=50)  # Aisle where the product is placed
#     bin = models.CharField(max_length=50)  # Bin where the product is placed
#     batchid = models.ForeignKey(Batch, on_delete=models.CASCADE)  # Foreign key to Batch table
#     createduser = models.CharField(max_length=100)  # User who created the placement entry
#     modifieduser = models.CharField(max_length=100)  # User who last modified the placement entry
#     createdtime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
#     modifiedtime = models.DateTimeField(auto_now=True)  # Timestamp when last modified
#     rowstatus = models.BooleanField(default=True)  # Boolean field for row status

#     def __str__(self):
#         return f'Placement {self.placementId} - Product: {self.productid}, Warehouse: {self.warehouseid}'  # String representation of the placement entry



from django.db import models
from django.contrib.postgres.fields import ArrayField
from Authentication.models import Login

# Model for product categories
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    name = models.CharField(max_length=255, unique=True)  # Name of the category
    image = models.URLField(null=True, blank=True)  # URL field to store image
    rowstatus = models.BooleanField(default=True)  # Boolean field for row status

# Model for products
class Product(models.Model):
    productid = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    productcode = models.CharField(max_length=100)  # Product code
    qrcode = models.TextField()  # QR code for the product
    productname = models.CharField(max_length=255)  # Name of the product
    productdescription = models.TextField()  # Description of the product
    productcategory = models.IntegerField()  # Category ID for the product
    reorderpoint = models.IntegerField()  # Reorder point quantity
    brand = models.CharField(max_length=100)  # Brand name of the product
    weight = models.CharField(max_length=50)  # Weight of the product
    dimensions = models.CharField(max_length=100)  # Dimensions of the product
    images = models.JSONField()  # JSON field to store multiple images
    createduser = models.CharField(max_length=100)  # User who created the product
    modifieduser = models.CharField(max_length=100)  # User who last modified the product
    createdtime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
    modifiedtime = models.DateTimeField(auto_now=True)  # Timestamp when last modified
    rowstatus = models.BooleanField(default=True)  # Boolean field for row status

    def __str__(self):
        return self.productname  # String representation of the product
    
# Model for inventory
class Inventory(models.Model):
    inventoryid = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    productid = models.ForeignKey(Product, on_delete=models.CASCADE)  # Foreign key to Product table
    quantityavailable = models.CharField(max_length=50)  # Available quantity in inventory
    minstocklevel = models.CharField(max_length=50,null=True, blank=True)  # Minimum stock level
    maxstocklevel = models.CharField(max_length=50,null=True, blank=True)  # Maximum stock level
    invreorderpoint = models.IntegerField(null=True, blank=True)  # Allow null values
    warehouseid = models.ForeignKey('Warehouse', on_delete=models.CASCADE)  # Foreign key to Warehouse table
    createduser = models.CharField(max_length=100)  # User who created the inventory entry
    modifieduser = models.CharField(max_length=100)  # User who last modified the inventory entry
    createdtime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
    modifiedtime = models.DateTimeField(auto_now=True)  # Timestamp when last modified
    rowstatus = models.BooleanField(default=True)  # Boolean field for row status

    def __str__(self):
        return f"Inventory for {self.productid.productname}"  # String representation of the inventory entry

    


# Model for warehouses
class Warehouse(models.Model):
    warehouseid = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    locationid = models.ForeignKey('Location', on_delete=models.CASCADE)  # Foreign key to Location table
    warehousename = models.CharField(max_length=255)  # Name of the warehouse
    createduser = models.CharField(max_length=100)  # User who created the warehouse
    modifieduser = models.CharField(max_length=100)  # User who last modified the warehouse
    createdtime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
    modifiedtime = models.DateTimeField(auto_now=True)  # Timestamp when last modified
    rowstatus = models.BooleanField(default=True)  # Boolean field for row status

    def __str__(self):
        return self.warehousename  # String representation of the warehouse

# Model for locations
class Location(models.Model):
    locationid = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    locationname = models.CharField(max_length=255)  # Name of the location
    locationaddress = models.TextField()  # Address of the location
    createduser = models.CharField(max_length=100)  # User who created the location
    modifieduser = models.CharField(max_length=100)  # User who last modified the location
    createdtime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
    modifiedtime = models.DateTimeField(auto_now=True)  # Timestamp when last modified
    rowstatus = models.BooleanField(default=True)  # Boolean field for row status

    def __str__(self):
        return self.locationname  # String representation of the location

# # Model for batches of products
class Batch(models.Model):
    batchid = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    productid = models.ForeignKey(Product, on_delete=models.CASCADE)  # Foreign key to Product table
    manufacturedate = models.DateField(null=True)  # Date of batch manufacturing
    expirydate = models.DateField(null=True, blank=True)  # Expiry date of the batch
    quantity = models.CharField()  # Quantity of products in the batch
    createduser = models.CharField(max_length=100)  # User who created the batch
    modifieduser = models.CharField(max_length=100)  # User who last modified the batch
    createdtime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
    modifiedtime = models.DateTimeField(auto_now=True)  # Timestamp when last modified
    rowstatus = models.BooleanField(default=True)  # Boolean field for row status

    def __str__(self):
        return f'Batch {self.batchid} for {self.productid}'  # String representation of the batch

# Model for placement of products in warehouses
class Placement(models.Model):
    placementId = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    batchid = models.ForeignKey(Batch, on_delete=models.CASCADE)
    productid = models.ForeignKey(Product, on_delete=models.CASCADE)  # Foreign key to Product table
    warehouseid = models.ForeignKey(Warehouse, on_delete=models.CASCADE)  # Foreign key to Warehouse table
    placementQuantity = models.IntegerField() 
    aile = models.CharField(max_length=50)  # Aisle where the product is placed
    bin = models.CharField(max_length=50)  # Bin where the product is placed
    createduser = models.CharField(max_length=100)  # User who created the placement entry
    modifieduser = models.CharField(max_length=100)  # User who last modified the placement entry
    createdtime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
    modifiedtime = models.DateTimeField(auto_now=True)  # Timestamp when last modified
    rowstatus = models.BooleanField(default=True)  # Boolean field for row status

    def __str__(self):
        return f'Placement {self.placementId} - Product: {self.productid}, Warehouse: {self.warehouseid}'  # String representation of the placement entry


class DeleteRequest(models.Model):
    deleteId = models.AutoField(primary_key=True)
    userId = models.ForeignKey('Authentication.Login', on_delete=models.CASCADE)  
    productId = models.ForeignKey(Product, on_delete=models.CASCADE) 
    message = models.CharField(max_length=255)
    approverId = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=255,null=True, blank=True)
    createdtime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
    modifiedtime = models.DateTimeField(auto_now=True)  # Timestamp when last modified
    
    def __str__(self):
        return f"DeleteRequest {self.deleteId}"
    

class RequestProduct(models.Model):
    requestId = models.AutoField(primary_key=True)
    userId = models.ForeignKey(Login, on_delete=models.CASCADE)
    productId = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    approvedManagerId = models.IntegerField(null=True, blank=True)
    approvedAdminId = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=255)
    createdtime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
    modifiedtime = models.DateTimeField(auto_now=True)  # Timestamp when last modified

    def __str__(self):
        return f"RequestProduct {self.requestId}"


class Features(models.Model):
    featureId = models.AutoField(primary_key=True)
    userId = models.ForeignKey(Login, on_delete=models.CASCADE)
    stock_control = models.BooleanField(default=False)
    override_manager_approval = models.BooleanField(default=False)
    view_product_details = models.BooleanField(default=False)
    update_stock = models.BooleanField(default=False)
    delete_product = models.BooleanField(default=False)
    image_search = models.BooleanField(default=False)
    qr_scan = models.BooleanField(default=False)
    qr_generation = models.BooleanField(default=False)
    add_product = models.BooleanField(default=False)
    approval = models.BooleanField(default=False)
    request_product = models.BooleanField(default=False)
    notifications = models.BooleanField(default=False)
    raise_request = models.BooleanField(default=False)
    low_stock_items = models.BooleanField(default=False)
    expiry_date_items = models.BooleanField(default=False)

    def __str__(self):
        return f"Features {self.featureId} for User {self.userId.username}"
