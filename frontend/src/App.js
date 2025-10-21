import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'react-widgets/styles.css';
import { BrowserRouter } from 'react-router-dom';
import { NotificationProvider } from './contexts/NotificationContext';
import MainNav from './components/MainNav/MainNav';
import MainContent from './components/MainContent/MainContent';


function App() {
    return (
        <div className="App">
            <NotificationProvider>
                <BrowserRouter>
                    <MainNav />
                    <MainContent />
                </BrowserRouter>
            </NotificationProvider>
        </div>
    );
}

export default App;
