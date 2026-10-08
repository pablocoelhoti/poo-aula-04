import csv
import time
import argparse
from datetime import datetime
import psutil

# 1. Classe Base (Superclasse)
class Metrica:
    def __init__(self, nome):
        self.nome = nome
        self.valor = None
        self.unidade = None

    def coletar(self):
        """Método polimórfico a ser implementado pelas classes filhas."""
        raise NotImplementedError("As subclasses devem implementar o método coletar.")

    def obter_dados(self):
        self.coletar()
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return [agora, self.nome, self.valor, self.unidade]


# 2. Subclasses (Herança e Polimorfismo)
class CpuMetrica(Metrica):
    def __init__(self):
        super().__init__("CPU")

    def coletar(self):
        # interval=0.5 garante uma amostragem precisa da CPU
        self.valor = psutil.cpu_percent(interval=0.5)
        self.unidade = "%"


class MemoriaMetrica(Metrica):
    def __init__(self):
        super().__init__("Memoria")

    def coletar(self):
        # Retorna o uso de memória em MB
        mem = psutil.virtual_memory()
        self.valor = round(mem.used / (1024 * 1024), 2)
        self.unidade = "MB"


class DiscoMetrica(Metrica):
    def __init__(self):
        super().__init__("Disco")

    def coletar(self):
        # Retorna o espaço livre em disco em MB
        disco = psutil.disk_usage('/')
        self.valor = round(disco.free / (1024 * 1024), 2)
        self.unidade = "MB"


# 3. Função para gerenciar o arquivo CSV
def salvar_csv(arquivo, dados):
    # Cria o arquivo com cabeçalho caso ele não exista
    try:
        with open(arquivo, mode="x", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f)
            escritor.writerow(["datetime", "metrica", "valor", "unidade"])
    except FileExistsError:
        pass

    # Adiciona a linha de métrica
    with open(arquivo, mode="a", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(dados)


# 4. Aplicação Principal com suporte a Parâmetros de Terminal (Desafio B)
def main():
    parser = argparse.ArgumentParser(description="Coletor de Métricas de Sistema (DevOps)")
    parser.add_argument("--arquivo", type=str, default="metricas.csv", help="Nome do arquivo CSV de saída")
    parser.add_argument("--intervalo", type=int, default=5, help="Intervalo em segundos entre as coletas")
    parser.add_argument("--iteracoes", type=int, default=5, help="Número de coletas a realizar (0 para infinito)")
    parser.add_argument("--metrica", type=str, choices=["cpu", "memoria", "disco", "todas"], default="todas", help="Escolher métrica específica")

    args = parser.parse_args()

    # Seleção das métricas com base no polimorfismo
    metricas_ativas = []
    if args.metrica in ["cpu", "todas"]:
        metricas_ativas.append(CpuMetrica())
    if args.metrica in ["memoria", "todas"]:
        metricas_ativas.append(MemoriaMetrica())
    if args.metrica in ["disco", "todas"]:
        metricas_ativas.append(DiscoMetrica())

    print(f"🚀 Iniciando coleta de métricas...")
    print(f"📂 Arquivo de saída: {args.arquivo}")
    print(f"⏱️ Intervalo: {args.intervalo}s | Iterações: {args.iteracoes if args.iteracoes > 0 else 'Infinito'}\n")

    contador = 0
    try:
        while True:
            contador += 1
            print(f"--- Coleta #{contador} ---")
            
            for m in metricas_ativas:
                dados = m.obter_dados()
                salvar_csv(args.arquivo, dados)
                print(f"[{dados[0]}] {dados[1]}: {dados[2]} {dados[3]}")

            if args.iteracoes > 0 and contador >= args.iteracoes:
                print("\n✅ Coletas finalizadas com sucesso!")
                break

            time.sleep(args.intervalo)

    except KeyboardInterrupt:
        print("\n👋 Monitoramento interrompido manualmente pelo usuário.")

if __name__ == "__main__":
    main()
    