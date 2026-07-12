import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import pearsonr


from scipy.stats import gaussian_kde

color_palette21 = [
    "#004C4C", "#006666", "#008080", "#199191", "#29A3A3",
    "#40B5B5", "#55C7C7", "#66D9D9", "#80ECEC", "#99FFFF",
    "#FFD580", "#FFC460", "#FFB240", "#FFA020", "#FF8E00",
    "#FF7C00", "#FF6400", "#FF4C00", "#FF3300", "#FF1A00", "#FF0000"]

color_palette16 = sns.color_palette('RdBu_r', 16)

sns.set_palette(color_palette21 )


def inital_describe(df, simple=False):
    """
    Realiza análise exploratória inicial do DataFrame

    Parameters:
    df (pd.DataFrame): DataFrame a ser analisado
    """

    print("=" * 60)
    print("📊 ANÁLISE EXPLORATÓRIA DO DATAFRAME")
    print("=" * 60)

    # Informações sobre o shape dos dados
    print(f"\n📈 DIMENSÕES DO DATASET:")
    print(f"   • {df.shape[0]} linhas")
    print(f"   • {df.shape[1]} colunas")
    print(f"   • Total de células: {df.shape[0] * df.shape[1]:}")

    # Informações sobre tipos de dados
    print(f"\n🔧 TIPOS DE DADOS:")
    tipo_counts = df.dtypes.value_counts()
    for tipo, count in tipo_counts.items():
        print(f"   • {tipo}: {count} colunas")
    if not simple:
        # Detalhamento dos tipos de dados
        print(f"\n📋 DETALHAMENTO DOS TIPOS POR COLUNA:")
        print(df.dtypes.to_frame('Tipo').to_string())

    # Verificação de duplicatas e nulos
    print("\n" + "=" * 60)
    print("🔍 VERIFICAÇÃO DE QUALIDADE DOS DADOS")
    print("=" * 60)

    # Duplicatas
    duplicatas = df.duplicated().sum()
    print(f"\n📝 REGISTROS DUPLICADOS:")
    print(f"   • Total: {duplicatas}")
    print(f"   • Percentual: {(duplicatas / len(df)) * 100:.2f}%")

    # Valores nulos
    nulos_totais = df.isnull().sum().sum()
    nulos_por_coluna = df.isnull().sum()
    colunas_com_nulos = nulos_por_coluna[nulos_por_coluna > 0]

    print(f"\n❌ VALORES NULOS:")
    print(f"   • Total: {nulos_totais}")
    print(f"   • Percentual: {(nulos_totais / (df.shape[0] * df.shape[1])) * 100:.2f}%")

    if not colunas_com_nulos.empty:
        print(f"\n📊 COLUNAS COM VALORES NULOS:")
        for coluna, nulos in colunas_com_nulos.items():
            percentual = (nulos / len(df)) * 100
            print(f"   • {coluna}: {nulos} nulos ({percentual:.2f}%)")
    else:
        print(f"   ✓ Nenhuma coluna com valores nulos")

    if not simple:
        col_obj = df.select_dtypes(include=object).columns.tolist()
        print("\n" + "=" * 60)
        print("🔎 ANÁLISE DAS COLUNAS CATEGÓRICAS")
        print("=" * 60)
        for col in col_obj:
            if col in df.columns:
                print(f"\n{str.upper(col)}")
                print(f"Quantidade de valores únicos: {df[col].nunique()}")
                print(f"Valores: {df[col].unique()}")

        # Estatísticas básicas para colunas numéricas
        print(f"\n📊 ESTATÍSTICAS BÁSICAS (colunas numéricas):")
        colunas_numericas = df.select_dtypes(include=['number']).columns
        if len(colunas_numericas) > 0:
            display(df[colunas_numericas].describe().T)
            # print(df[colunas_numericas].describe().T.round(2))
            # print(df[colunas_numericas].describe().T.round(2).to_string())

        else:
            print("   • Nenhuma coluna numérica encontrada")

    print("\n" + "=" * 60)
    print("✅ ANÁLISE CONCLUÍDA")
    print("=" * 60)


