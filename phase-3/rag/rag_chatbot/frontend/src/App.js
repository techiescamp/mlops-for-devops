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
      </header>
      
      <Chatbot />
    </div>
  );
}

export default App;
