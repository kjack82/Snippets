import ReactDOM from 'react-dom/client'

const rootEl = document.querySelector('#root')

ReactDOM.createRoot(rootEl).render(
<main>
<h1>Hello, React!</h1>
<p>What is 1 +1?</p>
<p>The answer is {1+1}!</p>
</main>)