def remove_outliers_iqr(data, target, threshold=1.5, verbose=True):
    """
    Remove outliers de um DataFrame usando o método do IQR e exibe estatísticas detalhadas.

    Parâmetros
    ----------
    data : pd.DataFrame
        DataFrame de entrada.
    cols : list
        Lista de colunas numéricas para verificar e remover outliers.
    threshold : float, padrão=1.5
        Fator multiplicativo do IQR para definir limites (ex.: 1.5 ou 3.0).
    verbose : bool, padrão=True
        Se True, exibe o resumo das remoções.

    Retorno
    -------
    df_clean : pd.DataFrame
        DataFrame sem outliers.
    summary : pd.DataFrame
        Tabela com resumo das remoções por coluna.
    """
    cols = data.drop(target, axis=1).select_dtypes(include=['number']).columns

    df_clean = data.copy()
    n_total = len(data)
    summary_data = []
    for col in cols:
        if col not in df_clean.columns:
            continue

        # Quantis e IQR
        Q1 = df_clean[col].quantile(0.25)
        Q3 = df_clean[col].quantile(0.75)
        IQR = Q3 - Q1

        # Limites inferior e superior
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR

        # Identifica outliers
        mask_outliers = (df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)
        n_outliers = mask_outliers.sum()

        # Guarda informações
        summary_data.append({
            'feature': col,
            'count_initial': len(df_clean),
            'count_removed': n_outliers,
            'percent_removed': (n_outliers / len(df_clean) * 100) if len(df_clean) > 0 else 0
        })

        # Remove outliers da coluna atual
        df_clean = df_clean[~mask_outliers]

    # Cria DataFrame resumo
    summary = pd.DataFrame(summary_data)

    # Totais gerais
    total_removed = n_total - len(df_clean)
    percent_total_removed = total_removed / n_total * 100 if n_total > 0 else 0

    if verbose:
        print("\n" + "=" * 60)
        print("Remoção de Outliers (Método IQR) 🧹")
        print("=" * 60)
        print(summary.to_string(index=False, formatters={
            'percent_removed': '{:.2f}%'.format
        }))
        print("-" * 60)
        print(f"Total removido: {total_removed} registros ({percent_total_removed:.2f}%) de {n_total}")

    return df_clean

