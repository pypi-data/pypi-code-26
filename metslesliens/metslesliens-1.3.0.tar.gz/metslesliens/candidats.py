# -*- coding: utf-8 -*-
#
# Les deux fonctions publiques sont :
# - donnelesliens( texte, format = 'texte', options = [], degradations = [] )
# - generateur_donnelesliens( texte, format = 'texte', options = [], degradations = [] )
#

import os.path
import re
from collections import OrderedDict
import parsimonious


# Constantes
longueur_debug_avant_texte = 20
longueur_debug_texte = 120

ordre_subdivisions = [ 'texte', 'partie', 'livre', 'titre', 'chapitre', 'section', 'sous-section', 'paragraphe', 'sous-paragraphe', 'article', 'alinea' ]

repertoire = os.path.realpath( os.path.dirname( __file__ ) )


def _lire_grammaires( func ):

    """
    Décorateur fournissant les grammaires.

    :param func:
        Fonction à décorer.
    :returns:
        Fonction donnée en argument, décorée.
    """

    with open( os.path.join( repertoire, 'grammaire-liens.txt' ), encoding = 'UTF-8' ) as f:
        texte_grammaire_articles = f.read()

    setattr( func, 'grammaires', texte_grammaire_articles )
    setattr( func, 'grammaires_articles', {} )
    setattr( func, 'separateurs', {} )

    return func


def donnelescandidats( texte, format = 'texte', options = [], degradations = [] ):

    """
    Donne des expressions candidates pour être des liens dans texte de loi.

    :param texte:
        (str) Texte.
    :param format:
        ('texte'|'structuré'|'arbre') Format de résultat.
            - 'texte' = aperçu rapide notamment pour contrôle
            - 'structuré' = réutilisation dans d’autres programmes Python
            - 'arbre' = arbre capturé par Parsimonious notamment pour débuggage
    :param options:
        (list[str]) Liste d’options à ajouter à la grammaire, parmi : 'Conseil constitutionnel'.
    :param degradations:
        (list[str]) Liste de dégradations à appliquer sur la grammaire, parmi : 'accents', 'code du commerce'.
    :returns:
        (list[dict|(int,str)|parsimonious.Node]) Candidats de liens, ordonnés par ordre d’apparition dans le texte.
            - ((int,str)) format 'texte' : index dans le texte, à partir de 0, et expression capturée entière,
            - (dict) format 'structuré' :
                - 'index' (int, int) = index de début et fin+1
                - 'alinea' (str) = alinéa (optionnel)
                - 'article', 'chapitre', 'titre', 'livre' (list[str|(str,str)]) = liste des articles/etc, les tuples sont les plages d’articles/etc correspondant au premier et au dernier de la série (optionnel)
                - 'texte' (dict[str]) = 'nom', 'date', et 'numero' du texte (optionnel)
            - (parsimonious.Node) format 'arbre' : tout l’arbre capturé,
            - ((int,str,str)) format 'debug' : index dans le texte, à partir de 0, une vingtaine de caractères avant le pré-candidat, et 120 caractères du pré-candidat avec l’éventuelle expression capturée délimitée entre les caractères "⬤ " (noter une espace après le disque, il semble prendre l’espace de deux caractères).
    """

    return list( generateur_donnelescandidats( texte, format, options, degradations ) )


