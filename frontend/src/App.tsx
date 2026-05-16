import "./App.css";

function App() {
  return (
    <div className="app-container">
      <div className="card text-center">
        <h1 style={{ marginBottom: "1rem", color: "var(--color-primary)" }}>
          Appfasia
        </h1>
        <p style={{ marginBottom: "2rem", color: "var(--color-text-muted)" }}>
          Sistema de Diseño Base Inicializado
        </p>

        <div style={{ display: "flex", gap: "1rem", justifyContent: "center" }}>
          <button className="btn btn-primary">Botón Primario</button>
          <button className="btn btn-secondary">Botón Secundario</button>
        </div>
      </div>
    </div>
  );
}

export default App;
