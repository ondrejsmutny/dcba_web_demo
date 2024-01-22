import datetime
import os

from django.shortcuts import render, redirect, reverse
from django.views import generic
from .models import User, GeneralData, ProductProperty, PurchaseOrder, Visit
from .forms import NewUserForm, LoginUserForm, SetPasswordUserForm, UserForm, LoginForm, GeneralDataForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from .tables import GeneralDataTable
from .filters import GeneralDataFilter
from django_tables2.config import RequestConfig
from django.core.mail import EmailMessage, get_connection
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib.auth.views import PasswordResetConfirmView
from secret_keys import secret_keys
from django.utils import timezone
from django.conf import settings


# Visitors counter #####################################################################################################
def create_visit_record(request, path):
    '''
    Creates record of visited page

    Requires:
        request, instance: Instance of request from web
        path, str: Path of page visited
    '''
    # Getting user
    if request.user.is_authenticated:
        user = request.user
    else:
        user = None

    # Getting visit date
    now_date = datetime.datetime.now()
    visit_date = now_date.replace(microsecond=0)

    # Creating visit
    visit = Visit(user=user, path=path, visit_date=visit_date)
    visit.save()


# Services #############################################################################################################
def services(request):
    # Redirecting to services page
    create_visit_record(request, "user_zone/services.html")
    return render(request, "user_zone/services.html")


# Products #############################################################################################################
def handle_purchase_order(product_id, request):
    '''
    Handles purchase order workflow based on request from web. Saves purchase order to database. Sends email with
    instruction to users.

    Requires:
        product_id, str: Identification of product passed from web
        request, instance: Instance of request from web
    '''
    # Getting values for purchase order
    product_property = ProductProperty.objects.filter(product_id=product_id)
    product_name = product_property[0]

    now_date = datetime.datetime.now()
    order_date = now_date.replace(microsecond=0)

    product_property_values = ProductProperty.objects.filter(product_id=product_id).values()
    licence_duration = product_property_values[0]["licence_duration"]
    price = product_property_values[0]["price"]

    # Creating purchase order
    purchase_order = PurchaseOrder(
        user=request.user,
        product_name=product_name,
        order_date=order_date,
        payment_date=None,
        license_expiration_date=order_date,
        last_license_validation_date=None,
        licence_duration=licence_duration,
        price=price
    )
    purchase_order.save()

    # Getting information for email
    purchase_order_info = PurchaseOrder.objects.filter(user=request.user).values()
    purchase_order_info = purchase_order_info.order_by("-id")

    purchase_order_number = purchase_order_info[0]["id"]
    product_name_id = purchase_order_info[0]["product_name_id"]

    product_property_info = ProductProperty.objects.filter(id=product_name_id).values()
    product_name_info = product_property_info[0]["product_name"]
    licence_duration_info = product_property_info[0]["licence_duration"]
    price_info = product_property_info[0]["price"]

    # Sending email with purchase order and payment details
    email_template_name = "user_zone/purchase_order_email.txt"
    c = {
        'email': request.user.email,
        # 'domain': '127.0.0.1:8000',  # For mirror
        'domain': 'dcba.cz',  # For production
        'site_name': 'Website',
        "uid": urlsafe_base64_encode(force_bytes(request.user.pk)),
        "user": request.user,
        'token': default_token_generator.make_token(request.user),
        'protocol': 'http',
        'purchase_order_number': purchase_order_number,
        'product_name_info': product_name_info,
        'licence_duration_info': licence_duration_info,
        'price_info': price_info
    }

    subject = f"Objednávka číslo {purchase_order_number} produktu {product_name_info}"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [request.user.email]
    message = render_to_string(email_template_name, c)

    with get_connection(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS
    ) as connection:
        EmailMessage(subject, message, email_from, recipient_list, connection=connection).send()


def download_file(file_name):
    '''
    Handles download request from user and returns desired file download

    Requires:
        file_name, str: Passed name of file to be downloaded

    Returns:
        response, instance: Instance of response containing file to be downloaded
    '''
    current_path = os.getcwd()
    file_path = f"{current_path}/user_zone/files_download/{file_name}"

    with open(file_path, "rb") as file_download:
        response = HttpResponse(file_download.read())
        response["Content-Disposition"] = f"attachment; filename={file_name}"
    file_download.close()

    return response

