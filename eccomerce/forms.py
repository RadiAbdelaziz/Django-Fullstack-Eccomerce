from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'stock_quantity', 'category', 'brand', 'tags', 'discount']
