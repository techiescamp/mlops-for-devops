import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { prism } from 'react-syntax-highlighter/dist/esm/styles/prism'
import './chatbot.css'
import axiosCustomApi from '../axiosLib'


const Chatbot = () => {
    const [loading, setLoading] = useState(false)
    const [inputText, setInputText] = useState('')
    const [messages, setMessages] = useState([])
    const [showDetails, setShowDetails] = useState(false)
    const messageEndRef = useRef(null)

    // scroll to bottom of the chat when new messages are added
    const scrollToBottom = () => {
        messageEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
    useEffect(() => {
        scrollToBottom()
    },[messages])

    // form submit function
    const handleSubmit = async(e) => {
        e.preventDefault()
        if(!inputText.trim()) return

        // add user message to the client
        const userMessage = {
            role: 'user',
            content: inputText
        }
        setMessages(prev => [...prev, userMessage])
        setLoading(true)

        try {
            const res = await axiosCustomApi.post('/query', { query: inputText })
            const { answer, sources } = res.data
            setInputText('')
            // add bot message to messages
            const botMessage = {
                role: 'bot',
                content: answer,
                sources
            }
            setMessages(prev => [...prev, botMessage])
        } catch(err) {
            console.error('Error: ', err)
            const errorMessage = {
                role: 'bot',
                content: 'Sorry, something went wrong. Please try again.'
            }
            setMessages(prev => [...prev, errorMessage])
        }
        finally {
            setLoading(false)
        }
    }

    // code syntax higlighter
    function CodeBlock({inline, children, className, ...props}) {
        const match = /language-(\w+)/.exec(className || '')
        const language = match ? match[1] : ''
        // Handle copy functionality
        const handleCopy = () => {
            const codeText = String(children).replace(/\n$/, ''); // Get the code content
            navigator.clipboard.writeText(codeText) // Copy to clipboard
                .then(() => {
                    alert('Code copied!');
                })
                .catch(err => {
                    alert('Failed to copy: ', err);
                });
        };

        return !inline && language && (
            <div className='code-container'>
                <div className='code-language'>
                    {language.toLowerCase()}
                    <button className='copy' onClick={handleCopy}>copy</button>
                </div>

                <SyntaxHighlighter className='code-highlighter' style={prism} PreTag='div' language={match[1]} {...props} >
                    {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
            </div>
        )
    }

    // show details button
    const handleDetails = () => {
        setShowDetails(prev => !prev)
    } 

  return (
    <div className='container'>
        <div className='chatbot-messages'>
            {messages.length === 0 ? (
                <div className='chatbot-welcome'>
                    <p>Hello! I'm your chatbot assistant. Ask me anything about the React and I will help you with your doubts.</p>
                </div>
            ) : (
                messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.role}`}>
                        <div className='message-content'>
                            <ReactMarkdown components={{ code: CodeBlock }}>
                                {msg.content}
                            </ReactMarkdown>
                            {msg.role === 'bot' && msg.sources && (
                                <div className='message-details'>
                                    <button onClick={handleDetails}>Details</button>
                                    <div className={showDetails ? 'active' : 'not-active'}>
                                        <ul className='sources'>
                                            <p><strong>Sources: </strong></p>
                                            {msg.sources.map((source, i) => (
                                                <li key={i}>{source}</li>
                                            ))}
                                        </ul>  
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                ))
            )}
            {/* add scroll effect */}
            <div ref={messageEndRef} />
        </div>
        <form className='chatbot-form' onSubmit={handleSubmit}>
            <input 
                type='text'
                value={inputText}
                onChange={e => setInputText(e.target.value)}
                placeholder="Ask me anything..."
                disabled={loading}
            />
            <button type='submit' disabled={loading}>
                {loading ? 'Loading...' : 'Send'}
            </button>
        </form>
    </div>
  )
}

export default Chatbot