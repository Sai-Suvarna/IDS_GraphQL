from django.db import models
from django.contrib.postgres.fields import ArrayField

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
    minstocklevel = models.CharField(max_length=50)  # Minimum stock level
    maxstocklevel = models.CharField(max_length=50)  # Maximum stock level
    invreorderpoint = models.IntegerField()  # Reorder point for the product
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

# Model for batches of products
class Batch(models.Model):
    batchid = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    productid = models.ForeignKey(Product, on_delete=models.CASCADE)  # Foreign key to Product table
    manufacturedate = models.DateField(null=True, blank=True)  # Date of batch manufacturing
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
    productid = models.ForeignKey(Product, on_delete=models.CASCADE)  # Foreign key to Product table
    warehouseid = models.ForeignKey(Warehouse, on_delete=models.CASCADE)  # Foreign key to Warehouse table
    aile = models.CharField(max_length=50)  # Aisle where the product is placed
    bin = models.CharField(max_length=50)  # Bin where the product is placed
    batchid = models.ForeignKey(Batch, on_delete=models.CASCADE)  # Foreign key to Batch table
    createduser = models.CharField(max_length=100)  # User who created the placement entry
    modifieduser = models.CharField(max_length=100)  # User who last modified the placement entry
    createdtime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
    modifiedtime = models.DateTimeField(auto_now=True)  # Timestamp when last modified
    rowstatus = models.BooleanField(default=True)  # Boolean field for row status

    def __str__(self):
        return f'Placement {self.placementId} - Product: {self.productid}, Warehouse: {self.warehouseid}'  # String representation of the placement entry
