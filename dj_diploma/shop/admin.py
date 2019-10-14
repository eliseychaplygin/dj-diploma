from django.contrib import admin

from .models import Article, Section, Category, Product, Review, Customer, Order, ProductsInOrder


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('name', 'created')

class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'slug',)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description', 'slug',)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'rating', 'created')

class ProductsInOrderInline(admin.TabularInline):
    model = ProductsInOrder

    verbose_name = 'Заказанный товар'
    verbose_name_plural = 'Заказанные товары'


class OrderAdmin(admin.ModelAdmin):
    ordering = ('created',)
    list_display = ('customer', 'quantity', 'created', )

    inlines = (ProductsInOrderInline,)

    def quantity(self, obj):
        return ProductsInOrder.objects.filter(order=obj).count()

    quantity.short_description = 'Количество позиций'


admin.site.register(Article, ArticleAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Customer)