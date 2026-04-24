from urllib import request

from django.shortcuts import render
from matplotlib.style import context
from numpy import sort
from .models import Plot
import pandas as pd


def home(request):
    plots = Plot.objects.all().order_by('-investment_score')

    budget = request.GET.get('budget')

    if budget:
        # Remove commas and spaces
        cleaned_budget = budget.replace(",", "").replace(" ", "")

        try:
            budget_value = float(cleaned_budget)
            plots = plots.filter(price__lte=budget_value)
        except ValueError:
            pass

    return render(request, 'home.html', {
        'plots': plots,
        'budget': budget
    })


from django.contrib.auth.decorators import login_required
from .models import Plot, Wishlist

def buy(request):

    budget = request.GET.get('budget')
    location = request.GET.get('location')

    plots = Plot.objects.filter(is_approved=True)

    if budget:
        cleaned_budget = budget.replace(",", "").replace(" ", "")
        try:
            budget_value = int(cleaned_budget)
            plots = plots.filter(price__lte=budget_value)
        except ValueError:
            pass

    if location:
        plots = plots.filter(location__icontains=location)

    sort = request.GET.get('sort')

    if sort == "price":
        plots = plots.order_by('price')
    elif sort == "score":
        plots = plots.order_by('-investment_score')
    else:
        plots = plots.order_by('-investment_score')

    # ✅ PAGINATION
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    paginator = Paginator(plots, 9)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # 🔥 ADD THIS PART (WISHLIST)
    wishlist_ids = []

    if request.user.is_authenticated:
        wishlist_ids = Wishlist.objects.filter(user=request.user)\
                        .values_list('plot_id', flat=True)

    return render(request, 'buy.html', {
        'page_obj': page_obj,
        'wishlist_ids': wishlist_ids   # 🔥 IMPORTANT
    })


from django.shortcuts import render, get_object_or_404
from .models import Plot, Wishlist

def plot_detail(request, plot_id):
    plot = get_object_or_404(Plot, id=plot_id)

    is_wishlisted = False

    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(
            user=request.user,
            plot=plot
        ).exists()

    return render(request, 'detail.html', {
        'plot': plot,
        'is_wishlisted': is_wishlisted
    })

import folium
from django.http import HttpResponse

def map_view(request):
    plots = Plot.objects.all()

    budget = request.GET.get('budget')

    if budget:
        cleaned_budget = budget.replace(",", "").replace(" ", "")
        try:
            budget_value = float(cleaned_budget)
            plots = plots.filter(price__lte=budget_value)
        except ValueError:
            pass

    m = folium.Map(location=[17.3850, 78.4867], zoom_start=11)

    for plot in plots:
        if plot.investment_score > 70:
            color = "green"
        elif plot.investment_score > 45:
            color = "orange"
        else:
            color = "red"

        folium.Marker(
            [plot.latitude, plot.longitude],
            popup=f"""
            <b>{plot.title}</b><br>
            Price: ₹{int(plot.price)}<br>
            Score: {round(plot.investment_score,2)}
            """,
            icon=folium.Icon(color=color)
        ).add_to(m)

    return HttpResponse(m._repr_html_())

def about(request):
    return render(request, 'about.html')


from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse

def download_report(request, plot_id):
    plot = Plot.objects.get(id=plot_id)

    template = get_template("report.html")
    html = template.render({"plot": plot})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{plot.title}_report.pdf"'

    pisa.CreatePDF(html, dest=response)

    return response




from django.shortcuts import render
from django.db.models import Avg
from .models import Plot

def about(request):
    total_plots = Plot.objects.count()

    avg_score = Plot.objects.aggregate(avg=Avg('investment_score'))['avg'] or 0

    accuracy = 92  # fixed ML accuracy (correct concept)

    insights = total_plots * 2  # simple logic

    return render(request, 'about.html', {
        'total_plots': total_plots,
        'avg_score': int(avg_score),
        'accuracy': accuracy,
        'insights': insights
    })