@_lire_grammaires
def generateur_donnelescandidats( texte, format = 'structuré', options = [], degradations = [] ):

    """
    Donne des expressions candidates pour être des liens dans texte de loi.

    :param texte:
        (str) Texte.
    :param format:
        ('texte'|'structuré'|'arbre') Format de résultat.
            - 'texte' = aperçu rapide notamment pour contrôle
            - 'structuré' = réutilisation dans d’autres programmes Python
            - 'arbre' = arbre capturé par Parsimonious notamment pour débuggage
            - 'debug' = format spécifique facilitant la recherche de faux négatifs
    :param options:
        (list[str]) Liste d’options à ajouter à la grammaire, parmi : 'Conseil constitutionnel'.
    :param degradations:
        (list[str]) Liste de dégradations à appliquer sur la grammaire, parmi : 'accents', 'code du commerce'.
    :returns:
        (générateur(list[dict|(int,str)|parsimonious.Node])) Candidats de liens, ordonnés par ordre d’apparition dans le texte.
            - ((int,str)) format 'texte' : index dans le texte, à partir de 0, et expression capturée entière,
            - (dict) format 'structuré' :
                - 'index' (int, int) = index de début et fin+1
                - 'alinea' (str) = alinéa (optionnel)
                - 'article', 'chapitre', 'titre', 'livre' (list[str|(str,str)]) = liste des articles/etc, les tuples sont les plages d’articles/etc correspondant au premier et au dernier de la série (optionnel)
                - 'texte' (dict[str]) = 'nom', 'date', et 'numero' du texte (optionnel)
            - (parsimonious.Node) format 'arbre' : tout l’arbre capturé,
            - ((int,str,str)) format 'debug' : index dans le texte, à partir de 0, une vingtaine de caractères avant le pré-candidat, et 120 caractères du pré-candidat avec l’éventuelle expression capturée délimitée entre les caractères "⬤ " (noter une espace après le disque, il semble prendre l’espace de deux caractères).
    """

    grammaire_articles, separateurs_optionnels = _obtenir_grammaire( options, degradations )

    # Les pré-candidats sont les expressions commençant par les mots suivants, permettant d’accélérer le traitement
    separateurs = [ 'au(dit)? ', 'le(dit)? ', 'la(dite)? ', 'du(dit)? ', "l['’]", 'aux(dits)? ', 'les(dits)? ', 'des(dits)? ' ]
    separateurs.extend( separateurs_optionnels )
    regex_precandidats = re.compile( '(?<![a-záàâäéèêëíìîïóòôöøœúùûüýỳŷÿ])(' + '|'.join( separateurs ) + ')', flags=re.IGNORECASE )

    # Les candidats sont reconnus par la grammaire
    avancement = 0
    for precandidat in regex_precandidats.finditer( texte ):

        # Ne pas re-capturer une partie d’expression déjà capturée
        if precandidat.start() < avancement:
            continue

        try:

            arbre = grammaire_articles.match( texte, precandidat.start() )

        except parsimonious.exceptions.ParseError:

            if format == 'debug':
                debut_texte = texte[ precandidat.start() - longueur_debug_avant_texte : precandidat.start() ].rsplit( '\n', 1 )[-1]
                fin_texte = texte[ precandidat.start() : precandidat.start() + longueur_debug_texte + 4 ].split( '\n', 1 )[0]
                yield ( precandidat.start(), debut_texte, fin_texte )

            continue

        avancement = arbre.start + len( arbre.text )

        if format == 'arbre':

            yield arbre

        elif format == 'texte':

            # Retrait de l’article défini ou proposition, sauf si c’est « dudit, auxdits, … »
            if not re.match( r'^(aux?|les?|la|du|des)dite?s? ', arbre.text ) and arbre.children[0].expr_name in { 'entree_singulier', 'entree_pluriel' }:
                arbre = arbre.children[0].children[1]

            yield ( arbre.start, arbre.text )

        elif format == 'structuré' or format == 'structuré-index':

            # Table de correspondance entre les règles et les captures à extraire effectivement
            table_captures = {
                'nom_texte_francais': 'nom_texte',
                'nom_texte_europeen': 'nom_texte',
                'code_francais': 'nom_texte',
                'nom_Conseil_constitutionnel': 'nom_texte',
                'texte_relatif': 'relatif_texte',
                'numero_annee_identifiant': 'numero_texte',
                'numero_reglement_europeen': 'numero_texte',
                'numero_Conseil_constitutionnel': 'numero_texte',
                'date': 'date_texte',
                'designation_article': [ 'article' ],
                'designation_articles_relatifs': [ 'article' ],
                'article_relatif1': [ 'article' ],
                'articles_relatifs1': [ 'article' ],
                'articles_relatifs2': [ 'article' ],
                'liste_articles': ( 'article', 'liste implicite', 'article' ),
                'nature_supra_article_singulier': [ 'type_partie' ],
                'designation_chapitre': [ 'numero_partie' ],
                'designation_chapitres_relatifs': [ 'numero_partie' ],
                'chapitre_relatif1': [ 'numero_partie' ],
                'chapitre_relatif2': [ 'numero_partie' ],
                'chapitre_relatif3': [ 'numero_partie' ],
                'chapitres_relatifs1': [ 'numero_partie' ],
                'chapitres_relatifs2': [ 'numero_partie' ],
                'liste_chapitres': ( 'numero_partie', 'liste implicite', 'numero_partie' ),
                'chapitre': [ ( 'nom_partie', 'liste', 'numero_partie' ) ],
                'chapitres': [ ( 'nom_partie', 'liste', 'numero_partie' ) ],
                'designation_alinea': [ 'designation_alinea' ],
                'plusieurs_alineas_lettres': [ 'designation_alinea' ],
                'liste_alinea': [ ( 'liste_alinea', 'liste implicite', 'designation_alinea' ) ],
                'liste_plusieurs_alineas': [ ( 'liste_alinea', 'liste implicite', 'designation_alinea' ) ],
                'liste_quelques_alineas': [ ( 'liste_alinea', 'liste implicite', 'designation_alinea' ) ],
                'alinea': [ ( 'alinea', 'liste', 'liste_alinea' ) ],
                'alineas': [ ( 'alinea', 'liste', 'liste_alinea' ) ],
            }

            # Lecture de l’arbre
            capture = CaptureVisitor( table_captures, format == 'structuré-index' )
            capture.visit( arbre )
            candidat = capture.captures

            candidat['index'] = ( arbre.start, arbre.end )

            # Texte concerné, regroupé dans un dictionnaire
            if 'nom_texte' in candidat:
                candidat['texte'] = { k: candidat[k+'_texte'] for k in [ 'nom', 'relatif', 'numero', 'date' ] if k+'_texte' in candidat }
                if format == 'structuré-index':
                    candidat['texte']['index'] = ( min( [ t[0] for t in candidat['texte'].values() ] ), max( [ t[0] + len( t[1] ) for t in candidat['texte'].values() ] ) )

            # Simplification des listes d’un seul élément pour les articles et alinéas
            for k in { 'alinea', 'article' } & candidat.keys():
                candidat[k] = _simplifie_chaines( candidat[k] )

            # Niveaux hiérarchiques hormis alinéas et articles
            if 'type_partie' in candidat and 'nom_partie' in candidat:
                for type_partie, nom_partie in zip( candidat['type_partie'], candidat['nom_partie'] ):
                    type_partie = type_partie[1].lower() if format == 'structuré-index' else type_partie.lower()
                    candidat[type_partie] = _simplifie_chaines( nom_partie )

            # Retrait des clés non-finales
            for k in candidat.keys() - ordre_subdivisions:
                del candidat[k]

            # Ordonne les clés par niveau hiérarchique
            for k in ordre_subdivisions:
                if k in candidat:
                    candidat.move_to_end( k )

            yield candidat

        elif format == 'debug':

            debut_texte = texte[ arbre.start - longueur_debug_avant_texte : arbre.start ].rsplit( '\n', 1 )[-1]
            fin_texte = texte[ arbre.end : arbre.start + longueur_debug_texte ].split( '\n', 1 )[0]

            yield ( arbre.start, debut_texte, '⬤ ' + arbre.text + '⬤ ' + fin_texte )


