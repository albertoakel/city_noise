import os
import folium
import pandas as pd
import webbrowser



def criar_mapa_belem(csv_path="estabelecimentos_belem2.csv"):
    # 1. Verificar se o arquivo CSV existe
    if not os.path.exists(csv_path):
        print(f"Erro: O arquivo '{csv_path}' nao foi encontrado.")
        print("Execute o script de coleta primeiro para gerar os dados.")
        return

    # 2. Ler os dados coletados
    print(f"Lendo dados de {csv_path}...")
    df = pd.read_csv(csv_path)

    # 3. Limpar dados sem coordenadas válidas
    df = df.dropna(subset=["latitude", "longitude"])

    if df.empty:
        print("Nenhum dado com coordenadas válidas para plotar.")
        return

    # Coordenadas centrais aproximadas de Belém/PA
    lat_belem, lon_belem = -1.4558, -48.4902

    # 4. Inicializar o mapa do Folium
    # Usamos o zoom_start=13 para já abrir cobrindo o centro urbano principal
    mapa = folium.Map(location=[lat_belem, lon_belem], zoom_start=13)

    # Dicionário para definir cores diferentes para cada categoria no mapa
    cores_categorias = {
        "Restaurante": "blue",
        "Bar": "orange",
        "Pub/Bar": "purple",
        "Casa de Show/Boate": "red",
        "Depósito de Bebidas":"green",
        "Loja de Conveniência":'yellow',
    }


    print("Adicionando os marcadores ao mapa...")

    # 5. Iterar sobre as linhas do DataFrame para adicionar cada local
    for index, linha in df.iterrows():
        # Define a cor do marcador baseado na categoria (padrão 'gray' se não achar)
        cor_marcador = cores_categorias.get(linha["categoria"], "gray")

        # Criar o texto que vai aparecer dentro do balão (Popup) ao clicar no ponto
        popup_conteudo = f"""
        <strong>Nome:</strong> {linha['nome']}<br>
        <strong>Categoria:</strong> {linha['categoria']}<br>
        <strong>Bairro:</strong> {linha['bairro'] if pd.notna(linha['bairro']) else 'Não informado'}<br>
        <strong>Endereço:</strong> {linha['endereco_formatado']}
        """

        # Criar o objeto HTML popup com tamanho configurado
        popup_html = folium.Popup(popup_conteudo, max_width=300)

        # Adicionar o Marcador no mapa
        # Adicionar o Marcador no mapa
        folium.Marker(
            location=[linha["latitude"], linha["longitude"]],  # Corrigido aqui
            popup=popup_html,
            tooltip=linha["nome"],
            icon=folium.Icon(color=cor_marcador, icon="info-sign"),
        ).add_to(mapa)

    # 6. Salvar o mapa gerado em um arquivo HTML
    nome_mapa_html = "mapa_estabelecimentos_belem.html"
    mapa.save(nome_mapa_html)
    webbrowser.open("mapa_estabelecimentos_belem.html")

    print(f"\nMapa gerado com sucesso!")
    print(f"Para visualizar, basta abrir o arquivo '{nome_mapa_html}' no seu navegador web.")


if __name__ == "__main__":
    criar_mapa_belem()