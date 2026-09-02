import json
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(title="API Mobile - Biblioteca de Jogos")

# Configuração de CORS (mantida conforme projeto)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ARQUIVO_DADOS = Path("jogos.json")

# ==========================================
# MODELOS DE DADOS (PYDANTIC)
# ==========================================

class LoginRequest(BaseModel):
    # EmailStr valida automaticamente se o formato de e-mail é válido
    email: EmailStr
    password: str


class JogoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    tipo: str = Field(..., min_length=1, max_length=50)
    # Validação de nota entre 0 e 10
    nota: int = Field(..., ge=0, le=10, description="Nota de 0 a 10")
    review: str = Field(..., max_length=500)


class JogoRequest(JogoBase):
    pass


class JogoResponse(JogoBase):
    id: int


# ==========================================
# FUNÇÕES DE PERSISTÊNCIA (JSON)
# ==========================================

def carregar_dados() -> List[dict]:
    if not ARQUIVO_DADOS.exists():
        dados_iniciais = [
            {
                "id": 1,
                "nome": "The Legend of Zelda",
                "tipo": "Aventura",
                "nota": 10,
                "review": "Um clássico absoluto.",
            },
            {
                "id": 2,
                "nome": "FIFA 23",
                "tipo": "Esporte",
                "nota": 7,
                "review": "Bom para jogar com amigos.",
            },
        ]
        salvar_dados(dados_iniciais)
        return dados_iniciais

    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        # Recuperação graciosa caso o arquivo esteja corrompido/vazio
        return []


def salvar_dados(dados: List[dict]) -> None:
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as file:
        json.dump(dados, file, indent=4, ensure_ascii=False)


# ==========================================
# ENDPOINTS
# ==========================================

@app.post("/login")
def login(dados: LoginRequest) -> dict:
    # OBS: Em produção, armazene credenciais em variáveis de ambiente/banco de dados
    if dados.email == "usuario@esoft.com" and dados.password == "Abc123":
        return {"token": "550e8400-e29b-41d4-a716-446655440000"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas"
    )


@app.get("/jogos", response_model=List[JogoResponse])
def listar_jogos() -> List[dict]:
    return carregar_dados()


@app.get("/jogos/{id}", response_model=JogoResponse)
def buscar_jogo(id: int) -> dict:
    jogos = carregar_dados()
    # Busca idiomática do elemento pelo ID
    jogo = next((j for j in jogos if j["id"] == id), None)
    if jogo:
        return jogo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jogo não encontrado")


@app.post("/jogos", status_code=status.HTTP_201_CREATED, response_model=JogoResponse)
def cadastrar_jogo(jogo_novo: JogoRequest) -> dict:
    jogos = carregar_dados()

    # 'default=0' previne ValueError caso a lista esteja vazia
    proximo_id = max([j["id"] for j in jogos], default=0) + 1

    # Compatível com Pydantic v2 (.model_dump()) e fallback para v1 (.dict())
    novo_jogo_dict = getattr(jogo_novo, "model_dump", jogo_novo.dict)()
    novo_jogo_dict["id"] = proximo_id

    jogos.append(novo_jogo_dict)
    salvar_dados(jogos)
    return novo_jogo_dict


@app.put("/jogos/{id}", response_model=JogoResponse)
def atualizar_jogo(id: int, jogo_atualizado: JogoRequest) -> dict:
    jogos = carregar_dados()

    for index, jogo in enumerate(jogos):
        if jogo["id"] == id:
            dados_atualizados = getattr(jogo_atualizado, "model_dump", jogo_atualizado.dict)()
            dados_atualizados["id"] = id
            jogos[index] = dados_atualizados
            salvar_dados(jogos)
            return dados_atualizados

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jogo não encontrado")


@app.delete("/jogos/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_jogo(id: int) -> Response:
    jogos = carregar_dados()

    for index, jogo in enumerate(jogos):
        if jogo["id"] == id:
            jogos.pop(index)
            salvar_dados(jogos)
            return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jogo não encontrado")
