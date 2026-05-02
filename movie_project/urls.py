from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# ✅ import ALL views (including new one)
from pmax.views import (
    home,
    signup,
    login,
    dashboard,
    logout,
    movie_detail,
    book_show,
    my_bookings,
    ticket_view,
    download_ticket,
    payment_page,
    confirm_payment
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path("", home, name="home"),
    path("signup/", signup, name="signup"),
    path("login/", login, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", logout, name="logout"),

    path("movie_detail/<int:movie_id>/", movie_detail, name="movie_detail"),
    path("book_show/<int:show_id>/", book_show, name="book_show"),

    # ✅ NEW ROUTE
    path("my_bookings/", my_bookings, name="my_bookings"),
    path("ticket/<int:booking_id>/", ticket_view, name="ticket_view"),
    path("download_ticket/<int:booking_id>/", download_ticket, name="download_ticket"),
    path("payment/", payment_page, name="payment_page"),
path("confirm_payment/", confirm_payment, name="confirm_payment"),
]

# media files (images)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)