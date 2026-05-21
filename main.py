from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API Mobile - Biblioteca de Jogos")

# Configuração exata baseada na documentação oficial do FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # Permite acesso de qualquer lugar (Expo, Navegador, etc.)
    allow_credentials=False, # OBRIGATÓRIO ser False quando allow_origins for ["*"]
    allow_methods=["*"],     # Libera todos os métodos (GET, POST, PUT, DELETE)
    allow_headers=["*"],     # Libera todos os cabeçalhos
)

# Arquivo onde os dados ficarão salvos para sempre (Persistência)
ARQUIVO_DADOS = "jogos.json"

# ==========================================
# FUNÇÕES DO BANCO DE DADOS (JSON)
# ==========================================

def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        dados_iniciais = [
            {"id": 1, "nome": "The Legend of Zelda", "tipo": "Aventura", "nota": 10, "review": "Um clássico absoluto."},
            {"id": 2, "nome": "FIFA 23", "tipo": "Esporte", "nota": 7, "review": "Bom para jogar com amigos."}
        ]
        salvar_dados(dados_iniciais)
        return dados_iniciais
    with open(ARQUIVO_DADOS, "r", encoding="utf-8") as file:
        return json.load(file)

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as file:
        json.dump(dados, file, indent=4, ensure_ascii=False)

# ==========================================
# MODELOS DE DADOS
# ==========================================

class LoginRequest(BaseModel):
    email: str
    password: str

class JogoRequest(BaseModel):
    nome: str
    tipo: str
    nota: int
    review: str

# ==========================================
# ENDPOINTS (As rotas que vão pro Thunder Client)
# ==========================================

@app.post("/login")
def login(dados: LoginRequest):
    if dados.email == "usuario@esoft.com" and dados.password == "Abc123":
        return {"token": "550e8400-e29b-41d4-a716-446655440000"}
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

@app.get("/jogos")
def listar_jogos():
    return carregar_dados()

@app.get("/jogos/{id}")
def buscar_jogo(id: int):
    jogos = carregar_dados()
    for jogo in jogos:
        if jogo["id"] == id:
            return jogo
    raise HTTPException(status_code=404, detail="Jogo não encontrado")

@app.post("/jogos", status_code=status.HTTP_201_CREATED)
def cadastrar_jogo(jogo_novo: JogoRequest):
    jogos = carregar_dados()
    novo_id = max([jogo["id"] for jogo in jogos], default=0) + 1
    
    novo_jogo_dict = jogo_novo.model_dump()
    novo_jogo_dict["id"] = novo_id
    
    jogos.append(novo_jogo_dict)
    salvar_dados(jogos)
    return novo_jogo_dict

@app.put("/jogos/{id}")
def atualizar_jogo(id: int, jogo_atualizado: JogoRequest):
    jogos = carregar_dados()
    for index, jogo in enumerate(jogos):
        if jogo["id"] == id:
            dados_atualizados = jogo_atualizado.model_dump()
            dados_atualizados["id"] = id
            
            jogos[index] = dados_atualizados
            salvar_dados(jogos)
            return dados_atualizados
    raise HTTPException(status_code=404, detail="Jogo não encontrado")

@app.delete("/jogos/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_jogo(id: int):
    jogos = carregar_dados()
    for index, jogo in enumerate(jogos):
        if jogo["id"] == id:
            jogos.pop(index)
            salvar_dados(jogos)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail="Jogo não encontrado")