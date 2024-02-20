from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib import messages

from django.core.files.storage import default_storage

from django.db import IntegrityError
from .models import UserFollows, Ticket, Review
from .forms import UserFollowsForm, TicketForm, DeleteTicketForm, ReviewForm


# Ticket ---------------------------------------------------------------------


@login_required
def create_ticket(request):
    """Create Ticket"""

    ticket_form = TicketForm()
    if request.method == "POST":
        ticket_form = TicketForm(request.POST, request.FILES)
        if ticket_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()

            return redirect("flux")
        else:
            # Afficher les erreurs de validation du formulaire
            for field, errors in ticket_form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans le champ '{field}': {error}")

    context = {
        "ticket_form": ticket_form,
    }

    return render(request, "bookreview/create_ticket.html", context=context)


@login_required
def edit_ticket(request, ticket_id):
    """Update ticket"""

    ticket = get_object_or_404(Ticket, id=ticket_id)
    edit_form = TicketForm(instance=ticket)

    if request.method == "POST":

        edit_form = TicketForm(request.POST, request.FILES, instance=ticket)
        if edit_form.is_valid():
            edit_form.save()
            messages.success(
                request, f"Le Ticket {ticket.title} a été modifié avec succès."
            )
            return redirect("posts")
        else:
            # Afficher les erreurs de validation du formulaire
            for field, errors in edit_form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans le champ '{field}': {error}")

    context = {
        "edit_form": edit_form,
    }
    return render(request, "bookreview/edit_ticket.html", context=context)


@login_required
def delete_ticket(request, ticket_id):
    """delete ticket"""
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # Vérifie que l'utilisateur est autorisé à supprimer l'objet
    if ticket.user != request.user:

        return HttpResponseForbidden(
            "Vous n'êtes pas autorisé à effectuer cette action."
        )

    try:
        # Supprimer le fichier image associé au ticket s'il existe
        if ticket.image:
            # Obtenir le chemin du fichier
            file_path = ticket.image.path
            # Supprimer le fichier
            default_storage.delete(file_path)

        ticket.delete()

        messages.success(
            request, f"Le Ticket {ticket.title} a été supprimé avec succès."
        )
    except IntegrityError as e:
        # Gérer les erreurs spécifiques liées à l'intégrité de la base de données
        messages.error(
            request,
            f"Une erreur d'intégrité de la base de données s'est produite : {e}",
        )
    except Exception as e:
        # Gérer les autres exceptions génériques
        messages.error(
            request,
            f"Une erreur s'est produite lors de la suppression de l'objet : {e}",
        )

    return redirect("posts")


# Review ---------------------------------------------------------------------


@login_required
def create_review(request):
    review_form = ReviewForm()
    ticket_form = TicketForm()
    if request.method == "POST":
        review_form = ReviewForm(request.POST)
        ticket_form = TicketForm(request.POST, request.FILES)
        if all([review_form.is_valid(), ticket_form.is_valid()]):
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            review = review_form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()
            return redirect("flux")
        else:
            # Afficher les erreurs de validation du formulaire
            for field, errors in review_form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans le champ '{field}': {error}")

    context = {"review_form": review_form, "ticket_form": ticket_form}
    return render(request, "bookreview/create_review.html", context=context)


@login_required
def create_review_ticket(request, ticket_id):
    """Creation d'une Critique"""

    ticket = get_object_or_404(Ticket, id=ticket_id)
    review_form = ReviewForm()
    if request.method == "POST":
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()
            return redirect("flux")
        else:
            # Afficher les erreurs de validation du formulaire
            for field, errors in review_form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans le champ '{field}': {error}")

    context = {
        "ticket": ticket,
        "review_form": review_form,
    }
    return render(request, "bookreview/create_review_ticket.html", context=context)