def mult_plt(df,kind='hist', ncols=3, max_bins=15, figsize=(16, 24),min_boxplot=6,suptitle=None):

    """
    Gera automaticamente visualizações (histogramas ou boxplots)
    para todas as colunas numéricas de um DataFrame.

    Parâmetros
    ----------
    df : pd.DataFrame
        DataFrame contendo as colunas numéricas para visualização.
    kind : str, padrão="hist"
        Tipo de visualização: "hist" para histograma ou "box" para boxplot.
    ncols : int, padrão=3
        Número de colunas no grid de subplots.
    max_bins : int, padrão=15
        Máximo de bins para histogramas.
    figsize : Tuple[int, int], padrão=(16, 24)
        Tamanho da figura.
    suptitle : str, opcional
        Título geral da figura.
    min_unique_values_for_boxplot : int, padrão=6
        Número mínimo de valores únicos para incluir a variável em boxplot.

    Retorno
    -------
    None
        Exibe os gráficos diretamente.
    """

    def nice_bin_width(data_range: float, max_bins: int) -> float:
        """Calcula largura de bin 'redonda' para histogramas."""
        raw_dx = data_range / max_bins
        nice_steps = [1, 2, 2.5, 5, 10]
        scale = 10 ** math.floor(math.log10(raw_dx))
        for step in nice_steps:
            candidate = step * scale
            n_bins = math.ceil(data_range / candidate)
            if n_bins <= max_bins:
                return candidate
        return data_range / max_bins

    cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # FILTRAR COLUNAS para boxplot
    if kind == "box":
        cols = [col for col in cols if df[col].nunique() >= min_boxplot]

    nrows = math.ceil(len(cols) / ncols)

    fig, ax = plt.subplots(nrows, ncols, figsize=figsize)
    ax = np.array(ax).reshape(nrows, ncols)

    if not suptitle:
        suptitle = "Histogramas" if kind == "hist" else "Boxplots"
    fig.suptitle(suptitle, fontsize=18, y=1.007)

    for idx, col in enumerate(cols):
        row, col_idx = divmod(idx, ncols)
        temp = df[col].dropna()

        if kind == "hist":
            unique_vals = np.sort(temp.unique())
            if np.issubdtype(temp.dtype, np.integer) and len(unique_vals) <= 8:
                dx = 1
                align = 'center'
                bins = np.arange(min(unique_vals), max(unique_vals) + dx + 1, dx)
            else:
                data_range = temp.max() - temp.min()
                dx = nice_bin_width(data_range, max_bins)
                align = 'edge'
                bins = np.arange(temp.min(), temp.max() + dx, dx)

            counts, edges = np.histogram(temp, bins)
            perc = counts / len(temp) * 100

            ax[row, col_idx].bar(
                edges[:-1], perc, width=np.diff(bins), align=align,color=color_palette16[3] ,
                edgecolor='black'
            )
            ax[row, col_idx].set_title(col)
            ax[row, col_idx].set_xlabel(col)
            ax[row, col_idx].set_ylabel('Percentual (%)')
            ax[row, col_idx].set_xticks(bins[:-1])
            if len(bins) >= 10:
                ax[row, col_idx].set_xticklabels(np.round(bins[:-1], 2), rotation=45)


            for i in range(len(counts)):
                fs = max(6, 10 - len(counts) // 5)
                if align == 'center':
                    bar_center = bins[i]
                else:
                    bar_center = bins[i] + (bins[i + 1] - bins[i]) / 2
                ax[row, col_idx].text(
                    bar_center, perc[i], f'{perc[i]:.1f}%',
                    ha='center', va='bottom', fontsize=fs
                )

        elif kind == "box":
            sns.boxplot(x=temp, color=color_palette16[14], ax=ax[row, col_idx])
            ax[row, col_idx].set_title(col)
            ax[row, col_idx].set_xlabel(col)
            ax[row, col_idx].set_ylabel("")

    # Remove subplots extras
    for j in range(len(cols), nrows * ncols):
        row, col_idx = divmod(j, ncols)
        ax[row, col_idx].set_visible(False)

    plt.tight_layout()
    plt.show()


def mult_plt2(df, kind='hist', ncols=3, max_bins=15, figsize=(16, 24),
             min_boxplot=6, paleta=None,suptitle=None):

    """
    Gera automaticamente visualizações (histogramas, boxplots ou histogramas categóricos)
    para todas as colunas de um DataFrame e retorna também os dados utilizados no gráfico.

    Parâmetros
    ----------
    df : pd.DataFrame
        DataFrame contendo as colunas para visualização.
    kind : str, padrão="hist"
        Tipo de visualização: "hist" para histograma (numérico e categórico)
        ou "box" para boxplot (apenas numérico).
    ncols : int, padrão=3
        Número de colunas no grid de subplots.
    max_bins : int, padrão=15
        Máximo de bins para histogramas numéricos.
    figsize : Tuple[int, int], padrão=(16, 24)
        Tamanho da figura.
    suptitle : str, opcional
        Título geral da figura.
    min_boxplot : int, padrão=6
        Número mínimo de valores únicos para incluir a variável em boxplot.

    Retorno
    -------
    plot_data : pd.DataFrame
        DataFrame contendo as colunas:
        ["feature", "x_value", "percentual", "contagem"]
    """

    if paleta is None:
        paleta = color_palette21

    def nice_bin_width(data_range: float, max_bins: int) -> float:
        """Calcula largura de bin 'redonda' para histogramas numéricos."""
        raw_dx = data_range / max_bins
        nice_steps = [1, 2, 2.5, 5, 10]
        scale = 10 ** math.floor(math.log10(raw_dx))
        for step in nice_steps:
            candidate = step * scale
            n_bins = math.ceil(data_range / candidate)
            if n_bins <= max_bins:
                return candidate
        return data_range / max_bins

    # Separar nome das colunas numéricas e categóricas
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    # Para boxplot: filtrar apenas numéricas com número mínimo de valores únicos
    if kind == "box":
        cols = [col for col in num_cols if df[col].nunique() >= min_boxplot]
    else:
        cols = num_cols + cat_cols

    nrows = math.ceil(len(cols) / ncols)
    fig, ax = plt.subplots(nrows, ncols, figsize=figsize)
    ax = np.array(ax).reshape(nrows, ncols)

    if not suptitle:
        suptitle = "Distribuições (numéricas e categóricas)" if kind == "hist" else "Boxplots"
    fig.suptitle(suptitle, fontsize=18, y=1.007)

    # Lista para armazenar dados dos gráficos
    data_plot = []

    for idx, col in enumerate(cols):
        row, col_idx = divmod(idx, ncols)
        temp = df[col].dropna()
        ax_ = ax[row, col_idx]
        ax_.set_title(col)

        # --- Histogramas numéricos ---
        if kind == "hist" and col in num_cols:
            unique_vals = np.sort(temp.unique())
            if np.issubdtype(temp.dtype, np.integer) and len(unique_vals) <= 8:
                dx = 1
                align = 'center'
                bins = np.arange(min(unique_vals), max(unique_vals) + dx + 1, dx)
            else:
                data_range = temp.max() - temp.min()
                dx = nice_bin_width(data_range, max_bins)
                align = 'edge'
                bins = np.arange(temp.min(), temp.max() + dx, dx)

            counts, edges = np.histogram(temp, bins)
            perc = counts / len(temp) * 100

            ax_.bar(edges[:-1], perc, width=np.diff(bins), align=align,
                    color=paleta[2], edgecolor='black')
            #print(col,df[col].mean())
            ax_.axvline(df[col].mean(),color='red', linestyle='--', label=f'Média: {df[col].mean():.2f}')
            ax_.axvline(df[col].median(), color='green', linestyle='--',label=f'Mediana: {df[col].median():.2f}')

            ax_.legend()
            ax_.set_xlabel(col)
            ax_.set_ylabel('Percentual (%)')
            ax_.set_xticks(bins[:-1])
            if len(bins) >= 10:
                ax_.set_xticklabels(np.round(bins[:-1], 2), rotation=45)

            # Adiciona texto e registra dados
            for i in range(len(counts)):
                fs = max(6, 10- len(counts) // 8)
                fs=6

                bar_center = bins[i] if align == 'center' else bins[i] + (bins[i + 1] - bins[i]) / 2
                ax_.text(bar_center, perc[i], f'{perc[i]:.1f}%',
                         ha='center', va='bottom', fontsize=fs)

                # Adiciona ao registro
                data_plot.append({
                    "feature": col,
                    "x_value": round(bar_center, 4),
                    "percentual": round(perc[i], 2),
                    "contagem": int(counts[i])
                })

        # --- Histogramas categóricos ---
        elif kind == "hist" and col in cat_cols:
            counts = temp.value_counts()
            perc = counts / len(temp) * 100

            ax_.bar(counts.index.astype(str), perc, color=paleta[5], edgecolor='black')
            ax_.set_xlabel(col)
            ax_.set_ylabel('Percentual (%)')
            ax_.tick_params(axis='x', rotation=45)

            for i, (cat, p) in enumerate(zip(counts.index, perc)):
                ax_.text(i, p, f'{p:.1f}%', ha='center', va='bottom', fontsize=9)
                # Adiciona ao registro
                data_plot.append({
                    "feature": col,
                    "x_value": str(cat),
                    "percentual": round(p, 2),
                    "contagem": int(counts.loc[cat])
                })

        # --- Boxplots numéricos ---
        elif kind == "box":
            sns.boxplot(y=temp, color=paleta[2], ax=ax_)
            ax_.set_xlabel(col)
            ax_.set_ylabel("")

    # Remove subplots extras
    for j in range(len(cols), nrows * ncols):
        row, col_idx = divmod(j, ncols)
        ax[row, col_idx].set_visible(False)

    plt.tight_layout()
    plt.show()

    # Retornar DataFrame com os dados
    out_data = pd.DataFrame(data_plot, columns=["feature", "x_value", "percentual", "contagem"])
    return out_data


def correlation_bar(df, target, threshold=None, paleta=None,metodo=None,plot_type='all'):
    """
    Plot heatmap and/or barplot of correlation with target variable.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with numeric variables.
    target : str
        Name of target column.
    threshold : float, optional
        Threshold to filter correlations
    plot_type : str, optional
        Type of plot:
        - 'all'  : heatmap + barplot (default)
        - 'corr' : only heatmap
        - 'bar'  : only barplot

    Returns:
    --------
    tuple
        Ordered correlation matrix and target correlation series

    """
    if paleta is None:
        paleta = color_palette21[::-1]  #[::-1] padrçao inverso de cores
    if metodo is None:
        metodo=pearson

    # --- Correlation ---
    corr = df.corr(numeric_only=True,method=metodo)

    # --- Normalization ---
    vmin, vmax = -1, 1
    norm = plt.Normalize(vmin=vmin, vmax=vmax)

    # --- Custom colormap ---
    cmap60 = LinearSegmentedColormap.from_list(
        "custom_21", paleta, N=60
    )

    # --- Sorting by target ---
    order = corr[target].sort_values(ascending=True).index
    corr_ordered = corr.loc[order, order]
    dfcm = corr_ordered.copy()

    if isinstance(threshold, (int, float)):
        dfcm[(dfcm < threshold) & (dfcm > -threshold)] = pd.NA
        dfcm[dfcm >= 0.99] = pd.NA

    # --- Correlation with target variable ---
    corr_target = dfcm[target].drop(target).sort_values(ascending=False)
    #corr_target = corr[target].drop(target).sort_values(ascending=False)

    cmap60_bar = [cmap60(norm(value)) for value in corr_target.values]

    # --- Plotting ---
    if plot_type == 'all':
        fig, axes = plt.subplots(
            1, 2,
            figsize=(18, 8),
            gridspec_kw={'width_ratios': [1.6, 0.6]}
        )
        ax_corr, ax_bar = axes
    else:
        fig, ax = plt.subplots(figsize=(10, 8))

    if plot_type in ['all', 'corr']:
        ax = ax_corr if plot_type == 'all' else ax
        fig = ax.get_figure()
        fig.set_size_inches(16, 8)
        sns.heatmap(
            dfcm,
            cmap=cmap60,
            annot=True,
            fmt=".2f",
            center=0,
            vmin=vmin,
            vmax=vmax,
            linewidths=0.4,
            cbar_kws={'label': metodo.title() +' Correlation'},
            ax=ax
        )
        ax.set_title(
            f"Correlation Map Ordered by '{target}'",
            fontsize=14,
            weight='bold'
        )

    if plot_type in ['all', 'bar']:
        ax = ax_bar if plot_type == 'all' else ax

        # CORREÇÃO: Criar DataFrame para o barplot com hue
        bar_data = pd.DataFrame({
            'features': corr_target.index,
            'correlation': corr_target.values,
            'hue': corr_target.values  # Adiciona hue baseado nos valores
        })

        sns.barplot(
            data=bar_data,
            x='correlation',
            y='features',
            #hue='hue',  # Especifica hue
            palette=cmap60_bar,
            #legend=False,  # Remove a legenda do hue
            ax=ax
        )
        ax.set_title(
            f"Variable Correlation with '{target}'",
            fontsize=14,
            weight='bold'
        )
        ax.set_xlabel(metodo.title()+" Correlation Coefficient")

        # Color bar
        sm = plt.cm.ScalarMappable(cmap=cmap60, norm=norm)
        sm.set_array([])
        cbar = fig.colorbar(
            sm,
            ax=ax,
            fraction=0.03,
            pad=0.04
        )
        cbar.set_label(
            'Correlation Scale (shared with heatmap)',
            rotation=270,
            labelpad=15
        )

    plt.tight_layout()
    plt.show()

    return corr_ordered, corr_target

def scatter_by_category(df, x_var, y_var, hue_var, category_var,
                        ncols=3, figsize=[16, 16], palette=None,
                        suptitle=None, alpha=0.6, s=45,category_name=None):
    """
    Gera scatterplots de x_var vs y_var com hue_var, separados por category_var.
    """

    # categorias e hue
    categories = df[category_var].unique()
    n_categories = len(categories)
    n_hue = df[hue_var].nunique()

    maxY=df[y_var].max()
    minY=df[y_var].min()

    indices = np.linspace(2, len(color_palette21) - 3, n_hue, dtype=int)
    custom_palette = [color_palette21[i] for i in indices]

    # Calcular número de linhas
    nrows = math.ceil(n_categories / ncols)

    #print('nrows',nrows,round(nrows*4.5))
    figsize[1]=round(nrows*4.5)

    # Criar figura e subplots
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)

    # Garantir que axes seja sempre um array 2D
    if nrows == 1 and ncols == 1:
        axes = np.array([[axes]])  # Dupla camada para [row, col]
    elif nrows == 1:
        axes = np.array([axes])  # Transforma em 2D: [1, ncols]
    elif ncols == 1:
        axes = np.array([[ax] for ax in axes])  # Transforma em 2D: [nrows, 1]
    else:
        axes = np.array(axes)

    # Título principal
    if not suptitle:
        suptitle = f"{x_var} vs {y_var} por {hue_var} - Separado por {category_var}"
    fig.suptitle(suptitle, fontsize=16, y=1.007)

    #lista de saida
    dados_grupos = []

    # Plotar cada categoria
    for idx, category in enumerate(categories):
        row, col = divmod(idx, ncols)
        ax = axes[row, col]

        # Filtrar dados da categoria
        temp_df = df[df[category_var] == category]

        # Calcular distribuição do hue_var para esta categoria
        hue_distribution = temp_df[hue_var].value_counts(normalize=True) * 100
        hue_info = []

        for hue_val, percent in hue_distribution.items():
            hue_info.append(f"{hue_val}: {percent:.1f}%")

        # Juntar todas as informações do hue
        hue_summary = " | ".join(hue_info)

        # Criar scatterplot
        sns.scatterplot(data=temp_df, x=x_var, y=y_var, hue=hue_var,
                        s=s, alpha=alpha, palette=custom_palette, ax=ax)


        # Configurar título e labels com informações detalhadas
        #print(idx,category )
        if category_name is None:
            None
        else:
            category=category_name[idx]


        ax.set_title(f"{category}\nN={len(temp_df)} ({hue_summary})",
        fontsize=11, weight='bold')  # Reduzi para 11 para caber melhor
        ax.set_xlabel(x_var)
        ax.set_ylabel(y_var)
        ax.set_ylim([minY,maxY])

        # Melhorar legenda (manter apenas no primeiro gráfico)
        if idx > 0:
            ax.get_legend().remove()
        else:
            ax.legend(title=hue_var)

            # Coletar estatísticas para o DataFrame
        for hue_val in hue_distribution.index:
            hue_df = temp_df[temp_df[hue_var] == hue_val]
            if len(hue_df) > 0:
                dados_grupos.append({
                    category_var: category,
                    hue_var: hue_val,
                    'contagem': len(hue_df),
                    'percentual_hue': hue_distribution[hue_val],
                    f'media_{x_var}': hue_df[x_var].mean(),
                    f'mediana_{x_var}': hue_df[x_var].median(),
                    f'std_{x_var}': hue_df[x_var].std(),
                    f'min_{x_var}': hue_df[x_var].min(),
                    f'max_{x_var}': hue_df[x_var].max(),
                    f'media_{y_var}': hue_df[y_var].mean(),
                    f'mediana_{y_var}': hue_df[y_var].median(),
                    f'std_{y_var}': hue_df[y_var].std(),
                    f'min_{y_var}': hue_df[y_var].min(),
                    f'max_{y_var}': hue_df[y_var].max(),
                    'correlacao_xy': hue_df[[x_var, y_var]].corr().iloc[0, 1] if len(hue_df) > 1 else np.nan
                    })

    # Remover subplots vazios
    for idx in range(len(categories), nrows * ncols):
        row, col = divmod(idx, ncols)
        axes[row, col].set_visible(False)

    plt.tight_layout()
    plt.show()

    # Criar DataFrame final
    df_resultados = pd.DataFrame(dados_grupos)

    # Ordenar e formatar
    if not df_resultados.empty:
        df_resultados = df_resultados.sort_values([category_var, hue_var])
        df_resultados['percentual_hue'] = df_resultados['percentual_hue'].round(2)

        # Arredondar colunas numéricas
        colunas_numericas = df_resultados.select_dtypes(include=[np.number]).columns
        df_resultados[colunas_numericas] = df_resultados[colunas_numericas].round(4)

    return df_resultados

def bar_bar_cat(df, cat_1, cat_2=None, paleta=None,figsize=(12,6)):
    """
    Gráfico de barras categórico.

    - 1 categoria: distribuição simples (percentual)
    - 2 categorias: distribuição percentual condicional

    - h altura(tamanho) da figura
    - paleta de cor
    """

    if paleta is None:
        paleta = color_palette21

    #figsize = (10, h)

    # ==================================================
    # CASO 1 — APENAS UMA CATEGORIA
    # ==================================================
    if cat_2 is None:

        contagem = df[cat_1].value_counts()
        percentual = df[cat_1].value_counts(normalize=True) * 100

        df_plot = pd.DataFrame({
            cat_1: contagem.index,
            'count': contagem.values,
            'percentual': percentual.values})

        n_bars = df_plot.shape[0]
        indices = np.linspace(5, len(paleta) - 6, n_bars, dtype=int)
        custom_palette = [paleta[i] for i in indices]


        plt.figure(figsize=figsize)
        ax = sns.barplot(data=df_plot,
                         x=cat_1,
                         y='percentual',
                         palette=custom_palette,
                         edgecolor='black')

        ax.set_title(f'Distribuição de {cat_1}', fontsize=14, weight='bold')
        ax.set_xlabel(cat_1)
        ax.set_ylabel('Percentual (%)')

        for i, bar in enumerate(ax.containers[0]):
            h = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + 0.5,
                f'{df_plot["count"].iloc[i]} ({h:.1f}%)',
                ha='center',
                va='bottom',
                fontsize=9
            )

        plt.tight_layout()
        plt.show()
        return df_plot

    # ==================================================
    # CASO 2 — DUAS CATEGORIAS
    # ==================================================
    contagem = pd.crosstab(df[cat_1], df[cat_2])
    percentual = pd.crosstab(df[cat_1], df[cat_2], normalize='index') * 100

    df_plot = percentual.reset_index()
    df_plot = pd.melt(
        df_plot,
        id_vars=[cat_1],
        value_vars=percentual.columns,
        var_name=cat_2,
        value_name='percentual'
    )

    n_hue = percentual.shape[1]
    #indices = np.linspace(2, len(paleta) - 3, n_hue, dtype=int)
    indices = np.linspace(3, len(paleta) - 6, n_hue , dtype=int)

    custom_palette = [paleta[i] for i in indices]

    plt.figure(figsize=figsize)

    ax = sns.barplot(
        data=df_plot,
        x=cat_1,
        y='percentual',
        hue=cat_2,
        palette=custom_palette,
        edgecolor='black'
    )

    ax.set_title(f'Distribuição de {cat_2} por {cat_1}', fontsize=14, weight='bold')
    ax.set_xlabel(cat_1)
    ax.set_ylabel('Percentual (%)')
    ax.legend(title=cat_2, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45)

    # Labels
    for i, container in enumerate(ax.containers):
        for j, bar in enumerate(container):
            h = bar.get_height()
            if h > 0:
                count = contagem.iloc[j, i]
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    h + 0.5,
                    f'{count} ({h:.1f}%)',
                    ha='center',
                    va='bottom',
                    fontsize=8
                )

    plt.tight_layout()
    plt.show()

    return contagem, percentual


