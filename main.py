from jira import JIRA
import pandas as pd
import os
import matplotlib.pyplot as plt
import logging
from dotenv import load_dotenv
from services import all_data, data_test, data_link_task

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

if __name__ == "__main__":
    # CONFIGURATION
    jira = JIRA(
        server=os.getenv("JIRA_SERVER"),
        basic_auth=(os.getenv("JIRA_EMAIL"),
                    os.getenv("JIRA_API_TOKEN"))
    )

    # EXTRACTION DES DONNÉES
    issues = jira.search_issues("project=SCRUM", maxResults=1000)
    # bugs = []

    # DATAFRAME
    df_tests = pd.DataFrame(data_test(issues))
    # df_bugs = pd.DataFrame(bugs)
    df_rel = pd.DataFrame(data_link_task(issues))
    df = pd.DataFrame(all_data(issues))

    print("Tableau de Tache")
    print(df.head())

    print("------------------------------------------")

    # Taux de succès
    success = len(df[df["status"] == "Terminé(e)"])
    total = len(df)
    print("Taux de succès :", success / total)

    print("------------------------------------------")

    # Nombre de bugs
    bugs = df[df["type"] == "Bug"]
    print("Nombre de bugs :", len(bugs))

    print("------------------------------------------")
    print("------------------------------------------")

    # Nombre de bugs par test
    print("Nombre de bugs par test : ")
    bugs_per_test = df_rel.groupby("test").count()
    print(bugs_per_test)

    print("------------------------------------------")

    # Tests les plus critiques
    print("Tests les plus critiques : ")
    critical_tests = bugs_per_test.sort_values(by="bug", ascending=False)
    print(critical_tests.head())

    print("------------------------------------------")

    print("Corrélation NOK - Bugs : ")

    # Vérifier que la colonne existe
    print(df_tests.columns)

    df_tests["has_bug"] = df_tests["key"].isin(df_rel["test"])

    correlation = pd.crosstab(
        df_tests["test_status"],
        df_tests["has_bug"]
    )

    print(correlation)
    print("------------------------------------------")

    print("Calcul score de criticité")
    # nombre de bugs par test
    bugs_per_test = df_rel.groupby("test").size()

    # mapping
    df_tests["bug_count"] = df_tests["key"].map(bugs_per_test).fillna(0)

    # score = bug_count * NOK
    df_tests["criticality_score"] = df_tests["bug_count"] * (
            df_tests["test_status"] == "NOK"
    )
    # tri
    df_sorted = df_tests.sort_values(by="criticality_score", ascending=False)

    print(df_sorted)
    print("------------------------------------------")

    # Graphiques
    df["status"].value_counts().plot(kind="bar")
    plt.title("Répartition des tests")
    plt.show()

    bugs_per_test.plot(kind="bar", legend=False)
    plt.title("Nombre de bugs par test")
    plt.xlabel("Tests")
    plt.ylabel("Nombre de bugs")
    plt.show()

    # Sauvegarde Excel
    df.to_excel("rapport_tfu.xlsx", index=False)
