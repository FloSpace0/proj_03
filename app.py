from flask import Flask, request, render_template, jsonify
from geopy.distance import geodesic
import pandas as pd
import os
from ASTAR.pathfinding import PathFinding

app = Flask(__name__)

# Configurazione base del progetto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Assicurati che la directory dei dati esista
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Carica i dataset all'avvio dell'applicazione per evitare di ricaricarli ad ogni richiesta
try:
    jobs_df = pd.read_csv(os.path.join(DATA_DIR, 'job_descriptions.csv'), encoding='utf-8')
except Exception as e:
    print(f"Errore nel caricare job_descriptions.csv: {e}")
    jobs_df = None

try:
    cost_df = pd.read_csv(os.path.join(DATA_DIR, 'Cost_of_Living_Index_2022.csv'), encoding='utf-8')
except Exception as e:
    print(f"Errore nel caricare Cost_of_Living_Index_2022.csv: {e}")
    cost_df = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calcola-distanza', methods=['POST'])
def calcola_distanza():
    data = request.get_json()
    start = (float(data['startLat']), float(data['startLng']))
    end = (float(data['endLat']), float(data['endLng']))
    distanza = geodesic(start, end).km
    return jsonify({'distanza_km': round(distanza, 2)})

@app.route('/test_dataset', methods=['GET'])
def test_dataset():
    if cost_df is not None:
        try:
            italy_cost = cost_df.loc[cost_df['Country'] == 'Italy', 'Cost of Living Index'].values[0]
            return jsonify({'Nazione test dataset Cost of Living Index': float(italy_cost)})
        except (IndexError, KeyError):
            return jsonify({'error': 'Dati per Italia non trovati'})
    else:
        return jsonify({'error': 'Dataset non disponibile'})

@app.route('/get_job_titles', methods=['GET'])
def get_job_titles():
    """
    Restituisce una lista di tutti i titoli di lavoro disponibili nel dataset.
    """
    if jobs_df is not None:
        job_titles = jobs_df['Job Title'].unique().tolist()
        return jsonify({'job_titles': job_titles})
    else:
        # Se il dataset non è disponibile, restituisce alcuni titoli di esempio
        return jsonify({'job_titles': ['Data Scientist', 'Software Engineer', 'Project Manager']})

'''
AI SEARCH METODO PER COMUNICARE CON IL WEBSITE
'''
@app.route('/find_best_jobs', methods=['POST'])
def find_best_jobs():
    """
    Trova i migliori lavori in base alla posizione dell'utente e al titolo del lavoro desiderato.
    """
    try:
        data = request.get_json()
        lat = data.get('latitude')
        lon = data.get('longitude')
        job_title = data.get('job_title')
        dalla_mia_posizione = data.get('dalla_mia_posizione', True)  # Default True
        
        if not lat or not lon or not job_title:
            return jsonify({'error': 'Dati mancanti. Fornire latitudine, longitudine e titolo del lavoro.'})
        
        # Imposta w in base alla scelta dell'utente
        if dalla_mia_posizione:
            w = 1
        else:
            w = 0
   
        # Crea un'istanza di PathFinding
        pathfinder = PathFinding(lat, lon, job_title)
        # Trova i migliori 10 lavori con il peso specificato
        best_jobs = pathfinder.find_best_jobs(w = w, top_n=20)
        
        # Formatta i risultati per la risposta JSON
        results = []
        for item in best_jobs:
            job = item['job']
            job_dict = {
                'job_title': job['Job Title'],
                'country': job['Country'],
                'location': job['location'],
                'salary_range': job['Salary Range'],
                'latitude': float(job['latitude']),
                'longitude': float(job['longitude']),
                'distanza': item['distanza'],
                'costo': item['costo']
            }
            results.append(job_dict)
        
        return jsonify({'best_jobs': results})
    
    except Exception as e:
        print(f"Errore nella ricerca dei migliori lavori: {e}")
        return jsonify({'error': f'Si è verificato un errore: {str(e)}'})
    

