# C:\Foodypedia\apps\chefs\models.py

from django.db import models

class Chef(models.Model):
    """
    Modèle pour les profils des chefs célèbres.
    Contient les informations biographiques sans liens complexes aux recettes (M2M).
    """
    
    CATEGORIE_CHOICES = [
        ('CUISINE', 'Cuisine'),
        ('PATISSERIE', 'Pâtisserie'),
        ('BOULANGERIE', 'Boulangerie'),
        ('AUTRE', 'Autre'),
    ]

    # --- INFORMATIONS REQUISES ---
    
    nom = models.CharField(max_length=255, verbose_name="Nom complet")
    
    # ForeignKey vers l'application core (Pays)
    pays_d_origine = models.ForeignKey(
        'atlas.Pays', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Pays d'origine"
    )
    
    email = models.EmailField(max_length=254, unique=True, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    
    categorie = models.CharField(
        max_length=20,
        choices=CATEGORIE_CHOICES,
        default='CUISINE',
        verbose_name="Catégorie de cuisine"
    )
    
    restaurant = models.CharField(max_length=255, blank=True, verbose_name="Restaurant principal")
    
    date_de_naissance = models.DateField(blank=True, null=True, verbose_name="Date de naissance")
    date_de_deces = models.DateField(blank=True, null=True, verbose_name="Date de décès")
    
    # --- CHAMP EN CONFLIT (DÉSORMAIS ABSENT) ---
    # Le champ 'ingredients' qui causait les erreurs E304/E305/E331 n'est plus là.

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Chef Célèbre"
        verbose_name_plural = "Chefs Célèbres"