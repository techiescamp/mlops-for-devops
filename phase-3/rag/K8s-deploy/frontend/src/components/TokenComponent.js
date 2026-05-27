import React from 'react'
import TokenImg from '../token.png'


const TokenComponent = ({ count, name }) => {
  return (
    <p className='token-container'> 
        <img src={TokenImg} alt="token" className='token-img' />
        {count} 
        <strong>{name}</strong>  
    </p>

  )
}

export default TokenComponent