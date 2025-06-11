import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

# Cargar datos de exámenes
DATA_PATH = 'ml/datos_ml_examenes.csv'
df = pd.read_csv(DATA_PATH)

# Crear columna 'aprobado_examen' (1 si target_nota >= 51, 0 si < 51)
df['aprobado_examen'] = (df['target_nota'] >= 51).astype(int)

# Features: todas las columnas de notas previas, asistencia y participación
feature_cols = [col for col in df.columns if (
    (col.startswith('Tarea') or col.startswith('Examen') or col.startswith('Exposición')) and not col == 'target_nota')]
feature_cols += ['porcentaje_asistencia', 'promedio_participacion']

X = df[feature_cols].fillna(0)
y = df['aprobado_examen']

# Separar en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entrenar modelo Random Forest Classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluar modelo
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Accuracy: {acc:.2f}")
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("Classification Report:")
print(classification_report(y_test, y_pred))

# Guardar modelo entrenado
joblib.dump(model, 'ml/modelo_random_forest_examen_clf.pkl')
print("Modelo de clasificación de exámenes guardado en ml/modelo_random_forest_examen_clf.pkl")
