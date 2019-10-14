from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Section(models.Model):
    name = models.CharField(max_length=128, verbose_name='Наименование раздела')
    slug = models.SlugField(max_length=128, unique=True)

    class Meta:
        verbose_name = 'Раздел'
        verbose_name_plural = 'Разделы'

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=128, verbose_name='Наименование категории')
    section = models.ForeignKey(Section, related_name='categories', on_delete=models.PROTECT, verbose_name='Раздел')
    slug = models.SlugField(max_length=128, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=128, verbose_name='Наименование')
    category = models.ForeignKey(Category, related_name='products', on_delete=models.PROTECT, verbose_name='Категория')
    slug = models.SlugField(max_length=128, unique=True)
    image = models.ImageField(upload_to='img/products/', blank=True, verbose_name='Изображение')
    description = models.CharField(max_length=256, verbose_name='Описание')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

class Article(models.Model):
    name = models.CharField(max_length=128, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Основной текст')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    products = models.ManyToManyField(Product, verbose_name='Товары', blank=True)

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def __str__(self):
        return self.name

class Review(models.Model):
    product = models.ForeignKey(Product,related_name='reviews', on_delete=models.PROTECT, verbose_name='Товар')
    name = models.CharField(max_length=128, verbose_name='Имя')
    content = models.TextField(verbose_name='Отзыв', default=False)
    rating = models.PositiveSmallIntegerField(verbose_name='Рейтинг')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'{self.name} {self.content[:30]}'

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'

    def __str__(self):
        return self.user.email

    @receiver(post_save, sender=User)
    def create_user_customer(sender, instance, created, **kwargs):
        if created and instance.email:
            Customer.objects.create(user=instance)


class Order(models.Model):
    customer = models.ForeignKey(Customer, related_name='customer', on_delete=models.CASCADE, verbose_name='Покупатель')
    products = models.ManyToManyField(Product, verbose_name='Товары', blank=True, through='ProductsInOrder')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.customer} - {self.created}'


class ProductsInOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Товар', related_name='count_in_order',)
    quantity = models.PositiveSmallIntegerField(verbose_name='Количество товара в заказе')