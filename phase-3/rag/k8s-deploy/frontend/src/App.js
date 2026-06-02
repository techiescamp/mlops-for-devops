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
        <p className='copyright'>Powered by <span>&copy; techiescamp 2025</span></p>
      </header>
      
      <Chatbot />
    </div>
  );
}

export default App;
