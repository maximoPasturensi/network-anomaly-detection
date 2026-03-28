import sqlite3
import logging
import pandas as pd

class DatabaseManager:
    def __init__(self):
        # SQLite usa un archivo local en lugar de un servidor
        self.db_name = 'sopnet_monitoring.db'

    def init_db(self):
        """Crea la tabla de alertas en un archivo local .db"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            query = """
            CREATE TABLE IF NOT EXISTS network_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                bandwidth_mbps FLOAT,
                latency_ms FLOAT,
                packet_loss_pct FLOAT,
                severity TEXT,
                ticket_status TEXT DEFAULT 'Open'
            )
            """
            cursor.execute(query)
            conn.commit()
            logging.info("Base de datos SQLite inicializada correctamente.")
        except Exception as e:
            logging.error(f"Error al inicializar SQLite: {e}")
        finally:
            conn.close()

    def save_alerts(self, df_anomalies: pd.DataFrame):
        """Filtra y guarda las anomalías en la base de datos."""
        if df_anomalies.empty:
            return
            
        try:
            conn = sqlite3.connect(self.db_name)
            
            # Creamos una copia para no modificar los datos originales
            to_save = df_anomalies.copy()
            
            # Agregamos la severidad (Lógica de negocio solicitada)
            to_save['severity'] = to_save['latency_ms'].apply(
                lambda x: 'Critical' if x > 80 else 'Medium'
            )
            
            # DEFINIMOS exactamente qué columnas queremos guardar en SQL
            # Esto ignora 'anomaly_status' y evita el error
            columnas_permitidas = [
                'timestamp', 'bandwidth_mbps', 'latency_ms', 
                'packet_loss_pct', 'severity'
            ]
            
            # Guardamos solo las columnas permitidas
            to_save[columnas_permitidas].to_sql(
                'network_alerts', 
                conn, 
                if_exists='append', 
                index=False
            )
            
            conn.commit()
            logging.info(f"Se guardaron {len(to_save)} alertas correctamente.")
        except Exception as e:
            logging.error(f"Error al guardar en DB: {e}")
        finally:
            conn.close()