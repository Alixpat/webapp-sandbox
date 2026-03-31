# Budget Manager

Application web de gestion budgétaire construite avec Flask et PostgreSQL.

## Fonctionnalités

- **Utilisateurs** : créer des projets, ajouter des lignes budgétaires avec justifications et pièces jointes
- **Superviseur** : vue globale de tous les projets et du montant total

## Modèle de données

- **User** : utilisateurs avec rôle (`user` ou `supervisor`)
- **Project** : projets rattachés à un utilisateur
- **BudgetNeedExpression** : expressions de besoin budgétaire (libellé, montant MCO, montant investissement, justification) rattachées à un projet
- **Attachment** : pièces jointes rattachées à une expression de besoin

## Lancer avec Docker Compose

```bash
docker compose up --build
```

Ouvrir http://localhost:10000

## Comptes de démonstration

| Email | Mot de passe | Rôle |
|---|---|---|
| alice@example.com | alice123 | Utilisateur |
| bob@example.com | bob123 | Utilisateur |
| admin@example.com | admin123 | Superviseur |

## Données fictives injectées

- **Alice** : 2 projets (Refonte site web, Formation Data Science) avec lignes budgétaires
- **Bob** : 1 projet (Migration ERP) avec lignes budgétaires
- **Sophie** (superviseur) : accès en lecture à tous les projets
