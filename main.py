import matplotlib.pyplot as plt
import logging
from network_analyzer import NetworkAnomalyDetector
from database_manager import DatabaseManager # Importamos tu nueva clase
from config import SETTINGS

# Configuración básica de logging para ver qué pasa con la DB
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # 1. Inicialización de componentes
    detector = NetworkAnomalyDetector(SETTINGS)
    db = DatabaseManager()
    
    # 2. Preparación de la Infraestructura
    # Intentamos inicializar la DB. Si falla, el programa sigue.
    db.init_db()
    
    # 3. Ejecución del Pipeline de Datos e Inferencia
    logging.info("Iniciando análisis de red...")
    data = detector.generate_data()
    results = detector.run_inference(data)
    
    # 4. Filtrado de alertas (Anomalías detectadas por el modelo)
    anomalies = results[results['anomaly_status'] == -1].copy()
    
    # 5. Persistencia de Datos (SQL)
    # Aquí es donde demostrás que sabés integrar Python con MySQL
    if not anomalies.empty:
        db.save_alerts(anomalies)
    else:
        logging.info("No se detectaron anomalías en este ciclo.")

    # 6. Visualización Técnica 
    plt.figure(figsize=(12, 6))
    plt.plot(results['timestamp'], results['latency_ms'], color='lightgray', alpha=0.5, label='Tráfico Normal')
    
    if not anomalies.empty:
        plt.scatter(anomalies['timestamp'], anomalies['latency_ms'], 
                    color='red', s=40, label='Alerta Crítica (Guardada en DB)')
    
    plt.title('Sistema de Observabilidad ISP - Detección de Anomalías', fontsize=14)
    plt.xlabel('Tiempo')
    plt.ylabel('Latencia (ms)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    print(f"\n" + "="*30)
    print(f"--- REPORTE FINAL DE OPERACIONES ---")
    print(f"Eventos analizados: {len(results)}")
    print(f"Anomalías persistidas en MySQL: {len(anomalies)}")
    print("="*30)
    
    plt.show()

if __name__ == "__main__":
    main()