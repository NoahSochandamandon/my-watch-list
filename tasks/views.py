import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from .models import *
from .forms import *

# Create your views here.


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
            if not Task.objects.filter(tmdb_id=item["id"]).exists():
                Task.objects.create(
                    title=item["name"],
                    tmdb_id=item["id"],
                    poster_path=item.get("poster_path"),
                    platform=platform_name,
                    complete=False,
                )
                added_count += 1

        page += 1

    return redirect("/")


def index(request):
    tasks = Task.objects.all()

    form = TaskForm()

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            # adds to the database if valid
            form.save()
        return redirect("/")

    context = {"tasks": tasks, "form": form}
    return render(request, "tasks/list.html", context)


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


def deleteTask(request, pk):
    item = Task.objects.get(id=pk)

    if request.method == "POST":
        item.delete()
        return redirect("/")

    context = {"item": item}
    return render(request, "tasks/delete.html", context)
