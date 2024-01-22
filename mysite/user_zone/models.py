from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    # Create user
    def create_user(self, email, password):
        print(self.model)
        if email and password:
            user = self.model(email=self.normalize_email(email))
            user.set_password(password)
            user.save()
        return user
    # Create admin
    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_admin = True
        user.save()
        return user

class User(AbstractBaseUser):
    # Storage of users
    email = models.EmailField(max_length=300, unique=True, verbose_name="Email")
    is_admin = models.BooleanField(default=False, verbose_name="Admin")

    class Meta:
        verbose_name = "Uživatel"
        verbose_name_plural = "Uživatelé"

    objects = UserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return "{}".format(self.email)

    @property
    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

class GeneralData(models.Model):
    # Storage of general data of users
    user = models.ForeignKey(User, on_delete=models.RESTRICT, verbose_name="Email")
    name = models.CharField(max_length=200, verbose_name="Jméno")
    surname = models.CharField(max_length=200, verbose_name="Příjmení")
    telephone_number = models.CharField(max_length=200, verbose_name="Telefon")
    company_name = models.CharField(max_length=200, verbose_name="Název firmy")
    register_id = models.CharField(max_length=200, verbose_name="IČO")
    vat_id = models.CharField(max_length=200, verbose_name="DIČ")
    street = models.CharField(max_length=200, verbose_name="Ulice")
    building_number = models.CharField(max_length=200, verbose_name="Číslo popisné")
    zip_code = models.CharField(max_length=200, verbose_name="PSČ")
    city = models.CharField(max_length=200, verbose_name="Město")
    country = models.CharField(max_length=200, verbose_name="Země")

    class Meta:
        verbose_name = "Email"
        verbose_name_plural = "Osobní údaje"

    def __str__(self):
        return "{}".format(self.user)

class ProductProperty(models.Model):
    # Storage of products properties

    # Setting the LICENCE_DURATION_CHOICES
    ONE_YEAR = "1 rok"
    THREE_MONTHS = "3 měsíce"

    LICENCE_DURATION_CHOICES = [(ONE_YEAR, "1 rok"), (THREE_MONTHS, "3 měsíce")]

    # Setting model fields
    product_id = models.CharField(max_length=200, verbose_name="ID produktu")
    product_name = models.CharField(max_length=200, verbose_name="Název produktu")
    licence_duration = models.CharField(max_length=200, verbose_name="Trvání licence", choices=LICENCE_DURATION_CHOICES,
                                        blank=True, null=True)
    price = models.CharField(max_length=200, verbose_name="Cena", blank=True, null=True)

    class Meta:
        verbose_name = "Produkt"
        verbose_name_plural = "Produkty"

class PurchaseOrder(models.Model):
    # Storage of all products sold
    user = models.ForeignKey(User, on_delete=models.RESTRICT, verbose_name="Email")
    product_name = models.ForeignKey(ProductProperty, on_delete=models.RESTRICT, verbose_name="Produkt")
    order_date = models.DateTimeField(verbose_name="Datum objednávky")
    payment_date = models.DateTimeField(blank=True, null=True, verbose_name="Datum platby")
    license_expiration_date = models.DateTimeField(blank=True, null=True, verbose_name="Datum expirace licence")
    last_license_validation_date = models.DateTimeField(blank=True, null=True,
                                                        verbose_name="Datum posledního ověření licence")
    licence_duration = models.CharField(max_length=200, verbose_name="Trvání licence", blank=True, null=True)
    price = models.CharField(max_length=200, verbose_name="Cena", blank=True, null=True)

    class Meta:
        verbose_name = "Prodej produktu"
        verbose_name_plural = "Prodeje produktů"

class Visit(models.Model):
    # Records of pages visited
    # Not all pages are recorded. Only those relevant for marketing purposes.
    user = models.ForeignKey(User, on_delete=models.RESTRICT, verbose_name="Email", blank=True, null=True)
    path = models.CharField(max_length=200, verbose_name="Cesta", blank=True, null=True)
    visit_date = models.DateTimeField(blank=True, null=True, verbose_name="Datum návštěvy")

    class Meta:
        verbose_name = "Návštěva"
        verbose_name_plural = "Návštěvy"
