# Σειρά συγγραφής

## Κατάσταση

Τα έγγραφα και οι ρυθμίσεις έχουν αρχικό περιεχόμενο. Όλα τα Python αρχεία, περιλαμβανομένων των tests, είναι κενά. Τα στάδια παρακάτω είναι σχέδιο και δεν αποτελούν αναφορά ολοκληρωμένων λειτουργιών.

## Προεργασία

Διαβάζουμε project_scope.md, market_and_data.md, data_contract.md, mathematical_model.md, research_protocol.md και architecture.md. Επιθεωρούμε τα πρώτα XLSX και οριστικοποιούμε το μικρότερο υποστηριζόμενο πείραμα πριν γράψουμε parser ή στρατηγική.

Η σειρά είναι εξαρτησιακή, όχι απαίτηση να γραφτεί κάθε αρχείο μία φορά. Κάθε επόμενη εγκεκριμένη φάση μπορεί να επεκτείνει ήδη υπάρχοντα modules.

## Python modules

Οι σύνδεσμοι δείχνουν τα πραγματικά αρχεία του σκελετού.

| Σειρά | Αρχείο | Χρησιμότητα | Κριτήριο πριν συνεχίσουμε |
| --- | --- | --- | --- |
| 1 | [config.py](../src/aegean/config.py) | Ρυθμίσεις χαρτοφυλακίου, χρονισμού, κόστους και solver. | Σαφείς μονάδες, έλεγχος ορίων και μη αποδεκτών τιμών. |
| 2 | [data/schema.py](../src/aegean/data/schema.py) | Εσωτερικό σχήμα και τύποι δεδομένων. | Σαφής διάκριση actual, forecast, revision και available_at. |
| 3 | [data/excel.py](../src/aegean/data/excel.py) | Ανάγνωση XLSX και καταγραφή προέλευσης. | Επιθεωρημένο πραγματικό XLSX· ανίχνευση sheets, τύπων και cached formulas. |
| 4 | [data/validation.py](../src/aegean/data/validation.py) | Έλεγχοι ποιότητας χωρίς σιωπηλές διορθώσεις. | Διπλότυπα, κενά, μονάδες, αρνητικές τιμές και μηδενική παραγωγή. |
| 5 | [data/preprocessing.py](../src/aegean/data/preprocessing.py) | Ενοποίηση ονομάτων, χρόνου και χρονικής ανάλυσης. | Συμφωνία ενέργειας πριν/μετά από μετασχηματισμούς. |
| 6 | [backtesting/timeline.py](../src/aegean/backtesting/timeline.py) | Snapshots πληροφοριών ανά χρόνο απόφασης. | Καμία εγγραφή με available_at μετά την απόφαση· σωστές αναθεωρήσεις και DST. |
| 7 | [trading/portfolio.py](../src/aegean/trading/portfolio.py) | Θέσεις, υποχρεώσεις και καταγεγραμμένα fills. | Order και fill παραμένουν διαφορετικά· μοναδικά identifiers. |
| 8 | [optimization/battery.py](../src/aegean/optimization/battery.py) | Κατάσταση μπαταρίας και φυσική μετάβαση. | Ισοζύγιο, απώλειες, όρια, αρχική ενέργεια και πραγματική εφικτή λειτουργία. |
| 9 | [backtesting/settlement.py](../src/aegean/backtesting/settlement.py) | Υπολογισμός ταμειακών ροών και αποκλίσεων. | Επαληθευμένοι εφαρμοστέοι κανόνες· χειροκίνητα ελέγξιμα παραδείγματα. |
| 10 | [forecasting/baselines.py](../src/aegean/forecasting/baselines.py) | Απλές persistence/εποχικές προβλέψεις. | Αποκλειστική χρήση διαθέσιμου παρελθόντος. |
| 11 | [trading/risk.py](../src/aegean/trading/risk.py) | Έλεγχος νέων ενεργειών και ορίων. | Προκαθορισμένη απόρριψη με αιτία και ελεγμένη συμπεριφορά fallback. |
| 12 | [trading/execution.py](../src/aegean/trading/execution.py) | Προσομοίωση fills και κόστους. | Χωριστές παραδοχές για auction και continuous execution· μερικά fills. |
| 13 | [trading/policies.py](../src/aegean/trading/policies.py) | Αρχική απλή πολιτική αποφάσεων. | Λειτουργεί χωρίς optimizer· αργότερα προστίθεται κοινή διεπαφή optimizer policy. |
| 14 | [backtesting/engine.py](../src/aegean/backtesting/engine.py) | Σύνδεση χρόνου, αποφάσεων, fills, παράδοσης και settlement. | Πλήρες baseline χωρίς πρόσβαση της πολιτικής σε future actuals. |
| 15 | [backtesting/metrics.py](../src/aegean/backtesting/metrics.py) | Μετρικές οικονομικού και φυσικού αποτελέσματος. | Συμφωνία με ledger, baseline και κοινό παρονομαστή EUR/MWh. |
| 16 | [optimization/formulation.py](../src/aegean/optimization/formulation.py) | Σύνθεση objective, πινάκων, bounds και integrality. | Ελεγχόμενα μικρά προβλήματα με γνωστή λύση· ονομαστικός χάρτης indices. |
| 17 | [optimization/solver.py](../src/aegean/optimization/solver.py) | Κλήση SciPy linprog/milp και κανονικοποίηση αποτελέσματος. | Ρητό status, εφικτή λύση, χρόνος και gap όπου διατίθεται. |
| 18 | [optimization/validation.py](../src/aegean/optimization/validation.py) | Ανεξάρτητος έλεγχος λύσης. | Επανυπολογισμός ισοζυγίων/objective χωρίς εμπιστοσύνη μόνο στο success flag. |
| 19 | [forecasting/features.py](../src/aegean/forecasting/features.py) | Χρονικά ορθά χαρακτηριστικά. | Lagged/rolling μεταβλητές χωρίς χρήση του υπό πρόβλεψη target. |
| 20 | [forecasting/models.py](../src/aegean/forecasting/models.py) | Εκπαίδευση και πρόβλεψη στατιστικών/ML μοντέλων. | Fit μόνο στο επιτρεπτό train· reproducible configuration. |
| 21 | [forecasting/evaluation.py](../src/aegean/forecasting/evaluation.py) | Walk-forward σύγκριση και αξιολόγηση αβεβαιότητας. | Ίδια splits για μοντέλα και baselines· σωστός χρονισμός labels. |
| 22 | [forecasting/scenarios.py](../src/aegean/forecasting/scenarios.py) | Σενάρια παραγωγής/τιμών και πιθανότητες. | Βάρη αθροίζουν σε 1, εξάρτηση στον χρόνο και μη πρόσβαση στο holdout. |
| 23 | [reporting/excel.py](../src/aegean/reporting/excel.py) | Εξαγωγή ledger, μετρικών και provenance σε XLSX. | Σωστές μονάδες και timestamps· επανάνοιγμα χωρίς απώλεια σημασίας. |
| 24 | [reporting/charts.py](../src/aegean/reporting/charts.py) | Οικονομικά, φυσικά και forecast γραφήματα. | Άξονες, μονάδες, περίοδοι και έντιμη σύγκριση baseline. |
| 25 | [cli.py](../src/aegean/cli.py) | Εκτέλεση της κοινής ροής από τερματικό. | Κατανοητά arguments/errors και σταθερό run identifier. |
| 26 | [app/streamlit_app.py](../app/streamlit_app.py) | Διαδραστική χρήση κοινών modules. | Ελεγμένη backend ροή· οθόνες με status, περιορισμούς και σαφές simulation label. |

