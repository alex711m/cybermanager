# CyberManager

**Application de gestion de Cybercafé Cloud-Native.**
Ce projet éducatif a pour but de comparer deux architectures logicielles pour le même besoin métier.

## 📂 Structure du projet

Le projet est divisé en deux versions distinctes :

* **`/v1-monolithe`** :
    * Version initiale.
    * Architecture simple : Flask + MySQL.
    * Déploiement Kubernetes standard.

* **`/v2-microservices`** (En développement) :
    * Évolution Cloud-Native.
    * Services découplés (Auth, Billing, Sessions).
    * Innovation : Instances de PC virtuels à la demande (Cloud Gaming).

## 🛠 Technologies

* **Langage :** Python (Flask)
* **Container :** Docker
* **Orchestration :** Kubernetes
* **Base de données :** MySQL