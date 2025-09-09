from django.contrib import admin


# Register your models here.
from django.contrib import admin
from .models import Category, Brand, Product, ProductImage, Tag
from django.contrib import admin
from .models import Product, Category, Tag, Brand, ProductImage

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'price', 'is_featured', 'is_approved']
    list_filter = ['is_featured', 'is_approved', 'category']
    search_fields = ['title', 'description']
    actions = ['approve_products', 'reject_products', 'mark_as_featured']

    def approve_products(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Selected products have been approved.")
    
    def reject_products(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, "Selected products have been rejected.")

    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, "Selected products marked as featured.")

    approve_products.short_description = "✅ Approve selected products"
    reject_products.short_description = "❌ Reject selected products"
    mark_as_featured.short_description = "⭐ Mark as featured"

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Brand)
admin.site.register(ProductImage)
