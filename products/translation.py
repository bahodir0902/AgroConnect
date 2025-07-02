from modeltranslation.translator import translator, TranslationOptions
from products.models import Product

class ProductTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(Product, ProductTranslationOptions)
