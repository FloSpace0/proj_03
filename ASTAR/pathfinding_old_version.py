from .search_problem import SearchProblem
import heapq
from geopy.distance import geodesic
import pandas as pd
import os
import re #serve per andare a modificare le String in modo più rapido

class PriorityQueue:
    def __init__(self):
        self.pq = []  # lista per la coda con priorità
        self.counter = 0  # contatore per gestire l'ordine di inserimento

    def push(self, item, priority):
        # Inserisce un elemento nella coda con priorità
        heapq.heappush(self.pq, (priority, self.counter, item))
        self.counter += 1

    def pop(self):
        # Rimuove e restituisce l'elemento con la priorità più alta
        return heapq.heappop(self.pq)[-1]
    
    def empty(self):
        return len(self.pq) == 0

class PathFinding(SearchProblem):
    def __init__(self, init_lat, init_lon, job_title):
        # Inizializza con la posizione dell'utente e il tipo di lavoro desiderato
        self.init_lat = float(init_lat)
        self.init_lon = float(init_lon)
        self.job_title = job_title
        
        # Definisci i percorsi dei file di dati in base alla struttura del progetto
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        
        # Carica i dataset necessari
        try:
            self.jobs_df = pd.read_csv(os.path.join(data_dir, "job_descriptions.csv"), encoding="utf-8")
        except Exception as e:
            print(f"Errore nel caricare il file dei lavori: {e}")
            # Crea un DataFrame vuoto come fallback
            self.jobs_df = pd.DataFrame(columns=['Job Title', 'Country', 'Salary Range', 'location', 'latitude', 'longitude'])
        
        try:
            self.cost_df = pd.read_csv(os.path.join(data_dir, "Cost_of_Living_Index_2022.csv"), encoding="utf-8")
        except Exception as e:
            print(f"Errore nel caricare il file del costo della vita: {e}")
            # Crea un DataFrame vuoto come fallback
            self.cost_df = pd.DataFrame(columns=['Country', 'Cost of Living Index', 'Rent Index'])
        
        # Lo stato iniziale è la posizione dell'utente
        init_state = {
            'latitude': self.init_lat,
            'longitude': self.init_lon,
            'job': None,
            'country': self.get_country_from_coordinates(self.init_lat, self.init_lon)
        }
        
        # Lo stato goal è trovare uno dei migliori 10 lavori
        # Non abbiamo un vero goal state, quindi lo impostiamo a None
        goal_state = None
        
        # Le azioni sono i possibili lavori a cui candidarsi
        self.actions = ["apply_to_job"]
        
        # Inizializza la classe padre
        super().__init__(init_state, goal_state, [(a, 1) for a in self.actions])
        
        # Trova tutti i lavori disponibili per il titolo richiesto
        self.available_jobs = self.find_available_jobs()
    
    def get_country_from_coordinates(self, lat, lon):
        # In un'implementazione reale, questa funzione dovrebbe determinare il paese 
        # in base alle coordinate usando un servizio di geocoding
        # Per semplicità, usiamo un valore predefinito
        return "Italy"
    
    def find_available_jobs(self):
        # Ottiene tutti i lavori che corrispondono al titolo desiderato
        jobs = self.jobs_df.loc[self.jobs_df['Job Title'] == self.job_title]
        return jobs
    
    @staticmethod
    def calcolaDistanza(lat_init, lon_init, lat_fin, lon_fin) -> float:
        start = (float(lat_init), float(lon_init))
        end = (float(lat_fin), float(lon_fin))
        distanza = geodesic(start, end).km
        return round(distanza, 2)
    
    def getSuccessors(self, state) -> list:
        """
        Ottiene tutti i possibili stati successivi dato lo stato corrente.
        Ogni successore rappresenta l'accettazione di un'offerta di lavoro.
        """
        successori = []
        
        for _, job in self.available_jobs.iterrows():
            distanza = self.calcolaDistanza(state['latitude'], state['longitude'], job['latitude'], job['longitude'])
            
            # Crea un nuovo stato per questo lavoro
            new_state = {
                'latitude': job['latitude'],
                'longitude': job['longitude'],
                'job': job,
                'country': job['Country'],
                'distanza': distanza
            }
            
            # L'azione è "apply_to_job" con i dettagli del lavoro
            action = f"apply_to_job:{job['location']}"
            
            # Il costo è calcolato dalla nostra euristica
            costo = self.calculate_cost(state, new_state)
            
            successori.append((new_state, action, costo))
        
        return successori
    
    def calculate_cost(self, current_state, new_state):
        """
        Calcola il costo di passare dallo stato corrente al nuovo stato.
        Il costo è (costo della vita + affitto medio - stipendio) / distanza
        """
        job = new_state['job']
        distanza = new_state['distanza']
        
        # Ottiene il costo della vita e l'affitto per il paese del lavoro dal dataset
        cost_living_rent = self.get_cost_and_rent(job['Country'])
        cost_of_living = cost_living_rent['cost_of_living']
        rent = cost_living_rent['rent']
        
        # Estrae lo stipendio dal range salariale
        salary = self.extract_salary(job['Salary Range'])
        
        g = distanza * 1000
        h = cost_of_living + rent - salary

        # Calcola il costo finale
        cost = g + h
        
        # Normalizziamo per avere valori positivi (per A*)
        # normalized_cost = max(0.1, cost + 1000)  # Assicura che il costo sia positivo
        
        return cost
    
    def isGoal(self, state) -> bool:
        """
        In questo problema non abbiamo un vero goal state, vogliamo trovare i migliori 10 lavori.
        Per A* dovremo usare una versione modificata dell'algoritmo.
        """
        return False  # Non raggiungiamo mai un goal in questo problema
    
    def get_cost_and_rent(self, country):
        """
        Ottiene l'indice del costo della vita e l'indice di affitto per un paese.
        Entrambi i valori sono nel dataset Cost_of_Living_Index_2022.csv
        """
        try:
            country_data = self.cost_df.loc[self.cost_df['Country'] == country]
            cost_of_living = country_data['Cost of Living Index'].values[0]
            rent = country_data['Rent Index'].values[0]
            return {
                'cost_of_living': float(cost_of_living),
                'rent': float(rent)
            }
        except (IndexError, KeyError, ValueError) as e:
            print(f"Errore nel recuperare i dati per {country}: {e} | Country_data: {country_data}")
            # Se il paese non è nel dataset, usa valori medi
            return {
                'cost_of_living': 50.0,
                'rent': 30.0
            }
    
    def extract_salary(self, salary_range):
        """
        Estrae un valore numerico da una stringa che rappresenta un intervallo di stipendio.

        LIBRERIA USATA = re
        """
        try:
            # Converte in stringa se non lo è già
            salary_range = str(salary_range).strip()
            
            # Rimuovi simboli di valuta e spazi
            cleaned = re.sub(r'[$€£¥]', '', salary_range)
            
            # Gestisci K/k (migliaia)
            cleaned = re.sub(r'([0-9]+(?:\.[0-9]+)?)[Kk]', lambda m: str(float(m.group(1)) * 1000), cleaned)
            
            # Estrai tutti i numeri
            numbers = re.findall(r'\d+(?:\.\d+)?', cleaned)
            
            if len(numbers) >= 2:
                # Se ci sono almeno 2 numeri, prendi i primi due come min e max
                min_salary = float(numbers[0])
                max_salary = float(numbers[1])
                return (min_salary + max_salary) / 2
            elif len(numbers) == 1:
                # Se c'è solo un numero, usalo direttamente
                return float(numbers[0])
            else:
                # Se non ci sono numeri, usa il valore predefinito
                return 50000.0
        
        except Exception as e:
            print(f"Errore nell'estrarre lo stipendio da '{salary_range}': {e}")
            return 50000.0
        

        
    def find_best_jobs(self, top_n=5):
        """
        Trova i migliori n lavori usando una versione modificata di A*.
        Restituisce una lista ordinata dei migliori lavori.
        """
        # Creiamo una coda con priorità per i lavori
        best_jobs = PriorityQueue()
        
        # Per ogni lavoro disponibile
        for _, job in self.available_jobs.iterrows():
            # Calcola la distanza dalla posizione iniziale
            distanza = self.calcolaDistanza(self.init_lat, self.init_lon, job['latitude'], job['longitude'])
            
            # Crea uno stato per questo lavoro
            job_state = {
                'latitude': job['latitude'],
                'longitude': job['longitude'],
                'job': job,
                'country': job['Country'],
                'distanza': distanza
            }
            
            # Calcola il costo (utilizzando lo stato iniziale e il nuovo stato)
            costo = self.calculate_cost(self.init, job_state)
            
            # Aggiungi alla coda con priorità
            best_jobs.push((job, distanza, costo), costo)
        
        # Estrai i migliori n lavori
        result = []
        for _ in range(min(top_n, len(self.available_jobs))):
            if not best_jobs.empty():
                job, distanza, costo = best_jobs.pop()
                result.append({
                    'job': job,
                    'distanza': distanza,
                    'costo': costo
                })
        
        return result