@app.route('/init_test_data', methods=['GET'])
def init_test_data():
    """
    Inizializza alcuni dati di test se non ci sono i file CSV richiesti.
    Questa route può essere chiamata per creare dati di test.
    """
    try:
        # Crea il file job_descriptions.csv se non esiste
        if not os.path.exists(os.path.join(DATA_DIR, 'job_descriptions.csv')):
            # Crea un DataFrame di esempio per job_descriptions
            job_data = {
                'Job Title': ['Data Scientist', 'Data Scientist', 'Data Scientist', 'Software Engineer', 'Software Engineer', 'Project Manager'],
                'Country': ['Italy', 'Germany', 'France', 'Italy', 'United Kingdom', 'Spain'],
                'Salary Range': ['50000-70000', '60000-80000', '55000-75000', '45000-65000', '50000-85000', '60000-90000'],
                'location': ['Milan', 'Berlin', 'Paris', 'Rome', 'London', 'Madrid'],
                'latitude': [45.4642, 52.5200, 48.8566, 41.9028, 51.5074, 40.4168],
                'longitude': [9.1900, 13.4050, 2.3522, 12.4964, -0.1278, -3.7038]
            }
            jobs_df = pd.DataFrame(job_data)
            jobs_df.to_csv(os.path.join(DATA_DIR, 'job_descriptions.csv'), index=False, encoding='utf-8')
            print("File job_descriptions.csv creato con successo")
        
        # Usa il dataset Cost_of_Living_Index_2022.csv che hai condiviso
        if not os.path.exists(os.path.join(DATA_DIR, 'Cost_of_Living_Index_2022.csv')):
            # Crea un file temporaneo con il contenuto del paste
            with open(os.path.join(DATA_DIR, 'Cost_of_Living_Index_2022.csv'), 'w', encoding='utf-8') as f:
                f.write("Rank,Country,Cost of Living Index,Rent Index,Cost of Living Plus Rent Index,Groceries Index,Restaurant Price Index,Local Purchasing Power Index\n")
                # Aggiungi le righe per vari paesi (qui solo alcuni esempi)
                f.write("59,Italy,66.47,20.55,44.95,57.95,70.58,61.74\n")
                f.write("44,Germany,65.58,27.62,47.78,52.31,60.91,103.08\n")
                f.write("42,France,74.13,25.33,51.26,73.64,71.84,85.41\n")
                f.write("131,United Kingdom,69.65,31.84,51.93,56.58,76.79,88.78\n")
                f.write("116,Spain,53.88,21.25,38.58,45.69,53.96,70.04\n")
                f.write("132,United States,70.13,42.07,56.98,70.37,70.07,106.34\n")
            
            print("File Cost_of_Living_Index_2022.csv creato con successo")
        
        return jsonify({
            'status': 'success',
            'message': 'Dati di test inizializzati correttamente. Ora puoi utilizzare l\'applicazione.'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Errore nell\'inizializzazione dei dati di test: {str(e)}'
        })
    

@app.route('/add_job', methods=['POST'])
def add_job():
    """
    Aggiunge una nuova offerta di lavoro al dataset.
    """
    global jobs_df
    try:
        data = request.get_json()
        
        # Validazione dei dati richiesti
        required_fields = ['job_title', 'country', 'salary_range', 'location', 'latitude', 'longitude']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'status': 'error',
                'message': f'Campi mancanti: {", ".join(missing_fields)}'
            }), 400
        
        # Carica il dataset esistente
        job_file_path = os.path.join(DATA_DIR, 'job_descriptions.csv')
        
        if os.path.exists(job_file_path):
            jobs_df = pd.read_csv(job_file_path, encoding='utf-8')
        else:
            # Se il file non esiste, crea un DataFrame vuoto con le colonne necessarie
            jobs_df = pd.DataFrame(columns=['Job Title', 'Company', 'Job Description', 'Requirements', 
                                            'Country', 'Salary Range', 'Currency', 'Employment Type', 
                                            'Experience Level', 'location', 'latitude', 'longitude', 
                                            'Remote', 'Posted Date'])
        
        # Prepara i dati per la nuova riga
        new_job = {
            'Job Title': data['job_title'],
            'Company': data.get('company', 'Azienda non specificata'),
            'Job Description': data.get('job_description', 'Descrizione non disponibile'),
            'Requirements': data.get('requirements', 'Requisiti non specificati'),
            'Country': data['country'],
            'Salary Range': data['salary_range'],
            'Currency': data.get('currency', 'EUR'),
            'Employment Type': data.get('employment_type', 'Full-time'),
            'Experience Level': data.get('experience_level', 'Mid-level'),
            'location': data['location'],
            'latitude': float(data['latitude']),
            'longitude': float(data['longitude']),
            'Remote': data.get('remote', False),
            'Posted Date': data.get('posted_date', pd.Timestamp.now().strftime('%Y-%m-%d'))
        }
        
        # Aggiungi la nuova riga al DataFrame
        jobs_df = pd.concat([jobs_df, pd.DataFrame([new_job])], ignore_index=True)
        
        # Salva il DataFrame aggiornato
        jobs_df.to_csv(job_file_path, index=False, encoding='utf-8')
        
        # Ricarica il dataset globale
        jobs_df = pd.read_csv(job_file_path, encoding='utf-8')
        
        return jsonify({
            'status': 'success',
            'message': 'Offerta di lavoro aggiunta con successo!',
            'job_id': len(jobs_df) - 1  # Restituisce l'indice della nuova riga
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Errore durante l\'aggiunta del lavoro: {str(e)}'
        }), 500

