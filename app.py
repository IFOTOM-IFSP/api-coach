from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# =======================================================
# 1. LIVRO DE REGRAS (O Cérebro da IA)
# =======================================================

RULEBOOK = {
    'HIGH_ABS': {
        'level': 'Alto',
        'title': 'Absorbância Alta',
        'sugestao': 'Dilua sua amostra (1:2) e repita.',
        'explicacao': 'Leitura fora da faixa confiável (saturação).',
        'risk_impact': 40,
        'id': 'ERR_ABS_HIGH'
    },
    'ERR_R2_LOW': {
        'level': 'Alto',
        'title': 'Curva de Calibração Ruim',
        'sugestao': 'Revise seus padrões e refaça a curva.',
        'explicacao': 'Seus pontos-padrão não formam uma linha reta.',
        'risk_impact': 50,
        'id': 'ERR_R2_LOW'
    },
    'HIGH_CV': {
        'level': 'Médio',
        'title': 'Alta Variação (Ruído)',
        'sugestao': 'Repita a leitura desta amostra.',
        'explicacao': 'A leitura está instável (ex: bolhas, sujeira).',
        'risk_impact': 25,
        'id': 'WARN_CV_HIGH'
    },
    'HIGH_INTERCEPT': {
        'level': 'Médio',
        'title': '"Branco" da Curva Alto',
        'sugestao': 'Verifique seu reagente "Branco" (Zero).',
        'explicacao': 'Sua curva não está começando do zero.',
        'risk_impact': 30,
        'id': 'WARN_INTERCEPT_HIGH'
    },
    'NEGATIVE_ABS': {
        'level': 'Médio',
        'title': 'Absorbância Negativa',
        'sugestao': 'Refaça o "Branco" do equipamento.',
        'explicacao': 'Seu "Branco" está lendo mais que sua amostra.',
        'risk_impact': 35,
        'id': 'WARN_ABS_NEG'
    }
}

# =======================================================
# 2. MOTOR DE REGRAS (SpectroCoachService)
# =======================================================

def spectro_coach_analyze(data):
    """Lógica principal de análise de regras."""
    tips = []
    risk_score = 0
    
    if data.get('absorbance', 0) > 1.2:
        tips.append(RULEBOOK['HIGH_ABS'])
        risk_score += RULEBOOK['HIGH_ABS']['risk_impact']
        
    if data.get('r_squared', 1) < 0.990:
        tips.append(RULEBOOK['ERR_R2_LOW'])
        risk_score += RULEBOOK['ERR_R2_LOW']['risk_impact']
        
    if data.get('cv_percent', 0) > 5.0:
        tips.append(RULEBOOK['HIGH_CV'])
        risk_score += RULEBOOK['HIGH_CV']['risk_impact']
        
    if data.get('intercept', 0) > 0.05:
        tips.append(RULEBOOK['HIGH_INTERCEPT'])
        risk_score += RULEBOOK['HIGH_INTERCEPT']['risk_impact']
        
    if data.get('absorbance', 0) < -0.01:
        tips.append(RULEBOOK['NEGATIVE_ABS'])
        risk_score += RULEBOOK['NEGATIVE_ABS']['risk_impact']

    if risk_score >= 50:
        risk_level = "Alto"
    elif risk_score > 0:
        risk_level = "Médio"
    else:
        risk_level = "Baixo"
        
    return {
        'risk_score': risk_score,
        'risk_level': risk_level,
        'tips': tips
    }


# =======================================================
# 3. FASTAPI SETUP
# =======================================================

app = FastAPI(title="SpectroCoach API")

# Define a Estrutura de Dados de Entrada (Contrato API)
class AnalysisRequest(BaseModel):
    absorbance: float
    cv_percent: float
    r_squared: float
    intercept: float

# Habilita CORS (CRÍTICO! Permite que o index.html chame esta API)
origins = ["*"] # Permite qualquer origem para PoC

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint: POST /ai/advise
@app.post("/ai/advise")
def advise(request_data: AnalysisRequest):
    # Converte o objeto Pydantic em um dicionário para a função de análise
    data_dict = request_data.model_dump()
    
    # Chama o motor de regras
    results = spectro_coach_analyze(data_dict)
    
    # Retorna o JSON de resposta
    return results