def scatterplot_bairro(x1, x2, x3, y, df, hue_var=None,savefilename=None):
    """
    Versão avançada com opção de variável para cor (hue) e retorno de estatísticas

    Parâmetros:
    x1, x2, x3: variáveis para os eixos x dos gráficos
    y: variável para o eixo y (comum a todos os gráficos)
    df: DataFrame com os dados
    hue_var: variável para colorir os pontos (opcional)

    Retorna:
    tuple: (stats_x1, stats_x2, stats_x3) - estatísticas de cada relação
    """

    # Definindo a paleta de cores
    color_palette = sns.color_palette('RdBu_r', 16)
    sns.set_palette(color_palette)

    # Criando a figura
    fig, axes = plt.subplots(1, 3, figsize=(22, 6))

    # Configurações dos gráficos
    configs = [
        {'x': x1, 'title': f'{x1} vs {y}', 'color': color_palette[0]},
        {'x': x2, 'title': f'{x2} vs {y}', 'color': color_palette[8]},
        {'x': x3, 'title': f'{x3} vs {y}', 'color': color_palette[15]}
    ]

    # Lista para armazenar as estatísticas
    estatisticas = []

    for i, config in enumerate(configs):
        ax = axes[i]
        x_var = config['x']

        # CORREÇÃO: Remover linhas onde qualquer uma das variáveis é NaN
        dados_validos = df[[x_var, y]].dropna()

        if len(dados_validos) < 2:
            print(f"Aviso: Dados insuficientes para {x_var} vs {y}")
            stats = {
                'variavel_x': x_var,
                'variavel_y': y,
                'correlacao': np.nan,
                'p_valor': np.nan,
                'r_quadrado': np.nan,
                'coef_angular': np.nan,
                'intercepto': np.nan,
                'equacao': "Dados insuficientes",
                'n_observacoes': len(dados_validos)
            }
        else:
            # Calcular estatísticas com dados válidos
            x_vals = dados_validos[x_var].values
            y_vals = dados_validos[y].values

            correlacao, p_valor = pearsonr(x_vals, y_vals)
            coef_angular, intercepto = np.polyfit(x_vals, y_vals, 1)
            r_quadrado = correlacao ** 2

            # Armazenar estatísticas
            stats = {
                'variavel_x': x_var,
                'variavel_y': y,
                'correlacao': correlacao,
                'p_valor': p_valor,
                'r_quadrado': r_quadrado,
                'coef_angular': coef_angular,
                'intercepto': intercepto,
                'equacao': f"y = {coef_angular:.4f}x + {intercepto:.4f}",
                'n_observacoes': len(dados_validos)
            }

        estatisticas.append(stats)

        # Criar scatterplot com ou sem hue
        if hue_var:
            # Para hue, também precisamos remover NaNs da variável hue
            dados_plot = df[[x_var, y, hue_var]].dropna()
            scatter = sns.scatterplot(
                data=dados_plot,
                x=x_var,
                y=y,
                hue=hue_var,
                palette='RdBu_r',
                s=100,
                ax=ax
            )
            # Adicionar legenda se houver hue
            ax.legend(title=hue_var, title_fontsize=10)
        else:
            scatter = sns.scatterplot(
                data=df,
                x=x_var,
                y=y,
                color=config['color'],
                s=100,
                ax=ax
            )

        # Linha de regressão apenas se houver dados suficientes
        if len(dados_validos) >= 2:
            sns.regplot(
                data=df,
                x=x_var,
                y=y,
                scatter=False,
                line_kws={'color': 'black', 'linestyle': '--', 'alpha': 0.7},
                ax=ax
            )

        # # Adicionar estatísticas no gráfico (se disponíveis)
        # if not np.isnan(stats['correlacao']):
        #     texto_stats = f"r = {stats['correlacao']:.3f}\nr² = {stats['r_quadrado']:.3f}\np = {stats['p_valor']:.3f}\nn = {stats['n_observacoes']}"
        #     ax.text(0.05, 0.95, texto_stats, transform=ax.transAxes,
        #             fontsize=10, verticalalignment='top',
        #             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        # else:
        #     ax.text(0.05, 0.95, "Dados insuficientes", transform=ax.transAxes,
        #             fontsize=10, verticalalignment='top',
        #             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))

        # Anotações dos bairros
        for j, row in df.iterrows():
            # Verificar se os dados existem antes de annotar
            if not (pd.isna(row[x_var]) or pd.isna(row[y])):
                ax.annotate(
                    row['Bairro'],
                    (row[x_var], row[y]),
                    xytext=(8, 8),
                    textcoords='offset points',
                    fontsize=9,
                    alpha=0.8)

        # Configurações do gráfico
        ax.set_title(config['title'], fontsize=14, pad=20)
        ax.set_xlabel(x_var, fontsize=12, labelpad=10)
        ax.set_ylabel(y, fontsize=12, labelpad=10)
        ax.grid(True, alpha=0.2)

    plt.tight_layout()

    # Salva apenas se um nome foi fornecido
    if savefilename is not None:
        # Garante extensão .png
        filename = savefilename
        if not filename.lower().endswith('.png'):
            filename += '.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Gráfico salvo como: {filename}")

    plt.show()
    # Retornar as estatísticas
    return estatisticas[0], estatisticas[1], estatisticas[2]


