import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
from sklearn.model_selection import cross_val_score
import numpy as np

# Cargar datos combinados (real + sintéticos)
DATA_PATH = 'ml/datos_ml.csv'
print(f"Cargando datos desde: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)
print(f"Shape del dataset: {df.shape}")

# Features: todas las columnas de notas, cantidad y promedio de participaciones, asistencia
feature_cols = [
    col for col in df.columns
    if col not in ['alumno_id', 'materia_asignada_id', 'materia', 'ciclo', 'aprobado', 'fecha_corte', 'promedio_nota']
]
X = df[feature_cols].fillna(0)
y = df['aprobado']

# Revisar balance de clases
print('Conteo de clases (aprobado=1, no aprobado=0):')
print(y.value_counts())
if y.value_counts().min() / y.value_counts().max() < 0.2:
    print('ADVERTENCIA: El dataset está muy desbalanceado. Considera técnicas de balanceo adicionales.')

# Separar en entrenamiento y prueba (estratificado para mantener proporción de clases)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

# Entrenar modelo Random Forest Classifier con balanceo de clases
model = RandomForestClassifier(n_estimators=200, random_state=42, class_weight='balanced_subsample', max_depth=10, min_samples_leaf=5)
model.fit(X_train, y_train)

# Evaluar modelo
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Accuracy: {acc:.3f}")
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("Classification Report:")
print(classification_report(y_test, y_pred, digits=3))

# Robustez extra: validación cruzada y feature importance

# Validación cruzada (5-fold)
scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
print(f"Accuracy promedio (5-fold CV): {np.mean(scores):.3f} ± {np.std(scores):.3f}")

# Importancia de features
importances = model.feature_importances_
feature_importance = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)
print("Top 10 features más importantes:")
for feat, imp in feature_importance[:10]:
    print(f"{feat}: {imp:.4f}")

# Revisión rápida de fuga de información: correlación de features con el target
correlations = df[feature_cols + ['aprobado']].corr()['aprobado'].abs().sort_values(ascending=False)
print('Features más correlacionados con el target (posible fuga de información si es 1.0):')
print(correlations.head(10))

# Guardar modelo entrenado
joblib.dump(model, 'ml/modelo_random_forest_clf.pkl')
print("Modelo de clasificación guardado en ml/modelo_random_forest_clf.pkl")
