import './HomePage.css'

function HomePage() {
    return (
        <div className="home-page">
            <section className="hero">
                <h1>Calculator Încărcare Țeavă HDPE</h1>
                <p className="hero-subtitle">
                    Optimizați încărcarea camioanelor cu țevi HDPE folosind algoritmi avansați de telescopare
                </p>
                <div className="hero-actions">
                    <a href="/order" className="btn btn-primary">
                        Începe Comandă Nouă
                    </a>
                    <a href="/results" className="btn btn-secondary">
                        Vezi Rezultate
                    </a>
                </div>
            </section>

            <section className="features">
                <div className="feature-card">
                    <div className="feature-icon">📦</div>
                    <h3>Telescopare Inteligentă</h3>
                    <p>Algoritmul Matryoshka optimizează spațiul prin introducerea țevilor mici în cele mari</p>
                </div>
                <div className="feature-card">
                    <div className="feature-icon">⚖️</div>
                    <h3>Optimizare Greutate</h3>
                    <p>Respectă limita de 24 tone și distribuie uniform sarcina pe axe</p>
                </div>
                <div className="feature-card">
                    <div className="feature-icon">🎯</div>
                    <h3>Vizualizare 3D</h3>
                    <p>Inspectează încărcarea camionului în perspectivă realistă</p>
                </div>
            </section>

            <section className="stats">
                <div className="stat">
                    <span className="stat-value">24t</span>
                    <span className="stat-label">Capacitate Maximă</span>
                </div>
                <div className="stat">
                    <span className="stat-value">SDR 11-26</span>
                    <span className="stat-label">Clase Presiune</span>
                </div>
                <div className="stat">
                    <span className="stat-value">12-13m</span>
                    <span className="stat-label">Lungimi Țevi</span>
                </div>
            </section>
        </div>
    )
}

export default HomePage