def _obtenir_grammaire( options, degradations ):

    """
    Revoit une grammaire avec des règles légèrement dégradées selon certaines typologies d’erreurs.

    :param options:
        (list[str]) Liste d’options à ajouter à la grammaire, parmi : 'Conseil constitutionnel'.
    :param degradations:
        (list[str]) Liste de dégradations à appliquer sur la grammaire, parmi : 'accents', 'code du commerce'.
    :returns:
        (parsimonious.Grammar) Grammaire.
    """

    degradations.sort()
    cle = '|'.join( options ) + '_' + '|'.join( degradations )

    if cle in generateur_donnelescandidats.grammaires_articles:
        return generateur_donnelescandidats.grammaires_articles[ cle ], generateur_donnelescandidats.separateurs[ cle ]

    separateurs_optionnels = []
    texte_grammaire_articles = generateur_donnelescandidats.grammaires

    if 'Conseil constitutionnel' in options:

        texte_grammaire_articles = re.sub( r'(entree *= *[A-Za-z0-9/_? ]+)', r'\1 / entree_optionnelle_Conseil_constitutionnel', texte_grammaire_articles )
        separateurs_optionnels.append( 'décision' )

    if 'accents' in degradations:
        texte_grammaire_articles = re.sub( r'(?<!\[)[éèê](?!\])', '[éèêëe]', texte_grammaire_articles )
        texte_grammaire_articles = re.sub( r'à', '[áàâäa]', texte_grammaire_articles )
        texte_grammaire_articles = re.sub( r'ô', '[óòôöo]', texte_grammaire_articles )
        texte_grammaire_articles = re.sub( r'û', '[úùûüu]', texte_grammaire_articles )
        texte_grammaire_articles = texte_grammaire_articles.replace( '[a-zá[áàâäa]âä[éèêëe][éèêëe][éèêëe]ëíìîïóò[óòôöo]öøœúù[úùûüu]üýỳŷÿ]', '[a-záàâäéèêëíìîïóòôöøœúùûüýỳŷÿ]' )

    if 'code du commerce' in degradations:
        texte_grammaire_articles = texte_grammaire_articles.replace( 'de +commerce', 'd[eu] +commerce' )

    generateur_donnelescandidats.grammaires_articles[ cle ] = parsimonious.Grammar( texte_grammaire_articles )
    generateur_donnelescandidats.separateurs[ cle ] = separateurs_optionnels

    ordre_subdivisions[0:0] = [ 'index' ]

    return generateur_donnelescandidats.grammaires_articles[ cle ], separateurs_optionnels


