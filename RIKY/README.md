1) **preprocessing_pdr.py**:
   qui abbiamo L'EDA di pdr (missing data handling, univariate variables handling, ...), qui abbiamo solo la creazione della variablie new_evse_id per fare i join dopo e poi qualche variabile temporale estraendo mese e anno dalla data. Abbiamo droppato molte colonne che erano brutte.
   Alla fine dello script creo un nuovo dataset chiamato "pdr_preprocessed.csv", se runni il codice te lo crea direttamente nella nella cartella chiamata data.
   RICORDATI DI CAMBIARE I PATH (IL DATASET INIZIALE è IL FULL DI PDR)

2. **data_integration.py**:
   qui abbiamo l'integration con le regioni e la popolazione. sono state droppate molte colonne e fatto tanti merge. Alcuni missing values sono stati trattati visto che nel merge non coincidevano il numero di colonnine.
   Alla fine dello script creo un nuovo dataset chiamato "task_2_df.csv", se runni il codice te lo crea direttamente nella cartella chiamata data.
   RICORDATI DI CAMBIARE I PATH (IL DATASET INIZIALE è il pdr_preprocessed con i diversi delle regioni). MANCA come dataset cdr_preprocessed che era troppo grande da pushare, mettilo dentro la cartella data E NON LO PUSHARE IN FUTUROOOOOOOOOO.
3. **last_dataset_creation.py**:
   aggiunto la colonna fatta da pami, e droppato alcune colonne.
   Alla fine dello script creo un nuovo dataset chiamato "riky_final.csv", se runni il codice te lo crea direttamente nella cartella chiamata data, questo serve per creare poi il FINAL dataset con uno script di david.