@login_required
def edit_review(request, review_id):
    """Edition d'une Critique"""

    review = get_object_or_404(Review, id=review_id)
    edit_form = ReviewForm(instance=review)
    ticket = review.ticket
    if request.method == "POST":
        edit_form = ReviewForm(request.POST, instance=review)
        if edit_form.is_valid():
            edit_form.save()
            messages.success(
                request, f"La Critique {review.ticket} a été modifié avec succès."
            )
            return redirect("posts")
        else:
            # Afficher les erreurs de validation du formulaire
            for field, errors in edit_form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans le champ '{field}': {error}")

    context = {
        "edit_form": edit_form,
        "ticket": ticket,
    }
    return render(request, "bookreview/edit_review.html", context=context)


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if review.user != request.user:
        return HttpResponseForbidden(
            "Vous n'êtes pas autorisé à effectuer cette action."
        )

    try:
        review.delete()
        messages.success(
            request, f"La Critique {review.ticket} a été supprimé avec succès."
        )
    except IntegrityError as e:
        # Gérer les erreurs spécifiques liées à l'intégrité de la base de données
        messages.error(
            request,
            f"Une erreur d'intégrité de la base de données s'est produite : {e}",
        )
    except Exception as e:
        # Gérer les autres exceptions génériques
        messages.error(
            request,
            f"Une erreur s'est produite lors de la suppression de l'objet : {e}",
        )

    return redirect("posts")


# Follows users  ---------------------------------------------------------------------


@login_required
def follows(request):
    """Abonnements et abonés d'un utilisateur"""

    # Récupérer les utilisateurs suivis et les abonnés de l'utilisateur connecté
    followings = UserFollows.objects.filter(user=request.user)
    followers = UserFollows.objects.filter(followed_user=request.user)

    if request.method == "POST":
        form = UserFollowsForm(request.POST)
        if form.is_valid():
            try:
                user_follow = form.save(commit=False)
                user_follow.user = request.user
                user_follow.save()
            except IntegrityError:
                messages.error(
                    request,
                    f"L'utilisateur {user_follow.followed_user} est deja dans votre liste de suivis",
                )
                return render(
                    request,
                    "bookreview/follows.html",
                    {"form": form, "followings": followings, "followers": followers},
                )

            return redirect("follows")
    else:
        form = UserFollowsForm()

    context = {
        "form": form,
        "followings": followings,
        "followers": followers,
    }

    return render(request, "bookreview/follows.html", context=context)


@login_required
def follows_delete(request, follows_id):
    """Suppression des abonnements d'un utilisateur"""

    follow = get_object_or_404(UserFollows, id=follows_id)

    # Vérifie que l'utilisateur est autorisé à supprimer l'objet
    if follow.user != request.user:

        return HttpResponseForbidden(
            "Vous n'êtes pas autorisé à effectuer cette action."
        )

    try:
        follow.delete()
        messages.success(request, f"{follow.followed_user} a été supprimé avec succès.")
    except IntegrityError as e:
        # Gérer les erreurs spécifiques liées à l'intégrité de la base de données
        messages.error(
            request,
            f"Une erreur d'intégrité de la base de données s'est produite : {e}",
        )
    except Exception as e:
        # Gérer les autres exceptions génériques
        messages.error(
            request,
            f"Une erreur s'est produite lors de la suppression de l'objet : {e}",
        )

    return redirect("follows")


# Posts ---------------------------------------------------------------------


@login_required
def posts(request):
    """Liste de tous les tickets et reviews de l'utilisateur connecté"""

    tickets = Ticket.objects.filter(user=request.user)
    reviews = Review.objects.filter(user=request.user)
    posts = list(tickets) + list(reviews)

    # Trier les posts par ordre antéchronologique
    posts.sort(key=lambda x: x.time_created, reverse=True)

    delete_form_ticket = DeleteTicketForm()

    context = {
        "posts": posts,
        "delete_form_ticket": delete_form_ticket,
    }

    return render(request, "bookreview/posts.html", context)


# Flux ---------------------------------------------------------------------


@login_required
def flux(request):

    # récupération des posts de l'utilsateur connecté
    tickets = Ticket.objects.filter(user=request.user)
    reviews = Review.objects.filter(user=request.user)

    # Utilisation d'un ensemble pour éviter les doublons
    posts_set = set(tickets) | set(reviews)

    # récupération des posts des followers
    follows = UserFollows.objects.filter(user=request.user)
    for follow in follows:
        tickets_followed = Ticket.objects.filter(user=follow.followed_user)
        reviews_followed = Review.objects.filter(user=follow.followed_user)
        posts_set |= set(tickets_followed) | set(reviews_followed)

    # Trier les posts par ordre antéchronologique
    posts = sorted(posts_set, key=lambda x: x.time_created, reverse=True)

    context = {
        "posts": posts,
    }

    return render(request, "bookreview/flux.html", context)
