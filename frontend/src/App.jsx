import { useState, useRef, useEffect } from 'react';
import Login from './Login';
import './App.css';

function App() {
  // --- 1. ESTADO DE AUTENTICACIÓN ---
  const [usuarioActual, setUsuarioActual] = useState(null); 

  // --- 2. ESTADOS DEL CHATBOT Y DASHBOARD ---
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const chatEndRef = useRef(null);

  const [mensajes, setMensajes] = useState([
    {
      rol: 'ia',
      texto: '¡Hola! Con gusto te ayudaré. Por favor, selecciona la opción que necesitas o escribe tu consulta:',
      opcionesRapidas: [
        'Ver Estado de Triage', 
        'Pacientes en Urgencias', 
        'Medicamentos sin stock', 
        'Cirugías programadas'
      ],
      mostrarWidget: true
    }
  ]);

  // --- 3. EFECTOS Y FUNCIONES ---
  useEffect(() => {
    if (isChatOpen) {
      chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [mensajes, loading, isChatOpen]);

  const enviarOpcionRapida = (opcion) => {
    setInput(opcion);
    procesarConsulta(opcion);
  };

  const consultarIA = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    procesarConsulta(input);
  };

  const procesarConsulta = async (textoPregunta) => {
    setMensajes((prev) => [...prev, { rol: 'usuario', texto: textoPregunta }]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pregunta: textoPregunta })
      });

      if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
      const data = await response.json();
      
      // Mantenemos la respuesta completa (texto explicativo + tabla de resultados + SQL)
      setMensajes((prev) => [
        ...prev, 
        { 
          rol: 'ia', 
          texto: data.recomendacion_agente || "Consulta ejecutada con éxito.",
          resultados: data.resultados,
          sql: data.sql_ejecutado
        }
      ]);
    } catch (err) {
      console.error(err);
      setMensajes((prev) => [
        ...prev, 
        { rol: 'ia', error: "Error de conexión con el servidor. Verifica que FastAPI esté corriendo en el puerto 8000." }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // --- 4. VALIDACIÓN DE RUTAS (PROTECCIÓN) ---
  if (!usuarioActual) {
    return <Login onLoginSuccess={(datosUser) => setUsuarioActual(datosUser)} />;
  }

  // --- 5. RENDERIZADO PRINCIPAL (DASHBOARD PROTEGIDO) ---
  return (
    <>
      <style>{`
        body, html {
          margin: 0; padding: 0; background-color: #0f172a;
          font-family: 'Inter', system-ui, sans-serif;
          box-sizing: border-box; overflow-x: hidden;
        }
        * { box-sizing: inherit; }

        .dashboard-container { min-height: 100vh; width: 100%; background-color: #0f172a; display: flex; flex-direction: column; }
        .dashboard-header { padding: 15px 30px; background-color: #1e293b; border-bottom: 1px solid #334155; display: flex; align-items: center; gap: 15px; }
        .dashboard-content { flex: 1; padding: 25px 30px; overflow-y: auto; }

        .dashboard-grid-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 25px; }
        .dashboard-grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); gap: 20px; margin-bottom: 25px; }

        .kpi-card { background-color: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 20px; display: flex; flex-direction: column; gap: 12px; position: relative; }
        .trend-badge { position: absolute; top: 20px; right: 20px; padding: 4px 8px; border-radius: 20px; font-size: 11px; font-weight: bold; }
        .trend-up { background-color: rgba(52,211,153,0.15); color: #34d399; }
        .trend-down { background-color: rgba(239,68,68,0.15); color: #ef4444; }

        .chart-card { background-color: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 25px; display: flex; flex-direction: column; }
        .chart-title { color: #f8fafc; font-size: 16px; margin: 0 0 20px 0; font-weight: 600; display: flex; justify-content: space-between; align-items: center; }

        .progress-bg { width: 100%; background-color: #0f172a; border-radius: 6px; height: 8px; overflow: hidden; }
        .progress-fill { height: 100%; border-radius: 6px; }

        .donut-container { display: flex; justify-content: center; align-items: center; padding: 10px 0; gap: 30px; }
        .donut-chart { width: 140px; height: 140px; border-radius: 50%; background: conic-gradient(#3b82f6 0% 55%, #10b981 55% 85%, #ef4444 85% 100%); display: flex; justify-content: center; align-items: center; position: relative; box-shadow: inset 0 0 15px rgba(0,0,0,0.5); }
        .donut-inner { width: 100px; height: 100px; background-color: #1e293b; border-radius: 50%; display: flex; flex-direction: column; justify-content: center; align-items: center; }
        .legend-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 10px; }
        .legend-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #cbd5e1; }
        .legend-dot { width: 12px; height: 12px; border-radius: 3px; }

        .bar-chart-vertical { display: flex; align-items: flex-end; justify-content: space-around; height: 180px; padding-top: 20px; border-bottom: 1px solid #334155; }
        .bar-v-group { display: flex; flex-direction: column; align-items: center; gap: 8px; flex: 1; }
        .bar-v { width: 100%; max-width: 40px; border-radius: 4px 4px 0 0; position: relative; }
        .bar-v-label { color: #94a3b8; font-size: 12px; font-weight: 500; }
        .bar-v-value { position: absolute; top: -20px; width: 100%; text-align: center; color: #f8fafc; font-size: 12px; font-weight: bold; }

        .bar-chart-horizontal { display: flex; flex-direction: column; gap: 15px; }
        .bar-h-group { display: flex; flex-direction: column; gap: 6px; }
        .bar-h-header { display: flex; justify-content: space-between; font-size: 13px; }
        .bar-h-bg { width: 100%; background-color: #0f172a; height: 10px; border-radius: 6px; }
        .bar-h-fill { height: 100%; border-radius: 6px; }

        .timeline { border-left: 2px solid #334155; margin-left: 10px; padding-left: 20px; display: flex; flex-direction: column; gap: 20px; }
        .timeline-item { position: relative; }
        .timeline-item::before { content: ''; position: absolute; left: -27px; top: 2px; width: 12px; height: 12px; border-radius: 50%; background-color: #38bdf8; border: 2px solid #1e293b; }
        .time-text { font-size: 11px; color: #94a3b8; margin-bottom: 4px; display: block; }
        .event-text { font-size: 13px; color: #f8fafc; }

        .data-table-container { width: 100%; overflow-x: auto; }
        .custom-table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
        .custom-table th { padding: 12px 15px; color: #94a3b8; font-weight: 500; border-bottom: 1px solid #334155; }
        .custom-table td { padding: 12px 15px; color: #f8fafc; border-bottom: 1px solid #334155; }
        .status-badge { padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }

        .floating-btn { position: fixed; bottom: 25px; right: 25px; width: 60px; height: 60px; background-color: #38bdf8; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 28px; cursor: pointer; box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.5); border: none; z-index: 999; transition: transform 0.2s; }
        .floating-btn:hover { transform: scale(1.05); }
        
        .chat-widget { position: fixed; bottom: 100px; right: 25px; width: 400px; height: 65vh; max-height: 700px; background-color: #1e293b; border-radius: 20px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6); border: 1px solid #334155; display: flex; flex-direction: column; overflow: hidden; z-index: 1000; }
        
        @media (max-width: 768px) {
          .chat-widget { width: calc(100vw - 30px); right: 15px; bottom: 90px; height: 75vh; }
          .dashboard-grid-2, .dashboard-grid-4 { grid-template-columns: 1fr; }
          .donut-container { flex-direction: column; }
        }
        .chat-scroll::-webkit-scrollbar { width: 6px; height: 6px; }
        .chat-scroll::-webkit-scrollbar-thumb { background-color: #475569; border-radius: 4px; }
      `}</style>

      <div className="dashboard-container">
        
        {/* HEADER UNIFICADO (Logo + Usuario) */}
        <header className="dashboard-header">
          <div style={{ width: '40px', height: '40px', backgroundColor: '#38bdf8', borderRadius: '50%', display: 'flex', justifyContent: 'center', alignItems: 'center', color: '#0f172a', fontWeight: 'bold', fontSize: '20px' }}>+</div>
          <div>
            <h1 style={{ margin: 0, fontSize: '20px', color: '#f8fafc', letterSpacing: '0.5px' }}>HOSPITAL SAN JOSÉ</h1>
            <p style={{ margin: '0', fontSize: '12px', color: '#94a3b8' }}>Centro de Mando Inteligente</p>
          </div>
          
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '15px' }}>
            <div style={{ textAlign: 'right' }}>
               <span style={{ display: 'block', color: '#f8fafc', fontSize: '14px', fontWeight: 'bold' }}>{usuarioActual.username}</span>
               <span style={{ color: '#38bdf8', fontSize: '12px', textTransform: 'uppercase' }}>Rol: {usuarioActual.rol}</span>
            </div>
            <button onClick={() => setUsuarioActual(null)} style={{ background: 'transparent', border: '1px solid #ef4444', color: '#ef4444', padding: '6px 12px', borderRadius: '6px', cursor: 'pointer', fontSize: '12px', fontWeight: 'bold' }}>Salir</button>
          </div>
        </header>

        <div className="dashboard-content chat-scroll">

          {/* MENSAJE EXCLUSIVO PARA ADMINISTRADORES */}
          {String(usuarioActual.rol).toLowerCase() === 'admin' && (
            <div style={{ padding: '15px 20px', backgroundColor: 'rgba(56, 189, 248, 0.1)', border: '1px dashed #38bdf8', marginBottom: '25px', borderRadius: '10px', color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '10px' }}>
               <span style={{fontSize: '20px'}}>🛠️</span>
               <strong>Modo Administrador Activo:</strong> Tienes acceso a configuraciones críticas y métricas avanzadas del hospital.
            </div>
          )}
          
          {/* SECCIÓN 1: KPIs SUPERIORES */}
          <div className="dashboard-grid-4">
            <div className="kpi-card">
              <span className="trend-badge trend-up">+2% hoy</span>
              <span style={{fontSize: '13px', color: '#94a3b8', fontWeight: '500'}}>Ocupación UCI</span>
              <span style={{fontSize: '28px', color: '#f87171', fontWeight: 'bold'}}>85%</span>
              <div className="progress-bg"><div className="progress-fill" style={{width: '85%', backgroundColor: '#f87171'}}></div></div>
            </div>
            
            <div className="kpi-card">
              <span className="trend-badge trend-down">-5 min</span>
              <span style={{fontSize: '13px', color: '#94a3b8', fontWeight: '500'}}>Tiempo de Espera (T3)</span>
              <span style={{fontSize: '28px', color: '#fbbf24', fontWeight: 'bold'}}>45 min</span>
              <div className="progress-bg"><div className="progress-fill" style={{width: '60%', backgroundColor: '#fbbf24'}}></div></div>
            </div>
            
            <div className="kpi-card">
              <span className="trend-badge trend-up">+4 px</span>
              <span style={{fontSize: '13px', color: '#94a3b8', fontWeight: '500'}}>Cirugías Programadas</span>
              <span style={{fontSize: '28px', color: '#34d399', fontWeight: 'bold'}}>12</span>
              <div className="progress-bg"><div className="progress-fill" style={{width: '100%', backgroundColor: '#34d399'}}></div></div>
            </div>

            <div className="kpi-card">
              <span className="trend-badge trend-up">+15%</span>
              <span style={{fontSize: '13px', color: '#94a3b8', fontWeight: '500'}}>Altas Médicas Hoy</span>
              <span style={{fontSize: '28px', color: '#38bdf8', fontWeight: 'bold'}}>34</span>
              <div className="progress-bg"><div className="progress-fill" style={{width: '45%', backgroundColor: '#38bdf8'}}></div></div>
            </div>
          </div>

          {/* SECCIÓN 2: GRÁFICOS PRINCIPALES */}
          <div className="dashboard-grid-2">
            <div className="chart-card">
              <h3 className="chart-title">Distribución de Pacientes por Triage</h3>
              <div className="bar-chart-vertical">
                <div className="bar-v-group"><div className="bar-v" style={{height: '90%', backgroundColor: '#ef4444'}}><span className="bar-v-value">45</span></div><span className="bar-v-label">T1</span></div>
                <div className="bar-v-group"><div className="bar-v" style={{height: '75%', backgroundColor: '#f97316'}}><span className="bar-v-value">38</span></div><span className="bar-v-label">T2</span></div>
                <div className="bar-v-group"><div className="bar-v" style={{height: '100%', backgroundColor: '#eab308'}}><span className="bar-v-value">52</span></div><span className="bar-v-label">T3</span></div>
                <div className="bar-v-group"><div className="bar-v" style={{height: '40%', backgroundColor: '#22c55e'}}><span className="bar-v-value">20</span></div><span className="bar-v-label">T4</span></div>
                <div className="bar-v-group"><div className="bar-v" style={{height: '25%', backgroundColor: '#3b82f6'}}><span className="bar-v-value">12</span></div><span className="bar-v-label">T5</span></div>
              </div>
            </div>

            <div className="chart-card">
              <h3 className="chart-title">Estado Global de Camas</h3>
              <div className="donut-container">
                <div className="donut-chart">
                  <div className="donut-inner">
                    <span style={{color: '#f8fafc', fontSize: '24px', fontWeight: 'bold'}}>150</span>
                    <span style={{color: '#94a3b8', fontSize: '11px'}}>Total</span>
                  </div>
                </div>
                <ul className="legend-list">
                  <li className="legend-item"><div className="legend-dot" style={{backgroundColor: '#3b82f6'}}></div> Ocupadas (55%)</li>
                  <li className="legend-item"><div className="legend-dot" style={{backgroundColor: '#10b981'}}></div> Disponibles (30%)</li>
                  <li className="legend-item"><div className="legend-dot" style={{backgroundColor: '#ef4444'}}></div> En Mantenimiento (15%)</li>
                </ul>
              </div>
            </div>
          </div>

          {/* SECCIÓN 3: ACTIVIDAD Y HORIZONTALES */}
          <div className="dashboard-grid-2">
            <div className="chart-card">
              <h3 className="chart-title">Actividad Reciente del Sistema</h3>
              <div className="timeline chat-scroll" style={{maxHeight: '220px', overflowY: 'auto', paddingRight: '10px'}}>
                <div className="timeline-item"><span className="time-text">Hace 5 min</span><span className="event-text">Alerta: Stock crítico generado para <strong>Ibuprofeno 400mg</strong></span></div>
                <div className="timeline-item"><span className="time-text">Hace 12 min</span><span className="event-text">Ingreso a UCI: Paciente #8942 trasladado desde Urgencias.</span></div>
                <div className="timeline-item"><span className="time-text">Hace 45 min</span><span className="event-text">Alta médica registrada en área de Pediatría.</span></div>
                <div className="timeline-item"><span className="time-text">Hace 1 hora</span><span className="event-text">Mantenimiento preventivo completado en Quirófano B.</span></div>
              </div>
            </div>

            <div className="chart-card">
              <h3 className="chart-title">Pacientes por Especialidad</h3>
              <div className="bar-chart-horizontal chat-scroll" style={{maxHeight: '220px', overflowY: 'auto', paddingRight: '10px'}}>
                <div className="bar-h-group"><div className="bar-h-header"><span>Medicina Interna</span><span style={{color: '#94a3b8'}}>34 px</span></div><div className="bar-h-bg"><div className="bar-h-fill" style={{width: '85%', backgroundColor: '#8b5cf6'}}></div></div></div>
                <div className="bar-h-group"><div className="bar-h-header"><span>Pediatría</span><span style={{color: '#94a3b8'}}>28 px</span></div><div className="bar-h-bg"><div className="bar-h-fill" style={{width: '70%', backgroundColor: '#ec4899'}}></div></div></div>
                <div className="bar-h-group"><div className="bar-h-header"><span>Ortopedia</span><span style={{color: '#94a3b8'}}>18 px</span></div><div className="bar-h-bg"><div className="bar-h-fill" style={{width: '45%', backgroundColor: '#38bdf8'}}></div></div></div>
                <div className="bar-h-group"><div className="bar-h-header"><span>Ginecología</span><span style={{color: '#94a3b8'}}>15 px</span></div><div className="bar-h-bg"><div className="bar-h-fill" style={{width: '35%', backgroundColor: '#f43f5e'}}></div></div></div>
              </div>
            </div>
          </div>

          {/* SECCIÓN 4: TABLA FULL WIDTH */}
          <div className="chart-card" style={{marginBottom: '50px'}}>
            <h3 className="chart-title">Últimos Ingresos Registrados</h3>
            <div className="data-table-container chat-scroll">
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>ID Ingreso</th><th>Fecha y Hora</th><th>Vía de Ingreso</th><th>Servicio Asignado</th><th>Estado</th>
                  </tr>
                </thead>
                <tbody>
                  <tr><td>#ING-8942</td><td>Hoy, 08:30 AM</td><td>Urgencias</td><td>UCI</td><td><span className="status-badge" style={{backgroundColor: 'rgba(239,68,68,0.2)', color: '#ef4444'}}>Crítico</span></td></tr>
                  <tr><td>#ING-8943</td><td>Hoy, 09:15 AM</td><td>Consulta Externa</td><td>Pediatría</td><td><span className="status-badge" style={{backgroundColor: 'rgba(52,211,153,0.2)', color: '#34d399'}}>Estable</span></td></tr>
                  <tr><td>#ING-8944</td><td>Hoy, 10:05 AM</td><td>Remitido</td><td>Medicina Interna</td><td><span className="status-badge" style={{backgroundColor: 'rgba(251,191,36,0.2)', color: '#fbbf24'}}>Observación</span></td></tr>
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </div>

      {/* BOTÓN FLOTANTE Y WIDGET DEL CHAT */}
      <button className="floating-btn" onClick={() => setIsChatOpen(!isChatOpen)}>🤖</button>

      {isChatOpen && (
        <aside className="chat-widget">
          <header style={{ padding: '15px', backgroundColor: '#0f172a', borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '20px' }}>🤖</span>
              <span style={{ color: '#f8fafc', fontWeight: 'bold', fontSize: '15px' }}>SanitasIA Asistente</span>
            </div>
            <button onClick={() => setIsChatOpen(false)} style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '18px', cursor: 'pointer' }}>✖</button>
          </header>

          <div className="chat-scroll" style={{ flex: 1, overflowY: 'auto', padding: '15px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
            {mensajes.map((msg, index) => (
              <div key={index} style={{ display: 'flex', flexDirection: 'column', alignItems: msg.rol === 'usuario' ? 'flex-end' : 'flex-start' }}>
                {(msg.texto || msg.error) && (
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-end', maxWidth: '92%' }}>
                    {msg.rol === 'ia' && <div style={{ width: '24px', height: '24px', backgroundColor: '#38bdf8', borderRadius: '50%', flexShrink: 0, display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '12px' }}>🤖</div>}
                    <div style={{ padding: '12px 16px', backgroundColor: msg.rol === 'usuario' ? '#0284c7' : '#334155', color: '#f8fafc', borderRadius: msg.rol === 'usuario' ? '16px 16px 4px 16px' : '16px 16px 16px 4px', fontSize: '14px', lineHeight: '1.4', boxShadow: '0 2px 4px rgba(0,0,0,0.2)' }}>
                      {msg.texto && <p style={{ margin: 0 }}>{msg.texto}</p>}
                      {msg.error && <p style={{ margin: 0, color: '#f87171' }}>{msg.error}</p>}
                    </div>
                  </div>
                )}

                {msg.opcionesRapidas && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '10px', paddingLeft: '32px' }}>
                    {msg.opcionesRapidas.map((opcion, i) => (
                      <button key={i} onClick={() => enviarOpcionRapida(opcion)} style={{ padding: '8px 12px', backgroundColor: '#0f172a', border: '1px solid #475569', borderRadius: '16px', color: '#cbd5e1', fontSize: '12px', cursor: 'pointer', transition: 'all 0.2s' }}>{opcion}</button>
                    ))}
                  </div>
                )}

                {msg.resultados && Array.isArray(msg.resultados) && msg.resultados.length > 0 && (
                  <div className="chat-scroll" style={{ marginLeft: msg.rol === 'ia' ? '32px' : '0', marginTop: '10px', maxWidth: msg.rol === 'ia' ? 'calc(100% - 32px)' : '100%', width: '100%', maxHeight: '250px', overflowX: 'auto', overflowY: 'auto', backgroundColor: '#0f172a', borderRadius: '8px', border: '1px solid #334155' }}>
                    <table className="custom-table" style={{ fontSize: '12px' }}>
                      <thead>
                        <tr>
                          {Object.keys(msg.resultados[0]).map((columna, i) => (
                            <th key={i} style={{ padding: '8px 12px', textAlign: 'left', color: '#38bdf8', position: 'sticky', top: '0', backgroundColor: '#1e293b', borderBottom: '1px solid #334155', zIndex: 1 }}>{columna}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {msg.resultados.map((fila, i) => (
                          <tr key={i} style={{ borderBottom: '1px solid #1e293b' }}>
                            {Object.values(fila).map((valor, j) => (
                              <td key={j} style={{ padding: '8px 12px', wordBreak: 'break-word', minWidth: '100px', color: '#f8fafc' }}>{valor !== null ? String(valor) : '-'}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-end' }}>
                 <div style={{ width: '24px', height: '24px', backgroundColor: '#38bdf8', borderRadius: '50%', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '12px' }}>🤖</div>
                 <div style={{ padding: '10px 14px', backgroundColor: '#334155', color: '#94a3b8', borderRadius: '16px 16px 16px 4px', fontSize: '13px', fontStyle: 'italic' }}>Consultando base de datos...</div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <div style={{ padding: '12px', backgroundColor: '#0f172a', borderTop: '1px solid #334155' }}>
            <form onSubmit={consultarIA} style={{ display: 'flex', backgroundColor: '#1e293b', borderRadius: '20px', padding: '4px 10px', alignItems: 'center', border: '1px solid #334155', gap: '8px' }}>
              <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Pregúntale a la IA..." style={{ flex: 1, backgroundColor: 'transparent', border: 'none', color: '#f8fafc', padding: '8px 5px', outline: 'none', fontSize: '13px', width: '100%' }} disabled={loading} />
              <button type="submit" disabled={loading || !input.trim()} style={{ background: '#38bdf8', border: 'none', color: '#0f172a', cursor: 'pointer', padding: '8px', borderRadius: '50%', display: 'flex', justifyContent: 'center', alignItems: 'center', opacity: (loading || !input.trim()) ? 0.5 : 1 }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
              </button>
            </form>
          </div>
        </aside>
      )}
    </>
  );
}

export default App;