def pdf_view(file_name):
    '''
    Handles PDF view request from user and returns desired PDF view

    Requires:
        file_name, str: Passed name of PDF file to be viewed

    Returns:
        response, instance: Instance of response containing PDF file to be viewed
    '''
    current_path = os.getcwd()
    file_path = f"{current_path}/user_zone/files_download/{file_name}"

    with open(file_path, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline;filename={file_name}'
    pdf.close()

    return response

def products(request):
    # Redirecting to products page

    # Button clicked
    if request.method == 'POST':
        if 'StatS_2023_quarter_P_6_04_a_manual.pdf' in request.POST:
            response = pdf_view('StatS_2023_quarter_P_6_04_a_manual.pdf')
            create_visit_record(request, 'StatS_2023_quarter_P_6_04_a_manual.pdf')
            return response

        if request.user.is_authenticated:
            if '2023_quarter_P_6_04_a_one_year' in request.POST:
                handle_purchase_order('2023_quarter_P_6_04_a_one_year', request)
                return render(request, "user_zone/purchase_order_complete.html")
            if '2023_quarter_P_6_04_a_three_months' in request.POST:
                handle_purchase_order('2023_quarter_P_6_04_a_three_months', request)
                return render(request, "user_zone/purchase_order_complete.html")
            if 'StatS_2023_quarter_P_6_04_a.zip' in request.POST:
                response = download_file('StatS_2023_quarter_P_6_04_a.zip')
                create_visit_record(request, 'StatS_2023_quarter_P_6_04_a.zip')
                return response

        else:
            messages.info(request, "Pro objednání se prosím přihlašte.")
            return redirect(reverse("products"))

    create_visit_record(request, "user_zone/products.html")
    return render(request, "user_zone/products.html")


# Users ################################################################################################################
def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registrace byla úspěšná.")

            # Creating first blank record for this user in GeneralData
            user_general_data = GeneralData(
                user=request.user,
                name="",
                surname="",
                telephone_number="",
                company_name="",
                register_id="",
                vat_id="",
                street="",
                building_number="",
                zip_code="",
                city="",
                country=""
            )
            user_general_data.save()

            return redirect("edit_general_data")
        else:
            email = form.data.get("email")
            email_exists = User.objects.filter(email=email).exists()
            password1 = form.cleaned_data.get("password1")
            password2 = form.cleaned_data.get("password2")
            if email_exists:
                messages.error(request, "Email je již obsazen. Zkuste prosím jiný.")
            elif password1 != password2:
                messages.error(request, "Zadaná hesla nejsou stejná.")
            else:
                messages.error(request, "Neúspěšná registrace. Neplatné informace.")
    form = NewUserForm()
    create_visit_record(request, "user_zone/register.html")
    return render(request=request, template_name="user_zone/register.html", context={"register_form": form})


def login_request(request):
    if request.method == "POST":
        form = LoginUserForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("index")
            else:
                messages.error(request, "Neplatný email nebo heslo.")
        else:
            messages.error(request, "Neplatný email nebo heslo.")
    form = LoginUserForm()
    create_visit_record(request, "user_zone/login.html")
    return render(request=request, template_name="user_zone/login.html", context={"login_form": form})


class UserViewRegister(generic.edit.CreateView):
    '''
    Old registration of new user
    '''
    form_class = UserForm
    model = User
    template_name = "user_zone/login.html"

    def get(self, request):
        # Getting blank template
        if request.user.is_authenticated:
            messages.info(request, "Už jsi přihlášený, nemůžeš se registrovat.")
            return redirect(reverse("index"))
        else:
            form = self.form_class(None)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        # Posting new data
        if request.user.is_authenticated:
            messages.info(request, "Už jsi přihlášený, nemůžeš se registrovat.")
            return redirect(reverse("index"))
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data["password"]
            user.set_password(password)
            user.save()
            login(request, user)
            return redirect("index")

        return render(request, self.template_name, {"form": form})


class UserViewLogin(generic.edit.CreateView):
    '''
    Old login existing user
    '''
    form_class = LoginForm
    template_name = "user_zone/login.html"

    def get(self, request):
        # Getting blank template
        if request.user.is_authenticated:
            messages.info(request, "Už jsi přihlášený, nemůžeš se přihlásit znovu.")
            return redirect(reverse("index"))
        else:
            form = self.form_class(None)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        # Posting new data
        if request.user.is_authenticated:
            messages.info(request, "Už jsi přihlášený, nemůžeš se přihlásit znovu.")
            return redirect(reverse("index"))
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                return redirect("index")
            else:
                messages.error(request, "Tento účet neexistuje.")
        return render(request, self.template_name, {"form": form})


def logout_request(request):
    # Logout user logged in
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "Byli jste úspěšně odhlášeni.")
    else:
        messages.info(request, "Nemůžeš se odhlásit, pokud nejsi přihlášený.")
    return redirect(reverse("index"))


