import { React } from 'react'
import './App.css';
import Chatbot from './components/Chatbot';

function App() {

  return (
    <div className="App">
      <header className='header'>
        <h1>
          <span className='logo'>DM</span>
          <span>DocuMancer</span>
        </h1>
        <div className='header-details'>
          <p><b>Model:</b> gpt-4o-mini</p>
          <p><b>Embeddings:</b> text-embedding-3-small</p>
          <p><b>Vector store:</b> FAISS</p>
        </div>
        <p className='copyright'>Powered by <span>&copy; techiescamp 2025</span></p>
      </header>
      
      <Chatbot />
    </div>
  );
}

export default App;