@app.route('/get_job_stats', methods=['GET'])
def get_job_stats():
    """
    Restituisce statistiche sui lavori disponibili (numero totale, paesi, ecc.)
    """
    try:
        if jobs_df is None or jobs_df.empty:
            return jsonify({
                'status': 'error',
                'message': 'Nessun dato disponibile'
            })
        
        stats = {
            'total_jobs': len(jobs_df),
            'unique_countries': len(jobs_df['Country'].unique()),
            'unique_job_titles': len(jobs_df['Job Title'].unique()),
            'countries': jobs_df['Country'].unique().tolist(),
            'job_titles': jobs_df['Job Title'].unique().tolist(),
            'cities': jobs_df['location'].unique().tolist()
        }
        
        return jsonify({
            'status': 'success',
            'stats': stats
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Errore nel recuperare le statistiche: {str(e)}'
        }), 500

@app.route('/validate_location', methods=['POST'])
def validate_location():
    """
    Valida se una località esiste nel dataset del costo della vita.
    Utile per suggerire nomi corretti prima di aggiungere un lavoro.
    """
    try:
        data = request.get_json()
        country = data.get('country')
        
        if not country:
            return jsonify({
                'status': 'error',
                'message': 'Nome del paese non fornito'
            })
        
        # Verifica se il paese esiste nel dataset
        if cost_df is not None:
            # Cerca match esatti o parziali
            exact_match = cost_df[cost_df['Country'].str.lower() == country.lower()]
            partial_matches = cost_df[cost_df['Country'].str.contains(country, case=False, na=False)]
            
            response_data = {
                'status': 'success',
                'exists': not exact_match.empty,
                'suggested_names': []
            }
            
            if not exact_match.empty:
                response_data['correct_name'] = exact_match.iloc[0]['Country']
            elif not partial_matches.empty:
                response_data['suggested_names'] = partial_matches['Country'].tolist()[:5]
            else:
                # Suggerisci i paesi più comuni se non trova corrispondenze
                common_countries = ['Italy', 'Germany', 'France', 'United Kingdom', 'Spain', 'United States']
                response_data['suggested_names'] = common_countries
            
            return jsonify(response_data)
        else:
            return jsonify({
                'status': 'error',
                'message': 'Dataset del costo della vita non disponibile'
            })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Errore nella validazione: {str(e)}'
        }), 500

