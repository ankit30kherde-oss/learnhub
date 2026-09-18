from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme


def signup(request):
    next_url = request.POST.get("next") or request.GET.get("next") or reverse("dashboard")
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect("dashboard")
    else:
        form = CustomUserCreationForm()
    return render(request, "users/signup.html", {"form": form, "next": next_url})
