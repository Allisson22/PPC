# PPC

## Préliminaire

Il vous faut la librairie sysv_ipc téléchargeable [ici](http://semanchuk.com/philip/sysv_ipc/), puis, dans le répertoire du dossier, tapez la commande suivante :

```bash
login@hostame:~$ python3 setup.py install --user 
```

## Lancement du jeu

Pour démarrer le jeu : lancez le fichier server.py, puis dans un second terminal, lancez le fichier client.py et annoncez le nombre de joueurs quand cela vous sera demandé. Le nombre maximum de joueurs est 8.

Le jeu sera en pause le temps que tous les joueurs se connectent. Pour ce faire, dans des terminaux différents, lancez autant de fois le fichier client.py qu'il manque de joueurs à la partie.

## Déroulement de votre tour

Lors de votre tour, toutes les informations concernant l'avancement du jeu vous sont fournies. Vous pourrez ensuite jouer une carte ou donner une information à l'un de vos coéquipiers. Pour ce faire, répondez "jouer" ou "information".

### Jouer

Si vous décidez de jouer une carte, vous devez annoncer la carte que vous souhaitez jouer en donnant sa position dans votre main, de 1 à 5.

### Information

Si vous voulez donner une information, vous devez annoncer le numéro du joueur à qui annoncer cette information, puis dire si cette information va être une "couleur" ou un "numéro" et enfin dire le numéro que vous voulez annoncer, de 1 à 5, ou bien la couleur que vous voulez annoncer, dans la liste des couleurs disponibles.

### Pas d'inquiétudes

Si vous vous trompez lors de l'écriture des réponses, le message vous est renvoyé, et si vous ne savez pas quoi répondre, les réponses acceptables sont affichées à l'écran, souvent entre parenthèses.

## Déroulement des tours de vos coéquipiers

Patientez pendant que vos coéquipiers décident de leurs actions. Apres chaque décision effectuée, un récapitulatif vous est affiché.
