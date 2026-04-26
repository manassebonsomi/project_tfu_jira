import logging

data, tests, relations = [], [], []


# Données générales
def all_data(tickets):
    try:
        for issue in tickets:
            data.append({
                "key": issue.key,
                "type": issue.fields.issuetype.name,
                "status": issue.fields.status.name,
                "summary": issue.fields.summary
            })

        return data
    except Exception as e:
        logging.error(f"Erreur : {e}")


# Pour recuperer tous les liens entres les taches
def data_link_task(tickets):
    try:
        for issue in tickets:
            print("ISSUE:", issue.key, issue.fields.issuetype.name)

            if hasattr(issue.fields, "issuelinks"):
                for link in issue.fields.issuelinks:
                    print("  LINK:", link.type.name)

                    if hasattr(link, "outwardIssue"):
                        print("    outward:", link.outwardIssue.key, link.outwardIssue.fields.issuetype.name)

                    if hasattr(link, "inwardIssue"):
                        print("    inward:", link.inwardIssue.key, link.inwardIssue.fields.issuetype.name)

        for issue in tickets:
            if issue.fields.issuetype.name in ["Task", "Tâche"]:

                for link in issue.fields.issuelinks:

                    # CAS 1 : le test est bloqué par un bug
                    if hasattr(link, "inwardIssue") and link.type.name == "Blocks":
                        linked = link.inwardIssue

                        if linked.fields.issuetype.name == "Bug":
                            relations.append({
                                "test": issue.key,
                                "bug": linked.key
                            })

                    # CAS 2 : le test bloque un bug
                    if hasattr(link, "outwardIssue") and link.type.name == "Blocks":
                        linked = link.outwardIssue

                        if linked.fields.issuetype.name == "Bug":
                            relations.append({
                                "test": issue.key,
                                "bug": linked.key
                            })

        return relations
    except Exception as e:
        logging.error(f"Erreur : {e}")


# Pour les tests
def data_test(tickets):
    try:
        for issue in tickets:
            if issue.fields.issuetype.name.lower() in ["task", "tâche"]:

                field = getattr(issue.fields, "customfield_10071", None)

                test_status = None
                if field:
                    test_status = field.value

                tests.append({
                    "key": issue.key,
                    "status": issue.fields.status.name,
                    "test_status": test_status
                })

        return tests
    except Exception as e:
        logging.error(f"Erreur : {e}")