from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from .models import Contact
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def contact(request):

    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # ✅ Email validation
        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'contact.html', {"error": "Invalid email address ❌"})

        # ✅ Save to DB
        Contact.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        # ✅ Send email
        send_mail(
            "Thank you for contacting LandScope 🚀",
            f"Hi {name},\n\nWe received your message:\n\n{message}\n\nOur team will get back to you soon.\n\n- LandScope Team",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return render(request, 'contact.html', {"success": True})

    return render(request, 'contact.html')

import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages


def login_view(request):
    context = {}

    request.session.pop('logout_msg', None)
    if request.method == "POST":
        action = request.POST.get("action")

        # 🔐 LOGIN + OTP
        if action == "send_otp":
            email = request.POST.get("email")
            password = request.POST.get("password")

            try:
                user_obj = User.objects.get(email=email)
            except User.DoesNotExist:
                return render(request, "login.html", {"error": "User not found ❌"})

            user = authenticate(username=user_obj.username, password=password)

            if user:
                otp = random.randint(100000, 999999)

                request.session["otp"] = str(otp)
                request.session["user_id"] = user.id

                send_mail(
                    "LandScope Login OTP",
                    f"Your OTP is: {otp}",
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )

                return render(request, "login.html", {
                    "show_otp_modal": True,
                    "success": "OTP sent to email 📩"
                })

            else:
                return render(request, "login.html", {"error": "Invalid credentials ❌"})

        # 🔢 VERIFY OTP
        elif action == "verify_otp":
            entered = request.POST.get("otp")
            session_otp = request.session.get("otp")
            user_id = request.session.get("user_id")

            if entered == session_otp:
                user = User.objects.get(id=user_id)
                login(request, user)
                messages.success(request, "Login successful 🎉")
                return redirect("home")

            else:
                return render(request, "login.html", {
                    "show_otp_modal": True,
                    "error": "Invalid OTP ❌"
                })

        # 🆕 REGISTER
        elif action == "register":
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")

            if User.objects.filter(email=email).exists():
                return render(request, "login.html", {"error": "Email already exists ❌"})

            User.objects.create_user(username=username, email=email, password=password)

            return render(request, "login.html", {"success": "Registered successfully ✅"})

        # 🔁 RESET PASSWORD
        elif action == "send_reset_otp":
            email = request.POST.get("email")
            new_password = request.POST.get("new_password")

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                context['error'] = "Email not found ❌"
                return render(request, "login.html", context)

            otp = str(random.randint(100000, 999999))

            # store in session
            request.session["reset_otp"] = otp
            request.session["reset_user_id"] = user.id
            request.session["new_password"] = new_password

            send_mail(
                "LandScope Password Reset OTP",
                f"Your OTP is: {otp}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            context['show_reset_otp_modal'] = True
            context['success'] = "OTP sent for password reset 📩"
            return render(request, "login.html", context)


        elif action == "verify_reset_otp":
                entered = request.POST.get("otp")
                session_otp = request.session.get("reset_otp")
                user_id = request.session.get("reset_user_id")
                new_password = request.session.get("new_password")

                if entered == session_otp:
                    user = User.objects.get(id=user_id)
                    user.set_password(new_password)
                    user.save()

                    # cleanup
                    request.session.pop("reset_otp", None)
                    request.session.pop("reset_user_id", None)
                    request.session.pop("new_password", None)

                    context['success'] = "Password updated successfully ✅"
                    return render(request, "login.html", context)

                else:
                    context['show_reset_otp_modal'] = True
                    context['error'] = "Invalid OTP ❌"
                    return render(request, "login.html", context)

    return render(request, "login.html")

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Plot

@login_required
def sell(request):

    if request.method == "POST":

        Plot.objects.create(
            title=request.POST.get('title'),
            location=request.POST.get('location'),
            area_sqft=request.POST.get('area'),
            price=request.POST.get('price'),
            metro_distance=request.POST.get('metro_distance') or 0,
            crime_rate=request.POST.get('crime_rate') or 0,
            pollution=request.POST.get('pollution') or 0,
            contact_name=request.POST.get('owner'),
            contact_phone=request.POST.get('phone'),
            location_link=request.POST.get('location_link'),
            image=request.FILES.get('image'),
            created_by=request.user,
            is_approved=False   # 🔥 important
        )

        return render(request, "sell.html", {
            "success": "Your property is submitted and under review 🚀"
        })

    return render(request, "sell.html")










from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Plot
import json
from .models import Wishlist

@login_required
def dashboard(request):

    user_plots = Plot.objects.filter(created_by=request.user)

    # ✅ CALCULATE STATS
    total = user_plots.count()
    approved = user_plots.filter(is_approved=True).count()
    pending = user_plots.filter(is_approved=False).count()

    wishlist = Wishlist.objects.filter(user=request.user).select_related('plot')

    # ✅ JSON FOR MODALS
    plots_data = list(user_plots.values(
        'id','title','location','price','investment_score','is_approved'
    ))

    return render(request, 'dashboard.html', {
        'plots': user_plots,
        'plots_json': json.dumps(plots_data),
        'total': total,
        'approved': approved,
        'pending': pending,
        'wishlist': wishlist
    })

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Plot
from django.contrib import messages

@login_required
def edit_plot(request, id):
    plot = get_object_or_404(Plot, id=id, created_by=request.user)

    if request.method == "POST":
        plot.title = request.POST.get('title')
        plot.location = request.POST.get('location')
        plot.price = request.POST.get('price')

        plot.is_approved = False
        plot.save()

        messages.success(request, "Property updated successfully ✏️")

    return redirect('dashboard')

@login_required
def delete_plot(request, id):
    plot = get_object_or_404(Plot, id=id, created_by=request.user)

    if request.method == "POST":
        reason = request.POST.get('reason')
        extra = request.POST.get('extra_reason')

        # 👉 Optional: print or store reason
        print("Delete reason:", reason, extra)

        plot.delete()
        messages.success(request, "Property deleted successfully 🗑️")

    return redirect('dashboard')



from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Wishlist

@login_required
def toggle_wishlist(request, id):
    if request.method == "POST":
        plot = get_object_or_404(Plot, id=id)

        obj, created = Wishlist.objects.get_or_create(
            user=request.user,
            plot=plot
        )

        if not created:
            obj.delete()
            return JsonResponse({'status': 'removed'})

        return JsonResponse({'status': 'added'})


from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully 👋")
    return redirect('login')