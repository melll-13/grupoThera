from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from .database import get_db

app = FastAPI(title="Grupo Thera Careers API")

# Enable CORS so your HTML frontend can talk to this backend smoothly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Bienvenido al backend de vacantes de Grupo Thera"}

@app.get("/api/vacantes")
def get_vacantes(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("""
            SELECT id, titulo, departamento, ubicacion, descripcion, 
                   objetivo, funciones, formacion_academica, formacion_tecnica, competencias, aptitudes 
            FROM vacantes WHERE activa = TRUE
        """)).fetchall()
        
        vacantes_list = [
            {
                "id": row[0],
                "titulo": row[1],
                "departamento": row[2],
                "ubicacion": row[3],
                "descripcion": row[4],
                "objetivo": row[5],
                "funciones": row[6],
                "formacion_academica": row[7],
                "formacion_tecnica": row[8],
                "competencias": row[9],
                "aptitudes": row[10]
            }
            for row in result
        ]
        return vacantes_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    






from pydantic import BaseModel

class PostulacionCreate(BaseModel):
    vacante_id: int
    nombre: str
    apellido: str
    correo: str
    telefono: str
    pais: str
    ciudad: str
    ruta_cv: str = "" # Opcional por ahora si no suben archivo de momento

@app.post("/api/postulaciones")
def crear_postulacion(postulacion: PostulacionCreate, db: Session = Depends(get_db)):
    try:
        query = text("""
            INSERT INTO postulaciones (vacante_id, nombre, apellido, correo, telefono, pais, ciudad, ruta_cv)
            VALUES (:vacante_id, :nombre, :apellido, :correo, :telefono, :pais, :ciudad, :ruta_cv)
            RETURNING id;
        """)
        result = db.execute(query, {
            "vacante_id": postulacion.vacante_id,
            "nombre": postulacion.nombre,
            "apellido": postulacion.apellido,
            "correo": postulacion.correo,
            "telefono": postulacion.telefono,
            "pais": postulacion.pais,
            "ciudad": postulacion.ciudad,
            "ruta_cv": postulacion.ruta_cv
        })
        db.commit()
        new_id = result.fetchone()[0]
        return {"message": "Postulación registrada con éxito", "id": new_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))