1) **preprocessing_pdr.py**:
   qui abbiamo il preprocessing di pdr (missing data handling, univariate variables handling, ...), qui abbiamo solo la creazione della variablie new_evse_id per fare i join dopo e poi qualche variabile temporale estraendo mese e anno dalla data.
   Alla fine dello script creo un nuovo dataset chiamato "pdr_preprocessed.csv", se runni il codice te lo crea direttamente nella stessa cartella.
   RICORDATI DI CAMBIARE I PATH (IL DATASET INIZIALE è IL FULL DI PDR)
