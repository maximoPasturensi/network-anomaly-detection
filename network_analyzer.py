import pandas as pd
import numpy as np
import logging
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta
from typing import Tuple
import sqlite3

# Configuración de Logging profesional
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NetworkAnomalyDetector:
    def __init__(self, config: dict):
        self.config = config
        self.model = IsolationForest(
            contamination=self.config["contamination"], 
            random_state=self.config["random_seed"]
        )

    def generate_data(self) -> pd.DataFrame:
        """Simula ingesta de métricas desde nodos de red."""
        logging.info("Generando dataset de métricas de red...")
        np.random.seed(self.config["random_seed"])
        start_time = datetime.now()
        
        n = self.config["n_points"]
        df = pd.DataFrame({
            'timestamp': [start_time + timedelta(minutes=i) for i in range(n)],
            'bandwidth_mbps': np.random.normal(400, 30, n),
            'latency_ms': np.random.normal(15, 2, n),
            'packet_loss_pct': np.random.uniform(0, 0.5, n)
        })

        # Simulación de incidentes usando parámetros de configuración
        indices = np.random.choice(range(n), size=10, replace=False)
        t = self.config["thresholds"]
        df.loc[indices, 'bandwidth_mbps'] *= t["bandwidth_multiplier"]
        df.loc[indices, 'latency_ms'] += t["latency_spike"]
        df.loc[indices, 'packet_loss_pct'] += t["packet_loss_spike"]
        
        return df

    def run_inference(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica el modelo de Machine Learning sobre los datos."""
        logging.info("Ejecutando detección de anomalías...")
        features = self.config["features"]
        df['anomaly_status'] = self.model.fit_predict(df[features])
        return df
    
    def save_anomalies_to_db(self, results: pd.DataFrame, db_name: str = "network_alerts.db"):
        """Filtra las anomalías y las guarda en una base de datos SQL."""
        anomalies = results[results['anomaly_status'] == -1].copy()
        
        if anomalies.empty:
            logging.info("No se detectaron anomalías para guardar.")
            return
        # Establecer conexión y guardar datos
        conn = sqlite3.connect(db_name)
        try:
            # Guardamos las anomalías en una tabla llamada 'critical_events'
            anomalies.to_sql('critical_events', conn, if_exists='append', index=False)
            logging.info(f"Se han guardado {len(anomalies)} eventos críticos en {db_name}")
        finally:
            conn.close()