Μετά το στάδιο 18, το trading/policies.py συνδέεται με τον optimizer και η νέα πολιτική συγκρίνεται με το baseline. Μετά το στάδιο 22 επεκτείνονται formulation.py, validation.py και policies.py με σενάρια/CVaR. Δεν εισάγεται CVaR πριν περάσει η ντετερμινιστική έκδοση.

## Tests μαζί με την υλοποίηση

| Αρχείο | Πότε γράφεται | Χρησιμότητα |
| --- | --- | --- |
| [conftest.py](../tests/conftest.py) | Από το στάδιο 2 | Κοινά μικρά συνθετικά fixtures, χωρίς πρόσβαση σε πραγματικά μη δημόσια δεδομένα. |
| [test_data_validation.py](../tests/test_data_validation.py) | Στάδια 2–5 | Κενά, διπλότυπα, μονάδες, μηδενικά, αρνητικές τιμές και τύποι Excel. |
| [test_time_alignment.py](../tests/test_time_alignment.py) | Στάδιο 6 | Publication delays, revision selection, DST και διαρροή μελλοντικής πληροφορίας. |
| [test_battery.py](../tests/test_battery.py) | Στάδιο 8 | Ενέργεια, απόδοση, όρια ισχύος, terminal condition και φυσική εφικτότητα. |
| [test_settlement.py](../tests/test_settlement.py) | Στάδιο 9 | Σημεία προσήμων, deficit/surplus, αρνητικές τιμές, fees και απουσία διπλομέτρησης. |
| [test_forecasting.py](../tests/test_forecasting.py) | Στάδια 10 και 19–22 | Χρονικά έγκυρα features, train-only fit, splits και scenario weights. |
| [test_risk.py](../tests/test_risk.py) | Στάδιο 11 | Παραβίαση ορίων, stale data και απόρριψη μη επιτρεπτής ενέργειας. |
| [test_execution.py](../tests/test_execution.py) | Στάδιο 12 | Μερικά fills, καθυστερήσεις, fees και idempotency. |
| [test_backtest.py](../tests/test_backtest.py) | Στάδια 14–15 | Μικρή end-to-end ιστορία με γνωστό ledger και τελικό αποτέλεσμα. |
| [test_optimization.py](../tests/test_optimization.py) | Στάδια 16–18 και επέκταση σεναρίων | Γνωστές λύσεις, infeasible status, integer constraints και ανεξάρτητοι residuals. |

