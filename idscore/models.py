from django.db import models
from django.contrib.postgres.fields import ArrayField
from Authentication.models import Login

# Model for product categories
class Category(models.Model):
    categoryId = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    name = models.CharField(max_length=255, unique=True)  # Name of the category
    image = models.URLField(null=True, blank=True)  # URL field to store image
    rowstatus = models.BooleanField(default=True)  # Boolean field for row status

# Model for products
class Product(models.Model):
    productId = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    productCode = models.CharField(max_length=100)  # Product code
    qrCode = models.TextField()  # QR code for the product
    productName = models.CharField(max_length=255)  # Name of the product
    productDescription = models.TextField()  # Description of the product
    productCategory = models.IntegerField()  # Category ID for the product
    reOrderPoint = models.IntegerField()  # Reorder point quantity
    brand = models.CharField(max_length=100)  # Brand name of the product
    weight = models.CharField(max_length=50)  # Weight of the product
    dimensions = models.CharField(max_length=100)  # Dimensions of the product
    images = models.JSONField()  # JSON field to store multiple images
    createdUser = models.CharField(max_length=100)  # User who created the product
    modifiedUser = models.CharField(max_length=100)  # User who last modified the product
    createdTime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
    modifiedTime = models.DateTimeField(auto_now=True)  # Timestamp when last modified
    rowstatus = models.BooleanField(default=True)  # Boolean field for row status

    def __str__(self):
        return self.productName  # String representation of the product
    
# Model for inventory
class Inventory(models.Model):
    inventoryId = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    productId = models.ForeignKey(Product, on_delete=models.CASCADE)  # Foreign key to Product table
    quantityAvailable = models.CharField(max_length=50,null=True, blank=True)  # Available quantity in inventory
    minStockLevel = models.CharField(max_length=50,null=True, blank=True)  # Minimum stock level
    maxStockLevel = models.CharField(max_length=50,null=True, blank=True)  # Maximum stock level
    invreOrderPoint = models.IntegerField(null=True, blank=True)  # Allow null values
    warehouseId = models.ForeignKey('Warehouse', on_delete=models.CASCADE)  # Foreign key to Warehouse table
    createdUser = models.CharField(max_length=100)  # User who created the inventory entry
    modifiedUser = models.CharField(max_length=100)  # User who last modified the inventory entry
    createdTime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
    modifiedTime = models.DateTimeField(auto_now=True)  # Timestamp when last modified
    rowstatus = models.BooleanField(default=True)  # Boolean field for row status

    def __str__(self):
        return f"Inventory for {self.productId.productName}"  # String representation of the inventory entry

    


# Model for warehouses
class Warehouse(models.Model):
    warehouseId = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    locationId = models.ForeignKey('Location', on_delete=models.CASCADE)  # Foreign key to Location table
    warehouseName = models.CharField(max_length=255)  # Name of the warehouse
    createdUser = models.CharField(max_length=100)  # User who created the warehouse
    modifiedUser = models.CharField(max_length=100)  # User who last modified the warehouse
    createdTime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
    modifiedTime = models.DateTimeField(auto_now=True)  # Timestamp when last modified
    rowstatus = models.BooleanField(default=True)  # Boolean field for row status

    def __str__(self):
        return self.warehouseName  # String representation of the warehouse

# Model for locations
class Location(models.Model):
    locationId = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    locationName = models.CharField(max_length=255)  # Name of the location
    locationAddress = models.TextField()  # Address of the location
    createdUser = models.CharField(max_length=100)  # User who created the location
    modifiedUser = models.CharField(max_length=100)  # User who last modified the location
    createdTime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
    modifiedTime = models.DateTimeField(auto_now=True)  # Timestamp when last modified
    rowstatus = models.BooleanField(default=True)  # Boolean field for row status

    def __str__(self):
        return self.locationName  # String representation of the location

# # Model for batches of products
class Batch(models.Model):
    batchId = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    productId = models.ForeignKey(Product, on_delete=models.CASCADE)  # Foreign key to Product table
    manufactureDate = models.DateField(null=True)  # Date of batch manufacturing
    expiryDate = models.DateField(null=True, blank=True)  # Expiry date of the batch
    quantity = models.CharField()  # Quantity of products in the batch
    createdUser = models.CharField(max_length=100)  # User who created the batch
    modifiedUser = models.CharField(max_length=100)  # User who last modified the batch
    createdTime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
    modifiedTime = models.DateTimeField(auto_now=True)  # Timestamp when last modified
    rowstatus = models.BooleanField(default=True)  # Boolean field for row status

    def __str__(self):
        return f'Batch {self.batchId} for {self.productId}'  # String representation of the batch

# Model for placement of products in warehouses
class Placement(models.Model):
    placementId = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    batchId = models.ForeignKey(Batch, on_delete=models.CASCADE)
    productId = models.ForeignKey(Product, on_delete=models.CASCADE)  # Foreign key to Product table
    warehouseId = models.ForeignKey(Warehouse, on_delete=models.CASCADE)  # Foreign key to Warehouse table
    placementQuantity = models.IntegerField() 
    aile = models.CharField(max_length=50)  # Aisle where the product is placed
    bin = models.CharField(max_length=50)  # Bin where the product is placed
    createdUser = models.CharField(max_length=100)  # User who created the placement entry
    modifiedUser = models.CharField(max_length=100)  # User who last modified the placement entry
    createdTime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
    modifiedTime = models.DateTimeField(auto_now=True)  # Timestamp when last modified
    rowstatus = models.BooleanField(default=True)  # Boolean field for row status

    def __str__(self):
        return f'Placement {self.placementId} - Product: {self.productId}, Warehouse: {self.warehouseId}'  # String representation of the placement entry


class DeleteRequest(models.Model):
    deleteId = models.AutoField(primary_key=True)
    userId = models.ForeignKey('Authentication.Login', on_delete=models.CASCADE)  
    productId = models.ForeignKey(Product, on_delete=models.CASCADE) 
    message = models.CharField(max_length=255)
    approverId = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=255,null=True, blank=True)
    createdTime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
    modifiedTime = models.DateTimeField(auto_now=True)  # Timestamp when last modified
    
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
    createdTime = models.DateTimeField(auto_now_add=True)  # Timestamp when created
    modifiedTime = models.DateTimeField(auto_now=True)  # Timestamp when last modified

    def __str__(self):
        return f"RequestProduct {self.requestId}"


class Features(models.Model):
    featureId = models.AutoField(primary_key=True)
    userId = models.ForeignKey(Login, on_delete=models.CASCADE)
    stockControl = models.BooleanField(default=False)
    overrideManagerApproval = models.BooleanField(default=False)
    viewProductDetails = models.BooleanField(default=False)
    updateStock = models.BooleanField(default=False)
    deleteProduct = models.BooleanField(default=False)
    imageSearch = models.BooleanField(default=False)
    qrScan = models.BooleanField(default=False)
    qrGeneration = models.BooleanField(default=False)
    addProduct = models.BooleanField(default=False)
    approval = models.BooleanField(default=False)
    requestProduct = models.BooleanField(default=False)
    notifications = models.BooleanField(default=False)
    raiseRequest = models.BooleanField(default=False)
    lowStockItems = models.BooleanField(default=False)
    expiryDateItems = models.BooleanField(default=False)

    def __str__(self):
        return f"Features {self.featureId} for User {self.userId.username}"