def _simplifie_chaines( valeur ):

    """
    Transforme les listes imbriquées d’un seul élément en scalaire, sauf si l’élément est un tuple.

    :param valeur:
        (list[str|tuple]) Valeur à simplifier.
    :returns:
        (list[str|tuple]|str|tuple) Valeur éventuellement simplifiée.
    """

    original = valeur
    while isinstance( valeur, list ) and len( valeur ) == 1:
        valeur = valeur[0]
    if isinstance( valeur, str ) or isinstance( valeur, tuple ) and isinstance( valeur[0], int ):
        return valeur
    return original


class CaptureVisitor(parsimonious.NodeVisitor):

    def __init__( self, table, with_index = False ):

        self.table = table
        self.captures = OrderedDict()
        self.with_index = with_index

    def generic_visit( self, node, visited_children ):

        if node.expr_name in self.table:

            rule_name = node.expr_name
            semantic_rule_name = self.table[ rule_name ]
            semantic_rule_value = 'str'

            if isinstance( semantic_rule_name, list ) and len( semantic_rule_name ) == 1:
                semantic_rule_name = semantic_rule_name[0]
                semantic_rule_value = 'list'

            # Collect elements to create a list
            if isinstance( semantic_rule_name, tuple ) and len( semantic_rule_name ) == 3 and semantic_rule_name[1] == 'liste':
                value = self.captures[ semantic_rule_name[2] ]
                del self.captures[semantic_rule_name[2]]
                semantic_rule_name = semantic_rule_name[0]

            # Collect elements to create an "implicit" list (some elements could be implicitely defined)
            elif isinstance( semantic_rule_name, tuple ) and len( semantic_rule_name ) == 3 and semantic_rule_name[1] == 'liste implicite':
                value = [ self.captures[ semantic_rule_name[2] ][0] ]
                for subtree, subvalue in zip( node.children[1], self.captures[semantic_rule_name[2]][1:] ):
                    if subtree.children[0].children[0].expr_name == 'plage':
                        value[-1] = ( value[-1], subvalue )
                    else:
                        value.append( subvalue )
                del self.captures[semantic_rule_name[2]]
                semantic_rule_name = semantic_rule_name[0]

            # General behaviour: capture text
            elif self.with_index:
                value = ( node.start, node.text )
            else:
                value = node.text

            if semantic_rule_value == 'list':
                if semantic_rule_name not in self.captures:
                    self.captures[semantic_rule_name] = []
                self.captures[semantic_rule_name].append( value )
            else:
                self.captures[semantic_rule_name] = value

# vim: set ts=4 sw=4 sts=4 et:
