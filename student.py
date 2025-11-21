from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
import sqlite3


app = FastAPI()

# Database setup
def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            course TEXT NOT NULL,
            score REAL NOT NULL
            
        )
    ''')
    conn.commit()
    conn.close()
 
init_db()

class Student(BaseModel):
    id: Optional[int] = Field(None, example=1)
    name: str = Field(..., example="John Doe")
    age: int = Field(..., example=20)
    course: str = Field(..., example="Mathematics")
    score: float = Field(..., example=85.5)

class   studentCreate(BaseModel):
    name: str = Field(..., example="John Doe")
    age: int = Field(..., example=20)
    course: str = Field(..., example="Mathematics")
    score: float = Field(..., example=85.5)

class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, example="John Doe")
    age: Optional[int] = Field(None, example=20)
    course: Optional[str] = Field(None, example="Mathematics")
    score: Optional[float] = Field(None, example=85.5)


@app.post("/students/", response_model=Student, status_code=status.HTTP_201_CREATED)
def create_student(student: studentCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO students (name, age, course, score)
        VALUES (?, ?, ?, ?)
    ''', (student.name, student.age, student.course, student.score))
    conn.commit()
    student_id = cursor.lastrowid
    conn.close()
    return Student(id=student_id, **student.dict())

@app.get("/students/", response_model=List[Student])
def get_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students')
    rows = cursor.fetchall()
    conn.close()
    return [Student(**row) for row in rows]

@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return Student(**row)

@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, student: StudentUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
    row = cursor.fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    
    updated_data = student.dict(exclude_unset=True)
    for key, value in updated_data.items():
        cursor.execute(f'UPDATE students SET {key} = ? WHERE id = ?', (value, student_id))
    
    conn.commit()
    cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
    updated_row = cursor.fetchone()
    conn.close()
    return Student(**updated_row)

@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
    row = cursor.fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    
    cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
    conn.commit()
    conn.close()
    return None