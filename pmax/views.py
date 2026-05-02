from django.shortcuts import render, redirect
from django.http import HttpResponse
from pmax.models import User, Movie, Show, Review, Booking
from django.views.decorators.cache import never_cache


def home(request):
    return render(request, "./pmax/home.html")


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "./pmax/signup.html", {
                "error": "Username already exist"
            })

        User.objects.create(username=username, email=email, password=password)
        return redirect("login")

    return render(request, "./pmax/signup.html")


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username, password=password)
            request.session["user-id"] = user.id
            request.session["user-name"] = user.username
            return redirect("dashboard")
        except User.DoesNotExist:
            return render(request, "./pmax/login.html", {
                "error": "Invalid credentials"
            })

    return render(request, "./pmax/login.html")


@never_cache
def dashboard(request):
    user_id = request.session.get("user-id")

    if not user_id:
        return redirect("login")

    movies = Movie.objects.all()

    return render(request, "./pmax/dashboard.html", {
        "movies": movies
    })


@never_cache
def logout(request):
    request.session.flush()
    return redirect("login")


@never_cache
def movie_detail(request, movie_id):
    user_id = request.session.get("user-id")

    if not user_id:
        return redirect("login")

    movie = Movie.objects.get(id=movie_id)
    shows = Show.objects.filter(movie=movie)
    reviews = Review.objects.filter(movie=movie)

    if request.method == "POST":
        comment = request.POST.get("comment")
        rating = request.POST.get("rating")

        user = User.objects.get(id=user_id)

        Review.objects.create(
            movie=movie,
            user=user,
            comment=comment,
            rating=rating
        )

        return redirect(f"/movie_detail/{movie_id}")

    return render(request, "./pmax/movie_detail.html", {
        "movie": movie,
        "shows": shows,
        "reviews": reviews
    })

@never_cache
def book_show(request, show_id):
    user_id = request.session.get("user-id")

    if not user_id:
        return redirect("login")

    show = Show.objects.get(id=show_id)

    rows = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    # Get already booked seats
    bookings = Booking.objects.filter(show=show)
    booked_seats = []

    for b in bookings:
        booked_seats.extend(b.seats.split(","))

    total_seats = show.available_seats + len(booked_seats)

    seats = []
    seats_per_row = 10
    count = 0

    for row in rows:
        for num in range(1, seats_per_row + 1):
            if count >= total_seats:
                break
            seats.append(f"{row}{num}")
            count += 1
        if count >= total_seats:
            break

    if request.method == "POST":
        selected_seats = request.POST.get("selected_seats")

        if not selected_seats:
            return render(request, "./pmax/seat_selection.html", {
                "show": show,
                "booked_seats": booked_seats,
                "seats": seats,
                "error": "Please select atleast one seat"
            })

        seat_list = selected_seats.split(",")

        if len(seat_list) > show.available_seats:
            return render(request, "./pmax/seat_selection.html", {
                "show": show,
                "booked_seats": booked_seats,
                "seats": seats,
                "error": "Not enough seats"
            })

        total_price = len(seat_list) * show.price

        # ✅ STORE IN SESSION (instead of booking)
        request.session["pending_booking"] = {
            "show_id": show.id,
            "seats": selected_seats,
            "total_price": float(total_price)
        }

        return redirect("payment_page")

    return render(request, "./pmax/seat_selection.html", {
        "show": show,
        "booked_seats": booked_seats,
        "seats": seats
    })
@never_cache
def my_bookings(request):
    user_id = request.session.get("user-id")

    if not user_id:
        return redirect("login")

    bookings = Booking.objects.filter(user_id=user_id).order_by("-booking_time")

    return render(request, "./pmax/my_bookings.html", {
        "bookings": bookings
    })
    