@app.route('/get_location_coords', methods=['POST'])
def get_location_coords():
    """
    Restituisce le coordinate di una località basandosi su quelle già nel dataset.
    Utile per suggerire coordinate quando si aggiunge un nuovo lavoro.
    """
    try:
        data = request.get_json()
        location = data.get('location')
        country = data.get('country')
        
        if not location:
            return jsonify({
                'status': 'error',
                'message': 'Nome della località non fornito'
            })
        
        if jobs_df is not None:
            # Cerca lavori nella stessa località
            query = jobs_df['location'].str.lower() == location.lower()
            if country:
                query = query & (jobs_df['Country'].str.lower() == country.lower())
            
            matching_jobs = jobs_df[query]
            
            if not matching_jobs.empty:
                # Prendi le coordinate del primo match
                lat = matching_jobs.iloc[0]['latitude']
                lon = matching_jobs.iloc[0]['longitude']
                
                return jsonify({
                    'status': 'success',
                    'latitude': lat,
                    'longitude': lon,
                    'found': True
                })
            else:
                # Suggerisci coordinate basate sul paese
                country_jobs = jobs_df[jobs_df['Country'].str.lower() == country.lower()] if country else jobs_df
                
                if not country_jobs.empty:
                    # Calcola la media delle coordinate per quel paese
                    avg_lat = country_jobs['latitude'].mean()
                    avg_lon = country_jobs['longitude'].mean()
                    
                    return jsonify({
                        'status': 'success',
                        'latitude': avg_lat,
                        'longitude': avg_lon,
                        'found': False,
                        'suggestion': 'Coordinate suggerite basate sulla media del paese'
                    })
                else:
                    # Default: centro d'Europa
                    return jsonify({
                        'status': 'success',
                        'latitude': 46.0,
                        'longitude': 8.0,
                        'found': False,
                        'suggestion': 'Coordinate predefinite (centro Europa)'
                    })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Dataset dei lavori non disponibile'
            })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Errore nel recuperare le coordinate: {str(e)}'
        }), 500
    

'''
METODI SULLE CITTÀ
'''
@app.route('/add_city', methods=['POST'])
def add_city():
    """
    Aggiunge una nuova città/paese al dataset del costo della vita.
    """
    global cost_df  # Dichiara la variabile global all'inizio
    
    try:
        data = request.get_json()
        
        # Validazione dei dati richiesti
        required_fields = ['country_name', 'cost_of_living', 'rent_index', 'latitude', 'longitude']
        missing_fields = [field for field in required_fields if field not in data or data[field] == '']
        
        if missing_fields:
            return jsonify({
                'status': 'error',
                'message': f'Campi mancanti: {", ".join(missing_fields)}'
            }), 400
        
        # Carica il dataset esistente
        cost_file_path = os.path.join(DATA_DIR, 'Cost_of_Living_Index_2022.csv')
        
        if os.path.exists(cost_file_path):
            current_cost_df = pd.read_csv(cost_file_path, encoding='utf-8')
        else:
            # Se il file non esiste, crea un DataFrame vuoto con le colonne necessarie
            current_cost_df = pd.DataFrame(columns=['Rank', 'Country', 'Cost of Living Index', 'Rent Index', 
                                                   'Cost of Living Plus Rent Index', 'Groceries Index', 
                                                   'Restaurant Price Index', 'Local Purchasing Power Index'])
        
        # Verifica se il paese/città esiste già
        if data['country_name'] in current_cost_df['Country'].values:
            return jsonify({
                'status': 'error',
                'message': f'La località "{data["country_name"]}" esiste già nel database'
            }), 400
        
        # Calcola il nuovo rank (ultimo + 1)
        new_rank = 1 if current_cost_df.empty else current_cost_df['Rank'].max() + 1
        
        # Calcola il Cost of Living Plus Rent Index (media dei due)
        cost_living = float(data['cost_of_living'])
        rent = float(data['rent_index'])
        combined_index = (cost_living + rent) / 2
        
        # Prepara i dati per la nuova riga
        new_city = {
            'Rank': new_rank,
            'Country': data['country_name'],
            'Cost of Living Index': cost_living,
            'Rent Index': rent,
            'Cost of Living Plus Rent Index': combined_index,
            'Groceries Index': data.get('groceries_index', 50.0),  # Valore di default se non fornito
            'Restaurant Price Index': data.get('restaurant_index', 50.0),  # Valore di default se non fornito
            'Local Purchasing Power Index': data.get('purchasing_power', 50.0)  # Valore di default se non fornito
        }
        
        # Aggiungi la nuova riga al DataFrame
        current_cost_df = pd.concat([current_cost_df, pd.DataFrame([new_city])], ignore_index=True)
        
        # Salva il DataFrame aggiornato
        current_cost_df.to_csv(cost_file_path, index=False, encoding='utf-8')
        
        # Ricarica il dataset globale
        cost_df = pd.read_csv(cost_file_path, encoding='utf-8')
        
        # Salva anche le coordinate in un file separato per riferimento
        coords_file_path = os.path.join(DATA_DIR, 'city_coordinates.csv')
        
        # Carica o crea il file delle coordinate
        if os.path.exists(coords_file_path):
            coords_df = pd.read_csv(coords_file_path, encoding='utf-8')
        else:
            coords_df = pd.DataFrame(columns=['Country', 'latitude', 'longitude'])
        
        # Aggiungi le coordinate se non esistono già
        if data['country_name'] not in coords_df['Country'].values:
            new_coords = {
                'Country': data['country_name'],
                'latitude': float(data['latitude']),
                'longitude': float(data['longitude'])
            }
            coords_df = pd.concat([coords_df, pd.DataFrame([new_coords])], ignore_index=True)
            coords_df.to_csv(coords_file_path, index=False, encoding='utf-8')
        
        return jsonify({
            'status': 'success',
            'message': f'Città/Paese "{data["country_name"]}" aggiunta con successo!',
            'city_data': new_city
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Errore durante l\'aggiunta della città: {str(e)}'
        }), 500