class PasswordResetConfirmUserView(PasswordResetConfirmView):
    template_name = "user_zone/password_reset_confirm.html"
    form_class = SetPasswordUserForm


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    c = {
                        "email": user.email,
                        # 'domain': '127.0.0.1:8000',  # For mirror
                        'domain': 'dcba.cz',  # For production
                        'site_name': 'D_C_B_A',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email_template_name = "user_zone/password_reset_email.txt"

                    subject = "Požadavek na změnu hesla"
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [user.email]
                    message = render_to_string(email_template_name, c)

                    with get_connection(
                        host=settings.EMAIL_HOST,
                        port=settings.EMAIL_PORT,
                        username=settings.EMAIL_HOST_USER,
                        password=settings.EMAIL_HOST_PASSWORD,
                        use_tls=settings.EMAIL_USE_TLS
                    ) as connection:
                        EmailMessage(subject, message, email_from, recipient_list, connection=connection).send()

                    return redirect("password_reset/done/")
            else:
                messages.error(request, "Email není zaregistrovaný. Přejděte prosím k registraci.")
    password_reset_form = PasswordResetForm()
    create_visit_record(request, "user_zone/password_reset.html")
    return render(request=request, template_name="user_zone/password_reset.html",
                  context={"password_reset_form": password_reset_form})


class GeneralDataFilterView(SingleTableMixin, FilterView):
    # Show user list from table with lookup and filter functionality
    model = GeneralData
    table_class = GeneralDataTable
    template_name = "user_zone/general_data_list.html"
    filterset_class = GeneralDataFilter

    def get_table(self):
        # Getting table from model with is-admin authentication
        if self.request.user.is_admin:
            table_class = self.get_table_class()
            table = table_class(data=self.get_table_data())
            return RequestConfig(self.request, paginate=self.get_table_pagination(table)).configure(
                table
            )
        else:
            raise ValueError("Na tuto stránku má přístup jen administrátor!")


class EditGeneralData(generic.edit.UpdateView):
    # Edit general data for existing user
    form_class = GeneralDataForm
    template_name = "user_zone/edit_general_data.html"

    def get(self, request):
        # Getting form prefilled with data #############################################################################
        form = self.form_class(None)
        user_general_data = form.Meta.model.objects.filter(user=request.user).values()
        user_general_data = user_general_data.order_by("-id")

        # Prefilling data
        form.fields["name"].initial = user_general_data[0]["name"]
        form.fields["surname"].initial = user_general_data[0]["surname"]
        form.fields["telephone_number"].initial = user_general_data[0]["telephone_number"]
        form.fields["company_name"].initial = user_general_data[0]["company_name"]
        form.fields["register_id"].initial = user_general_data[0]["register_id"]
        form.fields["vat_id"].initial = user_general_data[0]["vat_id"]
        form.fields["street"].initial = user_general_data[0]["street"]
        form.fields["building_number"].initial = user_general_data[0]["building_number"]
        form.fields["zip_code"].initial = user_general_data[0]["zip_code"]
        form.fields["city"].initial = user_general_data[0]["city"]
        form.fields["country"].initial = user_general_data[0]["country"]

        # For User field only possible choice is authenticated user
        choices = list(form.fields["user"].choices)
        new_choices = list()
        for choice in choices:
            if not isinstance(choice[0], str):
                if choice[0].instance == request.user:
                    new_choices.append(choice)
        form.fields["user"].widget.choices = new_choices

        create_visit_record(request, self.template_name)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        # Posting new data
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save(commit=True)
            messages.info(request, "Osobní údaje byly změněny.")
        return redirect("index")


def login_external_request(request):
    '''
    Handles request from external application in order to check if user can be logged in. Checks if user exists, if user
    is authenticated and if users license for application is valid.

    Requires:
        request, instance: Instance of request from web

    Returns:
        response, instance: Instance of response of web
    '''
    # Setting decryption
    KEY = b'AAA='

    # Setting response
    response = HttpResponse()

    if request.method == "GET":
        # Getting credentials from request
        username_encrypted = request.GET.get("username_encrypted")
        password_encrypted = request.GET.get("password_encrypted")
        username_key_filename = request.GET.get("username_key_filename")
        password_key_filename = request.GET.get("password_key_filename")

        username = secret_keys.decrypt_message_with_key(username_encrypted, KEY, username_key_filename)
        password = secret_keys.decrypt_message_with_key(password_encrypted, KEY, password_key_filename)
        product_name = request.GET.get("product_name")

        user_exists = False
        user_is_authenticated = False
        licence_is_valid = False

        # User exists
        check_user = User.objects.filter(email=username).values()
        if check_user.count() > 0:
            if check_user[0]["email"] == username:
                user_exists = True

                # User is authenticated
                user = authenticate(username=username, password=password)
                if user is not None:
                    user_is_authenticated = user.is_authenticated

                    # License is valid
                    now_date = timezone.localtime()
                    product_collection = ProductProperty.objects.filter(product_name=product_name)

                    for product in product_collection:
                        check_licence = PurchaseOrder.objects.filter(user=user, product_name=product).values()
                        if check_licence.count() > 0:
                            check_licence = check_licence.order_by("-license_expiration_date")
                            license_expiration_date_latest = check_licence[0]["license_expiration_date"]

                            if license_expiration_date_latest is not None:
                                # Update last licence validation date on checked row
                                license_expiration_date_latest_id = check_licence[0]["id"]
                                PurchaseOrder.objects.filter(id=license_expiration_date_latest_id).update(
                                    last_license_validation_date=now_date)

                                # Checking licence validity
                                if now_date <= license_expiration_date_latest:
                                    licence_is_valid = True

        # Filling response
        response["user_exists"] = user_exists
        response["user_is_authenticated"] = user_is_authenticated
        response["licence_is_valid"] = licence_is_valid

    return response