@never_cache
def ticket_view(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return HttpResponse("Invalid Ticket")

    return render(request, "./pmax/ticket.html", {
        "booking": booking
    })
    
    
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from django.http import HttpResponse
from io import BytesIO
import qrcode

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.http import HttpResponse
from io import BytesIO
import qrcode

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.http import HttpResponse
from io import BytesIO
import qrcode


def download_ticket(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return HttpResponse("Invalid Ticket")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'ticket_{booking_id}.pdf'

    doc = SimpleDocTemplate(response)
    elements = []

    # 🔴 STYLES (Dark Theme)
    title_style = ParagraphStyle(
        name="Title",
        fontSize=22,
        textColor=colors.red,
        alignment=1,
        spaceAfter=15
    )

    movie_style = ParagraphStyle(
        name="Movie",
        fontSize=18,
        textColor=colors.whitesmoke,
        alignment=1,
        spaceAfter=20
    )

    label_style = ParagraphStyle(
        name="Label",
        fontSize=10,
        textColor=colors.grey,
    )

    value_style = ParagraphStyle(
        name="Value",
        fontSize=14,
        textColor=colors.whitesmoke,
        spaceAfter=12
    )

    # 🎬 HEADER
    elements.append(Paragraph("🎟 PMAX TICKET", title_style))
    elements.append(Paragraph(booking.show.movie.name, movie_style))

    # 🎯 DETAILS
    def field(label, value):
        elements.append(Paragraph(label, label_style))
        elements.append(Paragraph(value, value_style))

    field("Theatre", booking.show.theatre.name)
    field("Location", booking.show.theatre.location)
    field("Seats", booking.seats)
    field("Show Time", str(booking.show.show_time))
    field("Total Price", f"₹{booking.total_price}")
    field("Booking ID", str(booking.id))

    elements.append(Spacer(1, 20))

    # 🔳 QR CODE
    qr_text = f"BookingID:{booking.id};Movie:{booking.show.movie.name};Seats:{booking.seats}"
    qr = qrcode.make(qr_text)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    qr_img = Image(buffer, width=2.5*inch, height=2.5*inch)

    elements.append(qr_img)

    elements.append(Spacer(1, 20))

    elements.append(Paragraph(
        "<font color='grey'>Enjoy your show 🍿 | PMAX</font>",
        value_style
    ))

    # 🖤 DRAW DARK BACKGROUND
    def draw_bg(canvas, doc):
        canvas.setFillColorRGB(0, 0, 0)  # black
        canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1)

    doc.build(elements, onFirstPage=draw_bg, onLaterPages=draw_bg)

    return response
  
@never_cache
def payment_page(request):
    user_id = request.session.get("user-id")
    data = request.session.get("pending_booking")

    if not user_id or not data:
        return redirect("dashboard")

    show = Show.objects.get(id=data["show_id"])

    return render(request, "./pmax/payment.html", {
        "show": show,
        "seats": data["seats"],
        "total_price": data["total_price"]
    })
    
@never_cache
def confirm_payment(request):
    user_id = request.session.get("user-id")
    data = request.session.get("pending_booking")

    if not user_id or not data:
        return redirect("dashboard")

    show = Show.objects.get(id=data["show_id"])
    user = User.objects.get(id=user_id)

    seat_list = data["seats"].split(",")

    # ✅ Create booking
    booking = Booking.objects.create(
        user=user,
        show=show,
        seats=data["seats"],
        total_price=data["total_price"]
    )

    # Update seats
    show.available_seats -= len(seat_list)
    show.save()

    # 🔥 QR GENERATION (same as before)
    import qrcode
    from io import BytesIO
    import base64

    qr_text = f"🎟 Confirmed | {show.movie.name} | {show.theatre.name} | Seats: {data['seats']} | ₹{data['total_price']} | {show.show_time}"

    qr = qrcode.make(qr_text)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    # Clear session
    del request.session["pending_booking"]

    return render(request, "./pmax/success.html", {
        "show": show,
        "seats": data["seats"],
        "total_price": data["total_price"],
        "booking": booking,
        "qr_code": qr_base64
    })