#---------- ESTRUTURA INICIAL ----------#
# Bibliotecas 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
from typing import List, Dict
import json
import os
from statistics import mean, median, stdev

# Entrypoint
app = FastAPI()

# Models
class Aluno(BaseModel):
    nome: str
    id: int
    notas: Dict[str, float] = {Field(default=lambda: {} )}

########################################

# #---------- FUNÇÕES ----------#
# Carregar arquivo com os dados do aluno (se existir)
ARQUIVO_ALUNOS = "alunos.json"

# Função para salvar os dados em arquivos
def salvar_alunos(alunos):
   with open(ARQUIVO_ALUNOS, "w") as f:
        json.dump(alunos, f)

# Função para ler os dados em arquivos
def carregar_alunos():
    try:
        with open(ARQUIVO_ALUNOS, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Lista de alunos
alunos = carregar_alunos()


# Validator (notas devem estar ser de 0 a 10)
def validar_nota(nota: float):
    if not 0 <= nota <= 10:
        raise HTTPException(status_code=400, detail="Nota inválida. A nota deve estar entre 0 e 10.")
    return round(nota, 1)

########################################

#---------- ENDPOINTS ---------#
# Root
@app.get("/")
def root():
    return{"Root": "Use '/docs' to access Swagger "}

# Get All Alunos
@app.get("/alunos")
def get_todos_alunos():
    return alunos

# Post Aluno
@app.post("/alunos")
def adicionar_aluno(aluno: Aluno):
    for disciplina, nota in aluno.notas.items():
        aluno.notas[disciplina] = validar_nota(nota)
    alunos.append(aluno.dict())
    salvar_alunos(alunos)
    return {"mensagem": "Aluno adicionado com sucesso!"}

# Get notas de um aluno pela id
@app.get("/alunos/{id}")
def get_notas_aluno(aluno_id: int):
    for aluno in alunos:
        if aluno["id"] == aluno_id:
            return aluno
    raise HTTPException(status_code=404, detail="Aluno não encontrado.")

# Get notas de uma disciplina específica (em ordem crescente com o nome dos alunos)
@app.get("/disciplinas/{disciplina}")
def get_notas_disciplina(disciplina_nome: str):
    notas_da_disciplina = []
    for aluno in alunos:
        if disciplina_nome in aluno["notas"]:
            notas_da_disciplina.append(
                {"aluno": aluno["nome"],
                 "nota": aluno["notas"][disciplina_nome]})
    if not notas_da_disciplina:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada ou sem notas.")
    notas_da_disciplina.sort(key=lambda x: x["nota"])
    return notas_da_disciplina

##### EXTRAS #####

# Get média, mediana e desvio padrão das notas de uma disciplina
@app.get("/disciplinas/{disciplina_nome}/estatisticas")
def get_estatisticas_disciplina(disciplina_nome: str):
    notas = []
    for aluno in alunos:
        if disciplina_nome in aluno["notas"]:
            notas.append(aluno["notas"][disciplina_nome])
    if not notas:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada ou sem notas.")
    return {
        "disciplina": disciplina_nome,
        "media": mean(notas),
        "mediana": median(notas),
        "desvio_padrao": stdev(notas) if len(notas) > 1 else 0,
    }

# Get alunos com média menor de que 6.0
@app.get("/alunos/reprovados/{aluno_id}")
def get_alunos_reprovador():
    alunos_reprovados = []
    for aluno in alunos:
        nota_baixa = False
        for disciplina, nota in aluno["notas"].items():
            if nota < 6.0:
                tem_baixo_desempenho = True
                alunos_reprovados.append(
                    {"aluno_id": aluno["id"], "nome": aluno["nome"], "disciplina": disciplina, "nota": nota}
                )
        if nota_baixa:
            pass
    return alunos_reprovados

# Delete alunos com nenhuma nota registrada em nenhuma disciplina
@app.delete("/disciplinas/{disciplina}/alunos")
def delete_alunos_sem_notas():
    global alunos 
    alunos_com_notas = [aluno for aluno in alunos if aluno["notas"]]
    if len(alunos) != len(alunos_com_notas):
        alunos = alunos_com_notas
        salvar_alunos(alunos)
        return {"mensagem": "Alunos sem notas removidos com sucesso!"}
    else:
        return {"mensagem": "Nenhum aluno sem notas encontrado."}

#---------- INICIAÇÃO AUTOMÁTICA ---------#
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

#---------- REFERÊNCIAS ---------#
# FastAPI. Disponível em: https://fastapi.tiangolo.com/tutorial/first-steps. Acesso em 07/06/2024.
 
# Dezani, H. Materiais e exercícios das aulas. 2024.

# Programando Com Roger. COMO CRIAR UMA API EM PYTHON COM FASTAPI; YouTube, 13 de Julho de 2020. Disponível em: https://www.youtube.com/watch?v=bX5NrUWHqyo. Acesso em: 11 de Junho de 2024

# Python and FastAPI tutorial in Visual Studio Code https://code.visualstudio.com/docs/python/tutorial-fastapi 