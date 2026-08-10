animes = pd.read_csv("anime.csv")
similarity = np.load("similarity.npy")

st.write(animes.columns.tolist())   # TEMP DEBUG
st.write(animes.head())             # TEMP DEBUG