# Função auxiliar para imprimir estatísticas de forma organizada
import numpy as np

def print_estatisticas(*stats_list):
    """Imprime as estatísticas de forma organizada.
       Aceita 0..N dicionários contendo as chaves esperadas.
    """
    if len(stats_list) == 0:
        print("Nenhuma estatística fornecida.")
        return

    print("=" * 60)
    print("ESTATÍSTICAS DAS RELAÇÕES")
    print("=" * 60)

    for i, stats in enumerate(stats_list, 1):
        print(f"\n--- Relação {i} ---")
        if not stats or not isinstance(stats, dict):
            print("Entrada inválida (esperado dicionário). Pulando.")
            continue

        var_x = stats.get('variavel_x', '<x?>')
        var_y = stats.get('variavel_y', '<y?>')
        print(f"{var_x} vs {var_y}")

        n_obs = stats.get('n_observacoes')
        if n_obs is not None:
            print(f"Observações válidas: {n_obs}")
        else:
            print("Observações válidas: N/D")

        corr = stats.get('correlacao')
        # trata None e NaN
        if corr is None or (isinstance(corr, float) and np.isnan(corr)):
            print("Dados insuficientes para cálculo de estatísticas")
            continue

        p_valor = stats.get('p_valor', np.nan)
        r2 = stats.get('r_quadrado', np.nan)
        coef = stats.get('coef_angular', np.nan)
        intercepto = stats.get('intercepto', np.nan)
        equacao = stats.get('equacao')

        # Se não houver equação dada, montamos uma simples
        if not equacao:
            try:
                equacao = f"y = {coef:.4g}x + {intercepto:.4g}"
            except Exception:
                equacao = "equação não disponível"

        print(f"Correlação (r): {corr:.4f}")
        print(f"R-quadrado (r²): {r2:.4f}")
        print(f"Valor-p: {p_valor:.4f}")
        print(f"Equação da reta: {equacao}")
        print(f"Coeficiente angular: {coef:.4f}")
        print(f"Intercepto: {intercepto:.4f}")

        # Interpretação da correlação
        r_abs = abs(corr)
        if r_abs >= 0.8:
            força = "MUITO FORTE"
        elif r_abs >= 0.6:
            força = "FORTE"
        elif r_abs >= 0.4:
            força = "MODERADA"
        elif r_abs >= 0.2:
            força = "FRACA"
        else:
            força = "MUITO FRACA"

        direcao = "POSITIVA" if corr > 0 else "NEGATIVA"
        significancia = "ESTATISTICAMENTE SIGNIFICATIVA" if (isinstance(p_valor, (int,float)) and p_valor < 0.05) else "NÃO SIGNIFICATIVA"
        print(f"Interpretação: {força} correlação {direcao} ({significancia})")



