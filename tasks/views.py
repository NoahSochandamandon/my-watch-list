import requests
import uuid
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
import urllib.parse

# Create your views here.


@login_required(login_url="login")
def import_from_tmdb(request, provider_id):
    added_count = 0
    page = 1

    providers_names = {8: "Netflix", 119: "Amazon Prime", 350: "Apple TV+"}
    platform_name = providers_names.get(provider_id, "Inconnu")

    headers = {
        "Authorization": f"Bearer {settings.TMDB_API_KEY}",
        "accept": "application/json",
    }

    while added_count < 10 and page <= 10:
        url = f"{settings.BASE_URL}/discover/tv"
        params = {
            "with_watch_providers": provider_id,
            "watch_region": "FR",
            "language": "fr-FR",
            "sort_by": "popularity.desc",
            "page": page,
            "watch_monetization_types": "flatrate",
        }

        response = requests.get(url, params=params, headers=headers)
        data = response.json()

        print(
            f"Status: {response.status_code} | Platform: {platform_name} | Page: {page}"
        )

        results = data.get("results", [])

        if not results:
            print("Aucun résultat trouvé ou erreur API")
            break

        for item in results:
            if added_count >= 10:
                break

            # GESTION DES DOUBLONS : On vérifie si le tmdb_id existe déjà
            if not Task.objects.filter(tmdb_id=item["id"], user=request.user).exists():
                Task.objects.create(
                    user=request.user,
                    title=item["name"],
                    tmdb_id=item["id"],
                    poster_path=item.get("poster_path"),
                    platform=platform_name,
                    complete=False,
                )
                added_count += 1

        page += 1

    return redirect("/")


@login_required(login_url="login")
def index(request):
    tasks = Task.objects.filter(user=request.user).order_by("-created")

    form = TaskForm()

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
        return redirect("/")

    context = {"tasks": tasks, "form": form}
    return render(request, "tasks/list.html", context)


@login_required(login_url="login")
def updateTask(request, pk):
    task = Task.objects.get(id=pk)
    form = TaskForm(instance=task)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect("/")

    context = {"form": form}
    return render(request, "tasks/update_task.html", context)


@login_required(login_url="login")
def deleteTask(request, pk):
    item = Task.objects.get(id=pk)

    if request.method == "POST":
        item.delete()
        return redirect("/")

    context = {"item": item}
    return render(request, "tasks/delete.html", context)


def registerPage(request):
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("list")
    return render(request, "tasks/register.html", {"form": form})


def fc_login(request):
    state = str(uuid.uuid4())
    nonce = str(uuid.uuid4())
    request.session["fc_state"] = state
    request.session["fc_nonce"] = nonce

    params = {
        "response_type": "code",
        "client_id": settings.FC_CLIENT_ID,
        "redirect_uri": settings.FC_REDIRECT_URI,
        "scope": "openid profile email",
        "state": state,
        "nonce": nonce,
    }

    auth_url = (
        f"{settings.FC_BASE_URL}/api/v1/authorize?{urllib.parse.urlencode(params)}"
    )

    print("\n--- DEBUG FRANCE CONNECT ---")
    print(f"URL générée : {auth_url}")
    print(f"Redirect URI attendu : {settings.FC_REDIRECT_URI}")
    print(f"Client ID utilisé : {settings.FC_CLIENT_ID}")

    return redirect(auth_url)


def fc_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")

    # Vérification du state pour la sécurité
    if state != request.session.get("fc_state"):
        return redirect("login")

    # Échange du code contre un Access Token
    token_url = f"{settings.FC_BASE_URL}/api/v1/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.FC_CLIENT_ID,
        "client_secret": settings.FC_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.FC_REDIRECT_URI,
    }
    token_res = requests.post(token_url, data=data).json()
    access_token = token_res.get("access_token")

    # Récupération des infos de l'utilisateur (UserInfo)
    user_info_url = f"{settings.FC_BASE_URL}/api/v1/userinfo"
    user_data = requests.get(
        user_info_url, headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    # Création ou récupération de l'utilisateur Django
    # On utilise le 'sub' (identifiant unique FC) comme username ou un email
    username = user_data.get("sub")
    email = user_data.get("email", f"{username}@franceconnect.fr")

    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "first_name": user_data.get("given_name", ""),
            "last_name": user_data.get("family_name", ""),
            "email": email,
        },
    )

    login(request, user)
    return redirect("list")
