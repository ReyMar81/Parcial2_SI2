import pandas as pd
import numpy as np

# Cargar el CSV original para obtener materias_asignadas reales y columnas de notas
csv_path = 'ml/datos_ml.csv'
df_full = pd.read_csv(csv_path)

# Usar tuplas reales de (materia_asignada_id, materia, ciclo)
materias_asignadas = df_full[['materia_asignada_id', 'materia', 'ciclo']].drop_duplicates().values.tolist()
note_columns = [col for col in df_full.columns if '_1' in col or '_2' in col or '_Final' in col or 'Tarea' in col or 'Examen' in col or 'Exposición' in col]

rng = np.random.default_rng()
alumno_id = int(df_full['alumno_id'].max()) + 1 if not df_full.empty else 10000

# Generar 5000 registros sintéticos de reprobados
n_reprobados = 5000
nuevos_registros = []
for _ in range(n_reprobados):
    materia_asignada_id, materia, ciclo = rng.choice(materias_asignadas)
    features = {
        'alumno_id': alumno_id,
        'materia_asignada_id': materia_asignada_id,
        'materia': materia,
        'ciclo': ciclo,
        'fecha_corte': rng.choice(pd.date_range('2022-03-01', '2024-12-01', freq='W')),
    }
    # Notas bajas y dispersas
    for col in note_columns:
        if 'Examen Final' in col:
            features[col] = np.nan  # No usar nota final para predicción progresiva
        else:
            features[col] = rng.uniform(20, 50) if rng.random() < 0.7 else np.nan
    # Participación y asistencia bajas
    features['cantidad_participaciones'] = rng.integers(0, 2)
    features['porcentaje_participacion'] = rng.uniform(0, 0.3)
    features['promedio_participacion'] = rng.uniform(0, 4)
    features['porcentaje_asistencia'] = rng.uniform(0.2, 0.6)
    features['promedio_nota'] = rng.uniform(30, 50)
    features['aprobado'] = 0
    nuevos_registros.append(features)
    alumno_id += 1

# Guardar los sintéticos
cols = df_full.columns.tolist()
df_nuevos = pd.DataFrame(nuevos_registros)[cols]
output_path = 'ml/datos_ml_sinteticos_reprobados.csv'
df_nuevos.to_csv(output_path, index=False)
print(f"Generados {n_reprobados} registros sintéticos de reprobados en {output_path}")
