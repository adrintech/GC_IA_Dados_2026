import httpx
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="API Casa de Suco",
    description="API para gerenciamento de sucos com consulta nutricional via Fruityvice",
    version="1.0.0"
)

banco_de_dados_sucos = {}
id_counter = 1

FRUITYVICE_BASE_URL = "https://www.fruityvice.com/api/fruit/"


class SucoEntrada(BaseModel):
    nome: str
    frutas: List[str]
    tem_gosto_de: str


class SucoResposta(BaseModel):
    id: int
    nome: str
    frutas: List[str]
    tem_gosto_de: str
    total_calorias: float
    total_acucar: float


class FrutaResposta(BaseModel):
    nome: str
    calorias: float
    acucar: float


async def consultar_fruityvice(nome_fruta: str) -> dict:
    url = f"{FRUITYVICE_BASE_URL}{nome_fruta.lower().strip()}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Erro ao se comunicar com a API Fruityvice. Verifique sua conexão."
            )

    if response.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fruta '{nome_fruta}' não foi encontrada na base de dados (tente o nome em inglês)."
        )
    
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro inesperado na resposta da API Fruityvice."
        )
        
    return response.json()


@app.get("/")
async def root():
    return {"mensagem": "API Casa de Suco no ar! Acesse /docs para a documentação interativa."}


@app.get("/frutas/{nome}", response_model=FrutaResposta)
async def obter_fruta(nome: str):
    dados = await consultar_fruityvice(nome)
    nutricao = dados.get("nutritions", {})
    
    return FrutaResposta(
        nome=dados.get("name", nome),
        calorias=round(float(nutricao.get("calories", 0)), 2),
        acucar=round(float(nutricao.get("sugar", 0)), 2)
    )


@app.post("/sucos", response_model=SucoResposta, status_code=status.HTTP_201_CREATED)
async def cadastrar_suco(suco: SucoEntrada):
    global id_counter
    
    if not suco.frutas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A lista de frutas não pode estar vazia."
        )

    calorias_totais = 0.0
    acucar_total = 0.0

    for fruta in suco.frutas:
        dados = await consultar_fruityvice(fruta)
        nutricao = dados.get("nutritions", {})
        calorias_totais += float(nutricao.get("calories", 0))
        acucar_total += float(nutricao.get("sugar", 0))

    novo_suco = {
        "id": id_counter,
        "nome": suco.nome,
        "frutas": suco.frutas,
        "tem_gosto_de": suco.tem_gosto_de,
        "total_calorias": round(calorias_totais, 2),
        "total_acucar": round(acucar_total, 2)
    }

    banco_de_dados_sucos[id_counter] = novo_suco
    id_counter += 1

    return novo_suco


@app.get("/sucos", response_model=List[SucoResposta])
async def listar_sucos():
    return list(banco_de_dados_sucos.values())


@app.put("/sucos/{id_suco}", response_model=SucoResposta)
async def atualizar_suco(id_suco: int, suco_atualizado: SucoEntrada):
    if id_suco not in banco_de_dados_sucos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Suco com ID {id_suco} não encontrado."
        )

    if not suco_atualizado.frutas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A lista de frutas não pode estar vazia."
        )

    calorias_totais = 0.0
    acucar_total = 0.0

    for fruta in suco_atualizado.frutas:
        dados = await consultar_fruityvice(fruta)
        nutricao = dados.get("nutritions", {})
        calorias_totais += float(nutricao.get("calories", 0))
        acucar_total += float(nutricao.get("sugar", 0))

    suco_editado = {
        "id": id_suco,
        "nome": suco_atualizado.nome,
        "frutas": suco_atualizado.frutas,
        "tem_gosto_de": suco_atualizado.tem_gosto_de,
        "total_calorias": round(calorias_totais, 2),
        "total_acucar": round(acucar_total, 2)
    }

    banco_de_dados_sucos[id_suco] = suco_editado
    return suco_editado