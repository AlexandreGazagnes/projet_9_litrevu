from django.conf import settings
from django.conf.urls.static import (
    static,
)  # Importation pour servir les fichiers statiques en développement
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("authentication.urls")),
    path("", include("bookreview.urls")),
]

# Les images stockées dans le répertoire MEDIA_ROOT seront servies au chemin donné par MEDIA_URL
# Seulement en environnement de développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