@app.route('/get_city_stats', methods=['GET'])
def get_city_stats():
    """
    Restituisce statistiche sulle città/paesi disponibili.
    """
    try:
        if cost_df is None or cost_df.empty:
            return jsonify({
                'status': 'error',
                'message': 'Nessun dato disponibile'
            })
        
        # Conta le città/paesi per range di costo della vita
        cost_ranges = {
            'Molto economico (0-30)': len(cost_df[cost_df['Cost of Living Index'] <= 30]),
            'Economico (30-50)': len(cost_df[(cost_df['Cost of Living Index'] > 30) & (cost_df['Cost of Living Index'] <= 50)]),
            'Medio (50-70)': len(cost_df[(cost_df['Cost of Living Index'] > 50) & (cost_df['Cost of Living Index'] <= 70)]),
            'Costoso (70-90)': len(cost_df[(cost_df['Cost of Living Index'] > 70) & (cost_df['Cost of Living Index'] <= 90)]),
            'Molto costoso (90+)': len(cost_df[cost_df['Cost of Living Index'] > 90])
        }
        
        stats = {
            'total_cities': len(cost_df),
            'avg_cost_of_living': cost_df['Cost of Living Index'].mean(),
            'avg_rent': cost_df['Rent Index'].mean(),
            'most_expensive': cost_df.loc[cost_df['Cost of Living Index'].idxmax()]['Country'],
            'least_expensive': cost_df.loc[cost_df['Cost of Living Index'].idxmin()]['Country'],
            'cost_ranges': cost_ranges
        }
        
        return jsonify({
            'status': 'success',
            'stats': stats
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Errore nel recuperare le statistiche: {str(e)}'
        }), 500

@app.route('/search_cities', methods=['POST'])
def search_cities():
    """
    Cerca città/paesi nel database per nome o caratteristiche.
    """
    try:
        data = request.get_json()
        search_term = data.get('search_term', '').lower()
        min_cost = data.get('min_cost')
        max_cost = data.get('max_cost')
        min_rent = data.get('min_rent')
        max_rent = data.get('max_rent')
        
        if cost_df is None or cost_df.empty:
            return jsonify({
                'status': 'error',
                'message': 'Nessun dato disponibile'
            })
        
        # Filtra il DataFrame
        filtered_df = cost_df.copy()
        
        # Filtro per nome
        if search_term:
            filtered_df = filtered_df[filtered_df['Country'].str.lower().str.contains(search_term)]
        
        # Filtro per costo della vita
        if min_cost is not None:
            filtered_df = filtered_df[filtered_df['Cost of Living Index'] >= min_cost]
        if max_cost is not None:
            filtered_df = filtered_df[filtered_df['Cost of Living Index'] <= max_cost]
        
        # Filtro per affitto
        if min_rent is not None:
            filtered_df = filtered_df[filtered_df['Rent Index'] >= min_rent]
        if max_rent is not None:
            filtered_df = filtered_df[filtered_df['Rent Index'] <= max_rent]
        
        # Converti il risultato in una lista di dizionari
        results = []
        for _, row in filtered_df.iterrows():
            results.append({
                'rank': int(row['Rank']),
                'country': row['Country'],
                'cost_of_living': float(row['Cost of Living Index']),
                'rent_index': float(row['Rent Index']),
                'combined_index': float(row['Cost of Living Plus Rent Index'])
            })
        
        return jsonify({
            'status': 'success',
            'results': results,
            'count': len(results)
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Errore nella ricerca: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)