Τα tests αφορούν συμπεριφορά και ανεξάρτητα αναμενόμενα αποτελέσματα. Δεν αρκεί η αντιγραφή των ίδιων τύπων της υλοποίησης. Δεν εκτελούνται πριν υπάρξει ουσιαστικός κώδικας.

## Αρχεία package

Τα παρακάτω __init__.py παραμένουν κενά αρχικά. Καθιστούν τους φακέλους κανονικά Python packages. Δεν προσθέτουμε αυτόματα imports που εκτελούν I/O κατά το import.

- [src/aegean/__init__.py](../src/aegean/__init__.py)
- [src/aegean/data/__init__.py](../src/aegean/data/__init__.py)
- [src/aegean/forecasting/__init__.py](../src/aegean/forecasting/__init__.py)
- [src/aegean/optimization/__init__.py](../src/aegean/optimization/__init__.py)
- [src/aegean/trading/__init__.py](../src/aegean/trading/__init__.py)
- [src/aegean/backtesting/__init__.py](../src/aegean/backtesting/__init__.py)
- [src/aegean/reporting/__init__.py](../src/aegean/reporting/__init__.py)

## Τεκμηρίωση και ρυθμίσεις

| Αρχείο | Πότε ενημερώνεται / χρησιμότητα |
| --- | --- |
| [README.md](../README.md) | Στην αρχή και σε κάθε παραδοτέο· μόνο πραγματική κατάσταση και επαληθευμένες οδηγίες. |
| [pyproject.toml](../pyproject.toml) | Αρχικό package configuration· συμβατότητα επαληθεύεται κατά την εγκατάσταση. |
| [.gitignore](../.gitignore) | Αρχικοί αποκλεισμοί τοπικών δεδομένων, secrets και αποτελεσμάτων. |
| [project_scope.md](project_scope.md) | Πριν από κώδικα· επιχειρησιακό πρόβλημα και όρια. |
| [market_and_data.md](market_and_data.md) | Με την επιθεώρηση κάθε νέας πηγής· κάλυψη και εφαρμοστέοι κανόνες. |
| [data_contract.md](data_contract.md) | Πριν από τον reader· σχήμα, μονάδες και χρονισμός. |
| [mathematical_model.md](mathematical_model.md) | Πριν από optimization και σε κάθε αλλαγή διατύπωσης. |
| [research_protocol.md](research_protocol.md) | Πριν από πείραμα· παγωμένα splits, baselines και stop rules. |
| [architecture.md](architecture.md) | Πριν από modules· ευθύνες και όρια πρόσβασης στην πληροφορία. |
| [implementation_order.md](implementation_order.md) | Το παρόν πλάνο· κατάσταση σταδίων και εξαρτήσεις. |
| [operations.md](operations.md) | Πριν από risk/engine και ξανά πριν από demo· failure handling. |
| [data/README.md](../data/README.md) | Οδηγίες αποθήκευσης πρωτογενών και παράγωγων δεδομένων. |
| [notebooks/README.md](../notebooks/README.md) | Κανόνες για μελλοντικά έγκυρα notebooks. |
| [outputs/README.md](../outputs/README.md) | Οργάνωση και provenance παραγόμενων αναφορών. |

## Κενοί φάκελοι

Τα data/raw/.gitkeep, data/processed/.gitkeep, outputs/reports/.gitkeep, outputs/figures/.gitkeep και outputs/logs/.gitkeep είναι κενά markers για το Git. Δεν αποκτούν επιχειρησιακό περιεχόμενο.

## Ορόσημα

1. Ελεγμένη εισαγωγή δεδομένων και χρονική ευθυγράμμιση.
2. Βασικό backtest με συμφωνημένο ledger.
3. Φυσικά εφικτός ντετερμινιστικός optimizer.
4. Χρονικά ορθή αξιολόγηση forecasting και σεναρίων.
5. Αναφορές και dashboard με ελεγχόμενα failure scenarios.

Η συγγραφή αρχείου, το στατικό review, η επιτυχής εκτέλεση και η ερευνητική επιβεβαίωση είναι διαφορετικές καταστάσεις. Καμία δεν υποκαθιστά την επόμενη.
