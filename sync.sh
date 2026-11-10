#!/bin/bash

# Récupère la date et l'heure actuelle
NOW=$(date +"%Y-%m-%d %H:%M:%S")

# Exécution des commandes Git
git add .
git commit -m "manual sync $NOW"
git push
